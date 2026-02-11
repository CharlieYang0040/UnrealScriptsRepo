import unreal
import os

@unreal.uclass()
class CinematicShotLib(unreal.BlueprintFunctionLibrary):

    # --- [상수 설정] 우리 작업 공간 경로 ---
    ROOT_PATH = "/Game/A_Cinematic_Workspace"
    SHOT_PATH = "/Game/A_Cinematic_Workspace/Sequencer/PrologueTrailer/Shot"
    TOOL_PATH = "/Game/A_Cinematic_Workspace/Lighting/HC/CinematicShotTools"

    @unreal.ufunction(static=True, ret=unreal.Array(unreal.AssetData), meta=dict(Category="CinematicShotTools"))
    def get_my_sequences():
        """ 작업 공간 내의 모든 레벨 시퀀스 에셋 데이터를 반환 """
        asset_reg = unreal.AssetRegistryHelpers.get_asset_registry()
        
        filter = unreal.ARFilter(
            class_names=["LevelSequence"],
            recursive_paths=True,
            package_paths=[CinematicShotLib.SHOT_PATH] # 우리 폴더만 검색
        )
        
        return asset_reg.get_assets(filter)

    @unreal.ufunction(static=True, params=[str], meta=dict(Category="CinematicShotTools"))
    def open_shot_in_editor(asset_path):
        """ 경로만 주면 해당 에셋을 로드해서 에디터로 엽니다. """
        # 1. 에셋 로드
        asset_obj = unreal.load_asset(asset_path)
        if not asset_obj:
            unreal.log_warning(f"Failed to load asset: {asset_path}")
            return

        # 2. 에디터 서브시스템 가져오기
        subsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
        
        # 3. 열기 (리스트 형태로 전달해야 함)
        subsystem.open_editor_for_assets([asset_obj])

    @unreal.ufunction(static=True, params=[str], meta=dict(Category="CinematicShotTools"))
    def focus_asset_in_browser(asset_path):
        """
        경로를 주면 콘텐츠 브라우저에서 그 파일을 찾아 선택해줍니다.
        """
        if not unreal.EditorAssetLibrary.does_asset_exist(asset_path):
            unreal.log_warning(f"Asset not found: {asset_path}")
            return

        # 에디터 라이브러리의 Sync 기능 사용
        unreal.EditorAssetLibrary.sync_browser_to_objects([asset_path])

    # [상태 관리] 현재 선택된 위젯 기억 (하이라이트용)
    _current_focused_widget = None

    # =========================================================
    # 1. 시퀀스 (Master / Shot) 열기 기능
    # =========================================================
    @unreal.ufunction(static=True, params=[str], meta=dict(Category="CinematicShotTools"))
    def open_sequence_asset(asset_path):
        """
        경로(String)를 받아서 시퀀서 에디터를 엽니다.
        예: /Game/.../Prequel_Master.Prequel_Master
        """
        # 1. 경로가 비어있으면 무시
        if not asset_path:
            unreal.log_warning("CinematicShotLib: Path is empty.")
            return

        # 2. 에셋 로드
        asset_obj = unreal.load_asset(asset_path)
        if not asset_obj:
            unreal.log_error(f"CinematicShotLib: Failed to load sequence asset: {asset_path}")
            return

        # 3. 에디터 서브시스템을 통해 열기
        subsystem = unreal.get_editor_subsystem(unreal.AssetEditorSubsystem)
        subsystem.open_editor_for_assets([asset_obj])
        unreal.log(f"CinematicShotLib: Opened Sequence -> {asset_path}")

    # =========================================================
    # 2. 레벨 (Map) 열기 기능
    # =========================================================
    @unreal.ufunction(static=True, params=[str], meta=dict(Category="CinematicShotTools"))
    def open_level_asset(level_path):
        """
        경로(String)를 받아서 해당 레벨(Map)을 엽니다.
        예: /Game/.../Prologue_Cinema_P.Prologue_Cinema_P
        """
        if not level_path:
            return

        # 1. 경로 정리 (PackageName만 추출)
        # 입력이 "Folder/MapName.MapName" 형태라면 "Folder/MapName"으로 잘라줍니다.
        # load_level은 보통 패키지 경로를 선호합니다.
        clean_path = level_path.split('.')[0]

        # 2. 레벨 에디터 서브시스템 가져오기
        lvl_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)

        # 3. 레벨 로드 (성공 여부 반환)
        success = lvl_subsystem.load_level(clean_path)
        
        if success:
            unreal.log(f"CinematicShotLib: Level Loaded -> {clean_path}")
        else:
            unreal.log_error(f"CinematicShotLib: Failed to load level -> {clean_path}")

    # =========================================================
    # 3. UI 하이라이트 (Focus) 관리 기능
    # =========================================================
    @unreal.ufunction(static=True, params=[unreal.UserWidget], meta=dict(Category="CinematicShotTools"))
    def update_shot_focus(new_widget):
        """ 위젯 하나만 켜고 나머지 끄기 (라디오 버튼 로직) """
        
        # 이전 것 끄기
        if CinematicShotLib._current_focused_widget:
            try:
                # 위젯이 유효한지(삭제되지 않았는지) 확인 후 호출
                CinematicShotLib._current_focused_widget.call_method("SetFocusState", (False,))
            except:
                CinematicShotLib._current_focused_widget = None

        # 새 것 켜기
        if new_widget:
            try:
                new_widget.call_method("SetFocusState", (True,))
                CinematicShotLib._current_focused_widget = new_widget
            except:
                pass