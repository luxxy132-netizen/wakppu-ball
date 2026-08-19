#!/bin/bash
# 맥에서 소스로 실행. 더블클릭하면 된다.
# 처음 한 번은 "열 수 없습니다" 가 뜰 수 있는데, 우클릭 → 열기 를 고르면 된다.
cd "$(dirname "$0")" || exit 1

if ! command -v python3 >/dev/null 2>&1; then
  echo
  echo "  Python 3 이 설치되어 있지 않습니다."
  echo "  브라우저에서 python.org 를 열어 드립니다."
  echo
  open "https://www.python.org/downloads/"
  read -r -n 1 -p "  설치 후 이 창을 닫고 다시 실행해 주세요."
  exit 1
fi

if ! python3 -c "import webview" >/dev/null 2>&1; then
  echo
  echo "  처음 실행이라 필요한 구성요소를 설치합니다. 잠시만 기다려 주세요..."
  echo
  python3 -m pip install --quiet --user \
    pywebview pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-WebKit || {
      echo "  설치에 실패했습니다. 인터넷 연결을 확인해 주세요."
      read -r -n 1 -p "  아무 키나 누르면 닫힙니다."
      exit 1
    }
fi

python3 widget.py
