@echo off
chcp 65001 >nul
rem LoLDosa 실행기 (Windows): 더블클릭하면 필요한 것 설치 → 앱 실행
cd /d "%~dp0"
where uv >nul 2>nul
if errorlevel 1 (
  echo [LoLDosa] uv 설치 중... (처음 한 번만)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)
if not exist ".env" if exist ".env.example" copy ".env.example" ".env" >nul
cd backend
echo [LoLDosa] 준비 중... (처음엔 1~2분 걸려요)
uv sync --extra app --quiet
if errorlevel 1 (
  echo [LoLDosa] 설치에 실패했어요. 위 메시지를 확인하세요.
  pause
  exit /b 1
)
uv run loldosa app
if errorlevel 1 pause
