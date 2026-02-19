@echo off
echo [SVN Reset Manager] Build Start...

:: PyInstaller 설치 확인
pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
)

:: 기존 dist 폴더 정리
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist svn_reset_manager.spec del svn_reset_manager.spec

:: 빌드 실행 (onefile: 단일 실행파일, clean: 캐시 정리, noconfirm: 덮어쓰기)
:: icon 옵션은 아이콘 파일(.ico)이 있을 경우 사용: --icon=icon.ico
echo Building exe...
pyinstaller --onefile --clean --noconfirm --name "SVN_Reset_Manager" d:\WORKDATA\UnrealScriptsRepo\svn_reset_manager.py

if %errorlevel% == 0 (
    echo.
    echo ========================================================
    echo  Build API SUCCESS!
    echo  Executable: %CD%\dist\SVN_Reset_Manager.exe
    echo ========================================================
    
    :: 바로 폴더 열기
    start explorer dist
) else (
    echo.
    echo Build FAILED.
)

pause
