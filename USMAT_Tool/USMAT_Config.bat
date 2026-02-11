@echo off

:: ========================================================
:: [USMAT Configuration]
:: 사용자 환경에 맞게 아래 경로들을 수정해주세요.
:: ========================================================

:: 1. 소스(가져올) 프로젝트 설정
set SOURCE_UPROJECT="C:\Work\SourceProject\SourceProject.uproject"
set SOURCE_ENGINE_CMD="C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"

:: 2. 타겟(현재) 프로젝트 설정
set TARGET_UPROJECT="D:\Work\MyProject\Lionheart_Project.uproject"
:: Content 폴더 경로는 마이그레이션 타겟 지정용
set TARGET_CONTENT_DIR="D:\Work\MyProject\Content"
set TARGET_ENGINE_CMD="C:\Program Files\Epic Games\UE_5.4\Engine\Binaries\Win64\UnrealEditor-Cmd.exe"

:: 3. 이주 후 에셋이 모일 격리소 경로 (Unreal 패키지 경로)
set ISOLATION_PATH="/Game/A_Cinematic_Workspace/Migrated"

:: 4. 엔진 실행 최적화 옵션 (Performance Flags)
:: -NullRHI: 렌더링 없음 (GPU 로딩 제거)
:: -NoSound: 사운드 시스템 제거
:: -NoTextureStreaming: 텍스처 스트리밍 제거
:: -NoSplash: 로딩창 제거
:: -ddc=NoShared: 공유 캐시 대기 제거 (네트워크 병목 해소)
set ENGINE_OPT_FLAGS=-log -unattended -NullRHI -NoSound -NoTextureStreaming -NoSplash -ddc=NoShared
