import sys
import unreal

# 스크립트가 위치한 디렉토리 경로
script_directory = '/Game/Python'  # 실제 경로에 맞게 조정하세요.

# Unreal 경로를 실제 파일 시스템 경로로 변환
file_system_path = unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_content_dir(), script_directory)
print(file_system_path)
# 파이썬의 sys.path에 추가
if file_system_path not in sys.path:
    sys.path.append(file_system_path)
# sys.path.remove('/../../../Users/jooy1/Documents/Unreal Projects/materialStudy/Content/')
print(sys.path)