import unreal
import re

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
    @unreal.ufunction(static=True, params=[unreal.AssetData, str], ret=unreal.AssetData, meta=dict(Category="Cinematic Query"))
    def get_best_sub_sequence(main_shot_data, sub_type):
        """
        메인 샷이 '실제로 참조하고 있는' 하위 시퀀스를 찾아냅니다.
        (이름이 같아도 연결이 안 되어 있으면 무시합니다.)
        """
        # 데이터가 유효하지 않으면 즉시 리턴
        if not main_shot_data.is_valid():
            return unreal.AssetData()

        # 1. 검색할 타겟 폴더 키워드 결정 (/ANI/, /FX/ 등)
        target_keyword = ""
        if sub_type == "ANI": target_keyword = "/Subsequence/ANI/"
        elif sub_type == "FX": target_keyword = "/Subsequence/FX/"
        elif sub_type == "LIT": target_keyword = "/Subsequence/LIT/"
        else: return unreal.AssetData()

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

        # 메인 샷이 참조하는 모든 패키지 이름 가져오기
        dependencies = asset_reg.get_dependencies(main_pkg, dep_options)

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
                        # 5.1 이상에서는 asset_class_path 사용 권장, 하위 호환을 위해 asset_class도 체크
                        class_name = str(asset_item.asset_class_path.asset_name)
                        if class_name == "LevelSequence":
                            return asset_item

        # 못 찾았으면 빈 데이터 리턴
        return unreal.AssetData()

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