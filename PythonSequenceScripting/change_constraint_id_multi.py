import unreal
import re # 정규표현식 모듈 임포트

# --- 사용자 설정: 복잡한 이름 <-> 프리픽스 매핑 ---
# 소스 이름의 시작 부분 (PC_ 제외, 대문자)을 키로, 원하는 프리픽스를 값으로 추가하세요.
# 예: PC_DemiGod_F_... 이름을 'DGF' 프리픽스로 처리하려면 아래와 같이 추가
prefix_mapping = {
    "DEMIGOD_F": "DGF",
    # 다른 복잡한 매핑 규칙 추가...
}
# 매핑 성능을 위해 가장 긴 키부터 확인하도록 정렬
prefix_mapping_sorted = dict(sorted(prefix_mapping.items(), key=lambda item: len(item[0]), reverse=True))
# ----------------------------------------------

def auto_update_attach_constraints_by_name():
    """
    현재 Level Sequence에서 '단 하나' 선택된 소스 바인딩(PC_XX_...)을 기준으로,
    선택된 모든 타겟 바인딩(SpotLight_YY_... 또는 char)의 Attach 트랙 Constraint Binding ID를
    소스 바인딩 ID로 설정하고, 타겟 이름도 소스 프리픽스와 번호 기준으로 변경합니다.

    로직 변경:
    - 소스 이름 규칙 완화: 'PC_XX' 형태면 인식 (뒤에 숫자 없어도 가능)
    - 프리픽스 매핑: 복잡한 소스 이름 (예: PC_DemiGod_F_...)을 지정된 프리픽스 (예: DGF)로 변환
    - 반드시 '하나의' 소스 바인딩(PC_...)만 선택해야 합니다.
    - 선택된 모든 타겟(SpotLight_... 또는 char)이 단일 소스 기준으로 업데이트됩니다.
    """

    # 정규표현식 패턴 정의
    # 소스: PC_, 다음 그룹1: 나머지 이름 부분 (non-greedy), 선택적 그룹2: 끝의 (숫자)
    source_pattern = re.compile(r"^PC[\\s_](.+?)(?:\\s+\\((\\d+)\\))?$", re.IGNORECASE)
    target_pattern = re.compile(
        r"^SpotLight_"
        r"(?:"
            r"(char)(_.*?)(\d+)"  # Case 1: char prefix -> group(1)='char', group(2)=middle, group(3)=num
            r"|"
            r"(\w+)(.*?)(\d+)"   # Case 2: other prefix -> group(4)=prefix, group(5)=middle, group(6)=num
        r")"
        r"(?:\s+\(\d+\))*?$",
        re.IGNORECASE
    )
    target_char_pattern = re.compile(r"^char$", re.IGNORECASE)


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
    source_map = {} # key: final_prefix (e.g., 'DGF'), value: (binding, number_str)
    generic_targets = [] # list of (binding, middle_part | None, orig_num | None, is_char_only: bool)

    unreal.log("선택된 바인딩 분류 시작...")
    for binding in selected_bindings:
        binding_name = str(binding.get_display_name())
        unreal.log(f"  처리 중: '{binding_name}'")

        source_match = source_pattern.match(binding_name)
        if source_match:
            raw_identifier = source_match.group(1).strip() # PC_ 다음 부분 (예: HM_Gstar, DemiGod_F_4001_01_BD)
            number_str = source_match.group(2) if source_match.group(2) is not None else "00" # 괄호 숫자 또는 00
            raw_identifier_upper = raw_identifier.upper()

            final_prefix = None

            # 1. 매핑 규칙 확인 (가장 긴 키부터)
            for map_key, map_value in prefix_mapping_sorted.items():
                if raw_identifier_upper.startswith(map_key):
                    final_prefix = map_value
                    unreal.log(f"      -> 매핑 규칙 적용: '{map_key}' -> '{final_prefix}'")
                    break # 첫 번째 매칭 규칙 사용

            # 2. 매핑 규칙 없으면 기본 규칙 적용 (첫 단어 추출)
            if final_prefix is None:
                # 밑줄이나 공백 기준으로 첫 단어 추출
                prefix_part = raw_identifier.split('_', 1)[0].split(' ', 1)[0]
                if prefix_part: # 추출된 부분이 있으면
                    final_prefix = prefix_part.upper()
                    unreal.log(f"      -> 기본 규칙 적용: 첫 단어 '{final_prefix}' 사용")
                else:
                    unreal.log_warning(f"      -> 프리픽스를 추출할 수 없습니다: '{binding_name}'")
                    continue # 이 소스는 건너뛰기

            # 최종 프리픽스 확인 후 저장
            if final_prefix:
                if final_prefix in source_map:
                    unreal.log_warning(f"    소스 프리픽스 '{final_prefix}'가 중복 감지되었습니다. 이 스크립트는 단일 소스만 지원합니다. 이전 바인딩 '{source_map[final_prefix][0].get_display_name()}' 대신 '{binding_name}' 사용 시도 (하지만 오류 발생 가능)")
                    # 중복이어도 일단 덮어쓰고 나중에 개수 체크로 거름
                source_map[final_prefix] = (binding, number_str)
                unreal.log(f"    -> 소스 바인딩 발견: (프리픽스: {final_prefix}, 번호: {number_str})")
            continue # 다음 바인딩으로

        target_match = target_pattern.match(binding_name)
        if target_match:
            middle_part = None
            orig_num = None
            # Check which group matched to get middle part and number correctly
            if target_match.group(1) is not None and target_match.group(1).lower() == 'char': # Case 1: Explicit 'char' prefix
                middle_part = target_match.group(2)
                orig_num = target_match.group(3)
            elif target_match.group(4) is not None: # Case 2: Other prefix
                middle_part = target_match.group(5)
                orig_num = target_match.group(6)

            if middle_part is None: middle_part = "" # Use empty string if no middle part found

            generic_targets.append((binding, middle_part, orig_num, False)) # is_char_only = False
            unreal.log(f"    -> 일반 타겟 바인딩 발견 및 추가: (중간: '{middle_part}', 숫자: {orig_num})")
            continue

        char_match = target_char_pattern.match(binding_name)
        if char_match:
            generic_targets.append((binding, None, None, True))
            unreal.log(f"    -> 'char' 전용 타겟 바인딩 발견 및 추가")
            continue

        unreal.log(f"    -> 분류되지 않음 (이름 규칙 불일치)")

    # --- 소스 유효성 검사 ---
    num_sources = len(source_map)
    if num_sources == 0:
        unreal.log_error("오류: 소스 바인딩 (PC_XX_...)이 선택되지 않았습니다. 하나를 선택하고 다시 시도하세요.")
        return
    if num_sources > 1:
        # 어떤 프리픽스들이 감지되었는지 보여주면 더 좋음
        detected_prefixes = list(source_map.keys())
        unreal.log_error(f"오류: {num_sources}개의 소스 바인딩 (PC_XX_...)이 감지되었습니다 (프리픽스: {detected_prefixes}). 이 스크립트는 한 번에 하나의 소스 바인딩만 처리할 수 있습니다. 정확히 하나의 소스만 선택하고 다시 시도하세요.")
        return

    # --- 단일 소스 정보 추출 ---
    source_prefix, (source_binding, source_number_str) = list(source_map.items())[0]
    source_binding_name = source_binding.get_display_name()
    unreal.log(f"\n단일 소스 확인: '{source_binding_name}' (프리픽스: {source_prefix}, 번호: {source_number_str})")

    if not generic_targets:
        unreal.log_warning("처리할 타겟 바인딩 (SpotLight_... 또는 char)이 선택되지 않았거나 이름 규칙에 맞지 않습니다.")
        return

    # --- 매칭 및 처리 (단일 소스 기준) ---
    updated_count = 0
    renamed_count = 0

    unreal.log(f"\n매칭 및 처리 시작: 소스 '{source_prefix}'를 모든 타겟 {len(generic_targets)}개에 적용합니다...")

    # 소스 바인딩 ID 가져오기 (한 번만)
    source_binding_id_struct = None
    source_guid = None
    try:
        source_binding_id_struct = unreal.MovieSceneSequenceExtensions.get_binding_id(level_sequence, source_binding)
        if not source_binding_id_struct or not isinstance(source_binding_id_struct, unreal.MovieSceneObjectBindingID):
             unreal.log_error(f"  소스 '{source_binding_name}'에서 유효한 ID 얻기 실패.")
             return
        source_guid = source_binding_id_struct.get_editor_property('guid')
        if not source_guid:
            unreal.log_error(f"  소스 '{source_binding_name}'에서 유효한 GUID를 얻지 못했습니다.")
            return
        unreal.log(f"  소스 바인딩 ID 정보 얻음: GUID={source_guid}")
    except Exception as e:
        unreal.log_error(f"  소스 '{source_binding_name}' ID 가져오기 오류: {e}")
        return

    # 각 타겟에 대해 처리 수행
    for target_binding, middle_part, orig_num, is_char_only in generic_targets:
        target_binding_name = target_binding.get_display_name()
        unreal.log(f"\n  -> 타겟 처리 시작: '{target_binding_name}' (is_char_only: {is_char_only})")
        unreal.log(f"     소스 '{source_binding_name}' 적용 중...")

        # 1. 타겟 바인딩의 Attach 트랙 Constraint ID 업데이트
        found_attach_track = False
        attach_updated_for_this_target = False
        for track in target_binding.get_tracks():
            if isinstance(track, unreal.MovieScene3DAttachTrack):
                found_attach_track = True
                track_name = track.get_name()
                try: track_name = track.get_display_name() or track_name
                except AttributeError: pass
                unreal.log(f"      -> Attach 트랙 발견: '{track_name}'")

                for section in track.get_sections():
                    if isinstance(section, unreal.MovieScene3DAttachSection):
                        orig_guid = None
                        try:
                            orig_constraint_id_struct = section.get_editor_property("constraint_binding_id")
                            if orig_constraint_id_struct and hasattr(orig_constraint_id_struct, 'guid'):
                                orig_guid = orig_constraint_id_struct.get_editor_property("guid")
                        except Exception as e:
                            unreal.log_warning(f"        섹션 '{section.get_name()}'에서 기존 GUID 가져오는 중 오류: {e}")

                        if orig_guid != source_guid:
                            try:
                                section.set_editor_property("constraint_binding_id", source_binding_id_struct)
                                unreal.log(f"        -> 섹션 '{section.get_name()}' Constraint ID 업데이트됨 (소스 GUID: {source_guid})")
                                attach_updated_for_this_target = True
                            except Exception as e:
                                unreal.log_error(f"        섹션 '{section.get_name()}'에 constraint_binding_id 설정 중 오류: {e}")
                        else:
                            unreal.log(f"        -> 섹션 '{section.get_name()}' Constraint ID는 이미 소스 GUID와 동일합니다.")
        if not found_attach_track:
             unreal.log_warning(f"      타겟 '{target_binding_name}'에서 Attach 트랙을 찾을 수 없습니다.")
        if attach_updated_for_this_target:
             updated_count += 1


        # 2. 타겟 바인딩 이름 변경 (단일 소스 정보 사용)
        rename_occurred_for_this_target = False
        try:
            target_name_text = target_binding.get_display_name()
            target_name_str = str(target_name_text)
            formatted_source_number = source_number_str.zfill(2)

            new_target_name_str = None
            should_rename_binding = False

            if is_char_only:
                # 'char' 전용 타겟: 중간 부분을 '_face_'로 고정하고 소스 정보 사용
                new_target_name_str = f"SpotLight_{source_prefix}_face_{formatted_source_number}"
                unreal.log(f"      'char' 전용 타겟 이름 생성 (소스 정보 사용): '{target_name_str}' -> '{new_target_name_str}'")
                should_rename_binding = True

            else:
                # 일반 SpotLight 타겟: 추출된 middle_part와 소스 정보 사용
                actual_middle_part = middle_part if middle_part is not None else ""
                new_target_name_str = f"SpotLight_{source_prefix}{actual_middle_part}{formatted_source_number}"

                if target_name_str != new_target_name_str:
                    unreal.log(f"      타겟 바인딩 이름 변경 필요: '{target_name_str}' -> '{new_target_name_str}'")
                    should_rename_binding = True
                else:
                     unreal.log(f"      타겟 바인딩 이름이 이미 '{new_target_name_str}'(으)로 올바릅니다.")

            # --- 이름 변경 및 액터 레이블 업데이트 ---
            if should_rename_binding:
                # 표시 이름 설정
                try:
                    new_target_name_text = unreal.Text(new_target_name_str)
                    target_binding.set_display_name(new_target_name_text)
                    unreal.log(f"        -> 표시 이름 변경됨")
                    rename_occurred_for_this_target = True
                except Exception as display_name_e:
                     unreal.log_warning(f"        -> 표시 이름 변경 중 오류: {display_name_e}")

                # 오브젝트 이름 설정
                try:
                    target_binding.set_name(new_target_name_str)
                    unreal.log(f"        -> 오브젝트 이름 변경됨")
                    rename_occurred_for_this_target = True
                except Exception as name_e:
                    unreal.log_warning(f"        -> 오브젝트 이름 변경 중 오류: {name_e}")

            # 액터 레이블 업데이트 (이름 변경 여부와 관계없이 시도, new_target_name_str 필요)
            if new_target_name_str:
                try:
                    target_binding_id_struct = unreal.MovieSceneSequenceExtensions.get_binding_id(level_sequence, target_binding)
                    if target_binding_id_struct and isinstance(target_binding_id_struct, unreal.MovieSceneObjectBindingID):
                        bound_objects = unreal.LevelSequenceEditorBlueprintLibrary.get_bound_objects(target_binding_id_struct)
                        if bound_objects:
                            for obj in bound_objects:
                                if isinstance(obj, unreal.Actor):
                                    current_label = obj.get_actor_label()
                                    if current_label != new_target_name_str:
                                        try:
                                            obj.set_actor_label(new_target_name_str)
                                            unreal.log(f"          -> 연결된 액터 레이블 변경됨: '{current_label}' -> '{new_target_name_str}'")
                                        except Exception as label_e:
                                            unreal.log_warning(f"          -> 액터 '{current_label}' 레이블 변경 중 오류: {label_e}")
                                else:
                                    unreal.log_warning(f"          -> 바인딩된 오브젝트가 액터가 아님: {type(obj)}")
                    else:
                        unreal.log_error(f"        타겟 '{target_binding_name}'에서 유효한 ID 얻기 실패 (액터 레이블 업데이트)")
                except Exception as actor_label_e:
                    unreal.log_error(f"      -> 연결된 액터 레이블 변경 중 예외 발생: {actor_label_e}")

            # --- 이름 변경 및 액터 레이블 업데이트 끝 ---

        except Exception as e:
            unreal.log_error(f"      타겟 '{target_binding_name}' 이름 처리 중 오류 발생: {e}")

        # 이름 변경이 실제로 발생했는지 확인 후 renamed_count 증가
        if rename_occurred_for_this_target:
            renamed_count += 1


    # 최종 결과 로그
    unreal.log("\n----- 처리 완료 -----")
    if updated_count > 0:
        unreal.log(f"총 {updated_count}개의 타겟 바인딩에서 Attach 트랙 Constraint Binding ID 업데이트가 시도되었습니다.")
    if renamed_count > 0:
        unreal.log(f"총 {renamed_count}개의 타겟 바인딩 이름이 변경되었습니다.")
    if updated_count > 0 or renamed_count > 0:
        unreal.log("시퀀서를 저장하여 변경사항을 확정하세요.")
    else:
        unreal.log("업데이트하거나 이름을 변경할 항목이 없습니다 (이미 적용되었거나 규칙에 맞는 항목 없음).")

# 스크립트 실행
auto_update_attach_constraints_by_name()
