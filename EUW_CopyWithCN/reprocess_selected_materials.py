import unreal

# --- 외부 주입 변수 안내 ---
# 블루프린트 또는 다른 스크립트에서 이 스크립트를 실행하기 전에 아래 변수들을 반드시 정의해야 합니다.
# 예시:
#
# master_path = "/Game/MyProject/Masters/My_Master_Mat"
# parameters_str = "emissive_color_mult:0.1; Tint:1,0,0,1"
# do_reparent = True
# do_parameter_edit = True

def parse_parameters_string(params_string):
    """
    세미콜론(;)으로 구분된 파라미터 문자열을 파싱합니다.
    - 스칼라:   param_name:0.5
    - 벡터:     param_name:1,0,0,1  (R,G,B) 또는 (R,G,B,A)
    - 텍스처:   param_name:/Game/Textures/MyTexture.MyTexture
    예시: "scalar_param:0.5; vector_param:1,0,0,1; texture_param:/Game/Path/T_Tex"
    """
    unreal.log("파라미터 문자열 파싱 시작...")
    parsed_params = []
    if not params_string or not isinstance(params_string, str):
        return parsed_params
    
    asset_lib = unreal.EditorAssetLibrary
    
    # 파라미터 쌍을 세미콜론으로 분리합니다.
    pairs = [pair.strip() for pair in params_string.split(';') if pair.strip()]
    
    for pair in pairs:
        if ':' not in pair:
            unreal.log_warning(f"  - 파라미터 파싱 경고: 잘못된 형식의 쌍을 건너뜁니다 -> '{pair}'")
            continue
        
        key, value_str = pair.split(':', 1)
        key = key.strip()
        value_str = value_str.strip()

        if not key or not value_str:
            unreal.log_warning(f"  - 파라미터 파싱 경고: 비어있는 키 또는 값을 건너뜁니다 -> '{pair}'")
            continue

        if value_str.startswith('/Game/') or value_str.startswith('/Engine/'):
            texture_asset = asset_lib.load_asset(value_str)
            if isinstance(texture_asset, unreal.Texture):
                parsed_params.append({'name': key, 'type': 'texture', 'value': texture_asset})
                unreal.log(f"    - 텍스처 파라미터 발견: '{key}' -> '{value_str}'")
            else:
                unreal.log_warning(f"  - 파라미터 파싱 경고: 텍스처를 찾을 수 없거나 유효하지 않습니다 -> '{value_str}'")
        
        elif ',' in value_str:
            try:
                color_parts = [float(c.strip()) for c in value_str.split(',')]
                if len(color_parts) == 3:
                    color = unreal.LinearColor(color_parts[0], color_parts[1], color_parts[2], 1.0)
                    parsed_params.append({'name': key, 'type': 'vector', 'value': color})
                    unreal.log(f"    - 벡터 파라미터 발견: '{key}' -> {color}")
                elif len(color_parts) == 4:
                    color = unreal.LinearColor(color_parts[0], color_parts[1], color_parts[2], color_parts[3])
                    parsed_params.append({'name': key, 'type': 'vector', 'value': color})
                    unreal.log(f"    - 벡터 파라미터 발견: '{key}' -> {color}")
                else:
                    unreal.log_warning(f"  - 파라미터 파싱 경고: 벡터 값은 3개 또는 4개의 숫자여야 합니다 -> '{value_str}'")
            except ValueError:
                unreal.log_warning(f"  - 파라미터 파싱 경고: 벡터의 일부를 숫자로 변환할 수 없습니다 -> '{value_str}'")

        else:
            try:
                scalar_value = float(value_str)
                parsed_params.append({'name': key, 'type': 'scalar', 'value': scalar_value})
                unreal.log(f"    - 스칼라 파라미터 발견: '{key}' -> {scalar_value}")
            except ValueError:
                unreal.log_warning(f"  - 파라미터 파싱 경고: 스칼라 값을 숫자로 변환할 수 없습니다 -> '{value_str}'")
    
    return parsed_params

def reprocess_selected_materials():
    """
    콘텐츠 브라우저에서 선택된 머티리얼 인스턴스의 부모를 교체하고 파라미터를 수정한 뒤 저장합니다.
    """
    unreal.log("선택된 머티리얼 재처리 로직을 시작합니다.")

    # --- 내부 변수 재지정 ---
    NEW_PARENT_MATERIAL_PATH = master_path
    PARAMETERS_TO_SET = parse_parameters_string(parameters_str)
    DO_REPARENT = do_reparent
    DO_PARAMETER_EDIT = do_parameter_edit

    asset_lib = unreal.EditorAssetLibrary
    util_lib = unreal.EditorUtilityLibrary
    material_lib = unreal.MaterialEditingLibrary

    # 1. 새 부모 머티리얼 로드 및 유효성 검사
    new_parent_material = None
    if DO_REPARENT:
        new_parent_material = asset_lib.load_asset(NEW_PARENT_MATERIAL_PATH)
        if not new_parent_material or not isinstance(new_parent_material, unreal.Material):
            unreal.log_error(f"오류: 새 마스터 머티리얼을 찾을 수 없거나 유효하지 않습니다: {NEW_PARENT_MATERIAL_PATH}")
            return

    # 2. 콘텐츠 브라우저에서 선택된 에셋 가져오기
    selected_assets = util_lib.get_selected_assets()
    if not selected_assets:
        unreal.log_warning("오류: 콘텐츠 브라우저에서 머티리얼 인스턴스를 먼저 선택해주세요.")
        return

    # 3. 선택된 에셋 중 머티리얼 인스턴스만 필터링
    material_instances_to_process = [asset for asset in selected_assets if isinstance(asset, unreal.MaterialInstanceConstant)]
    if not material_instances_to_process:
        unreal.log_warning("오류: 선택된 에셋 중에 처리할 머티리얼 인스턴스가 없습니다.")
        return

    unreal.log(f"총 {len(material_instances_to_process)}개의 머티리얼 인스턴스를 처리합니다.")

    # 4. 각 머티리얼 인스턴스 처리
    processed_count = 0
    with unreal.ScopedEditorTransaction("Reprocess Selected Materials") as transaction:
        for mat_instance in material_instances_to_process:
            instance_name = mat_instance.get_name()
            mat_path = mat_instance.get_path_name()
            unreal.log(f"--- '{instance_name}' ({mat_path}) 처리 시작 ---")

            mat_to_edit = mat_instance
            was_modified = False

            # 4-1. 부모 머티리얼 교체
            if DO_REPARENT:
                mat_instance.modify()
                if mat_instance.get_editor_property('parent') != new_parent_material:
                    unreal.log(f"  > 부모 변경 시도: '{new_parent_material.get_name()}'")
                    material_lib.set_material_instance_parent(mat_instance, new_parent_material)
                    
                    if mat_instance.get_editor_property('parent') == new_parent_material:
                        unreal.log("    + 확인: 부모 변경이 성공적으로 적용되었습니다.")
                        unreal.log("  > 부모 변경사항을 디스크에 저장하고 에셋을 다시 로드합니다...")
                        asset_lib.save_loaded_asset(mat_instance)
                        mat_to_edit = asset_lib.load_asset(mat_path)
                        was_modified = True
                    else:
                        unreal.log_warning(f"  실패: '{instance_name}'의 부모 변경에 실패했습니다. 다음 에셋으로 넘어갑니다.")
                        continue
                else:
                    unreal.log("  > 부모가 이미 목표 머티리얼이므로 변경을 건너뜁니다.")

            # 4-2. 파라미터 수정
            if DO_PARAMETER_EDIT and PARAMETERS_TO_SET:
                mat_to_edit.modify()
                unreal.log(f"  > '{mat_to_edit.get_name()}'의 파라미터 값 수정을 시작합니다.")
                for param_info in PARAMETERS_TO_SET:
                    param_name = param_info['name']
                    param_type = param_info['type']
                    param_value = param_info['value']
                    
                    success = False
                    if param_type == 'scalar':
                        success = material_lib.set_material_instance_scalar_parameter_value(mat_to_edit, param_name, param_value)
                    elif param_type == 'vector':
                        success = material_lib.set_material_instance_vector_parameter_value(mat_to_edit, param_name, param_value)
                    elif param_type == 'texture':
                        success = material_lib.set_material_instance_texture_parameter_value(mat_to_edit, param_name, param_value)
                    
                    if success:
                        unreal.log(f"    - '{param_type}' 파라미터 '{param_name}' 값을 성공적으로 설정했습니다.")
                        was_modified = True
                    else:
                        unreal.log(f"    - 정보: '{param_name}' 파라미터가 없거나 타입이 일치하지 않아 건너뜁니다.")

            # 4-3. 최종 저장
            if was_modified:
                unreal.log(f"  > 변경사항을 저장합니다.")
                asset_lib.save_loaded_asset(mat_to_edit)
            else:
                unreal.log(f"  > 변경사항이 없어 저장을 건너뜁니다.")
                
            processed_count += 1

    if processed_count == 0:
        unreal.log_warning("처리된 머티리얼이 없어 작업을 종료합니다.")
    else:
        unreal.log(f"총 {processed_count}개의 머티리얼 재처리가 완료되었습니다.")


# 스크립트 실행
reprocess_selected_materials() 