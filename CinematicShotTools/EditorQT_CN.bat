@echo off
setlocal enabledelayedexpansion

:: ==============================================================================
:: [1] 프로젝트 루트 찾기 (핵심 로직)
:: 현재 배치 파일 위치에서 시작하여 .uproject 파일이 나올 때까지 상위로 이동합니다.
:: ==============================================================================

:: 배치 파일의 현재 위치 저장
set "START_DIR=%~dp0"
cd /d "%START_DIR%"

:FindProjectRoot
if exist "*.uproject" (
    set "PROJECT_ROOT=%CD%"
    :: .uproject 파일 이름 가져오기 (확장자 포함)
    for %%f in (*.uproject) do set "UPROJECT_NAME=%%f"
    goto :FoundRoot
)

:: 드라이브 루트까지 갔는데도 없으면 에러
cd ..
if "%CD%"=="%PROJECT_ROOT%" (
    echo [ERROR] .uproject 파일을 찾을 수 없습니다!
    echo 배치 파일을 프로젝트 폴더 안에 위치시켜주세요.
    pause
    exit /b
)
set "PROJECT_ROOT=%CD%"
goto :FindProjectRoot

:FoundRoot
echo ----------------------------------------------------------------
echo [INFO] Project Root Found: "%PROJECT_ROOT%"
echo [INFO] Project File: "%UPROJECT_NAME%"
echo ----------------------------------------------------------------

:: ==============================================================================
:: [2] Python 경로 설정 (프로젝트 루트 기준)
:: 루트를 찾았으므로, 이제부터는 상대 경로 고민 없이 루트 기준으로 경로를 합칩니다.
:: ==============================================================================

:: [설정] 프로젝트 루트로부터 Python 스크립트까지의 상대 경로
set "REL_PYTHON_PATH=Content\A_Cinematic_Workspace\Lighting\HC\CinematicShotTools\Python"

:: 절대 경로 생성
set "MY_PYTHON_DIR=%PROJECT_ROOT%\%REL_PYTHON_PATH%"

:: 검증
if not exist "%MY_PYTHON_DIR%\init_unreal.py" (
    echo [ERROR] Python 경로를 찾을 수 없습니다.
    echo 경로: "%MY_PYTHON_DIR%"
    pause
    exit /b
)

echo [SUCCESS] Python Path Set: "%MY_PYTHON_DIR%"
set "UE_PYTHONPATH=%MY_PYTHON_DIR%"

:: ==============================================================================
:: [3] 엔진 경로 설정 (상대 경로 자동 계산)
:: 팀원들이 모두 같은 SVN 구조를 쓴다면 엔진은 프로젝트 폴더의 '형제 폴더'일 확률이 높습니다.
:: ==============================================================================

:: [설정] 프로젝트 루트 폴더 기준 엔진의 상대 경로 (예: 프로젝트 상위 폴더의 Engine 폴더)
:: 기존 코드의 ..\Engine\UE5.6.1... 을 기준으로 작성했습니다.
:: 프로젝트 루트(ProjectQT)의 상위(..) -> Engine -> UE5.6.1 ...
set "ENGINE_REL_PATH=..\Engine\UE5.6.1\Engine\Binaries\Win64\UnrealEditor.exe"

pushd "%PROJECT_ROOT%"
:: 엔진 실행 파일의 절대 경로를 계산하여 변수에 담습니다.
for %%i in ("%ENGINE_REL_PATH%") do set "ENGINE_EXE=%%~fi"
popd

if not exist "%ENGINE_EXE%" (
    echo [ERROR] 언리얼 엔진 실행 파일을 찾을 수 없습니다!
    echo 예상 경로: "%ENGINE_EXE%"
    echo.
    echo 1. SVN에서 Engine 폴더를 제대로 받았는지 확인하세요.
    echo 2. 배치 파일 내 ENGINE_REL_PATH 설정을 확인하세요.
    pause
    exit /b
)

echo [SUCCESS] Engine Found: "%ENGINE_EXE%"

:: ==============================================================================
:: [4] 에디터 실행
:: ==============================================================================
echo.
echo Launching Unreal Editor...
echo Project: "%PROJECT_ROOT%\%UPROJECT_NAME%"
echo.

:: start 명령어에서 첫 번째 따옴표 ""는 창 제목(Title)으로 인식되므로 비워두는 것이 안전합니다.
start "" "%ENGINE_EXE%" "%PROJECT_ROOT%\%UPROJECT_NAME%"

:: 실행 확인을 위해 잠시 대기
timeout /t 5
exit