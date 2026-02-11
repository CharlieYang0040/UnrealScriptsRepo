import unreal
import sys
import os

# Argument Parsing
list_file_path = sys.argv[1]  # new_assets_list.txt 경로
isolation_root = sys.argv[2]  # /Game/A_Cinematic_Workspace/Migrated

print(f"--- [Python] Start Isolation & FixUp ---")
print(f"Processing List: {list_file_path}")
print(f"Isolation Target: {isolation_root}")

if not os.path.exists(list_file_path):
    print(f"Error: List file not found at {list_file_path}")
    sys.exit(0)

# 1. 파일 리스트 읽기 & 파싱
assets_to_move = []
with open(list_file_path, "r", encoding='utf-8') as f:
    lines = f.readlines()
    for line in lines:
        # svn status output: "?       Content\Char\Hero.uasset"
        # 더 안전한 파싱: 와일드카드나 공백 처리 강화
        line = line.strip()
        if not line.endswith(".uasset"):
            continue
            
        # "?       " 접두어 제거 (유연하게)
        # svn status 출력이 다양할 수 있으므로, 파일 경로 부분만 추출 시도
        parts = line.split()
        if len(parts) > 1 and parts[0] == "?":
            # "?   Path" 형태
            path = " ".join(parts[1:])
        else:
            # 혹시 순수 경로만 있는 경우 대비
            path = line

        assets_to_move.append(path)

print(f"Found {len(assets_to_move)} assets to move.")

# 2. 에셋 이동 (Rename)
editor_asset_lib = unreal.EditorAssetLibrary

for file_os_path in assets_to_move:
    # 경로 정규화 (Backslash -> Slash)
    file_os_path = file_os_path.replace("\\", "/")
    
    # Unreal Package Path 계산
    # 기존: 단순 문자열 split
    # 개선: unreal.Paths.make_standard_filename 사용 권장되지만, 
    #       외부 경로(Abs Path)가 아닌 상대 경로(Content/...)가 들어오는 경우
    #       Content 폴더를 기준으로 잘라내는 것이 명확함.
    
    # "Content/" 를 기준으로 우측 경로 취득
    if "/Content/" in file_os_path:
        rel_path = file_os_path.split("/Content/")[-1]
    elif "Content/" in file_os_path: # 시작 부분이 Content/ 인 경우
        rel_path = file_os_path.split("Content/")[-1]
    else:
        print(f"[Warning] Could not find 'Content/' in path. Skipping: {file_os_path}")
        continue
        
    # rel_path: Char/Hero/Data/MyAsset
    rel_path = rel_path.replace(".uasset", "")
    source_package_path = f"/Game/{rel_path}"
    
    asset_name = os.path.basename(source_package_path)
    # dest_package_path calculation updated to preserve structure
    # Source: /Game/Char/Hero/Data/MyAsset
    # Target: /Game/A_Cinematic_Workspace/Migrated/Char/Hero/Data/MyAsset
    
    dest_package_path = f"{isolation_root}/{rel_path}"
    
    # 유효성 검사
    if not editor_asset_lib.does_asset_exist(source_package_path):
        print(f"[Skip] Source asset not found: {source_package_path}")
        continue
        
    # 이미 존재하면 건너뜀 (중복 방지)
    if editor_asset_lib.does_asset_exist(dest_package_path):
         print(f"[Skip] Destination already exists: {dest_package_path}")
         continue

    # 폴더 생성 및 이동
    # rename_asset은 자동으로 리디렉터를 생성하고 참조를 업데이트함
    success = editor_asset_lib.rename_asset(source_package_path, dest_package_path)
    if success:
        print(f"[Moved] {asset_name} -> {dest_package_path}")
    else:
        print(f"[Fail] Failed to move {asset_name}")

# 3. 리디렉터 Fix Up (매우 중요)
print("Fixing up redirectors in isolation folder...")
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
asset_tools.fix_up_redirectors_in_folder(isolation_root)

print("--- [Python] Logic Completed ---")
