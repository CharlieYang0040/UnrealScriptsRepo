@echo off
pushd %~dp0

:: 가상환경 활성화 (필요한 경우 주석 해제)
:: call venv\Scripts\activate

python svn_manager.py

pause
popd
