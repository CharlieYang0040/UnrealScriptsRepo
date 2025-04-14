import unreal

def add_attach_track_with_guid():
    """
    현재 열려있는 Level Sequence에서 첫 번째로 선택된 바인딩에
    Attach 트랙과 섹션을 추가하고, 지정된 GUID를 Constraint Binding ID로 설정합니다.
    """

    # !!! 아래 문자열을 원하는 타겟 바인딩의 GUID로 직접 수정하세요 !!!
    target_guid_string = "A4F64ECC4E418B6CDBA7DF8D0F1272E9" # 예시 GUID, 반드시 수정 필요

    # 현재 열려있는 Level Sequence 가져오기
    level_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
    if not level_sequence:
        unreal.log_warning("현재 열려있는 Level Sequence가 없습니다. Sequencer를 열고 다시 시도하세요.")
        return

    # 선택된 바인딩 가져오기 (정확히 하나만 선택되어야 함)
    selected_bindings = unreal.LevelSequenceEditorBlueprintLibrary.get_selected_bindings()
    if not selected_bindings or len(selected_bindings) != 1:
        unreal.log_error("정확히 하나의 바인딩만 선택해야 합니다.")
        return

    target_binding = selected_bindings[0]
    unreal.log(f"타겟 바인딩: '{target_binding.get_display_name()}'")

    # 입력된 GUID 문자열을 unreal.Guid 객체로 변환
    try:
        target_guid = unreal.Guid.from_string(target_guid_string)
        if not target_guid.is_valid():
             unreal.log_error(f"입력된 GUID 문자열 '{target_guid_string}'이 유효하지 않습니다.")
             return
        unreal.log(f"사용할 타겟 GUID: {target_guid}")
    except Exception as e:
        unreal.log_error(f"GUID 문자열 변환 중 오류 발생: {e}")
        return

    # Attach 트랙 추가
    try:
        attach_track = target_binding.add_track(unreal.MovieScene3DAttachTrack)
        if not attach_track:
            unreal.log_error("Attach 트랙을 추가하지 못했습니다.")
            return
        unreal.log(f"'{target_binding.get_display_name()}'에 Attach 트랙 추가됨.")
    except Exception as e:
        unreal.log_error(f"Attach 트랙 추가 중 오류 발생: {e}")
        return

    # Attach 섹션 추가
    try:
        attach_section = attach_track.add_section()
        if not attach_section:
            unreal.log_error("Attach 섹션을 추가하지 못했습니다.")
            # 추가된 트랙 롤백 (선택 사항)
            # target_binding.remove_track(attach_track)
            return
        unreal.log("Attach 섹션 추가됨.")

        # 섹션 범위 설정 (예: 시퀀스 전체 길이)
        start_frame = level_sequence.get_playback_start()
        end_frame = level_sequence.get_playback_end()
        attach_section.set_range(start_frame, end_frame)
        unreal.log(f"섹션 범위 설정됨: {start_frame} - {end_frame}")

        # Constraint Binding ID 설정
        new_binding_id = unreal.MovieSceneObjectBindingID()
        new_binding_id.set_editor_property("guid", target_guid) # GUID만 설정

        attach_section.set_editor_property("constraint_binding_id", new_binding_id)
        unreal.log(f"Constraint Binding ID 설정됨: GUID={new_binding_id.get_editor_property('guid')}")

        # 시퀀서 UI 새로고침 (선택 사항)
        unreal.LevelSequenceEditorBlueprintLibrary.refresh_current_level_sequence()
        unreal.log("테스트 스크립트 완료. 시퀀스를 저장하여 변경사항을 확정하세요.")

    except Exception as e:
        unreal.log_error(f"Attach 섹션 처리 또는 ID 설정 중 오류 발생: {e}")
        # 오류 발생 시 트랙 롤백 (선택 사항)
        # target_binding.remove_track(attach_track)
        return

# --- 스크립트 실행 ---
add_attach_track_with_guid()