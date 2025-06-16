#!/usr/bin/env bash
# ------------------------------------------
# fix_py27_to_py3.sh
#   Recursively convert every *.py file under
#   the given path (or current dir) with 2to3.
#
#   ./fix_py27_to_py3.sh            # 현재 디렉터리
#   ./fix_py27_to_py3.sh /project   # /project 부터
# ------------------------------------------

set -euo pipefail

ROOT="${1:-.}"            # 기본은 현재 폴더
LOGFILE="$(pwd)/py2to3_errors.log"
TMPLOG="$(mktemp)"

# 로그파일 초기화
: > "$LOGFILE"

echo ">> Scanning under: $ROOT"
echo ">> Logging to     : $LOGFILE"
echo

# 원하는 경우 제외할 디렉터리
EXCLUDE_DIRS="\.git\|\.venv\|env\|build\|dist"

# find 로 전체 순회
#  -print0 / read -d ''  : 공백/한글 파일명 안전
find "$ROOT" -type f -name "*.py" ! -regex ".*\(${EXCLUDE_DIRS}\).*" -print0 |
while IFS= read -r -d '' file; do
  printf "  * %s\n" "${file#$ROOT/}"      # 깔끔하게 상대경로 표시

  # 2to3 변환: -w (실제 수정)  -n (백업 *.bak 만들지 않음)
  # 오류 · 경고는 TMPLOG 에 남김
  if ! 2to3 -w -n "$file" 2>>"$TMPLOG"; then
    echo "    !! 2to3 failed on $file" | tee -a "$LOGFILE"
  fi
done

# 2to3 가 출력한 stderr 중 필요한 것만 error log 로 이동
if [[ -s "$TMPLOG" ]]; then
  grep -E -v '^RefactoringTool: (Skipping implicit module|No changes|Refactored|Warnings enabled)' \
    "$TMPLOG" >> "$LOGFILE" || true
fi
rm -f "$TMPLOG"

echo
echo ">> DONE."
[[ -s "$LOGFILE" ]] \
  && echo "   일부 파일에서 오류/경고가 발생했습니다. → $LOGFILE" \
  || echo "   변환 완료 – 오류 없음."
