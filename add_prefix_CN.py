import unreal

def add_prefix_to_assets_in_selected_folders():
    # 설정: 추가할 접두사 정의
    PREFIX = "CN_"
    
    # 1. 콘텐츠 브라우저에서 선택된 폴더 경로들을 가져옵니다.
    selected_folders = unreal.EditorUtilityLibrary.get_selected_folder_paths()

    if not selected_folders:
        unreal.log_warning("선택된 폴더가 없습니다.")
        return

    renamed_count = 0

    with unreal.ScopedEditorTransaction("Add Prefix CN_"):
        
        for folder_path in selected_folders:
            # === [중요] 경로 보정 로직 추가 ===
            # /All/Game/... 형태로 들어올 경우 /All을 제거하여 /Game/... 으로 변경
            if folder_path.startswith("/All/"):
                folder_path = folder_path[4:]  # 앞의 "/All" 4글자 제거
            
            unreal.log(f"Processing folder: {folder_path}")
            
            # 경로 유효성 검사 (실제 존재하는지 확인)
            if not unreal.EditorAssetLibrary.does_directory_exist(folder_path):
                unreal.log_warning(f"폴더를 찾을 수 없거나 유효하지 않은 경로입니다: {folder_path}")
                continue

            # 3. 해당 폴더 및 하위 폴더의 모든 에셋 경로를 가져옵니다.
            asset_paths = unreal.EditorAssetLibrary.list_assets(folder_path, recursive=True, include_folder=False)
            
            for asset_path in asset_paths:
                asset_data = unreal.EditorAssetLibrary.find_asset_data(asset_path)
                
                old_name = str(asset_data.asset_name)
                package_path = str(asset_data.package_path)
                
                # 4. 이름 변경 로직
                if not old_name.startswith(PREFIX):
                    new_name = PREFIX + old_name
                    new_asset_path = f"{package_path}/{new_name}"
                    
                    success = unreal.EditorAssetLibrary.rename_asset(asset_path, new_asset_path)
                    
                    if success:
                        unreal.log(f"Renamed: {old_name} -> {new_name}")
                        renamed_count += 1
                    else:
                        unreal.log_error(f"Failed to rename: {asset_path}")

    unreal.log(f"작업 완료: 총 {renamed_count}개의 에셋 이름이 변경되었습니다.")

# 함수 실행
add_prefix_to_assets_in_selected_folders()