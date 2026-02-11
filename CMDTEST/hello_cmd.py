import unreal

# 로그에 눈에 띄게 출력하기 위해 Warning(노란색)과 Error(빨간색)로 출력해봅니다.
unreal.log_warning("========================================")
unreal.log_warning("   HELLO UNREAL CMD! 파이썬 연결 성공!   ")
unreal.log_warning("========================================")

# 실제로 엔진 기능이 동작하는지 테스트 (현재 프로젝트 이름 출력)
project_path = unreal.Paths.get_project_file_path()
unreal.log_error(f"Current Project: {project_path}")