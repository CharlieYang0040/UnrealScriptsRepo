# -*- coding: utf-8 -*-
import unreal

def bake_binding_transform_to_duplicate(level_sequence, source_binding_id_struct, clear_keys_on_duplicate=True):
    """
    지정된 레벨 시퀀스에서 source_binding_id_struct에 해당하는 바인딩의
    평가된(evaluated) 트랜스폼을 복제된 스포너블 바인딩에 베이크합니다.
    원본 바인딩은 동적으로 움직이는 스포너블 액터라고 가정합니다.

    Args:
        level_sequence (unreal.LevelSequence): 베이크할 대상 레벨 시퀀스 에셋.
        source_binding_id_struct (unreal.MovieSceneObjectBindingID): 원본 스포너블 바인딩의 ID 구조체.
        clear_keys_on_duplicate (bool): True이면 베이크 전 복제된 액터의 기존 트랜스폼 키를 삭제합니다.
    """
    unreal.log("복제된 스포너블 바인딩으로 트랜스폼 베이크 시작...")

    # --- 입력 유효성 검사 ---
    if not level_sequence:
        unreal.log_error("베이크 실패: 레벨 시퀀스가 유효하지 않습니다.")
        return False
    # source_binding_id_struct 자체는 None이 아닐 것으로 가정 (호출부에서 확인)
    # GUID 유효성 검사 (선택적이지만 추가 가능)
    source_guid = source_binding_id_struct.guid
    if source_guid == unreal.Guid():
         unreal.log_error("베이크 실패: 소스 바인딩 ID의 GUID가 유효하지 않습니다.")
         return False

    # --- 원본 바인딩 찾기 --- (GUID 사용)
    try:
        source_binding = level_sequence.find_binding_by_id(source_guid)
        if not source_binding:
            # 로그 출력 시 GUID를 문자열로 변환하는 것이 안전할 수 있음
            unreal.log_error(f"베이크 실패: ID '{str(source_guid)}'에 해당하는 바인딩을 찾을 수 없습니다.")
            return False
        unreal.log(f"소스 바인딩 찾음: {source_binding.get_name()}")

        # 원본이 스포너블인지 확인 (선택적이지만 권장)
        if not source_binding.get_spawnable():
             unreal.log_warning(f"소스 바인딩 '{source_binding.get_name()}'은(는) 스포너블이 아닐 수 있습니다. 계속 진행합니다.")

    except Exception as e:
        unreal.log_error(f"베이크 실패 (소스 바인딩 검색 중): {e}")
        return False

    # --- 스포너블 복제 (새로운 스포너블 추가 방식) ---
    duplicate_binding = None # 나중에 정리하기 위해 변수 선언
    try:
        unreal.log(f"다음을 기반으로 새 스포너블 생성 중: {source_binding.get_name()}")
        object_template = source_binding.get_object_template() # 원본 스포너블의 템플릿 가져오기
        if not object_template:
            unreal.log_error("베이크 실패: 소스 스포너블 바인딩에서 오브젝트 템플릿을 가져올 수 없습니다.")
            return False

        # 템플릿을 사용하여 새로운 스포너블 바인딩 추가
        duplicate_binding = level_sequence.add_spawnable_from_instance(object_template)
        if not duplicate_binding:
             unreal.log_error("베이크 실패: 시퀀스에 새 스포너블 바인딩을 추가할 수 없습니다.")
             return False

        # 복제된 스포너블 이름 설정 (옵션)
        # 기본 이름은 클래스 이름으로 생성됨. 필요시 수정.
        # duplicate_binding.set_name(f"{source_binding.get_name()}_Baked") # 이름 직접 설정 API 가 없을 수 있음
        # 스포너블 자체의 이름 변경은 다른 방식 필요할 수 있음 (예: 내부 오브젝트 접근)
        unreal.log(f"새 스포너블 바인딩 추가됨: {duplicate_binding.get_name()}")

    except Exception as e:
         unreal.log_error(f"베이크 실패 (스포너블 복제 중): {e}")
         return False

    # --- 시간 및 프레임 정보 가져오기 ---
    frame_rate = level_sequence.get_display_rate()
    start_frame = level_sequence.get_playback_start_frame()
    end_frame = level_sequence.get_playback_end_frame()
    unreal.log(f"시퀀스 정보: {start_frame}-{end_frame} 프레임 @ {frame_rate.numerator}/{frame_rate.denominator} fps")

    # --- 복제된 스포너블의 트랜스폼 트랙 찾기 또는 추가 ---
    transform_track = None
    channels = []
    try:
        transform_track = duplicate_binding.find_track_by_type(unreal.MovieSceneTransformTrack)
        if not transform_track:
            unreal.log("복제된 스포너블에서 트랜스폼 트랙을 찾을 수 없어 새로 추가합니다.")
            transform_track = duplicate_binding.add_track(unreal.MovieSceneTransformTrack)

        if not transform_track:
             unreal.log_error("베이크 실패: 복제된 스포너블 바인딩에서 트랜스폼 트랙을 찾거나 추가할 수 없습니다.")
             # 실패 시 복제된 스포너블 정리 필요
             level_sequence.remove_spawnable(duplicate_binding)
             return False

        channels = transform_track.get_channels()
        if len(channels) != 9:
             unreal.log_warning(f"복제된 스포너블에 대해 9개의 트랜스폼 채널이 예상되었으나 {len(channels)}개를 찾았습니다. 키프레임이 잘못될 수 있습니다.")

    except Exception as e:
        unreal.log_error(f"베이크 실패 (복제된 스포너블 트랙/채널 설정 중): {e}")
        if duplicate_binding:
            level_sequence.remove_spawnable(duplicate_binding)
        return False

    # --- 기존 키 삭제 (옵션 - 복제된 스포너블 대상) ---
    if clear_keys_on_duplicate:
        unreal.log("복제된 스포너블 트랙의 기존 트랜스폼 키 삭제 중...")
        try:
            for channel in channels:
                channel.reset_to_default()
            unreal.log("복제된 스포너블의 기존 키 삭제 완료.")
        except Exception as e:
            unreal.log_error(f"복제된 스포너블의 키 삭제 중 오류 발생: {e}")

    # --- 프레임별 베이크 루프 ---
    bake_success_count = 0
    bake_fail_count = 0
    unreal.log(f"{end_frame - start_frame + 1} 프레임에 대한 베이크 루프 시작...")

    with unreal.ScopedEditorTransaction("복제된 스포너블로 트랜스폼 베이크 스크립트") as trans:
        for frame_num in range(start_frame, end_frame + 1):
            try:
                current_frame_time = unreal.FrameTime(frame_number=frame_num)

                # 1. *원본* 바인딩의 트랜스폼 평가 (source_binding_id_struct 사용)
                source_transform = unreal.MovieSceneSequenceExtensions.evaluate_binding_transform(
                    level_sequence, source_binding_id_struct, current_frame_time
                )

                # 2. 평가된 트랜스폼을 복제된 스포너블의 트랙에 키프레임으로 추가
                loc = source_transform.location
                rot = source_transform.rotation.rotator()
                scale = source_transform.scale3d

                key_values_corrected = [
                    loc.x, loc.y, loc.z,
                    rot.x, rot.y, rot.z, # Roll, Pitch, Yaw
                    scale.x, scale.y, scale.z
                ]

                if len(channels) == 9:
                    for i in range(9):
                        channels[i].add_key(time=current_frame_time, new_value=key_values_corrected[i])
                else:
                     if frame_num == start_frame:
                          unreal.log_warning("예상치 못한 채널 수로 인해 복제된 스포너블에 키를 추가할 수 없습니다.")

                if frame_num % 10 == 0 or frame_num == end_frame:
                    unreal.log(f"  프레임 처리됨: {frame_num}")
                bake_success_count += 1

            except Exception as e:
                unreal.log_error(f"프레임 {frame_num} 베이크 실패: {e}")
                bake_fail_count += 1

    # --- 최종 결과 로그 및 저장 ---
    unreal.log(f"베이크 처리 완료. 성공: {bake_success_count}, 실패: {bake_fail_count}")
    if bake_success_count > 0:
        try:
            unreal.EditorAssetLibrary.save_loaded_asset(level_sequence)
            unreal.log(f"레벨 시퀀스 '{level_sequence.get_path_name()}' 저장 완료.")
            return True
        except Exception as e:
            unreal.log_error(f"레벨 시퀀스 저장 실패: {e}")
            return False
    else:
         unreal.log("성공적으로 베이크된 프레임이 없습니다.")
         # 실패 시 복제된 스포너블 삭제
         if duplicate_binding:
             unreal.log("베이크 실패로 인해 스포너블 복제 롤백 중.")
             # 트랜잭션 밖에서 실행해야 할 수 있음. Scoped Transaction 끝나고 실행.
             # level_sequence.remove_spawnable(duplicate_binding) # 여기서하면 트랜잭션 문제 발생 가능
             # 임시 해결책: 그냥 두거나, 별도 함수로 빼서 처리
             unreal.log_warning("베이크 실패: 복제된 스포너블이 자동으로 제거되지 않았습니다. 필요시 수동으로 제거해주세요.")
         return False

# --- 스크립트 직접 실행 테스트용 (옵션) ---
if __name__ == "__main__":
    unreal.log("포커스된 시퀀스와 선택된 바인딩을 사용하여 bake_binding_transform_to_duplicate 함수 테스트 중...")

    # 현재 포커스된 레벨 시퀀스 가져오기
    test_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_focused_level_sequence()

    if not test_sequence:
        unreal.log_warning("현재 에디터에 포커스된 레벨 시퀀스가 없습니다. 시퀀스 또는 서브시퀀스를 열고 포커스해주세요.")
    else:
        unreal.log(f"포커스된 시퀀스 사용: {test_sequence.get_path_name()}")

        # 시퀀서에서 현재 선택된 바인딩 가져오기
        selected_binding_proxies = unreal.LevelSequenceEditorBlueprintLibrary.get_selected_bindings()

        if not selected_binding_proxies:
            unreal.log_warning("시퀀서에서 선택된 바인딩이 없습니다. 포커스된 시퀀스에서 소스 스포너블 바인딩을 선택해주세요.")
        else:
            selected_binding_proxy = selected_binding_proxies[0]
            # Guid 가져오기
            selected_guid = selected_binding_proxy.binding_id

            # 선택된 바인딩 ID 유효성 검사 (Guid 비교)
            if selected_guid == unreal.Guid():
                unreal.log_warning("선택된 바인딩의 GUID가 유효하지 않습니다.")
            else:
                # MovieSceneObjectBindingID 구조체 생성
                # Guid만으로는 부족하고, Sequence 정보도 필요할 수 있음. resolve_binding_id 사용 시도.
                # Alternatively, construct directly if possible.
                try:
                    # Method 1: Resolve Binding ID (Potentially better if it exists and works)
                    # resolved_binding_id = unreal.LevelSequenceEditorBlueprintLibrary.resolve_binding_id(test_sequence, selected_guid)
                    # if not resolved_binding_id or not resolved_binding_id.is_valid(): ...

                    # Method 2: Construct MovieSceneObjectBindingID directly (Requires knowing the structure)
                    # This might require sequence information for context. Let's assume it's implicit for now or try simple construction.
                    # A simple Guid might not be enough context for some operations like evaluate_binding_transform.
                    # Let's try finding the binding first, then getting its struct ID.

                    source_binding = test_sequence.find_binding_by_id(selected_guid)
                    if not source_binding:
                         unreal.log_error(f"선택된 GUID '{str(selected_guid)}'에 해당하는 바인딩을 포커스된 시퀀스에서 찾을 수 없습니다.")
                    else:
                        # 바인딩을 찾았으면, 그 바인딩으로부터 완전한 MovieSceneObjectBindingID 구조체를 가져옴
                        # This mirrors the pattern in change_constraint_id_multi.py
                        source_binding_id_struct = unreal.MovieSceneSequenceExtensions.get_binding_id(level_sequence=test_sequence, binding=source_binding)

                        if not source_binding_id_struct:
                            unreal.log_error(f"바인딩 '{source_binding.get_name()}'에서 MovieSceneObjectBindingID 구조체를 가져올 수 없습니다.")
                        else:
                            unreal.log(f"선택된 바인딩 사용: {source_binding.get_name()} (GUID: {str(selected_guid)})")
                            # 베이크 함수 호출 (구조체 전달)
                            test_clear_keys = True
                            bake_binding_transform_to_duplicate(test_sequence, source_binding_id_struct, test_clear_keys)

                except Exception as e:
                    unreal.log_error(f"MovieSceneObjectBindingID 처리 중 오류 발생: {e}")