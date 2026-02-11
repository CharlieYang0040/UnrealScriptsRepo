import unreal

# Unreal Python API에서 '/Game'은 실제 윈도우의 'Content' 폴더를 의미합니다.
target_path = "/Game"

unreal.log_warning("--------------------------------------------------")
unreal.log_warning(f"[{target_path}] 폴더 접근 테스트 시작...")

# EditorAssetLibrary를 이용해 Content 폴더 하위의 모든 에셋 리스트를 가져옵니다.
# recursive=True: 하위 폴더까지 싹 다 뒤짐
# include_folder=False: 폴더 이름은 빼고 파일만
all_assets = unreal.EditorAssetLibrary.list_assets(target_path, recursive=True, include_folder=False)

# 결과 출력
asset_count = len(all_assets)

if asset_count > 0:
    unreal.log_warning(f"✅ 성공! 총 {asset_count}개의 에셋을 발견했습니다.")
    unreal.log_warning("--- [샘플 에셋 5개 출력] ---")
    
    # 너무 많으니 5개만 보여줍니다.
    for i in range(min(5, asset_count)):
        unreal.log_warning(f"Found: {all_assets[i]}")
        
    unreal.log_warning("--------------------------------------------------")
else:
    unreal.log_warning("⚠️ 경고: 에셋을 하나도 찾지 못했습니다. (빈 프로젝트인가요?)")

unreal.log_warning("테스트 종료.")