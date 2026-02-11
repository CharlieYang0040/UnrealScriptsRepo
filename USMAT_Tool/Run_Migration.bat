@echo off
setlocal EnableDelayedExpansion

:: ================= [Configuration Load] =================
:: 설정 파일이 없으면 에러 처리
if not exist "%~dp0USMAT_Config.bat" (
    echo [ERROR] 'USMAT_Config.bat' file not found!
    echo Please create the configuration file first.
    pause
    exit /b
)
call "%~dp0USMAT_Config.bat"

:: ================= [입력 구간] =================
cls
echo ========================================================
echo        USMAT : Unreal Safe Migration Automation Tool
echo ========================================================
echo.
set /p MIGRATE_DIR="[INPUT] 이주할 소스 폴더 경로를 입력하세요 (예: /Game/Characters/Hero): "

:: ================= [Step 1] SVN 상태 무결성 검사 (Interactive) =================
echo.
echo [Step 1] SVN 상태 무결성 검사 중...
svn status | findstr "^[MC!]" > "%~dp0svn_status.txt"

for %%A in ("%~dp0svn_status.txt") do if %%~zA==0 (
    echo [PASS] SVN 상태 Clean. 진행합니다.
    goto :START_PROCESS
)

:: 더러우면 목록 출력
color 4F
echo.
echo [WARNING] SVN 상태가 깨끗하지 않습니다!
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

:: ================= [Step 2] 에셋 이주 (Migrate) =================
echo.
echo [Step 2] 소스 프로젝트에서 에셋을 가져옵니다... (Optimized Launch)
%SOURCE_ENGINE_CMD% %SOURCE_UPROJECT% -run=pythonscript -script="%~dp0Scripts\Step2_Export.py" --arg "%TARGET_CONTENT_DIR%" "%MIGRATE_DIR%" %ENGINE_OPT_FLAGS%

if %errorlevel% neq 0 (
    echo [ERROR] 마이그레이션 실패. 경로를 확인해주세요.
    pause
    exit /b
)

:: ================= [Step 3] 신규 유입 분석 =================
echo.
echo [Step 3] 신규 유입된 파일 리스트 추출 중...
:: 상태가 '?' (Unversioned)인 파일만 추출하여 리스트화
svn status | findstr "^?" > "%~dp0new_assets_list.txt"

:: ================= [Step 4] 격리 및 FixUp =================
echo.
echo [Step 4] 에셋 격리 이동 및 리디렉터 FixUp 수행... (Optimized Launch)
:: 엔진을 켜서 1)이동 2)FixupRedirectors를 한 번에 수행
%TARGET_ENGINE_CMD% %TARGET_UPROJECT% -run=pythonscript -script="%~dp0Scripts\Step4_MoveFixup.py" --arg "%~dp0new_assets_list.txt" "%ISOLATION_PATH%" %ENGINE_OPT_FLAGS%

:: ================= [Step 5] 오염 제거 (Revert & Clean) =================
echo.
echo [Step 5] 오염 제거 작업 준비...

:: 5-1. 기존 파일 보호 (Modified Revert)
:: A_Cinematic 폴더는 'Added' 상태가 될 것이므로, 'Modified(M)' 상태인 것만 찾으면
:: 기존 프로젝트 파일이 오염된 것(참조 변경 등)을 정확히 타겟팅 가능함.
echo   - 기존 데이터 변경사항(M) 스캔 중...
svn status | findstr "^M" > "%~dp0modified_list.txt"

:: ================= [Step 6] 최종 경고 및 커밋 =================
cls
color 4F
echo ===============================================================================
echo                           !!! FINAL WARNING !!!
echo ===============================================================================
echo 1. 신규 에셋은 '%ISOLATION_PATH%' 로 이동되었습니다.
echo 2. 기존 프로젝트 파일 중 수정된(Modified) 파일들은 전량 REVERT(초기화) 됩니다.
echo    (목록 확인: modified_list.txt)
echo 3. 승인 시 즉시 SVN COMMIT이 수행됩니다.
echo ===============================================================================
echo.
set /p CONFIRM="진행하려면 대문자로 'COMMIT' 을 입력하세요: "

if "%CONFIRM%" neq "COMMIT" (
    color 07
    echo [CANCEL] 작업이 취소되었습니다. 수동으로 확인하세요.
    goto :CLEANUP
)

echo.
echo [Processing] 기존 파일 Revert 수행 중...
for /f "tokens=2*" %%i in (%~dp0modified_list.txt) do (
    echo Reverting: %%i
    svn revert "%%i"
)

echo.
echo [Processing] 이주 찌꺼기(Redirectors) 청소...
:: 안전을 위해 이 부분은 SVN Add를 먼저 하고 (새로 들어온 파일들)
svn add Content\A_Cinematic_Workspace --force

echo.
echo [Processing] SVN Commit 수행 중...
svn commit -m "[USMAT] Migrated %MIGRATE_DIR% to Cinematic Workspace."

echo.
echo [SUCCESS] 모든 작업이 완료되었습니다.

:CLEANUP
:: ================= [Cleanup] =================
echo.
echo [Cleanup] 임시 파일 정리 중...
if exist "%~dp0new_assets_list.txt" del "%~dp0new_assets_list.txt"
if exist "%~dp0modified_list.txt" del "%~dp0modified_list.txt"
pause
