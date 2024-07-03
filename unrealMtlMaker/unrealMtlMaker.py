import unreal
from collections import OrderedDict

def get_texture_paths(directory):
    texture_dict = {}
    assets = unreal.EditorAssetLibrary.list_assets(directory, recursive=True)
    for asset in assets:
        asset_name = asset.split('/')[-1].split('.')[0]
        package_name = '/'.join(asset.split('/')[:-1]) + '/' + asset_name  # 패키지 이름으로 변경
        if "basecolor" in asset.lower():
            texture_dict["BaseColor"] = package_name
            unreal.log(f'Found BaseColor texture: {asset_name} at {package_name}')
        elif "metallic" in asset.lower():
            texture_dict["Metallic"] = package_name
            unreal.log(f'Found Metallic texture: {asset_name} at {package_name}')
        elif "roughness" in asset.lower():
            texture_dict["Roughness"] = package_name
            unreal.log(f'Found Roughness texture: {asset_name} at {package_name}')
        elif "normal" in asset.lower():
            texture_dict["Normal"] = package_name
            unreal.log(f'Found Normal texture: {asset_name} at {package_name}')
    ordered_texture_dict = OrderedDict(
        sorted(texture_dict.items(), key=lambda item: ["BaseColor", "Metallic", "Roughness", "Normal"].index(item[0]))
    )
    return ordered_texture_dict

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
            tex_sampler.sampler_type = unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE
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

def execute_material_creation(directory, material_name):
    texture_dict = get_texture_paths(directory)
    create_material_with_textures(material_name, texture_dict)
