import unreal

def get_texture_paths(directory):
    texture_dict = {}
    assets = unreal.EditorAssetLibrary.list_assets(directory, recursive=True)
    # unreal.log(assets)
    for asset in assets:
        asset_name = asset.split('/')[-1].split('.')[0]
        if "basecolor" in asset.lower():
            texture_dict["BaseColor"] = asset
            unreal.log(f'Found BaseColor texture: {asset_name} at {asset}')
        elif "metallic" in asset.lower():
            texture_dict["Metallic"] = asset
            unreal.log(f'Found Metallic texture: {asset_name} at {asset}')
        elif "roughness" in asset.lower():
            texture_dict["Roughness"] = asset
            unreal.log(f'Found Roughness texture: {asset_name} at {asset}')
        elif "normal" in asset.lower():
            texture_dict["Normal"] = asset
            unreal.log(f'Found Normal texture: {asset_name} at {asset}')
    return texture_dict

def create_material_with_textures(material_name, texture_dict):
    # AssetTools 인스턴스 가져오기
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    # 새로운 머티리얼 생성
    material_factory = unreal.MaterialFactoryNew()
    package_path = f'/Game/{material_name}'
    material_name = material_name.split('/')[-1]

    unique_package_name, unique_asset_name = asset_tools.create_unique_asset_name(package_path, material_name)
    new_material = asset_tools.create_asset(
        asset_name=unique_asset_name,
        package_path=package_path,
        asset_class=unreal.Material,
        factory=material_factory
    )

    if not new_material:
        unreal.log_error(f'Failed to create material: {material_name}')
        return

    node_offset_x = -600
    node_offset_y = 0

    # 텍스처 샘플러 추가 및 연결
    for tex_name, tex_path in texture_dict.items():
        texture = unreal.EditorAssetLibrary.load_asset(tex_path)
        if not texture:
            unreal.log_error(f'Failed to load texture: {tex_path}')
            continue

        # 텍스처 샘플러 표현식 생성
        tex_sampler = unreal.MaterialEditingLibrary.create_material_expression(new_material, unreal.MaterialExpressionTextureSample)
        tex_sampler.texture = texture

        # 텍스처 이름을 기준으로 머티리얼 속성에 연결 및 설정
        if "basecolor" in tex_name.lower():
            unreal.MaterialEditingLibrary.connect_material_property(tex_sampler, '', unreal.MaterialProperty.MP_BASE_COLOR)
        elif "metallic" in tex_name.lower():
            unreal.MaterialEditingLibrary.connect_material_property(tex_sampler, '', unreal.MaterialProperty.MP_METALLIC)
        elif "roughness" in tex_name.lower():
            unreal.MaterialEditingLibrary.connect_material_property(tex_sampler, '', unreal.MaterialProperty.MP_ROUGHNESS)
        elif "normal" in tex_name.lower():
            tex_sampler.sampler_type = unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL
            unreal.MaterialEditingLibrary.connect_material_property(tex_sampler, '', unreal.MaterialProperty.MP_NORMAL)

        # 노드 위치 설정
        tex_sampler.material_expression_editor_x = node_offset_x
        tex_sampler.material_expression_editor_y = node_offset_y
        node_offset_y += 300

    # 머티리얼 그래프 업데이트
    unreal.MaterialEditingLibrary.recompile_material(new_material)
    unreal.log(f'Successfully created material: {material_name}')

# 예시 사용법
# directory = "/Game/Textures"
# material_name = "MyNewMaterial"
# texture_dict = get_texture_paths(directory)

# create_material_with_textures(material_name, texture_dict)

@unreal.uclass()
class MyEditorUtility(unreal.GlobalEditorUtilityBase):
    pass

class TextureMaterialCreatorUI:
    def __init__(self):
        self.editor_util = MyEditorUtility()
    
    def show_ui(self):
        # Create window
        self.window = unreal.ToolMenus.get().find_menu("LevelEditor.MainMenu.Window")
        if not self.window:
            unreal.log_error("Failed to find the 'Window' menu. Check if the path is correct.")
            return

        entry = unreal.ToolMenuEntry(
            name="unrealMtlMaker",
            type=unreal.MultiBlockType.MENU_ENTRY,
            insert_position=unreal.ToolMenuInsert("", unreal.ToolMenuInsertType.FIRST)
        )
        entry.set_label("Texture Material Creator")
        entry.set_tool_tip("Open the Texture Material Creator")
        # Correctly setting up the string command
        entry.set_string_command(unreal.ToolMenuStringCommandType.PYTHON, "Command", "import unrealMtlMaker; unrealMtlMaker.show_creator_ui()")
        self.window.add_menu_entry("PythonScripts", entry)
        unreal.ToolMenus.get().refresh_all_widgets()

def show_creator_ui():
    # 간단한 입력 대화상자로 디렉터리와 머티리얼 이름 입력 받기
    response = unreal.EditorDialog.show_message(
        "디렉터리 및 머티리얼 이름 입력",
        "디렉터리 및 머티리얼 이름을 입력하세요:",
        unreal.AppMsgType.OK_CANCEL
    )
    if response == unreal.AppReturnType.OK:
        directory = unreal.EditorUtilityLibrary.get_text_data("디렉터리: /Game/Textures")
        material_name = unreal.EditorUtilityLibrary.get_text_data("머티리얼 이름: MyNewMaterial")
        if directory and material_name:
            texture_dict = get_texture_paths(directory)
            create_material_with_textures(material_name, texture_dict)
        else:
            unreal.log_warning("디렉터리 또는 머티리얼 이름이 누락되었습니다.")

# 예시 사용
if __name__ == "__main__":
    ui_creator = TextureMaterialCreatorUI()
    ui_creator.show_ui()
