#!/usr/bin/env python3
"""WorKey 대시보드 시드 생성기.

'WorKey - 전체 진척도.md'(SSOT)를 읽기 전용으로 파싱해
dashboard/index.html 안의 SEED 블록(/*SEED_START*/ ... /*SEED_END*/)을 갱신한다.

SSOT 마크다운은 절대 수정하지 않는다. 쓰기 대상은 index.html 하나뿐.

사용법 (workey-workspace 루트 또는 dashboard/ 어디서든):
    python3 dashboard/generate_seed.py
"""

import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

DASHBOARD_DIR = Path(__file__).resolve().parent
WORKSPACE = DASHBOARD_DIR.parent
SSOT_PATH = WORKSPACE / "docs" / "WorKey - 전체 진척도.md"
HTML_PATH = DASHBOARD_DIR / "index.html"

# '# 1. MVP 기준 - 백엔드 ...' 류 톱레벨 섹션 -> (track, scope)
SECTION_MAP = [
    (re.compile(r"^# 1\."), ("MVP", "BE")),
    (re.compile(r"^# 2\."), ("MVP", "FE")),
    (re.compile(r"^# 3\."), ("EMP", "BE")),
    (re.compile(r"^# 4\."), ("EMP", "FE")),
    (re.compile(r"^# 5\."), None),  # 확인 기준 섹션 -> 파싱 종료
]

ITEM_RE = re.compile(r"^- \[( |x)\] ((?:MVP|EMP)-(?:BE|FE)-\d+) (.+)$")
PRIO_RE = re.compile(r"^## (P\d)")
DEP_RE = re.compile(r"의존성:\s*(.+?)\.?\s*$")
NOTE_RE = re.compile(r"^\s+- (현재 상태|남은 이유|남은 내용):\s*(.+)$")
SUB_RE = re.compile(r"^(\s+)- (.+)$")

NOTE_MAX = 120


def parse_ssot(text: str):
    items = []
    section = None  # (track, scope)
    prio = None
    cur = None  # 현재 파싱 중 아이템 (서브불릿 수집용)

    for line in text.splitlines():
        # 톱레벨 섹션 전환
        matched_section = False
        for pat, val in SECTION_MAP:
            if pat.match(line):
                if val is None:
                    return items  # '# 5.' 도달 -> 종료
                section = val
                prio = None
                cur = None
                matched_section = True
                break
        if matched_section:
            continue

        m = PRIO_RE.match(line)
        if m:
            prio = m.group(1)
            cur = None
            continue

        if line.startswith("## 검증"):
            prio = "VERIFY"
            cur = None
            continue

        m = ITEM_RE.match(line)
        if m and section:
            cur = {
                "id": m.group(2),
                "track": section[0],
                "scope": section[1],
                "priority": prio or "ETC",
                "title": m.group(3).strip(),
                "done": m.group(1) == "x",
                "note": "",
                "deps": "",
                "detail": [],
            }
            items.append(cur)
            continue

        if cur is None:
            continue

        # 서브불릿 전문을 detail로 수집 (들여쓰기 수준 보존)
        m = SUB_RE.match(line)
        if m:
            lvl = max(0, len(m.group(1)) // 2 - 1)
            cur["detail"].append({"lvl": lvl, "text": m.group(2).strip()})

        # note(카드 미리보기) / deps 보강
        m = NOTE_RE.match(line)
        if m and not cur["note"]:
            note = m.group(2).strip()
            if len(note) > NOTE_MAX:
                note = note[:NOTE_MAX].rstrip() + "..."
            cur["note"] = note
            continue
        m = DEP_RE.search(line)
        if m and line.lstrip().startswith("- 의존성"):
            cur["deps"] = m.group(1).strip()

    return items


def main() -> int:
    if not SSOT_PATH.exists():
        print(f"ERROR: SSOT 파일 없음: {SSOT_PATH}", file=sys.stderr)
        return 1
    if not HTML_PATH.exists():
        print(f"ERROR: 대시보드 파일 없음: {HTML_PATH}", file=sys.stderr)
        return 1

    items = parse_ssot(SSOT_PATH.read_text(encoding="utf-8"))
    if not items:
        print("ERROR: 파싱 결과 0개 - SSOT 형식이 바뀌었는지 확인 필요", file=sys.stderr)
        return 1

    kst = timezone(timedelta(hours=9))
    seed = {
        "generatedAt": datetime.now(kst).strftime("%Y-%m-%d %H:%M KST"),
        "items": items,
    }
    seed_js = (
        "/*SEED_START*/\n"
        f"const SEED = {json.dumps(seed, ensure_ascii=False, indent=2)};\n"
        "/*SEED_END*/"
    )

    html = HTML_PATH.read_text(encoding="utf-8")
    new_html, n = re.subn(
        r"/\*SEED_START\*/.*?/\*SEED_END\*/", lambda _: seed_js, html, count=1, flags=re.S
    )
    if n != 1:
        print("ERROR: index.html에서 SEED 블록 마커를 찾지 못함", file=sys.stderr)
        return 1
    HTML_PATH.write_text(new_html, encoding="utf-8")

    # 요약 출력
    def count(track, scope):
        sub = [i for i in items if i["track"] == track and i["scope"] == scope]
        done = sum(1 for i in sub if i["done"])
        return f"{done}/{len(sub)}"

    print(f"시드 갱신 완료: {len(items)}개 항목 -> {HTML_PATH}")
    print(f"  MVP-BE {count('MVP','BE')} | MVP-FE {count('MVP','FE')} | "
          f"EMP-BE {count('EMP','BE')} | EMP-FE {count('EMP','FE')}")
    total_done = sum(1 for i in items if i["done"])
    print(f"  전체 {total_done}/{len(items)} 완료")
    return 0


if __name__ == "__main__":
    sys.exit(main())
