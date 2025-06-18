import unreal

# --- 외부 주입 변수 안내 ---
# 이 스크립트는 'execute_copy_with_cn.py'와 'reprocess_selected_materials.py'의
# 실행 계획을 미리 보여줍니다. 실제 실행 스크립트와 동일한 변수들을 설정해야 합니다.
#
# 예시 (블루프린트의 Execute Python Script 노드의 'Python Script' 핀에 입력):
#
# # Actor 처리 미리보기용 변수
# output_path = "/Game/MyProject/Materials/Generated"
# master_path = "/Game/MyProject/Materials/Masters/My_Master_Mat"
# source_parent_prefix = "Basic_Master_Mat"
# suffix = "_CN"
# parameters_str = "emissive_color_mult:0.1; Tint:1,0,0,1"
# do_reparent = True
# do_parameter_edit = True
# do_apply_to_actor = True
# do_process_static_meshes = True
# do_check_source_prefix = True
# do_overwrite_existing = False
#
# # 재처리 미리보기용 변수 (위와 동일한 변수 사용)
# # master_path = "..."
# # parameters_str = "..."
# # do_reparent = True
# # do_parameter_edit = True

# --- 블루프린트 연동 안내 ---
# 이 스크립트는 실행 계획을 문자열(String)으로 반환합니다.
# 블루프린트의 'Execute Python Script' 노드의 'Return Value' 핀을 변수에 저장하거나
# 위젯의 텍스트 블록에 직접 연결하여 UI에 미리보기 결과를 표시할 수 있습니다.
# 스크립트 실행 결과는 여전히 언리얼의 'Output Log'에도 출력됩니다.

def parse_parameters_string(params_string):
    """
    세미콜론(;)으로 구분된 파라미터 문자열을 파싱합니다.
    - 스칼라:   param_name:0.5
    - 벡터:     param_name:1,0,0,1  (R,G,B) 또는 (R,G,B,A)
    - 텍스처:   param_name:/Game/Textures/MyTexture.MyTexture
    예시: "scalar_param:0.5; vector_param:1,0,0,1; texture_param:/Game/Path/T_Tex"
    """
    parsed_params = []
    if not params_string or not isinstance(params_string, str):
        return parsed_params
    
    asset_lib = unreal.EditorAssetLibrary
    pairs = [pair.strip() for pair in params_string.split(';') if pair.strip()]
    
    for pair in pairs:
        if ':' not in pair: continue
        
        key, value_str = pair.split(':', 1)
        key = key.strip()
        value_str = value_str.strip()

        if not key or not value_str: continue

        if value_str.startswith('/Game/') or value_str.startswith('/Engine/'):
            texture_asset = asset_lib.load_asset(value_str)
            if isinstance(texture_asset, unreal.Texture):
                parsed_params.append({'name': key, 'type': '텍스처', 'value': value_str})
            else:
                parsed_params.append({'name': key, 'type': '텍스처', 'value': f"{value_str} (경고: 찾을 수 없음)"})
        
        elif ',' in value_str:
            try:
                color_parts = [float(c.strip()) for c in value_str.split(',')]
                if len(color_parts) in [3, 4]:
                    parsed_params.append({'name': key, 'type': '벡터', 'value': value_str})
                else:
                    parsed_params.append({'name': key, 'type': '벡터', 'value': f"{value_str} (경고: 잘못된 형식)"})
            except ValueError:
                parsed_params.append({'name': key, 'type': '벡터', 'value': f"{value_str} (경고: 잘못된 형식)"})
        else:
            try:
                float(value_str)
                parsed_params.append({'name': key, 'type': '스칼라', 'value': value_str})
            except ValueError:
                parsed_params.append({'name': key, 'type': '스칼라', 'value': f"{value_str} (경고: 잘못된 형식)"})
    return parsed_params

def preview_actor_processing_logic(selected_actors, settings):
    report_lines = []
    report_lines.append("==========================================================")
    report_lines.append("         액터 기반 머티리얼 처리 작업 미리보기")
    report_lines.append("==========================================================")
    
    asset_lib = unreal.EditorAssetLibrary
    DESTINATION_FOLDER = settings['output_path']
    NEW_PARENT_MATERIAL_PATH = settings['master_path']
    SOURCE_PARENT_MATERIAL_PREFIX = settings['source_parent_prefix']
    SUFFIX = settings['suffix']
    PARAMETERS_TO_SET = settings['parameters_to_set']
    DO_REPARENT = settings['do_reparent']
    DO_PARAMETER_EDIT = settings['do_parameter_edit']
    DO_APPLY_TO_ACTOR = settings['do_apply_to_actor']
    DO_PROCESS_STATIC_MESHES = settings['do_process_static_meshes']
    DO_CHECK_SOURCE_PREFIX = settings['do_check_source_prefix']
    DO_OVERWRITE_EXISTING = settings['do_overwrite_existing']

    report_lines.append("주의: 이 스크립트는 실제 작업을 수행하지 않으며, 계획을 출력하기만 합니다.")

    if not all([DESTINATION_FOLDER, NEW_PARENT_MATERIAL_PATH, SOURCE_PARENT_MATERIAL_PREFIX, SUFFIX]):
        report_lines.append("미리보기를 위해 output_path, master_path, source_parent_prefix, suffix 변수를 모두 설정해야 합니다.")
        return "\n".join(report_lines)

    new_parent_material = asset_lib.load_asset(NEW_PARENT_MATERIAL_PATH)
    if DO_REPARENT and not new_parent_material:
        report_lines.append(f"오류: 목표 마스터 머티리얼을 찾을 수 없습니다: {NEW_PARENT_MATERIAL_PATH}")
        return "\n".join(report_lines)
        
    report_lines.append(f"총 {len(selected_actors)}개의 선택된 액터에 대한 처리 계획을 생성합니다.")
    report_lines.append(f" - 결과물 저장 기본 경로: {DESTINATION_FOLDER}")
    report_lines.append(f" - 생성될 머티리얼 접미사: {SUFFIX}")
    if DO_REPARENT: report_lines.append(f" - 목표 마스터 머티리얼: {NEW_PARENT_MATERIAL_PATH}")
    if DO_CHECK_SOURCE_PREFIX: report_lines.append(f" - 원본 부모 머티리얼 접두사: {SOURCE_PARENT_MATERIAL_PREFIX}")
    report_lines.append("----------------------------------------------------------")

    total_materials_to_process = 0
    
    for selected_actor in selected_actors:
        actor_label = selected_actor.get_actor_label()
        report_lines.append(f"▶ 액터 '{actor_label}' 처리 계획:")

        skeletal_mesh_components = selected_actor.get_components_by_class(unreal.SkeletalMeshComponent)
        static_mesh_components = selected_actor.get_components_by_class(unreal.StaticMeshComponent) if DO_PROCESS_STATIC_MESHES else []
        components_to_process = skeletal_mesh_components + static_mesh_components

        if not components_to_process:
            report_lines.append("  - 이 액터에는 처리할 스켈레탈 또는 스태틱 메시 컴포넌트가 없습니다.")
            continue

        base_name_for_folder = ""
        for comp in skeletal_mesh_components:
            if comp.skeletal_mesh:
                base_name_for_folder = comp.skeletal_mesh.get_name()
                report_lines.append(f"  - 폴더 기준 에셋: 스켈레탈 메시 '{base_name_for_folder}'")
                break
        if not base_name_for_folder and DO_PROCESS_STATIC_MESHES:
            for comp in static_mesh_components:
                if comp.static_mesh:
                    base_name_for_folder = comp.static_mesh.get_name()
                    report_lines.append(f"  - 폴더 기준 에셋: 스태틱 메시 '{base_name_for_folder}'")
                    break
        if not base_name_for_folder:
            base_name_for_folder = actor_label
            report_lines.append(f"  - 경고: 기준 에셋을 찾지 못해 액터 이름 '{base_name_for_folder}'을(를) 폴더 이름으로 사용합니다.")
        
        clean_base_name = base_name_for_folder.replace(' ', '_')
        actor_destination_folder = f"{DESTINATION_FOLDER.rstrip('/')}/{clean_base_name}"
        report_lines.append(f"  - 생성/사용될 폴더: '{actor_destination_folder}'")

        actor_material_count = 0
        for mesh_comp in components_to_process:
            comp_name = mesh_comp.get_name()
            num_materials = mesh_comp.get_num_materials()
            if num_materials == 0: continue
            
            report_lines.append(f"  - 컴포넌트 '{comp_name}':")
            
            for index in range(num_materials):
                material_instance = mesh_comp.get_material(index)
                
                if not isinstance(material_instance, unreal.MaterialInstanceConstant):
                    continue
                
                mat_name = material_instance.get_name()
                
                if mat_name.endswith(SUFFIX):
                    actor_material_count += 1
                    report_lines.append(f"    - [{index}] '{mat_name}' (재처리 대상)")
                    if DO_REPARENT and new_parent_material and material_instance.get_editor_property('parent') != new_parent_material:
                        report_lines.append(f"      - [계획] 부모를 '{NEW_PARENT_MATERIAL_PATH}' (으)로 변경합니다.")
                    if DO_PARAMETER_EDIT and PARAMETERS_TO_SET:
                        report_lines.append(f"      - [계획] 파라미터를 수정합니다.")
                    if not (DO_REPARENT or DO_PARAMETER_EDIT):
                        report_lines.append(f"      - [정보] 재처리 옵션이 꺼져있어 실제 변경은 없습니다.")

                else:
                    parent_material = material_instance.get_editor_property('parent')
                    
                    if not parent_material: continue
                    if DO_REPARENT and parent_material == new_parent_material: continue
                    if DO_CHECK_SOURCE_PREFIX and not parent_material.get_name().startswith(SOURCE_PARENT_MATERIAL_PREFIX): continue
                    
                    actor_material_count += 1
                    report_lines.append(f"    - [{index}] '{mat_name}' (신규 처리 대상)")
                    
                    new_name = f"{mat_name}{SUFFIX}"
                    new_path = f"{actor_destination_folder.rstrip('/')}/{new_name}"

                    if asset_lib.does_asset_exist(new_path) and not DO_OVERWRITE_EXISTING:
                        report_lines.append(f"      - [정보] 이미 존재하는 에셋 '{new_name}'을(를) 재사용/재처리합니다.")
                    elif asset_lib.does_asset_exist(new_path) and DO_OVERWRITE_EXISTING:
                        report_lines.append(f"      - [계획] '{new_name}'을(를) 강제로 덮어쓰기 복제합니다.")
                    else:
                        report_lines.append(f"      - [계획] '{new_name}' (으)로 신규 복제합니다.")

                    if DO_REPARENT:
                        report_lines.append(f"      - [계획] 부모를 '{NEW_PARENT_MATERIAL_PATH}' (으)로 변경합니다.")
                    if DO_PARAMETER_EDIT and PARAMETERS_TO_SET:
                        report_lines.append(f"      - [계획] 파라미터를 수정합니다.")
                    if DO_APPLY_TO_ACTOR:
                         report_lines.append(f"      - [계획] 처리된 머티리얼을 이 슬롯에 다시 적용합니다.")
        
        if actor_material_count == 0:
             report_lines.append(f"  - 이 액터에서 처리할 조건에 맞는 머티리얼을 찾지 못했습니다.")
        total_materials_to_process += actor_material_count
        report_lines.append("")

    report_lines.append("==================== 미리보기 요약 ====================")
    if total_materials_to_process > 0:
        report_lines.append(f"총 {len(selected_actors)}개 액터에서 {total_materials_to_process}개의 머티리얼이 처리될 예정입니다.")
    else:
        report_lines.append("선택된 액터들에서 처리할 조건에 맞는 머티리얼을 찾지 못했습니다.")
    report_lines.append("==========================================================")
    return "\n".join(report_lines)


def preview_reprocessing_logic(material_instances, settings):
    report_lines = []
    report_lines.append("==========================================================")
    report_lines.append("     콘텐츠 브라우저 기반 재처리 작업 미리보기")
    report_lines.append("==========================================================")
    
    asset_lib = unreal.EditorAssetLibrary
    NEW_PARENT_MATERIAL_PATH = settings['master_path']
    PARAMETERS_TO_SET = settings['parameters_to_set']
    DO_REPARENT = settings['do_reparent']
    DO_PARAMETER_EDIT = settings['do_parameter_edit']

    report_lines.append("주의: 이 스크립트는 실제 작업을 수행하지 않으며, 계획을 출력하기만 합니다.")

    new_parent_material = None
    if DO_REPARENT:
        if not NEW_PARENT_MATERIAL_PATH:
            report_lines.append("미리보기를 위해 master_path 변수를 설정해야 합니다.")
            return "\n".join(report_lines)
        new_parent_material = asset_lib.load_asset(NEW_PARENT_MATERIAL_PATH)
        if not new_parent_material:
            report_lines.append(f"오류: 목표 마스터 머티리얼을 찾을 수 없습니다: {NEW_PARENT_MATERIAL_PATH}")
            return "\n".join(report_lines)
    
    report_lines.append(f"총 {len(material_instances)}개의 선택된 머티리얼 인스턴스에 대한 처리 계획을 생성합니다.")
    if DO_REPARENT: report_lines.append(f" - 목표 마스터 머티리얼: {NEW_PARENT_MATERIAL_PATH}")
    report_lines.append("----------------------------------------------------------")
    
    for mat_instance in material_instances:
        report_lines.append(f"▶ 머티리얼 '{mat_instance.get_name()}' 처리 계획:")

        if DO_REPARENT and new_parent_material:
            if mat_instance.get_editor_property('parent') != new_parent_material:
                report_lines.append(f"  - [계획] 부모를 '{NEW_PARENT_MATERIAL_PATH}' (으)로 변경합니다.")
            else:
                report_lines.append(f"  - [정보] 부모가 이미 목표와 동일하여 변경하지 않습니다.")
        
        if DO_PARAMETER_EDIT and PARAMETERS_TO_SET:
            report_lines.append(f"  - [계획] 다음 파라미터를 수정합니다:")
            for param_info in PARAMETERS_TO_SET:
                report_lines.append(f"    - {param_info['type']} 파라미터 '{param_info['name']}'의 값을 '{param_info['value']}' (으)로 설정합니다.")
        
        if not DO_REPARENT and not DO_PARAMETER_EDIT:
            report_lines.append("  - [정보] 부모 변경과 파라미터 수정이 모두 비활성화되어, 실제 변경은 없습니다.")
        report_lines.append("")

    report_lines.append("==========================================================")
    return "\n".join(report_lines)


def main():
    # 전역 네임스페이스에서 변수를 가져옵니다. 없으면 None으로 설정합니다.
    g = globals()
    
    # 미리보기에 필요한 모든 변수 목록
    # Actor 처리와 재처리에 공통적으로 필요하거나, 어느 한쪽에만 필요한 모든 변수를 포함합니다.
    all_vars = {
        'output_path', 'master_path', 'source_parent_prefix', 'suffix',
        'parameters_str', 'do_reparent', 'do_parameter_edit', 'do_apply_to_actor',
        'do_process_static_meshes', 'do_check_source_prefix', 'do_overwrite_existing'
    }
    settings = {var: g.get(var) for var in all_vars}

    # 파라미터 문자열 파싱
    settings['parameters_to_set'] = parse_parameters_string(settings.get('parameters_str') or "")

    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    util_lib = unreal.EditorUtilityLibrary
    
    selected_actors = editor_actor_subsystem.get_selected_level_actors()
    selected_assets = util_lib.get_selected_assets()
    
    report = ""
    
    # 1. 액터 선택이 있으면, 액터 처리 로직 미리보기 실행
    if selected_actors:
        report = preview_actor_processing_logic(selected_actors, settings)
    # 2. 액터 선택이 없고, 콘텐츠 브라우저 에셋 선택이 있으면 재처리 로직 미리보기 실행
    elif selected_assets:
        material_instances = [asset for asset in selected_assets if isinstance(asset, unreal.MaterialInstanceConstant)]
        if material_instances:
            report = preview_reprocessing_logic(material_instances, settings)
        else:
             report = "콘텐츠 브라우저에 에셋이 선택되었으나, 미리보기를 실행할 머티리얼 인스턴스가 없습니다."
    # 3. 아무것도 선택되지 않았으면 안내 메시지 출력
    else:
        report = "작업을 미리보기하려면 레벨에서 액터를 선택하거나 콘텐츠 브라우저에서 머티리얼 인스턴스를 선택하세요."

    # Output Log에도 결과를 출력합니다.
    unreal.log("--- 스크립트 실행 계획 미리보기 ---")
    print(report)
    
    # 블루프린트에서 사용할 수 있도록 결과를 반환합니다.
    return report

# 스크립트 실행 및 결과 저장을 통해 블루프린트 연동.
# main() 함수의 반환값을 전역 변수 'report'에 할당합니다.
# 이렇게 하면 블루프린트의 'Execute Python Script' 노드에서 'report'라는 이름의
# 출력 핀을 설정했을 경우, 이 결과 문자열을 정상적으로 가져갈 수 있습니다.
report = main()
