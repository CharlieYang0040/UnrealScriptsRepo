import unreal

# --- 외부 주입 변수 안내 ---
# 블루프린트 또는 다른 스크립트에서 이 스크립트를 실행하기 전에 아래 변수들을 반드시 정의해야 합니다.
# 예시 (블루프린트의 Execute Python Script 노드의 'Python Script' 핀에 입력):
#
# output_path = "/Game/MyProject/Materials/Generated"
# master_path = "/Game/MyProject/Materials/Masters/My_Master_Mat"
# source_parent_prefix = "Basic_Master_Mat"
# suffix = "_CN"
# parameters_str = "emissive_color_mult:0.1; Tint:1,0,0,1"
# do_reparent = True
# do_parameter_edit = True
# do_apply_to_actor = True
# do_process_static_meshes = True # 스태틱 메시 컴포넌트도 처리할지 여부
# do_check_source_prefix = True   # 부모 머티리얼의 이름 접두사를 검사할지 여부
# do_overwrite_existing = False # 이미 존재하는 에셋을 강제로 덮어쓸지 여부

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

        # 값의 유형을 판별합니다.
        # 1. 텍스처 파라미터 (콘텐츠 브라우저 경로)
        if value_str.startswith('/Game/') or value_str.startswith('/Engine/'):
            texture_asset = asset_lib.load_asset(value_str)
            if isinstance(texture_asset, unreal.Texture):
                parsed_params.append({'name': key, 'type': 'texture', 'value': texture_asset})
                unreal.log(f"    - 텍스처 파라미터 발견: '{key}' -> '{value_str}'")
            else:
                unreal.log_warning(f"  - 파라미터 파싱 경고: 텍스처를 찾을 수 없거나 유효하지 않습니다 -> '{value_str}'")
        
        # 2. 벡터 파라미터 (r,g,b,a)
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

        # 3. 스칼라 파라미터
        else:
            try:
                scalar_value = float(value_str)
                parsed_params.append({'name': key, 'type': 'scalar', 'value': scalar_value})
                unreal.log(f"    - 스칼라 파라미터 발견: '{key}' -> {scalar_value}")
            except ValueError:
                unreal.log_warning(f"  - 파라미터 파싱 경고: 스칼라 값을 숫자로 변환할 수 없습니다 -> '{value_str}'")
    
    return parsed_params

def run_actor_material_conditional_reparent_logic():
    unreal.log("조건부 머티리얼 복사 및 부모 교체 로직을 시작합니다.")

    # --- 내부 변수 재지정 (가독성을 위해 외부 변수를 내부 변수로 할당) ---
    DESTINATION_FOLDER = output_path
    NEW_PARENT_MATERIAL_PATH = master_path
    SOURCE_PARENT_MATERIAL_PREFIX = source_parent_prefix
    SUFFIX = suffix
    PARAMETERS_TO_SET = parse_parameters_string(parameters_str)
    DO_REPARENT = do_reparent
    DO_PARAMETER_EDIT = do_parameter_edit
    DO_APPLY_TO_ACTOR = do_apply_to_actor
    DO_PROCESS_STATIC_MESHES = do_process_static_meshes
    DO_CHECK_SOURCE_PREFIX = do_check_source_prefix
    DO_OVERWRITE_EXISTING = do_overwrite_existing

    unreal.log(f"파싱된 파라미터: {PARAMETERS_TO_SET}")

    asset_lib = unreal.EditorAssetLibrary
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)

    # 교체할 부모 머티리얼 에셋 로드
    new_parent_material = asset_lib.load_asset(NEW_PARENT_MATERIAL_PATH)
    if DO_REPARENT and (not new_parent_material or not isinstance(new_parent_material, unreal.Material)):
        unreal.log_error(f"오류: 새 마스터 머티리얼을 찾을 수 없거나 유효하지 않습니다: {NEW_PARENT_MATERIAL_PATH}")
        return

    # 선택된 액터 가져오기
    selected_actors = editor_actor_subsystem.get_selected_level_actors()
    if not selected_actors:
        unreal.log_warning("오류: 레벨 뷰포트에서 액터를 먼저 선택해주세요.")
        return
    
    unreal.log(f"총 {len(selected_actors)}개의 선택된 액터에 대한 작업을 시작합니다.")

    total_materials_processed_across_actors = 0
    with unreal.ScopedEditorTransaction("Configurable Multi-Actor Material Processor") as transaction:
        for selected_actor in selected_actors:
            unreal.log(f"========== 액터 처리 시작: '{selected_actor.get_actor_label()}' ==========")
            selected_actor.modify()

            # 처리할 컴포넌트 목록을 준비합니다.
            components_to_process = []
            
            # 스켈레탈 메시 컴포넌트를 목록에 추가합니다.
            skeletal_mesh_components = selected_actor.get_components_by_class(unreal.SkeletalMeshComponent)
            components_to_process.extend(skeletal_mesh_components)

            # 스태틱 메시 컴포넌트도 처리하도록 설정된 경우, 목록에 추가합니다.
            if DO_PROCESS_STATIC_MESHES:
                static_mesh_components = selected_actor.get_components_by_class(unreal.StaticMeshComponent)
                components_to_process.extend(static_mesh_components)

            if not components_to_process:
                unreal.log_warning(f"  - 경고: 처리할 스켈레탈 또는 스태틱 메시 컴포넌트가 없어 건너뜁니다.")
                continue

            # --- 폴더 이름 결정을 위한 기준 에셋 이름 찾기 ---
            base_name_for_folder = ""
            # 1. 스켈레탈 메시에서 기준 이름 찾기
            for comp in skeletal_mesh_components:
                if comp.skeletal_mesh:
                    base_name_for_folder = comp.skeletal_mesh.get_name()
                    unreal.log(f"  - 폴더 기준 에셋: 스켈레탈 메시 '{base_name_for_folder}'")
                    break
            
            # 2. 스태틱 메시에서 기준 이름 찾기 (위에서 못 찾았을 경우)
            if not base_name_for_folder and DO_PROCESS_STATIC_MESHES:
                if "static_mesh_components" in locals() and static_mesh_components:
                    for comp in static_mesh_components:
                        if comp.static_mesh:
                            base_name_for_folder = comp.static_mesh.get_name()
                            unreal.log(f"  - 폴더 기준 에셋: 스태틱 메시 '{base_name_for_folder}'")
                            break

            # 3. 폴백: 액터 이름 사용
            if not base_name_for_folder:
                base_name_for_folder = selected_actor.get_actor_label()
                unreal.log(f"  - 경고: 기준 메시 에셋을 찾지 못해 액터 이름 '{base_name_for_folder}'을(를) 사용합니다.")

            # 기준 이름을 기반으로 대상 폴더 경로 생성
            clean_base_name = base_name_for_folder.replace(' ', '_')
            actor_destination_folder = f"{DESTINATION_FOLDER.rstrip('/')}/{clean_base_name}"

            # 경로 생성
            if not asset_lib.does_directory_exist(actor_destination_folder):
                asset_lib.make_directory(actor_destination_folder)

            unreal.log(f"  - 발견된 총 컴포넌트 수: {len(components_to_process)}개. 대상 폴더: '{actor_destination_folder}'")
            
            materials_processed_on_actor = 0
            for mesh_comp in components_to_process:
                component_name = mesh_comp.get_name()
                num_materials = mesh_comp.get_num_materials()
                unreal.log(f"--- 컴포넌트 처리 시작: '{component_name}' (머티리얼 슬롯: {num_materials}개) ---")

                if num_materials == 0:
                    continue

                mesh_comp.modify()

                materials_to_apply_on_comp = {}
                for index in range(num_materials):
                    material_instance = mesh_comp.get_material(index)

                    if not isinstance(material_instance, unreal.MaterialInstanceConstant):
                        continue
                    
                    material_to_process = None
                    is_newly_created = False

                    if material_instance.get_name().endswith(SUFFIX):
                        unreal.log(f"  [{index}번 슬롯] 이미 {SUFFIX} 머티리얼이 적용되어 있습니다. 재처리합니다: {material_instance.get_name()}")
                        material_to_process = material_instance
                    else:
                        parent_material = material_instance.get_editor_property('parent')
                    
                        if not parent_material:
                            unreal.log(f"  [{index}번 슬롯] 건너뜁니다. 이유: 부모 머티리얼이 없습니다.")
                            continue
                        if DO_REPARENT and parent_material == new_parent_material:
                            unreal.log(f"  [{index}번 슬롯] 건너뜁니다. 이유: 부모가 이미 목표 머티리얼입니다.")
                            continue
                        if DO_CHECK_SOURCE_PREFIX and not parent_material.get_name().startswith(SOURCE_PARENT_MATERIAL_PREFIX):
                            unreal.log(f"  [{index}번 슬롯] 건너뜁니다. 이유: 부모 이름이 '{SOURCE_PARENT_MATERIAL_PREFIX}'(으)로 시작하지 않습니다: {parent_material.get_name()}")
                            continue
                        
                        unreal.log(f"  [{index}번 슬롯] 조건 일치. 처리를 시작합니다: {material_instance.get_name()}")
                        original_path = material_instance.get_path_name()
                        original_name = material_instance.get_name()
                        new_name = f"{original_name}{SUFFIX}"
                        new_path = f"{actor_destination_folder.rstrip('/')}/{new_name}"
                        
                        if DO_OVERWRITE_EXISTING:
                            unreal.log(f"  덮어쓰기 옵션 활성화. '{new_name}'을(를) 강제로 복제합니다.")
                            material_to_process = asset_lib.duplicate_asset(original_path, new_path)
                        else:
                            if asset_lib.does_asset_exist(new_path):
                                unreal.log(f"  에셋이 이미 존재하여 로드합니다: {new_path}")
                                material_to_process = asset_lib.load_asset(new_path)
                            else:
                                material_to_process = asset_lib.duplicate_asset(original_path, new_path)
                        
                        is_newly_created = True

                    if not material_to_process:
                        if is_newly_created:
                            unreal.log_error(f"  실패: {SUFFIX} 에셋을 생성하거나 로드할 수 없어 건너뜁니다.")
                        continue

                    material_to_process.modify()
                    
                    if DO_REPARENT:
                        current_parent = material_to_process.get_editor_property('parent')
                        if current_parent != new_parent_material:
                            unreal.log(f"  > 부모 변경 시도: '{material_to_process.get_name()}'")
                            unreal.MaterialEditingLibrary.set_material_instance_parent(material_to_process, new_parent_material)
                            parent_after_change = material_to_process.get_editor_property('parent')
                            if parent_after_change == new_parent_material:
                                unreal.log("    + 확인: 부모 변경이 에셋에 성공적으로 적용되었습니다.")
                            else:
                                unreal.log_warning(f"  실패 확인: 부모 변경이 실제로 적용되지 않았습니다. 이 머티리얼의 나머지 처리를 건너뜁니다.")
                                continue
                        else:
                            unreal.log(f"  > 부모가 이미 목표 머티리얼이므로 변경을 건너뜁니다.")

                    if DO_PARAMETER_EDIT and PARAMETERS_TO_SET:
                        unreal.log(f"    - '{material_to_process.get_name()}'의 파라미터 값을 수정합니다.")
                        for param_info in PARAMETERS_TO_SET:
                            param_name = param_info['name']
                            param_type = param_info['type']
                            param_value = param_info['value']

                            success = False
                            if param_type == 'scalar':
                                success = unreal.MaterialEditingLibrary.set_material_instance_scalar_parameter_value(material_to_process, param_name, param_value)
                            elif param_type == 'vector':
                                success = unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(material_to_process, param_name, param_value)
                            elif param_type == 'texture':
                                if param_value:
                                    success = unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_to_process, param_name, param_value)
                            
                            if success:
                                unreal.log(f"      - '{param_type}' 파라미터 '{param_name}' 값을 성공적으로 설정했습니다.")
                            else:
                                unreal.log(f"      - 정보: '{param_name}' 파라미터가 없거나 타입이 일치하지 않아 건너뜁니다.")
                    
                    asset_lib.save_loaded_asset(material_to_process)
                    if is_newly_created:
                        materials_to_apply_on_comp[index] = material_to_process
                
                if materials_to_apply_on_comp:
                    materials_processed_on_actor += len(materials_to_apply_on_comp)

            if DO_APPLY_TO_ACTOR:
                if not materials_to_apply_on_comp:
                    unreal.log(f"  '{component_name}' 컴포넌트에 새로 적용할 머티리얼이 없어 적용 단계를 건너뜁니다.")
                else:
                    unreal.log(f"  -> '{component_name}' 컴포넌트에 {len(materials_to_apply_on_comp)}개의 새 머티리얼을 적용합니다.")
                    for index, new_mat in materials_to_apply_on_comp.items():
                        mesh_comp.set_material(index, new_mat)
                        material_after_set = mesh_comp.get_material(index)
                        if material_after_set != new_mat:
                            current_mat_path = material_after_set.get_path_name() if material_after_set else "None"
                            unreal.log_error(f"      - 적용 실패 확인! 슬롯의 머티리얼이 변경되지 않았습니다.")
                            unreal.log_error(f"        (현재 슬롯의 머티리얼: {current_mat_path})")
                            unreal.log_error(f"        - 원인 추정: Sequencer의 Material Track이 이 슬롯을 제어하고 있을 수 있습니다.")
            else:
                if materials_to_apply_on_comp:
                    unreal.log(f"  - 액터에 머티리얼 적용 단계(do_apply_to_actor=False)는 건너뜁니다.")

            total_materials_processed_across_actors += materials_processed_on_actor

        if total_materials_processed_across_actors == 0:
            unreal.log_warning("처리된 머티리얼이 없어 전체 작업을 취소합니다.")
            transaction.cancel()
            return

    unreal.log(f"모든 액터의 머티리얼 처리가 완료되었습니다. (총 {total_materials_processed_across_actors}개 처리)")

# 스크립트 실행
run_actor_material_conditional_reparent_logic()