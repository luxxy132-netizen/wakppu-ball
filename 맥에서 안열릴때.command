#!/bin/bash
# macOS 가 "손상되었기 때문에 열 수 없습니다 · 휴지통으로 이동" 이라며 막을 때 쓰는 수리 도구.
#
# 앱이 망가진 게 아니라, 서명·공증이 없는 앱에 붙는 격리(quarantine) 표식 때문입니다.
# 이 파일 자체도 막힌다면 터미널에서 이렇게 실행하세요:
#     bash "맥에서 안열릴때.command"

cd "$(dirname "$0")" || exit 1
echo
echo "  이 폴더의 격리 표식을 지웁니다: $(pwd)"
xattr -cr . 2>/dev/null
echo "  완료."

shopt -s nullglob
apps=(*.app dist/*.app)
if [ ${#apps[@]} -gt 0 ]; then
  for app in "${apps[@]}"; do
    echo "  임시 서명: $app"
    codesign --force --deep --sign - "$app" 2>/dev/null \
      && echo "    서명됨" || echo "    서명 실패 (Xcode 명령줄 도구가 필요할 수 있습니다)"
  done
else
  echo "  이 폴더에 .app 은 없습니다. 소스 실행만 쓰신다면 이대로 충분합니다."
fi

echo
echo "  이제 다시 실행해 보세요."
read -r -n 1 -p "  아무 키나 누르면 닫힙니다."
