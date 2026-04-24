import unreal

def get_clean_path(path_string):
    """ObjectPath(.Asset)를 패키지 경로로 정제"""
    return path_string.split('.')[0]

def rename_assets():
    PREFIX = "CN_"
    
    # 1. 폴더 선택 확인 및 경로 보정
    selected_folders = unreal.EditorUtilityLibrary.get_selected_folder_paths()
    if not selected_folders:
        unreal.log_warning("선택된 폴더가 없습니다.")
        return
        
    cleaned_folder_paths = [f[4:] if f.startswith("/All/") else f for f in selected_folders]
    
    # 2. 전체 작업 트랜잭션 시작 (에러 시 Undo 가능)
    with unreal.ScopedEditorTransaction("Rename Assets to CN_"):
        
        renamed_count = 0
        
        for folder_path in cleaned_folder_paths:
            if not unreal.EditorAssetLibrary.does_directory_exist(folder_path):
                continue
                
            asset_paths = unreal.EditorAssetLibrary.list_assets(folder_path, recursive=True, include_folder=False)
            
            for raw_path in asset_paths:
                clean_path = get_clean_path(raw_path)
                
                # 에셋 데이터 가져오기
                asset_data = unreal.EditorAssetLibrary.find_asset_data(clean_path)
                
                if not asset_data or not asset_data.is_valid():
                    continue
                    
                old_name = str(asset_data.asset_name)
                package_path = str(asset_data.package_path)
                
                # 접두사가 없는 경우에만 변경 진행
                if not old_name.startswith(PREFIX):
                    new_name = PREFIX + old_name
                    new_asset_path = f"{package_path}/{new_name}"
                    
                    # 목적지에 이미 에셋(또는 리다이렉터)이 있는지 최종 방어
                    if unreal.EditorAssetLibrary.does_asset_exist(new_asset_path):
                        unreal.log_warning(f"건너뜀: 해당 경로에 이미 에셋이 존재합니다 -> {new_asset_path}")
                        continue
                        
                    # 이름 변경 실행
                    if unreal.EditorAssetLibrary.rename_asset(clean_path, new_asset_path):
                        renamed_count += 1
                        unreal.log(f"Renamed: {old_name} -> {new_name}")
                    else:
                        unreal.log_error(f"Failed to rename: {clean_path}")
                        
    unreal.log(f"작업 완료: 총 {renamed_count}개의 에셋 이름이 변경되었습니다.")

# 실행
rename_assets()
