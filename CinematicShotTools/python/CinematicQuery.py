import unreal
import re
import os

@unreal.uclass()
class CinematicQueryLib(unreal.BlueprintFunctionLibrary):

    # --- 폴더 경로 상수 ---
    ROOT_PATH = "/Game/A_Cinematic_Workspace/Sequencer/PrologueTrailer"
    SHOT_ROOT = f"{ROOT_PATH}/Shot"

    # ----------------------------------------------------------------
    # [1] 메인 샷 리스트 가져오기 (기존과 동일)
    # ----------------------------------------------------------------
    @unreal.ufunction(static=True, ret=unreal.Array(unreal.AssetData), meta=dict(Category="Cinematic Query"))
    def get_main_shot_list():
        asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()
        filter = unreal.ARFilter(
            class_names=["LevelSequence"],
            recursive_paths=True,
            package_paths=[CinematicQueryLib.SHOT_ROOT]
        )
        all_assets = asset_reg.get_assets(filter)
        clean_list = []
        
        # 서브 폴더나 백업 폴더 제외하고 순수 샷만 골라내기
        for asset in all_assets:
            path_str = str(asset.package_name)
            if "/Legacy/" in path_str or "/Backup/" in path_str: continue
            if "/Subsequence/" in path_str: continue
            clean_list.append(asset)
            
        # 이름순 정렬
        clean_list.sort(key=lambda x: str(x.asset_name))
        return clean_list

    # ----------------------------------------------------------------
    # [2] ★핵심★ 레퍼런스(Dependency) 기반 서브 시퀀스 찾기
    # ----------------------------------------------------------------
    @unreal.ufunction(static=True, params=[unreal.AssetData, str], ret=unreal.Array(unreal.AssetData), meta=dict(Category="Cinematic Query"))
    def get_sub_sequences(main_shot_data, sub_type):
        """
        메인 샷이 '실제로 참조하고 있는' 하위 시퀀스 목록을 찾아냅니다.
        (과거에는 1개만 찾았지만, 이제는 다중 서브 시퀀스도 지원합니다.)
        """
        # 데이터가 유효하지 않으면 빈 배열 리턴
        if not main_shot_data.is_valid():
            return []

        # 1. 검색할 타겟 폴더 키워드 결정 (/ANI/, /FX/ 등)
        target_keyword = ""
        if sub_type == "ANI": target_keyword = "/Subsequence/ANI/"
        elif sub_type == "FX": target_keyword = "/Subsequence/FX/"
        elif sub_type == "LIT": target_keyword = "/Subsequence/LIT/"
        else: return []

        # 2. 에셋 레지스트리에서 '의존성(Dependencies)' 조회
        asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()
                
        # 옵션: Soft Reference와 Hard Reference 모두 추적
        dep_options = unreal.AssetRegistryDependencyOptions(
            include_soft_management_references=True, 
            include_hard_management_references=True, 
            include_searchable_names=False, 
            include_soft_package_references=True
        )
        
        # 메인 샷 패키지 이름
        main_pkg = main_shot_data.package_name

        # [중요] get_dependencies 는 기본적으로 Direct Dependency 만 리턴합니다.
        # 간접 참조 문제 해결을 위해 재귀(Recursion) 호출을 막아야 합니다.
        dependencies = asset_reg.get_dependencies(main_pkg, dep_options)

        found_list = []

        # 3. 의존성 목록 순회하며 찾기
        for dep_package_name in dependencies:
            dep_path_str = str(dep_package_name)
            
            # 조건 1: 경로에 해당 키워드(/ANI/ 등)가 포함되어 있는가?
            if target_keyword in dep_path_str:
                
                # 조건 2: 실제로 그 에셋이 'Level Sequence' 인가?
                # (패키지 이름으로 에셋 데이터를 가져와서 확인)
                found_assets = asset_reg.get_assets_by_package_name(dep_package_name)
                
                if found_assets:
                    # 패키지 안에 여러 에셋이 있을 수 있으니 순회 (보통은 1개)
                    for asset_item in found_assets:
                        # 클래스 확인 (LevelSequence인지)
                        class_name = str(asset_item.asset_class_path.asset_name)
                        if class_name == "LevelSequence":
                            found_list.append(asset_item)

        return found_list

    # ----------------------------------------------------------------
    # [3] 섹션 분류 (0000, 1000...)
    # ----------------------------------------------------------------
    @unreal.ufunction(static=True, ret=unreal.Array(str), meta=dict(Category="Cinematic Query"))
    def get_existing_section_keys():
        all_shots = CinematicQueryLib.get_main_shot_list()
        keys = set()
        for shot in all_shots:
            shot_name = str(shot.asset_name)
            match = re.search(r"Shot_(\d{4})", shot_name)
            if match:
                keys.add(match.group(1)[0]) # 첫 글자 ("1")
            else:
                keys.add("Etc")
        return sorted(list(keys))

    @unreal.ufunction(static=True, params=[str], ret=unreal.Array(unreal.AssetData), meta=dict(Category="Cinematic Query"))
    def get_shots_by_section_key(section_key):
        all_shots = CinematicQueryLib.get_main_shot_list()
        result = []
        for shot in all_shots:
            shot_name = str(shot.asset_name)
            match = re.search(r"Shot_(\d{4})", shot_name)
            if match:
                if match.group(1)[0] == section_key:
                    result.append(shot)
            elif section_key == "Etc":
                result.append(shot)
        return result

    @unreal.ufunction(static=True, params=[unreal.Array(str)], ret=unreal.Map(str, str), meta=dict(Category="Cinematic Query"))
    def get_svn_states_batch(asset_paths):

        # 1. 소스 컨트롤 켜져있는지 확인
        if not unreal.SourceControl.is_enabled():
            return {}

        content_dir = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir())
        
        file_to_asset_map = {}
        valid_file_paths = []

        # 2. 경로 변환 및 수집
        for asset_path in asset_paths:
            safe_path = asset_path.split('.')[0] if "." in asset_path else asset_path
            
            if safe_path.startswith("/Game/"):
                rel_path = safe_path[6:]
                full_path_base = os.path.join(content_dir, rel_path)
                
                target_file = ""
                if os.path.exists(full_path_base + ".uasset"):
                    target_file = full_path_base + ".uasset"
                elif os.path.exists(full_path_base + ".umap"):
                    target_file = full_path_base + ".umap"
                
                if target_file:
                    valid_file_paths.append(target_file)
                    # 정규화하여 저장 (경로 매칭 정확도 향상)
                    norm_path = os.path.normpath(target_file)
                    file_to_asset_map[norm_path] = asset_path

        if not valid_file_paths:
            return {}

        # 3. 일괄 쿼리 실행
        states = unreal.SourceControl.query_file_states(valid_file_paths, True)

        results = {}

        # [핵심] 호환성 헬퍼 함수 (함수면 호출하고, 변수면 값 가져옴)
        def check(obj, attr_name):
            if hasattr(obj, attr_name):
                val = getattr(obj, attr_name)
                if callable(val):
                    return val()
                return val
            return False

        # 4. 결과 매핑 및 상태 판별
        for state in states:
            if not state or not state.is_valid:
                continue
                
            status_str = "UNKNOWN"
            try:
                # [우선순위 1] 충돌 (제일 위험)
                if check(state, 'is_conflicted'): 
                    status_str = "CONFLICTED"
                
                # [우선순위 2] 남이 잠금
                elif check(state, 'is_checked_out_other'): 
                    status_str = "LOCKED_BY_OTHER"
                
                # [우선순위 3] 싱크 필요 (현재 버전이 최신이 아님)
                # is_current가 False라면 서버에 새 버전이 있다는 뜻
                elif not check(state, 'is_current'):
                    status_str = "NEEDS_SYNC"

                # [우선순위 4] 내가 잠금
                elif check(state, 'is_checked_out'): 
                    status_str = "CHECKED_OUT"

                # [우선순위 5] 신규 추가
                elif check(state, 'is_added'): 
                    status_str = "ADDED"

                # [우선순위 6] 수정됨 (체크아웃 없이 수정)
                elif check(state, 'is_modified'): 
                    status_str = "MODIFIED"

                # [우선순위 7] 깨끗함
                else: 
                    status_str = "CLEAN"

            except Exception as e:
                # 에러 나도 멈추지 말고 다음 파일로
                print(f"Error parsing state: {e}")
                continue

            # 파일 경로로 원본 에셋 경로 찾기
            fname = os.path.normpath(state.filename)
            if fname in file_to_asset_map:
                original_asset_path = file_to_asset_map[fname]
                results[original_asset_path] = status_str

        return results