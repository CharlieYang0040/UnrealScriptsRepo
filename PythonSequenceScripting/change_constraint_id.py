import unreal

def update_selected_attach_track_constraint_ids():
    """
    현재 Level Sequence에서 선택된 바인딩들을 대상으로 다음 작업을 수행합니다:
    1. 첫 번째 선택된 바인딩을 Constraint ID의 소스로 지정합니다.
    2. 나머지 선택된 바인딩들에서 Attach 트랙(MovieScene3DAttachTrack)을 찾습니다.
    3. 찾아낸 모든 Attach 트랙 섹션의 Constraint Binding ID를 1번 소스 바인딩의
       현재 시퀀스 컨텍스트에 맞는 ID로 설정합니다.
    """

    # 현재 열려있는 Level Sequence 가져오기
    level_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
    if not level_sequence:
        unreal.log_warning("현재 열려있는 Level Sequence가 없습니다. Sequencer를 열고 다시 시도하세요.")
        return

    # 선택된 바인딩 가져오기
    selected_bindings = unreal.LevelSequenceEditorBlueprintLibrary.get_selected_bindings()
    if not selected_bindings or len(selected_bindings) < 2:
        unreal.log_error("최소 2개 이상의 바인딩을 선택해야 합니다 (첫 번째는 GUID 소스, 나머지는 타겟).")
        return

    # 첫 번째 선택된 바인딩을 소스로 사용
    source_binding = selected_bindings[0]
    unreal.log(f"Constraint ID 소스 바인딩: '{source_binding.get_display_name()}' (현재 시퀀스)")

    # 소스 바인딩의 ID (MovieSceneObjectBindingID) 가져오기 (컨텍스트 포함)
    try:
        source_binding_id_struct = unreal.MovieSceneSequenceExtensions.get_binding_id(level_sequence, source_binding)
        if not source_binding_id_struct or not isinstance(source_binding_id_struct, unreal.MovieSceneObjectBindingID):
            unreal.log_error(f"소스 바인딩에서 유효한 MovieSceneObjectBindingID를 얻지 못했습니다: {source_binding_id_struct}")
            return
        # 비교를 위해 소스 GUID 추출
        source_guid = source_binding_id_struct.get_editor_property('guid')
        unreal.log(f"소스 바인딩 ID 정보 얻음: GUID={source_guid}")
    except Exception as e:
        unreal.log_error(f"소스 바인딩 '{source_binding.get_display_name()}'에서 Binding ID를 가져오는 중 오류 발생: {e}")
        return


    updated_count = 0
    # 두 번째 바인딩부터 타겟으로 순회
    for target_binding in selected_bindings[1:]:
        unreal.log(f"타겟 바인딩 처리 중: {target_binding.get_display_name()}")
        for track in target_binding.get_tracks():
            if isinstance(track, unreal.MovieScene3DAttachTrack):
                track_name = track.get_name()
                try:
                    # get_display_name()이 더 읽기 좋은 이름을 제공할 수 있음
                    track_name = track.get_display_name() or track_name
                except AttributeError:
                    pass # get_display_name 없으면 get_name() 사용
                unreal.log(f"  -> Attach 트랙 발견: '{track_name}'")

                for section in track.get_sections():
                    if isinstance(section, unreal.MovieScene3DAttachSection):
                        # 기존 Constraint ID의 GUID 가져오기
                        orig_guid = None
                        try:
                            orig_constraint_id_struct = section.get_editor_property("constraint_binding_id")
                            if orig_constraint_id_struct and hasattr(orig_constraint_id_struct, 'guid'):
                                orig_guid = orig_constraint_id_struct.get_editor_property("guid")
                        except Exception as e:
                            unreal.log_warning(f"섹션 '{section.get_name()}'에서 기존 GUID를 가져오는 중 오류: {e}")

                        # 소스 바인딩의 GUID와 다를 경우 업데이트
                        if orig_guid != source_guid:
                            try:
                                # get_binding_id()로 얻은 ID 구조체(source_binding_id_struct)를 직접 사용
                                section.set_editor_property("constraint_binding_id", source_binding_id_struct)
                                unreal.log(f"    -> 섹션 '{section.get_name()}' Constraint Binding ID 업데이트됨: GUID={source_guid}")
                                updated_count += 1
                            except Exception as e:
                                unreal.log_error(f"섹션 '{section.get_name()}'에 constraint_binding_id 설정 중 오류: {e}")
                        else:
                            unreal.log(f"    -> 섹션 '{section.get_name()}' Constraint Binding ID는 이미 타겟 GUID와 동일합니다.")

    # 최종 결과 로그
    if updated_count > 0:
        unreal.log(f"총 {updated_count}개의 Attach 트랙 섹션의 Constraint Binding ID가 업데이트되었습니다. 시퀀스를 저장하여 변경사항을 확정하세요.")
    else:
        unreal.log("업데이트할 Attach 트랙 섹션이 없거나 이미 올바른 GUID로 설정되어 있습니다.")

# 스크립트 실행
update_selected_attach_track_constraint_ids()
