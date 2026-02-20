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

    @unreal.ufunction(static=True, params=[unreal.Array(str)], meta=dict(Category="CinematicShotTools"))
    def focus_assets_in_browser(asset_paths):
        """
        여러 개의 경로(Array)를 받아서 리스트에 있는 모든 에셋을 
        콘텐츠 브라우저에서 한 번에 선택해줍니다.
        """
        if not asset_paths:
            return

        # 1. 존재하는 에셋만 필터링
        valid_paths = []
        for path in asset_paths:
            if unreal.EditorAssetLibrary.does_asset_exist(path):
                valid_paths.append(path)
        
        if not valid_paths:
            unreal.log_warning("No valid assets found to focus.")
            return

        # 2. 일괄 Sync (배열 전체 전달)
        unreal.EditorAssetLibrary.sync_browser_to_objects(valid_paths)

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
                CinematicShotLib._current_focused_widget.call_method("SetDoubleFocusState", (False,))
            except:
                CinematicShotLib._current_focused_widget = None

        # 새 것 켜기
        if new_widget:
            try:
                new_widget.call_method("SetDoubleFocusState", (True,))
                CinematicShotLib._current_focused_widget = new_widget
            except:
                pass

@unreal.uclass()
class CinematicSelectionLib(unreal.BlueprintFunctionLibrary):
    
    # -------------------------------------------------------------------------
    # [데이터 저장소]
    # 1. _all_paths_ordered: 전체 샷 경로가 '순서대로' 저장된 리스트 (순서 파악용)
    # 2. _selected_paths: 현재 선택된 샷들의 경로 리스트
    # 3. _widget_registry: 위젯 인스턴스 참조 (화면 갱신용)
    # 4. _shot_data_registry: [New] 샷 별 서브 데이터 저장소
    #    구조: { "Game/../Shot_0010": { "ANI": "...", "FX": "...", "LIT": "..." } }
    # -------------------------------------------------------------------------
    _all_paths_ordered = [] 
    _selected_paths = []
    _widget_registry = {} 
    _last_anchor_path = "" 
    _shot_data_registry = {} # [New] 중앙 데이터 명부

    # =========================================================================
    # [0] 초기화 및 데이터 등록
    # =========================================================================
    @unreal.ufunction(static=True, params=[unreal.Array(str)], meta=dict(Category="Cinematic Selection"))
    def set_available_shots(paths_in_order):
        """ 
        [필수] 전체 샷 리스트를 순서대로 등록합니다. 
        Shift 범위 선택을 계산하기 위해 반드시 필요합니다.
        
        Note: 이 함수가 Loop 완료 후(Completed)에 호출되므로, 
        여기서 데이터 레지스트리를 초기화하면 안 됩니다.
        """
        CinematicSelectionLib._all_paths_ordered = paths_in_order
        CinematicSelectionLib.clear_selection() 


    @unreal.ufunction(static=True, params=[str, unreal.Array(str), unreal.Array(str), unreal.Array(str)], meta=dict(Category="Cinematic Selection"))
    def register_shot_data(main_path, ani_paths, fx_paths, lit_paths):
        """
        [New] 개별 샷의 서브 정보를 파이썬 명부에 등록합니다.
        이제 각 카테고리별로 여러 개의 경로(List)를 저장할 수 있습니다.
        """
        if not main_path:
            return

        # [Fix] 키 통일: `.Asset`이나 `.uasset` 확장자 제거하여 패키지 경로만 사용
        clean_key = main_path.split('.')[0]

        CinematicSelectionLib._shot_data_registry[clean_key] = {
            "ANI": ani_paths,
            "FX": fx_paths,
            "LIT": lit_paths
        }

    # =========================================================================
    # [1] 위젯 등록/해제 (View)
    # =========================================================================
    @unreal.ufunction(static=True, params=[str, unreal.UserWidget], meta=dict(Category="Cinematic Selection"))
    def register_shot_widget(shot_path, widget_reference):
        if shot_path and widget_reference:
            CinematicSelectionLib._widget_registry[shot_path] = widget_reference
            is_selected = shot_path in CinematicSelectionLib._selected_paths
            CinematicSelectionLib._safe_update_widget(widget_reference, is_selected)

    @unreal.ufunction(static=True, params=[str], meta=dict(Category="Cinematic Selection"))
    def unregister_shot_widget(shot_path):
        if shot_path in CinematicSelectionLib._widget_registry:
            del CinematicSelectionLib._widget_registry[shot_path]

    # =========================================================================
    # [2] 클릭 처리 (핵심 로직)
    # =========================================================================
    @unreal.ufunction(static=True, params=[str, bool, bool], meta=dict(Category="Cinematic Selection"))
    def handle_shot_click(clicked_path, b_ctrl, b_shift):
        
        current_sel = CinematicSelectionLib._selected_paths
        anchor = CinematicSelectionLib._last_anchor_path
        all_shots = CinematicSelectionLib._all_paths_ordered
        
        new_selection = []

        # --- CASE 1: Shift 클릭 (범위 선택) ---
        if b_shift and anchor and (anchor in all_shots) and (clicked_path in all_shots):
            # 1. 기준점(Anchor)과 현재 클릭(Current)의 인덱스 찾기
            idx_start = all_shots.index(anchor)
            idx_end = all_shots.index(clicked_path)
            
            # 2. 대소 비교해서 실제 범위(Slice) 만들기
            lower = min(idx_start, idx_end)
            upper = max(idx_start, idx_end)
            
            # 3. 사이값들 가져오기 (upper + 1 해야 포함됨)
            range_paths = all_shots[lower : upper + 1]
            
            # 4. 기존 선택 유지 여부 (윈도우 탐색기는 Ctrl 없으면 기존꺼 날리고 범위만 잡음)
            if b_ctrl:
                new_selection = list(current_sel) # 기존 유지
                for p in range_paths:
                    if p not in new_selection:
                        new_selection.append(p)
            else:
                new_selection = range_paths # 기존 날리고 범위만 선택
                
        # --- CASE 2: Ctrl 클릭 (토글) ---
        elif b_ctrl:
            new_selection = list(current_sel)
            if clicked_path in new_selection:
                new_selection.remove(clicked_path)
            else:
                new_selection.append(clicked_path)
            # Ctrl 클릭은 앵커를 갱신함
            CinematicSelectionLib._last_anchor_path = clicked_path
            
        # --- CASE 3: 일반 클릭 (단일) ---
        else:
            new_selection = [clicked_path]
            CinematicSelectionLib._last_anchor_path = clicked_path

        # 상태 업데이트 및 화면 갱신
        CinematicSelectionLib._selected_paths = new_selection
        CinematicSelectionLib._refresh_all_widgets()

    # =========================================================================
    # [3] 내부 유틸리티
    # =========================================================================
    @classmethod
    def _refresh_all_widgets(cls):
        for path, widget in list(cls._widget_registry.items()):
            if not widget: 
                cls.unregister_shot_widget(path)
                continue
            try:
                # 선택 여부에 따라 노란 테두리 켜고 끄기
                is_selected = path in cls._selected_paths
                cls._safe_update_widget(widget, is_selected)
            except:
                cls.unregister_shot_widget(path)

    @classmethod
    def _safe_update_widget(cls, widget, is_selected):
        try:
            widget.call_method("SetFocusState", (is_selected,))
        except:
            pass

    @unreal.ufunction(static=True, params=[], ret=None, meta=dict(Category="Cinematic Selection"))
    def clear_selection():
        CinematicSelectionLib._selected_paths = []
        CinematicSelectionLib._last_anchor_path = ""
        CinematicSelectionLib._refresh_all_widgets()

    # =========================================================================
    # [4] 데이터 호출 (저장/SVN 관리용)
    # =========================================================================
    @unreal.ufunction(static=True, params=[], ret=unreal.Array(str), meta=dict(Category="Cinematic Selection"))
    def get_selected_shot_paths():
        """ 
        [외부 호출용] 현재 선택된 샷들의 경로 리스트를 반환합니다. 
        """
        return CinematicSelectionLib._selected_paths

    @unreal.ufunction(static=True, params=[unreal.Array(str)], ret=None, meta=dict(Category="Cinematic Asset"))
    def save_target_packages(target_paths):
        """ 
        전달받은 특정 경로들의 에셋들을 로드하여 저장 팝업을 띄웁니다.
        """
        if not target_paths or len(target_paths) == 0:
            unreal.log_warning("⚠️ No paths provided to save.")
            return

        packages_to_save = []
        for path in target_paths:
            if not path: 
                continue
            
            pkg_path = path.split(".")[0] 
            pkg = unreal.load_package(pkg_path)
            
            if pkg:
                packages_to_save.append(pkg)

        if packages_to_save:
            success = unreal.EditorLoadingAndSavingUtils.save_packages_with_dialog(packages_to_save, False)
            if success:
                unreal.log(f"💾 Successfully saved {len(packages_to_save)} packages.")
            else:
                unreal.log_warning("❌ Save cancelled or failed.")
        else:
            unreal.log_warning("⚠️ No valid packages found to save.")

    @unreal.ufunction(static=True, params=[str], ret=None, meta=dict(Category="Cinematic Asset"))
    def save_selected_category(category_type):
        """
        [New] 스마트 저장 함수
        현재 선택된 메인 샷들을 확인하고, 레지스트리에서 해당 카테고리(ANI, FX, LIT)의 
        서브 경로들(List)을 모두 모아서 일괄 저장합니다.
        """
        selected_mains = CinematicSelectionLib._selected_paths
        if not selected_mains:
            unreal.log_warning("⚠️ No shots selected.")
            return

        targets_to_save = []
        
        for main_path in selected_mains:
            if category_type == "MAIN":
                targets_to_save.append(main_path)
                continue

            # [Fix] 키 통일
            clean_key = main_path.split('.')[0]
            
            if clean_key in CinematicSelectionLib._shot_data_registry:
                data_map = CinematicSelectionLib._shot_data_registry[clean_key]
                if category_type in data_map:
                    # 이제 리스트(Array)가 반환되므로 extend로 합칩니다.
                    sub_paths = data_map[category_type]
                    if sub_paths:
                        targets_to_save.extend(sub_paths)
        
        if targets_to_save:
            unreal.log(f"🚀 Batch Saving [{category_type}] for {len(targets_to_save)} assets...")
            CinematicSelectionLib.save_target_packages(targets_to_save)
        else:
            unreal.log_warning(f"⚠️ No [{category_type}] assets found for current selection.")

    @unreal.ufunction(static=True, params=[], ret=None, meta=dict(Category="Cinematic Asset"))
    def save_selected_shots():
        CinematicSelectionLib.save_selected_category("MAIN")

    # [NEW] 메인 매니저(ShotManager)를 저장할 변수
    _main_manager_widget = None

    # =========================================================================
    # [NEW] 매니저 등록 (Manager가 생성될 때 호출)
    # =========================================================================
    @unreal.ufunction(static=True, params=[unreal.UserWidget], meta=dict(Category="Cinematic Selection"))
    def register_main_manager(manager_widget):
        """ ShotManager가 생성될 때 호출하여 자신을 등록함 """
        CinematicSelectionLib._main_manager_widget = manager_widget
        # unreal.log("✅ Main Manager Registered via Python.")

    @unreal.ufunction(static=True, params=[unreal.UserWidget], meta=dict(Category="Cinematic Selection"))
    def request_context_menu(clicked_widget):
        """ 
        [Modified] 데이터를 전달하지 않고 메뉴만 띄웁니다.
        """
        manager = CinematicSelectionLib._main_manager_widget
        
        if manager and clicked_widget:
            try:
                manager.call_method("OpenContextMenu", (clicked_widget,))
            except Exception as e:
                unreal.log_error(f"Failed to open menu via Manager: {e}")
        else:
            unreal.log_warning("⚠️ Main Manager or Clicked Widget is invalid!")

@unreal.uclass()
class CinematicAssetLib(unreal.BlueprintFunctionLibrary):

    @unreal.ufunction(static=True, params=[], ret=None, meta=dict(Category="Cinematic Asset"))
    def play_selected_shots_as_sequence():
        """
        선택된 샷들을 모아서 하나의 임시 마스터 시퀀스를 만들고 엽니다.
        """
        try:
            selected_paths = CinematicSelectionLib.get_selected_shot_paths()
        except:
            unreal.log_error("CinematicSelectionLib not found.")
            return

        if not selected_paths or len(selected_paths) == 0:
            unreal.log_warning("⚠️ No shots selected to play.")
            return

        # 1. 임시 마스터 시퀀스 경로 설정
        temp_folder = "/Game/A_Cinematic_Workspace/Sequencer/Temp"
        temp_name = "Temp_PreviewMaster"
        temp_full_path = f"{temp_folder}/{temp_name}.{temp_name}"

        # 2. 기존에 임시 파일이 있다면 삭제
        if unreal.EditorAssetLibrary.does_asset_exist(temp_full_path):
            unreal.EditorAssetLibrary.delete_asset(temp_full_path)

        # 3. 새 레벨 시퀀스 에셋 생성
        asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
        factory = unreal.LevelSequenceFactoryNew()
        master_seq = asset_tools.create_asset(temp_name, temp_folder, unreal.LevelSequence, factory)

        if not master_seq:
            unreal.log_error("Failed to create temporary master sequence.")
            return

        # -------------------------------------------------------------
        # 🛠️ 수정됨: LevelSequence 객체에서 직접 add_track 호출 (UE 5.6+ 규격)
        # -------------------------------------------------------------
        shot_track = master_seq.add_track(unreal.MovieSceneCinematicShotTrack)

        if not shot_track:
            unreal.log_error("Failed to add Cinematic Shot Track.")
            return

        current_start_frame = 0

        for path in selected_paths:
            shot_asset = unreal.load_asset(path)
            if not shot_asset:
                continue

            # 샷의 원래 길이(Duration) 구하기
            shot_start = shot_asset.get_playback_start()
            shot_end = shot_asset.get_playback_end()
            duration = shot_end - shot_start

            # 트랙에 섹션(클립) 추가
            section = shot_track.add_section()
            
            # 섹션에 샷 에셋 연결
            section.set_sequence(shot_asset)
            
            # -------------------------------------------------------------
            # 🛠️ [수정됨] 언리얼 Range 검사 에러를 피하기 위해 무조건 End부터 설정!
            # -------------------------------------------------------------
            section.set_end_frame(current_start_frame + duration)
            section.set_start_frame(current_start_frame)
            
            # 다음 샷을 위해 현재 시간을 끝점으로 이동
            current_start_frame += duration

        # 전체 재생 구간 설정
        master_seq.set_playback_start(0)
        master_seq.set_playback_end(current_start_frame)

        # 시퀀서 에디터로 열기
        unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([master_seq])
        
        unreal.log(f"🎬 Created preview master with {len(selected_paths)} shots.")

@unreal.uclass()
class CinematicUtilsBPLibrary(unreal.BlueprintFunctionLibrary):

    @unreal.ufunction(static=True, params=[str, unreal.Vector, str, unreal.Vector], meta={
        "Category": "Cinematic Utils",
        "ToolTip": "특정 피벗 모드(First 포함)를 기준으로 변환을 적용합니다. (Undo 지원)"
    })
    def apply_transform_with_pivot(transform_type, value_vector, pivot_mode, manual_pivot):
        """
        params:
            transform_type (str): "Location", "Rotation", "Scale"
            value_vector (Vector): 변화량
            pivot_mode (str): "Self", "Center", "First", "World", "Manual"
            manual_pivot (Vector): Manual 모드 좌표
        """
        selected_actors = unreal.EditorLevelLibrary.get_selected_level_actors()
        
        if not selected_actors:
            unreal.log_warning("선택된 액터가 없습니다.")
            return

        # --- [피벗 좌표 미리 계산] ---
        
        # 1. Center (중심점)
        center_location = unreal.Vector(0, 0, 0)
        if pivot_mode == "Center":
            sum_loc = unreal.Vector(0, 0, 0)
            for actor in selected_actors:
                sum_loc += actor.get_actor_location()
            center_location = sum_loc / len(selected_actors)

        # 2. First (첫 번째 선택 액터)
        first_actor_location = unreal.Vector(0, 0, 0)
        if len(selected_actors) > 0:
            # 리스트의 0번 인덱스를 기준으로 삼음
            first_actor_location = selected_actors[0].get_actor_location()

        # ---------------------------

        transaction_name = f"Transform {transform_type} ({pivot_mode})"
        
        with unreal.ScopedEditorTransaction(transaction_name):
            
            for actor in selected_actors:
                # Undo를 위해 수정 상태 알림
                actor.modify()
                
                current_loc = actor.get_actor_location()
                
                # --- 현재 루프 액터에 적용할 피벗 결정 ---
                pivot = unreal.Vector(0,0,0)
                
                if pivot_mode == "Self":
                    pivot = current_loc
                elif pivot_mode == "Center":
                    pivot = center_location
                elif pivot_mode == "First":       # <--- 추가된 부분
                    pivot = first_actor_location
                elif pivot_mode == "World":
                    pivot = unreal.Vector(0, 0, 0)
                elif pivot_mode == "Manual":
                    pivot = manual_pivot

                # --- 변환 로직 (Location / Rotation / Scale) ---

                # [A] Location (이동)
                if transform_type == "Location":
                    actor.add_actor_world_offset(value_vector, False, False)

                # [B] Rotation (회전)
                elif transform_type == "Rotation":
                    delta_rot = unreal.Rotator(value_vector.y, value_vector.z, value_vector.x)
                    
                    # 1. 액터 자체 회전
                    actor.add_actor_world_rotation(delta_rot, False, False)
                    
                    # 2. 피벗 공전 (Self가 아닐 때만)
                    if pivot_mode != "Self":
                        vector_from_pivot = current_loc - pivot
                        rotated_vector = delta_rot.rotate_vector(vector_from_pivot)
                        new_loc = pivot + rotated_vector
                        actor.set_actor_location(new_loc, False, False)

                # [C] Scale (크기)
                elif transform_type == "Scale":
                    # 1. 액터 자체 스케일
                    current_scale = actor.get_actor_scale3d()
                    new_scale = unreal.Vector(
                        current_scale.x * value_vector.x,
                        current_scale.y * value_vector.y,
                        current_scale.z * value_vector.z
                    )
                    actor.set_actor_scale3d(new_scale)

                    # 2. 피벗 기준 위치 이동 (Self가 아닐 때만)
                    if pivot_mode != "Self":
                        vector_from_pivot = current_loc - pivot
                        scaled_vector = unreal.Vector(
                            vector_from_pivot.x * value_vector.x,
                            vector_from_pivot.y * value_vector.y,
                            vector_from_pivot.z * value_vector.z
                        )
                        new_loc = pivot + scaled_vector
                        actor.set_actor_location(new_loc, False, False)

        unreal.log(f"[CinematicUtils] {transform_type} 완료 (Pivot: {pivot_mode})")