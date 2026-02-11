@echo off
setlocal EnableDelayedExpansion

:: ================= [Configuration Load] =================
if not exist "%~dp0USMAT_Config.bat" (
    echo [ERROR] 'USMAT_Config.bat' file not found!
    pause
    exit /b
)
call "%~dp0USMAT_Config.bat"

:: ================= [입력 구간] =================
cls
echo ========================================================
echo        USMAT : Internal Safe Duplication Tool
echo ========================================================
echo.
echo  [Info] Same Project Duplication Mode
echo  Copies assets to Cinematic Workspace with 'CN_' prefix.
echo  Original assets will be REVERTED to restore them.
echo.
set /p TARGET_DIR="[INPUT] 복제할 폴더 경로를 입력하세요 (예: /Game/Characters/Hero): "
echo.

:: ================= [Step 1] SVN Status Check (Interactive) =================
echo [Step 1] Checking SVN Status...
svn status | findstr "^[MC!]" > "%~dp0svn_status.txt"

for %%A in ("%~dp0svn_status.txt") do if %%~zA==0 (
    echo [PASS] SVN is clean.
    goto :START_PROCESS
)

:: 더러우면 목록 출력
color 4F
echo.
echo [WARNING] SVN Status is NOT clean!
echo --------------------------------------------------------
type "%~dp0svn_status.txt"
echo --------------------------------------------------------
echo.
echo 위 파일들이 변경된 상태입니다.
set /p FORCE_RUN="그래도 진행하시겠습니까? (Y/N): "
if /I "%FORCE_RUN%" neq "Y" (
    color 07
    echo [CANCEL] 작업을 취소합니다.
    del "%~dp0svn_status.txt"
    pause
    exit /b
)
color 07
echo [INFO] 사용자의 요청으로 강제 진행합니다...

:START_PROCESS
if exist "%~dp0svn_status.txt" del "%~dp0svn_status.txt"

:: ================= [Step 2] Move & Rename (Python) =================
echo.
echo [Step 2] Moving Assets to Cinematic Workspace... (Optimized Launch)
:: Config에 정의된 TARGET_UPROJECT (현재 프로젝트) 사용
%TARGET_ENGINE_CMD% %TARGET_UPROJECT% -run=pythonscript -script="%~dp0Scripts\Step_Internal_Move.py" --arg "%TARGET_DIR%" "%ISOLATION_PATH%" %ENGINE_OPT_FLAGS%

if %errorlevel% neq 0 (
    echo [ERROR] Python script failed.
    pause
    exit /b
)

:: ================= [Step 3] Revert Original (Source) =================
echo.
echo [Step 3] Reverting Source Directory to Restore Originals...
:: 주의: TARGET_DIR (Unreal Path)를 로컬 OS 경로로 변환해야 함.
:: 언리얼 경로가 /Game/... 으로 시작한다고 가정하고 Content 폴더 매핑
set "REL_PATH=%TARGET_DIR:/Game/=%"
set "REL_PATH=%REL_PATH:/=\%"
set "FULL_SOURCE_PATH=%TARGET_CONTENT_DIR%\%REL_PATH%"

:: 따옴표 제거 후 다시 씌우기 (중복 방지)
set "FULL_SOURCE_PATH=%FULL_SOURCE_PATH:"=%"

echo   - Reverting: "%FULL_SOURCE_PATH%"
svn revert -R "%FULL_SOURCE_PATH%"

:: ================= [Step 4] Final Commit Prep =================
echo.
echo [Step 4] Adding New Assets to SVN...
:: ISOLATION_PATH도 경로 변환이 필요하지만, 보통 /Game/A_Cinematic_Workspace 고정이므로
:: Config의 ISOLATION_PATH 값을 파싱하거나 하드코딩된 상대경로 사용
:: 여기서는 안전하게 전체 Content 폴더 내의 'A_Cinematic_Workspace'를 add 시도
:: (이미 있는 파일은 skip되고 새 파일만 add됨)

set "ISO_REL=%ISOLATION_PATH:/Game/=%"
set "ISO_REL=%ISO_REL:/=\%"
set "FULL_ISO_PATH=%TARGET_CONTENT_DIR%\%ISO_REL%"
set "FULL_ISO_PATH=%FULL_ISO_PATH:"=%"

echo   - Adding: "%FULL_ISO_PATH%"
svn add "%FULL_ISO_PATH%" --force --depth infinity

echo.
echo ========================================================
echo [Review] 작업 완료.
echo 1. '%TARGET_DIR%' 의 원본 파일들은 Revert 되었습니다.
echo 2. '%ISOLATION_PATH%' 에 'CN_' 접두어가 붙은 복제본이 생성되었습니다.
echo.
set /p CONFIRM="커밋 하시겠습니까? (COMMIT 입력): "

if "%CONFIRM%" neq "COMMIT" (
    echo [Info] 커밋하지 않고 종료합니다. 직접 확인하세요.
    pause
    exit /b
)

svn commit -m "[USMAT] Internal Deep Copy %TARGET_DIR% to %ISOLATION_PATH% as CN_*"

echo [SUCCESS] Done.
pause
