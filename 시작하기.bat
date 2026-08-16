@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 왁뿌볼

rem Python 찾기 (py 런처 우선)
set "PY="
set "PYW="
where pyw >nul 2>&1 && set "PYW=pyw -3"
where py  >nul 2>&1 && set "PY=py -3"
if not defined PY (
  where python >nul 2>&1 && set "PY=python"
)
if not defined PYW (
  where pythonw >nul 2>&1 && set "PYW=pythonw"
)

if not defined PY (
  echo.
  echo   Python 이 설치되어 있지 않습니다.
  echo   브라우저에서 python.org 를 열어 드립니다.
  echo   설치할 때 "Add python.exe to PATH" 를 꼭 체크해 주세요.
  echo.
  start https://www.python.org/downloads/
  pause
  exit /b 1
)

rem 처음 한 번만 필요한 구성요소 설치
%PY% -c "import webview" >nul 2>&1
if errorlevel 1 (
  echo.
  echo   처음 실행이라 필요한 구성요소를 설치합니다. 잠시만 기다려 주세요...
  echo.
  %PY% -m pip install --quiet --user pywebview
  if errorlevel 1 (
    echo   설치에 실패했습니다. 인터넷 연결을 확인해 주세요.
    pause
    exit /b 1
  )
)

if not defined PYW set "PYW=%PY%"
start "" %PYW% widget.py
exit /b 0
