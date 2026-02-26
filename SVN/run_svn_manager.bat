@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: ==============================================================================
:: [1] SVN CLI 설치 확인 및 자동 설치
:: PATH 환경 변수가 즉각 갱신되지 않을 수 있으므로 실제 파일 경로를 직접 체크합니다.
:: ==============================================================================
set SVN_BIN_DIR=C:\Program Files\TortoiseSVN\bin
set SVN_EXE=%SVN_BIN_DIR%\svn.exe

if not exist "%SVN_EXE%" (
    set "SVN_MSI_PATH=\\192.168.2.215\Share_151\art\영상연출\util\svn\TortoiseSVN-1.14.9.29743-x64-svn-1.14.5.msi"
    
    if not exist "!SVN_MSI_PATH!" (
        echo [ERROR] 네트워크 설치 파일을 찾을 수 없습니다! 공용 드라이브 연결 상태를 확인해주세요.
        echo 경로: "!SVN_MSI_PATH!"
        pause
        exit /b
    )

    :: /passive 옵션 부착 (기본 진행률 창만 표시, 사용자 개입 불필요)
    msiexec /i "!SVN_MSI_PATH!" ADDLOCAL=DefaultFeature,CLI /passive /norestart MSIRESTARTMANAGERCONTROL=Disable
    
    :: 설치 직후 다시 한번 파일이 제대로 생성되었는지 물리적으로 확인합니다.
    if not exist "%SVN_EXE%" (
        echo [ERROR] SVN 설치가 완료되었으나 svn.exe 파일을 찾을 수 없습니다.
        echo [ERROR] 설치가 취소되었거나 권한 문제가 발생했을 수 있습니다. 수동으로 설치를 확인해주세요.
        pause
        exit /b
    )
    echo [SUCCESS] SVN CLI 관련 도구 설치가 성공적으로 완료되었습니다.
)

:: 시스템 PATH에 등록이 아직 안 되었을 수 있으므로 이번 세션에 한해 PATH에 강제 추가
set "PATH=%PATH%;%SVN_BIN_DIR%"

:: ==============================================================================
:: [2] 현재 경로 기반 엔진 내장 파이썬 찾기
:: ==============================================================================
set "START_DIR=%~dp0"
cd /d "%START_DIR%"

:FindProjectRoot
if exist "*.uproject" (
    set "PROJECT_ROOT=%CD%"
    goto :FoundRoot
)

cd ..
if "%CD%"=="%PROJECT_ROOT%" (
    echo [ERROR] .uproject 파일을 찾을 수 없습니다! 프로젝트 폴더 내에서 실행해주세요.
    pause
    exit /b
)
set "PROJECT_ROOT=%CD%"
goto :FindProjectRoot

:FoundRoot
:: 프로젝트 폴더(ProjectQT) 기준으로 엔진에 내장된 파이썬 절대 경로 조합
:: 기본 엔진 경로: F:\ProjectOdin_Q\QTClient\Engine\UE5.6.1\Engine\Binaries\ThirdParty\Python3\Win64\python.exe
set "ENGINE_PYTHON_REL=..\Engine\UE5.6.1\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"

pushd "%PROJECT_ROOT%"
for %%i in ("%ENGINE_PYTHON_REL%") do set "UE_PYTHON_EXE=%%~fi"
popd

if not exist "%UE_PYTHON_EXE%" (
    :: 혹시 UE5.6.1 하위 폴더가 아니라 Engine 바로 밑에 있을 경우 대비
    set "ENGINE_PYTHON_REL_ALT=..\Engine\Engine\Binaries\ThirdParty\Python3\Win64\python.exe"
    pushd "%PROJECT_ROOT%"
    for %%i in ("!ENGINE_PYTHON_REL_ALT!") do set "UE_PYTHON_EXE=%%~fi"
    popd
)

if not exist "%UE_PYTHON_EXE%" (
    echo [ERROR] 언리얼 엔진 내장 Python을 찾을 수 없습니다!
    echo 예상 경로: "%UE_PYTHON_EXE%"
    echo 로컬에 설치된 기본 Python으로 실행을 시도합니다...
    set "UE_PYTHON_EXE=python"
) else (
    echo [INFO] 엔진 내장 Python 사용: "%UE_PYTHON_EXE%"
)

:: ==============================================================================
:: [3] SVN 매니저 스크립트 실행
:: ==============================================================================
cd /d "%START_DIR%"
"%UE_PYTHON_EXE%" svn_manager.py

pause
