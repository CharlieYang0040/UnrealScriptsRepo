import unreal
import re
import os
from collections import deque

# -----------------------------------------------------------------------------
# 스크립트 설정 및 전역 변수
# -----------------------------------------------------------------------------

# 파일 유형 약어 매핑: 필요에 따라 이 사전을 수정하거나 확장하세요.
ASSET_TYPE_MAPPING = {
    "Texture2D": "T", "TextureCube": "TC", "TextureRenderTarget2D": "TRT",
    "Material": "M", "MaterialInstanceConstant": "MI", "MaterialFunction": "MF",
    "MaterialParameterCollection": "MPC", "StaticMesh": "SM", "SkeletalMesh": "SK",
    "AnimSequence": "AS", "AnimMontage": "AM", "BlendSpace": "BS",
    "AnimBlueprint": "ABP", "Skeleton": "SKEL", "Blueprint": "BP",
    "DataTable": "DT", "UserDefinedEnum": "ENUM", "UserDefinedStruct": "STRUCT",
    "LevelSequence": "SEQ", "NiagaraSystem": "NS", "NiagaraEmitter": "NE",
    "StaticMeshActor": "SMA", "SkeletalMeshActor": "SKA", "Level": "MAP", "World": "MAP"
}

# 작업 경로의 고유 식별자 (이 경로가 포함된 에셋을 이동시킴)
WORKSPACE_IDENTIFIER = "/A_Cinematic_Workspace/"
# 빌드 포함 경로의 기본 경로
COOK_PATH_BASE = "/Game/Cinematic/"


class CinematicAssetSanitizer:
    """
    시네마틱 에셋 참조 및 네이밍 규칙을 자동으로 수정하는 메인 클래스
    """
    def __init__(self, error_handling_policy):
        self.logs = []
        self.stop_on_error = (error_handling_policy == "Stop on first error")
        self.asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
        # EditorAssetLibrary 대신 EditorAssetSubsystem을 사용합니다.
        # 서브시스템은 상태를 가지므로 복잡한 에셋 작업에 더 안정적입니다.
        self.editor_asset_subsystem = unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)

    def log(self, message, level="info"):
        """로그를 기록하고 언리얼 로그에 출력하는 함수"""
        # 언리얼 로그에 먼저 출력 (레벨에 따라 다른 함수 사용)
        if level == "warning":
            unreal.log_warning(message)
        elif level == "error":
            unreal.log_error(message)
        else:  # info, success 등
            unreal.log(message)

        # UI 리포트용 로그 저장 (접두사 포함)
        prefix_map = {"info": "[INFO]", "warning": "[WARNING]", "error": "[ERROR]", "success": "[SUCCESS]"}
        prefix = prefix_map.get(level.lower(), "[INFO]")
        log_message = f"{prefix} {message}"
        self.logs.append(log_message)

    def svn_checkout_files(self, asset_paths):
        """
        지정된 에셋 경로에 해당하는 파일들을 SVN에서 체크아웃(Lock)하는 함수.
        EditorAssetSubsystem.checkout_asset API를 사용합니다.
        """
        self.log(f"SVN Checking out {len(asset_paths)} asset(s) using EditorAssetSubsystem...")
        
        all_succeeded = True
        for asset_path in asset_paths:
            # checkout_asset은 에셋이 존재하지 않거나 다른 이유로 실패하면 False를 반환합니다.
            if not self.editor_asset_subsystem.does_asset_exist(asset_path):
                self.log(f"Asset to checkout does not exist, skipping: {asset_path}", "warning")
                continue # 존재하지 않는 에셋은 체크아웃을 시도하지 않음

            # EditorAssetSubsystem.checkout_asset를 직접 호출하여 체크아웃을 시도합니다.
            success = self.editor_asset_subsystem.checkout_asset(asset_path)
            if success:
                self.log(f"  - Checkout successful for: {asset_path}", "success")
            else:
                self.log(f"  - Checkout FAILED for: {asset_path}", "error")
                all_succeeded = False
        
        return all_succeeded

    def _get_all_workspace_dependencies(self, initial_asset_paths):
        """
        초기 에셋 목록에서 시작하여 작업 공간 내의 모든 재귀적 의존성을 찾습니다.
        """
        self.log(f"Finding all dependencies for {len(initial_asset_paths)} initial asset(s)...")
        
        # 의존성 검색을 위한 옵션. 패키지 의존성만 검색합니다.
        # 'include_manage_references'는 이전 버전의 API와 호환되지 않을 수 있으므로 제거합니다.
        dependency_options = unreal.AssetRegistryDependencyOptions(
            include_soft_package_references=True, 
            include_hard_package_references=True,
            include_searchable_names=False
        )

        assets_to_scan = deque(initial_asset_paths)
        all_dependencies = set(initial_asset_paths)
        
        scanned_assets = set() # 이미 스캔한 에셋을 추적하여 중복 작업을 피함

        self.log(f"Starting dependency scan loop. Initial queue size: {len(assets_to_scan)}")
        loop_iteration = 0
        while assets_to_scan:
            loop_iteration += 1
            if loop_iteration > 5000: # 매우 많은 수의 에셋을 대비해 안전장치 강화
                self.log(f"Dependency scan loop exceeded 5000 iterations. Aborting. This might indicate a circular dependency or an extremely large number of assets. Total assets found so far: {len(all_dependencies)}", "error")
                break

            asset_path = assets_to_scan.popleft()
            if asset_path in scanned_assets:
                continue
            
            self.log(f"[DepScan {loop_iteration}] Scanning: {os.path.basename(asset_path)} (Queue size: {len(assets_to_scan)})")
            scanned_assets.add(asset_path)

            try:
                # get_dependencies는 FName 배열을 반환하므로 문자열로 변환해야 합니다.
                self.log(f"  -> Querying dependencies for {os.path.basename(asset_path)}...")
                dependencies = self.asset_registry.get_dependencies(asset_path, dependency_options)
                self.log(f"  -> Query finished. Found {len(dependencies) if dependencies else 0} dependencies.")
                
                if not dependencies:
                    continue
                
                for dep_path_name in dependencies:
                    dep_path = str(dep_path_name)
                    # 작업 공간 내에 있고 아직 목록에 없는 에셋만 추가합니다.
                    if WORKSPACE_IDENTIFIER in dep_path and dep_path not in all_dependencies:
                        all_dependencies.add(dep_path)
                        assets_to_scan.append(dep_path)
                        self.log(f"    - Added to queue: {os.path.basename(dep_path)}", "info")

            except Exception as e:
                self.log(f"Could not get dependencies for {asset_path}: {e}", "warning")

        self.log(f"Dependency scan finished. Found a total of {len(all_dependencies)} assets to process (including dependencies).", "success")
        return all_dependencies

    def parse_cook_log(self, cook_log_text):
        """Cook 로그 텍스트를 파싱하여 (소스, 타겟) 쌍의 리스트를 반환"""
        self.log("Parsing cook log...")
        pattern = re.compile(
            r"Source package: (.*?)\s*\n\s*Target package: (.*?)\s*\n",
            re.MULTILINE
        )
        matches = pattern.findall(cook_log_text)
        
        if not matches:
            self.log("No valid 'Source package' -> 'Target package' references found in the log.", "warning")
            return []
            
        self.log(f"Found {len(matches)} problematic references.", "success")
        return list(set(matches)) # 중복 제거

    def _process_single_asset(self, asset_path_to_process, all_paths_in_workspace):
        """
        한 개의 에셋에 대해 이동 및 이름 변경 작업을 수행합니다.
        성공 시 (생성된 리디렉터 경로 set, None)을 반환합니다.
        참조 문제로 실패 시 (None, 블로킹 에셋 경로)를 반환합니다.
        """
        new_redirectors = set()
        self.log(f"--------------------------------------------------")
        self.log(f"Processing asset: {os.path.basename(asset_path_to_process)}")

        # 0. 수정 전, AssetData에서 미리 클래스 정보를 가져옵니다.
        #    rename 후 불안정한 상태에서 load_asset을 호출하는 것을 피하기 위함입니다.
        asset_data = self.editor_asset_subsystem.find_asset_data(asset_path_to_process)
        if not asset_data.is_valid():
            self.log(f"Could not find valid asset data for {asset_path_to_process}. Skipping this asset.", "warning")
            return None, None  # 치명적이지 않은 오류로 간주하고 건너뜁니다.
        # asset_class_path.get_asset_name() 대신 더 안정적인 asset_class 속성을 직접 사용합니다.
        asset_class = str(asset_data.asset_class)

        try:
            # 원자적 연산을 위해 전체 프로세스를 하나의 트랜잭션으로 묶습니다.
            # 이렇게 하면 rename 도중 다른 시스템이 반응하여 발생하는 크래시를 방지할 수 있습니다.
            with unreal.ScopedEditorTransaction(f"Sanitize Asset: {os.path.basename(asset_path_to_process)}") as trans:
                # 1. 에셋 이동
                new_path_after_move = asset_path_to_process.replace(WORKSPACE_IDENTIFIER, "/Cinematic/")
                
                # 경로에 'BackUp' 폴더가 포함되어 있으면 제거합니다.
                if "/BackUp/" in new_path_after_move:
                    self.log(f"Path contains 'BackUp' folder. Adjusting destination path...")
                    path_parts = new_path_after_move.split('/')
                    filtered_parts = [part for part in path_parts if part != "BackUp"]
                    new_path_after_move = "/".join(filtered_parts)
                    self.log(f"  -> New adjusted path: {new_path_after_move}")
                
                # 목적지에 에셋이 이미 있다면 백업합니다.
                if self.editor_asset_subsystem.does_asset_exist(new_path_after_move):
                    self.log(f"Asset already exists at destination: {new_path_after_move}", "warning")
                    backup_dir = os.path.dirname(new_path_after_move) + "/_Backup"
                    backup_path = os.path.join(backup_dir, os.path.basename(new_path_after_move))
                    
                    self.log(f"Attempting to back up existing asset to: {backup_path}")
                    if not self.svn_checkout_files([new_path_after_move]):
                        raise Exception(f"Failed to SVN checkout existing asset for backup: {new_path_after_move}")
                    self.editor_asset_subsystem.rename_asset(new_path_after_move, backup_path)
                    self.log(f"Backup successful.", "success")

                self.log(f"Moving asset: {asset_path_to_process} -> {new_path_after_move}")
                if not self.svn_checkout_files([asset_path_to_process]):
                    raise Exception(f"Failed to SVN checkout target asset for move: {asset_path_to_process}")
                
                rename_success = self.editor_asset_subsystem.rename_asset(asset_path_to_process, new_path_after_move)

                if not rename_success:
                    # 이동 실패 시, 참조하고 있는 에셋을 찾아 반환합니다.
                    referencers = self.editor_asset_subsystem.find_package_referencers_for_asset(asset_path_to_process)
                    for ref_name in referencers:
                        ref = str(ref_name)
                        # 작업 공간 내의 에셋이면서, 아직 처리 목록에 없는 경우
                        if WORKSPACE_IDENTIFIER in ref and ref in all_paths_in_workspace:
                            self.log(f"Asset move failed. Found blocking reference: {os.path.basename(ref)}", "warning")
                            # 트랜잭션이 진행 중이므로 예외를 발생시켜 롤백되도록 유도하고, 블로커를 반환합니다.
                            # 하지만 여기서는 블로커를 직접 반환하여 상위 루프에서 처리하도록 합니다.
                            return None, ref # 블로커 반환
                    raise Exception("Asset move failed for an unknown reason (no workspace referencers found).")
                
                self.log(f"Move successful.", "success")
                new_redirectors.add(asset_path_to_process)

                # 2. 에셋 이름 변경 (이동된 새 경로 기준)
                type_abbr = ASSET_TYPE_MAPPING.get(asset_class, None)
                asset_name = os.path.basename(new_path_after_move)
                
                if type_abbr and not asset_name.startswith(f"CN_{type_abbr}_"):
                    new_name_base = f"CN_{type_abbr}_{asset_name}"
                    if asset_name.startswith("CN_"):
                        new_name_base = f"CN_{type_abbr}_{asset_name[3:]}"
                    
                    final_name_path = os.path.join(os.path.dirname(new_path_after_move), new_name_base)
                    
                    self.log(f"Applying naming convention: {asset_name} -> {new_name_base}")
                    self.editor_asset_subsystem.rename_asset(new_path_after_move, final_name_path)
                    self.log(f"Rename successful.", "success")
                    new_redirectors.add(new_path_after_move)

        except Exception as e:
            # 트랜잭션은 예외 발생 시 자동으로 롤백됩니다.
            self.log(f"An error occurred during asset processing '{os.path.basename(asset_path_to_process)}': {e}", "error")
            if self.stop_on_error: raise
            return None, None # 치명적이지 않은 오류는 건너뜁니다.
        
        return new_redirectors, None

    def run(self, cook_log):
        """메인 실행 함수"""
        
        # 1. 쿡 로그에서 초기 작업 대상 에셋을 수집합니다.
        self.log("Parsing cook log to find initial assets...")
        initial_assets = set()
        fix_list = self.parse_cook_log(cook_log)
        if not fix_list:
            return self.logs

        for _, target_path in fix_list:
            if WORKSPACE_IDENTIFIER in target_path and self.editor_asset_subsystem.does_asset_exist(target_path):
                initial_assets.add(target_path)
        
        if not initial_assets:
            self.log("No existing assets from the cook log are located in the workspace.", "info")
            return self.logs

        # 2. 초기 에셋의 모든 작업 공간 내 의존성을 재귀적으로 찾습니다.
        all_assets_in_scope = self._get_all_workspace_dependencies(initial_assets)
        if not all_assets_in_scope:
             self.log("Could not identify any assets to process.", "warning")
             return self.logs

        # 3. 재귀적 의존성 해결 및 에셋 처리 루프
        assets_to_process = list(all_assets_in_scope)
        processed_assets = set()
        redirectors_to_fix = set()
        # 최대 재시도 횟수를 전체 에셋 수에 비례하여 설정
        max_retries = len(assets_to_process) * len(assets_to_process) + 20 

        with unreal.ScopedSlowTask(len(assets_to_process), "Processing Cinematic Assets...") as slow_task:
            slow_task.make_dialog(True)
            
            while assets_to_process and max_retries > 0:
                max_retries -= 1
                
                asset_path = assets_to_process.pop(0) # 큐의 맨 앞에서 하나를 꺼냅니다.

                if asset_path in processed_assets:
                    continue # 이미 성공적으로 처리된 에셋은 건너뜁니다.
                
                # slow_task의 전체 단계 수를 동적으로 업데이트하는 로직을 제거하고, 메시지만 업데이트합니다.
                slow_task.enter_progress_frame(1, f"Processing [{len(processed_assets) + 1}/{len(all_assets_in_scope)}]: {os.path.basename(asset_path)}")

                try:
                    # 전체 에셋 목록을 `_process_single_asset`에 전달합니다.
                    new_redirectors, blocker = self._process_single_asset(asset_path, all_assets_in_scope)

                    if blocker:
                        # 처리 실패, 블로커를 맨 앞에 두고 현재 에셋을 맨 뒤에 다시 추가
                        self.log(f"Re-queuing {os.path.basename(blocker)} to be processed first.", "info")
                        assets_to_process.insert(0, blocker)
                        assets_to_process.append(asset_path) # 현재 실패한 에셋은 나중에 다시 시도
                        # all_assets_in_scope는 이미 모든 의존성을 포함하므로 업데이트할 필요가 없습니다.
                    
                    elif new_redirectors is not None:
                        # 처리 성공
                        processed_assets.add(asset_path)
                        redirectors_to_fix.update(new_redirectors)
                    
                    # new_redirectors가 None이면 치명적이지 않은 오류로 간주하고 그냥 넘어감 (건너뜀)

                except Exception:
                    # _process_single_asset에서 예외가 발생하면 루프를 중단합니다.
                    import traceback
                    self.log(f"A critical error occurred while processing '{os.path.basename(asset_path)}'. See traceback below.", "error")
                    self.log(traceback.format_exc(), "error")
                    self.log("Stopping all processing.", "error")
                    break
            
            if max_retries <= 0:
                self.log("Max retries exceeded. There might be a circular dependency or unresolvable issue.", "error")
                self.log(f"Unprocessed assets: {[os.path.basename(p) for p in assets_to_process]}", "error")

        # 4. 모든 작업 완료 후, 수동 리디렉터 정리 안내
        if redirectors_to_fix:
            self.log("======== MANUAL ACTION REQUIRED ========", "warning")
            folder_paths = set(os.path.dirname(path) for path in redirectors_to_fix)
            self.log("Redirector fix-up could not be performed automatically.", "warning")
            self.log("Please fix them manually by right-clicking the following folder(s) in the Content Browser and choosing 'Fix Up Redirectors in Folder':", "warning")
            for folder in sorted(list(folder_paths)):
                self.log(f"  -> {folder}", "warning")

        self.log("======== PROCESSING COMPLETE ========", "info")
        return self.logs

# =============================================================================
# 이 아래 함수를 에디터 유틸리티 위젯의 버튼 OnClicked 이벤트에 연결합니다.
# =============================================================================

# 블루프린트와 연동하기 위한 전역 변수.
# 이 스크립트가 실행된 후, 블루프린트의 'Execute Python Script' 노드는
# 'report'라는 이름의 출력 핀에서 이 변수의 값을 읽을 수 있습니다.
report = ""

def run_sanitizer_from_ui(cook_log_text, error_policy):
    """
    UI로부터 호출될 엔트리 포인트 함수.
    처리 결과는 전역 변수 'report'에 저장되며, 값으로도 반환됩니다.
    :param cook_log_text: UI의 텍스트 박스에 있는 쿡 로그
    :param error_policy: "Stop on first error" 또는 "Skip errors and continue"
    :return: 처리 결과 로그 문자열
    """
    global report
    sanitizer = CinematicAssetSanitizer(error_policy)
    # TypeError 수정을 위해 UI에서 받은 Text 객체를 string으로 변환합니다.
    logs = sanitizer.run(str(cook_log_text))
    report = "\n".join(logs)
    return report

# 블루프린트의 'Execute Python Script' 노드는 이 스크립트 파일을 실행합니다.
# 노드의 입력 핀 'cook_log_text'와 'error_policy'는 이 스크립트의 전역 변수가 됩니다.
# run_sanitizer_from_ui 함수를 호출하여 로깅 작업을 수행한 후,
# 그 결과를 'report' 전역 변수에 저장합니다.
# 노드는 실행 후 이 'report' 변수의 값을 읽어 'report' 출력 핀으로 전달합니다.
report = run_sanitizer_from_ui(cook_log_text, error_policy)