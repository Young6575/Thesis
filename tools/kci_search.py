#!/usr/bin/env python3
"""KCI(한국학술지인용색인) 국내 선행연구 검색기.

국내 문헌은 Elicit·Consensus 같은 해외 AI 도구가 거의 찾지 못한다.
KCI Open API 로 직접 긁어와야 한다.

인증키 발급 (최초 1회)
---------------------
  https://open.kci.go.kr  →  회원가입  →  [Open API] 메뉴에서 신청
  발급받은 키를 환경변수에 넣는다:
      export KCI_KEY="발급받은키"

사용법
------
  # 단일 키워드
  python3 tools/kci_search.py --title 통제위치

  # 본 논문 변수의 동의어를 한꺼번에 (국내 문헌은 용어가 제각각이라 필수)
  python3 tools/kci_search.py --preset all

  # 결과를 CSV 로 저장해 git 에 넣기
  python3 tools/kci_search.py --preset all --out references/kci_국내선행연구.csv

주의
----
- **브라우저 User-Agent 가 반드시 필요하다.** curl/python 기본 UA 로 호출하면
  웹방화벽이 EUC-KR 로 깨진 차단 안내 HTML 을 돌려준다. API 가 죽은 게 아니다.
  (국회도서관 등 다른 국내 기관 API 도 대체로 같다.)
- OAI-PMH(`/oai/request`)는 키가 필요 없지만 **키워드 검색을 지원하지 않는다.**
  날짜 구간 벌크 수확만 되므로 주제 검색에는 쓸 수 없다.
- ⚠️ **미검증 부분**: 인증키가 없어 실제 검색 결과 XML 의 태그 구조는 확인하지 못했다.
  결과가 0건으로 나오거나 열이 비면 `_text()` 의 태그 경로를 KCI 응답에 맞게
  고쳐야 한다. 키 발급 후 아래로 원본 XML 을 먼저 확인할 것:
      curl -s -A "Mozilla/5.0" "https://open.kci.go.kr/po/openapi/openApiSearch.kci\
      ?apiCode=articleSearch&key=$KCI_KEY&title=통제위치&displayCount=2" | head -60
"""
import argparse
import csv
import os
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API = "https://open.kci.go.kr/po/openapi/openApiSearch.kci"

# 국내 문헌은 같은 개념을 다른 용어로 쓴다. 누락을 막으려면 동의어를 모두 훑어야 한다.
PRESETS = {
    "통제위치": ["통제위치", "통제소재", "내외통제성", "통제신념", "로터 통제위치"],
    "피드백추구": ["피드백추구행동", "피드백 추구", "피드백추구", "피드백 탐색"],
    "실책관리": ["실책관리", "오류관리", "실수관리", "실책관리풍토", "오류관리문화"],
    "안전행동": ["안전시민행동", "안전행동", "안전참여", "안전순응", "안전수행"],
    "소방": ["소방공무원 안전", "소방공무원 안전행동", "소방공무원 안전문화",
             "소방관 안전", "구급대원 안전"],
}

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")


def _fetch(params: dict, retries: int = 3):
    url = f"{API}?{urllib.parse.urlencode(params, encoding='utf-8')}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                raw = r.read()
            if b"<MetaData" not in raw and b"<OAI-PMH" not in raw:
                print("  ⚠️ 방화벽 차단 응답으로 보입니다 (User-Agent 문제)", file=sys.stderr)
                return None
            return ET.fromstring(raw)
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            print(f"  ⚠️ 조회 실패: {e}", file=sys.stderr)
            return None
    return None


def _text(node, *paths):
    for p in paths:
        el = node.find(p)
        if el is not None and (el.text or "").strip():
            return el.text.strip()
    return ""


def search(title: str, key: str, count: int = 100, page: int = 1):
    root = _fetch({"apiCode": "articleSearch", "key": key,
                   "title": title, "displayCount": count, "page": page})
    if root is None:
        return []

    msg = root.find(".//resultMsg")
    if msg is not None and msg.text:
        print(f"  ⚠️ KCI 응답: {msg.text.strip()}", file=sys.stderr)
        return []

    rows = []
    for rec in root.iter("record"):
        rows.append({
            "검색어": title,
            "제목": _text(rec, ".//article-title", ".//articleTitle", ".//title"),
            "영문제목": _text(rec, ".//article-title-en", ".//articleTitleEn"),
            "저자": "; ".join(
                a.text.strip() for a in rec.iter("author-name") if a is not None and a.text),
            "학술지": _text(rec, ".//journal-name", ".//journalName"),
            "발행년": _text(rec, ".//pub-year", ".//pubYear"),
            "권": _text(rec, ".//volume"), "호": _text(rec, ".//issue"),
            "DOI": _text(rec, ".//doi"),
            "UCI": _text(rec, ".//uci"),
            "피인용": _text(rec, ".//citation-count", ".//citationCount"),
            "URL": _text(rec, ".//url", ".//articleUrl"),
            "초록": _text(rec, ".//abstract")[:1500],
        })
    return rows


def main():
    ap = argparse.ArgumentParser(description="KCI 국내 선행연구 검색")
    ap.add_argument("--title", help="검색어 (제목 검색)")
    ap.add_argument("--preset", choices=list(PRESETS) + ["all"],
                    help="본 논문 변수별 동의어 묶음 검색")
    ap.add_argument("--count", type=int, default=100, help="검색어당 최대 건수")
    ap.add_argument("--out", help="CSV 저장 경로")
    ap.add_argument("--key", help="KCI 인증키 (없으면 환경변수 KCI_KEY)")
    args = ap.parse_args()

    key = args.key or os.environ.get("KCI_KEY", "")
    if not key:
        print(__doc__)
        print("\n❌ 인증키가 없습니다.  export KCI_KEY=\"발급받은키\"  후 다시 실행하세요.")
        return 2

    terms = []
    if args.title:
        terms.append(args.title)
    if args.preset:
        groups = PRESETS.values() if args.preset == "all" else [PRESETS[args.preset]]
        for g in groups:
            terms.extend(g)
    if not terms:
        ap.error("--title 또는 --preset 중 하나는 필요합니다")

    seen, rows = set(), []
    for t in terms:
        print(f"검색: {t} ...", end=" ", flush=True)
        got = search(t, key, args.count)
        new = 0
        for r in got:
            dedup = r["DOI"] or r["UCI"] or (r["제목"] + r["발행년"])
            if dedup in seen:
                continue
            seen.add(dedup)
            rows.append(r)
            new += 1
        print(f"{len(got)}건 (신규 {new})")
        time.sleep(0.5)

    print(f"\n총 {len(rows)}건 (중복 제거 후)")

    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["제목"])
            w.writeheader()
            w.writerows(rows)
        print(f"저장: {args.out}")
    else:
        for r in rows[:30]:
            print(f"  · {r['저자'][:20]} ({r['발행년']}). {r['제목'][:60]} — "
                  f"{r['학술지'][:25]} [피인용 {r['피인용']}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
