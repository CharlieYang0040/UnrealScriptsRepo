import unreal
import sys
import os

# Argument Parsing
# sys.argv[0]: Script Path
# sys.argv[1]: Target Content Dir
# sys.argv[2]: Source Dir to Migrate
target_content_dir = sys.argv[1]
source_dir_to_migrate = sys.argv[2]

print(f"--- [Python] Start Migration: {source_dir_to_migrate} -> {target_content_dir} ---")

# 1. 자산 목록 수집
asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets_data = asset_registry.get_assets_by_path(source_dir_to_migrate, recursive=True)

if not assets_data:
    print(f"Error: No assets found in {source_dir_to_migrate}")
    sys.exit(1)

package_names = [asset.package_name for asset in assets_data]

# 2. 마이그레이션 수행 (의존성 포함)
# migrate_packages 함수는 에디터의 Migrate 기능과 동일하게 동작합니다.
unreal.AssetToolsHelpers.get_asset_tools().migrate_packages(
    package_names=package_names,
    destination_path=target_content_dir
)

print("--- [Python] Migration Finished ---")
