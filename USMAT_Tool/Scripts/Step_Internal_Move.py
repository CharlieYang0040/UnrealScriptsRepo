import unreal
import sys
import os

# Argument Parsing
# sys.argv[0]: Script Path
# sys.argv[1]: Source Directory to Duplicate (e.g., /Game/Characters/Hero)
# sys.argv[2]: Base Isolation Path (e.g., /Game/A_Cinematic_Workspace)

source_path_root = sys.argv[1]
base_isolation_path = sys.argv[2] # 보통 /Game/A_Cinematic_Workspace

print(f"--- [Python] Start Internal Safe Duplication ---")
print(f"Source: {source_path_root}")
print(f"Base Target: {base_isolation_path}")

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
editor_asset_lib = unreal.EditorAssetLibrary

# 1. 대상 에셋 수집 (Recursive)
assets_data = asset_registry.get_assets_by_path(source_path_root, recursive=True)

if not assets_data:
    print(f"[Error] No assets found in {source_path_root}")
    sys.exit(0)

print(f"Found {len(assets_data)} assets.")

# 2. 이동 및 이름 변경 (CN_ Prefix)
for asset_data in assets_data:
    package_name = str(asset_data.package_name) # e.g. /Game/Char/Hero/Data/MyAsset
    asset_name = str(asset_data.asset_name)     # e.g. MyAsset
    
    # 2-1. 타겟 경로 계산
    #   Source: /Game/Char/Hero/Data/MyAsset
    #   Goal:   /Game/A_Cinematic_Workspace/Char/Hero/Data/CN_MyAsset
    
    # /Game/ 이후의 경로 구조를 그대로 가져감
    # 단, 사용자가 입력한 루트가 어디냐에 따라 상대경로를 어떻게 짤지 결정해야 함.
    # 안전하게는 "/Game/"을 떼고 Isolation Path 뒤에 붙이는 방식을 사용.
    
    if package_name.startswith("/Game/"):
        relative_path = package_name[len("/Game/"):] # Char/Hero/Data/MyAsset
    else:
        # Plugins or Engine content -> Skip or Warning
        print(f"[Skip] Non-Game content: {package_name}")
        continue
        
    # 폴더 경로와 파일명 분리
    path_parts = relative_path.split("/")
    folder_path = "/".join(path_parts[:-1]) # Char/Hero/Data
    
    # 타겟 패키지 경로 생성
    # 이름에 CN_ 접두어 추가
    new_asset_name = f"CN_{asset_name}"
    
    # 최종 타겟 패키지: /Game/A_Cinematic_Workspace + / + Char/Hero/Data + / + CN_MyAsset
    dest_package_path = f"{base_isolation_path}/{folder_path}/{new_asset_name}"
    
    # 이동 수행 (Rename)
    # rename_asset은 레퍼런스를 업데이트합니다.
    if editor_asset_lib.rename_asset(package_name, dest_package_path):
        print(f"[Moved] {asset_name} -> {new_asset_name}")
    else:
        print(f"[Fail] Could not move {package_name}")

print("--- [Python] Logic Completed ---")
