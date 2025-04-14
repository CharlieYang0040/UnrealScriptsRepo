import unreal
import re # 정규표현식 모듈 임포트

def auto_update_attach_constraints_by_name():
    """
    현재 Level Sequence에서 선택된 모든 바인딩들을 이름 규칙에 따라 분류하고,
    매칭되는 소스(예: PC_XX_...)와 타겟(예: SpotLight_XX_...) 바인딩 간에
    Attach 트랙의 Constraint Binding ID를 자동으로 설정하고 타겟 이름도 변경합니다.

    이름 규칙 예시:
    - 소스: PC_GM_1001 (3) 또는 PC GM 1001 (3) -> 'GM' 프리픽스와 숫자 '3' 추출
    - 타겟: SpotLight_GM_face_08 (2) -> 'GM' 프리픽스 추출, 이름을 'SpotLight_GM_face_03'으로 변경
    """

    # 정규표현식 패턴 정의 (신중하게 재검토 및 수정)
    # 소스 패턴: 'PC' 다음 (공백 또는 밑줄), 그룹1:프리픽스(\w+), (공백 또는 밑줄), 숫자(\d+), 공백, '(', 그룹2:괄호안숫자(\d+), ')
    source_pattern = re.compile(r"^PC[\s_](\w+)[\s_]\d+\s+\((\d+)\)$")
    # 타겟 패턴: 'SpotLight_' 다음 그룹1:프리픽스(\w+), '_face_', 숫자(\d+), 뒤따르는 ' (숫자)' 그룹들이 1개 이상(+) 있음
    target_pattern = re.compile(r"^SpotLight_(\w+)_face_\d+(?:\s+\(\d+\))*?$")
    # 타겟 이름 변경용 추출 패턴: 그룹1:(SpotLight_프리픽스_face_), 그룹2:숫자(\d+), 뒤따르는 ' (숫자)' 그룹들이 0개 이상(*) 있음
    target_rename_extraction_pattern = re.compile(r"^(SpotLight_\w+_face_)(\d+)(?:\s+\(\d+\))*?$")


    # 현재 열려있는 Level Sequence 가져오기
    level_sequence = unreal.LevelSequenceEditorBlueprintLibrary.get_current_level_sequence()
    if not level_sequence:
        unreal.log_warning("현재 열려있는 Level Sequence가 없습니다. Sequencer를 열고 다시 시도하세요.")
        return

    # 선택된 모든 바인딩 가져오기
    selected_bindings = unreal.LevelSequenceEditorBlueprintLibrary.get_selected_bindings()
    if not selected_bindings:
        unreal.log_warning("선택된 바인딩이 없습니다. 처리할 바인딩들을 선택하세요.")
        return

    # 바인딩 분류 (소스, 타겟)
    source_map = {} # key: prefix (e.g., 'GM'), value: (binding, number_str)
    target_map = {} # key: prefix (e.g., 'GM'), value: binding

    unreal.log("선택된 바인딩 분류 시작...")
    for binding in selected_bindings:
        binding_name = str(binding.get_display_name()) # Text -> str 변환
        unreal.log(f"  처리 중: '{binding_name}'") # 현재 처리중인 바인딩 로그 추가

        source_match = source_pattern.match(binding_name)
        if source_match:
            prefix = source_match.group(1)
            number_str = source_match.group(2)
            if prefix in source_map:
                unreal.log_warning(f"    소스 프리픽스 '{prefix}'가 중복됩니다. 첫 번째 바인딩만 사용합니다: '{binding_name}'")
            else:
                source_map[prefix] = (binding, number_str)
                unreal.log(f"    -> 소스 바인딩 발견: (프리픽스: {prefix}, 번호: {number_str})")
            continue # 다음 바인딩으로

        target_match = target_pattern.match(binding_name)
        if target_match:
            prefix = target_match.group(1)
            if prefix in target_map:
                unreal.log_warning(f"    타겟 프리픽스 '{prefix}'가 중복됩니다. 첫 번째 바인딩만 사용합니다: '{binding_name}'")
            else:
                target_map[prefix] = binding
                unreal.log(f"    -> 타겟 바인딩 발견: (프리픽스: {prefix})")
            continue # 다음 바인딩으로

        unreal.log(f"    -> 분류되지 않음 (이름 규칙 불일치)")

    # 매칭 및 처리
    updated_count = 0
    renamed_count = 0

    unreal.log("\n매칭 및 처리 시작...")
    for prefix, (source_binding, source_number_str) in source_map.items():
        if prefix in target_map:
            target_binding = target_map[prefix]
            unreal.log(f"\n매칭 발견: Prefix '{prefix}'")
            unreal.log(f"  - 소스: '{source_binding.get_display_name()}'")
            unreal.log(f"  - 타겟: '{target_binding.get_display_name()}'")

            # 1. 소스 바인딩 ID 가져오기
            source_binding_id_struct = None
            source_guid = None
            try:
                source_binding_id_struct = unreal.MovieSceneSequenceExtensions.get_binding_id(level_sequence, source_binding)
                if not source_binding_id_struct or not isinstance(source_binding_id_struct, unreal.MovieSceneObjectBindingID):
                    unreal.log_error(f"  소스 바인딩에서 유효한 MovieSceneObjectBindingID를 얻지 못했습니다: {source_binding_id_struct}")
                    continue # 다음 프리픽스로
                source_guid = source_binding_id_struct.get_editor_property('guid')
                unreal.log(f"  소스 바인딩 ID 정보 얻음: GUID={source_guid}")
            except Exception as e:
                unreal.log_error(f"  소스 바인딩 '{source_binding.get_display_name()}'에서 Binding ID를 가져오는 중 오류 발생: {e}")
                continue # 다음 프리픽스로

            # 2. 타겟 바인딩의 Attach 트랙 Constraint ID 업데이트
            found_attach_track = False
            for track in target_binding.get_tracks():
                if isinstance(track, unreal.MovieScene3DAttachTrack):
                    found_attach_track = True
                    track_name = track.get_name()
                    try: track_name = track.get_display_name() or track_name
                    except AttributeError: pass
                    unreal.log(f"    -> Attach 트랙 발견: '{track_name}'")

                    for section in track.get_sections():
                        if isinstance(section, unreal.MovieScene3DAttachSection):
                            orig_guid = None
                            try:
                                orig_constraint_id_struct = section.get_editor_property("constraint_binding_id")
                                if orig_constraint_id_struct and hasattr(orig_constraint_id_struct, 'guid'):
                                    orig_guid = orig_constraint_id_struct.get_editor_property("guid")
                            except Exception as e:
                                unreal.log_warning(f"      섹션 '{section.get_name()}'에서 기존 GUID 가져오는 중 오류: {e}")

                            if orig_guid != source_guid:
                                try:
                                    section.set_editor_property("constraint_binding_id", source_binding_id_struct)
                                    unreal.log(f"      -> 섹션 '{section.get_name()}' Constraint Binding ID 업데이트됨: GUID={source_guid}")
                                    updated_count += 1
                                except Exception as e:
                                    unreal.log_error(f"      섹션 '{section.get_name()}'에 constraint_binding_id 설정 중 오류: {e}")
                            else:
                                unreal.log(f"      -> 섹션 '{section.get_name()}' Constraint Binding ID는 이미 타겟 GUID와 동일합니다.")
            if not found_attach_track:
                 unreal.log_warning(f"    타겟 바인딩 '{target_binding.get_display_name()}'에서 Attach 트랙을 찾을 수 없습니다.")


            # 3. 타겟 바인딩 이름 변경
            try:
                target_name_text = target_binding.get_display_name()
                target_name_str = str(target_name_text)

                # 새로운 추출 패턴을 사용하여 이름 구성요소 분리
                rename_match = target_rename_extraction_pattern.match(target_name_str)
                if rename_match:
                    base_name_part = rename_match.group(1) # 예: "SpotLight_HM_face_"
                    original_number_part = rename_match.group(2) # 예: "08"

                    # 소스 번호를 두 자리 숫자로 포맷 (예: "3" -> "03")
                    formatted_source_number = source_number_str.zfill(2)
                    # 새 이름 생성 (괄호 및 추가 숫자 부분 모두 제거)
                    new_target_name_str = f"{base_name_part}{formatted_source_number}"

                    # 기존 이름(숫자 부분만 비교)과 비교하여 변경이 필요한 경우
                    if original_number_part != formatted_source_number:
                        # 표시 이름 설정
                        new_target_name_text = unreal.Text(new_target_name_str)
                        target_binding.set_display_name(new_target_name_text)
                        unreal.log(f"    타겟 바인딩 표시 이름 변경됨: '{target_name_str}' -> '{new_target_name_str}'")
                        
                        # 오브젝트 이름 설정 (문자열 전달)
                        try:
                            target_binding.set_name(new_target_name_str)
                            unreal.log(f"    타겟 바인딩 오브젝트 이름 변경됨 -> '{new_target_name_str}'")
                        except Exception as name_e:
                            unreal.log_warning(f"    타겟 바인딩 오브젝트 이름 변경 중 오류: {name_e}")

                        renamed_count += 1
                    else:
                         unreal.log(f"    타겟 바인딩 이름의 숫자 부분이 이미 '{formatted_source_number}'(으)로 올바릅니다.")

                    # --- 액터 레이블 변경 로직 (조건 밖으로 이동) ---
                    try:
                        target_binding_id_struct = unreal.MovieSceneSequenceExtensions.get_binding_id(level_sequence, target_binding) # MovieSceneObjectBindingID 얻기
                        if target_binding_id_struct and isinstance(target_binding_id_struct, unreal.MovieSceneObjectBindingID):
                            bound_objects = unreal.LevelSequenceEditorBlueprintLibrary.get_bound_objects(target_binding_id_struct) # 얻은 ID 사용
                            if bound_objects:
                                for obj in bound_objects:
                                    if isinstance(obj, unreal.Actor):
                                        current_label = obj.get_actor_label()
                                        if current_label != new_target_name_str: # 현재 레이블과 다를 경우에만 변경
                                            try:
                                                obj.set_actor_label(new_target_name_str)
                                                unreal.log(f"      -> 연결된 액터 레이블 변경됨: '{current_label}' -> '{new_target_name_str}'")
                                            except Exception as label_e:
                                                unreal.log_warning(f"      -> 액터 '{current_label}' 레이블 변경 중 오류: {label_e}")
                                        else:
                                            unreal.log(f"      -> 연결된 액터 레이블이 이미 '{new_target_name_str}'(으)로 올바릅니다.")
                                    else:
                                        unreal.log_warning(f"      -> 바인딩된 오브젝트가 액터가 아님: {type(obj)}")
                            else:
                                unreal.log_warning("      -> 바인딩에 연결된 오브젝트를 찾을 수 없습니다.")
                        else:
                            unreal.log_error(f"  타겟 바인딩에서 유효한 MovieSceneObjectBindingID를 얻지 못했습니다: {target_binding_id_struct}")
                    except Exception as actor_label_e:
                        unreal.log_error(f"    연결된 액터 레이블 변경 중 예외 발생: {actor_label_e}")
                    # --- 액터 레이블 변경 로직 끝 ---
                else:
                    unreal.log_warning(f"    타겟 바인딩 이름 '{target_name_str}'을(를) 이름 변경 규칙에 맞게 파싱할 수 없습니다.")

            except Exception as e:
                unreal.log_error(f"    타겟 바인딩 이름 변경 중 오류 발생: {e}")

        else:
            unreal.log(f"\n소스 프리픽스 '{prefix}'에 해당하는 타겟 바인딩을 찾지 못했습니다.")

    # 최종 결과 로그
    unreal.log("\n----- 처리 완료 -----")
    if updated_count > 0:
        unreal.log(f"총 {updated_count}개의 Attach 트랙 섹션의 Constraint Binding ID가 업데이트되었습니다.")
    if renamed_count > 0:
        unreal.log(f"총 {renamed_count}개의 타겟 바인딩 이름이 변경되었습니다.")
    if updated_count > 0 or renamed_count > 0:
        unreal.log("시퀀스를 저장하여 변경사항을 확정하세요.")
    else:
        unreal.log("업데이트하거나 이름을 변경할 항목이 없습니다.")

# 스크립트 실행
auto_update_attach_constraints_by_name()
