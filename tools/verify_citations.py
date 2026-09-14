#!/usr/bin/env python3
"""참고문헌 실재 검증기.

AI가 만들어낸 '존재하지 않는 논문'을 잡아내기 위한 도구.
Crossref 와 OpenAlex 에 실제로 질의하여 서지정보를 대조하고,
철회(retracted) 여부까지 확인한다.

사용법
------
  # 한 건 확인
  python3 tools/verify_citations.py --query "Spector 1988 Work Locus of Control Scale"

  # 참고문헌 파일 일괄 확인 (한 줄에 한 건)
  python3 tools/verify_citations.py --file references/references.md

  # 저자/연도까지 대조
  python3 tools/verify_citations.py --query "Climate as a moderator of the relationship between leader-member exchange" \
      --author Hofmann --year 2003

판정
----
  ✅ 일치      제목·저자·연도가 모두 맞음 → [검증됨] 태그 가능
  ⚠️  부분일치  제목은 찾았으나 저자 또는 연도가 다름 → 직접 확인 필요
  ❌ 없음      검색되지 않음 → 허위 인용 의심. 논문에 넣지 말 것
  🚫 철회됨    Retracted. 절대 인용 금지
"""
import argparse
import difflib
import json
import re
import sys
import time
import urllib.parse
import urllib.request

UA = "ThesisCitationVerifier/1.0 (mailto:researcher@example.org)"
CROSSREF = "https://api.crossref.org/works"
OPENALEX = "https://api.openalex.org/works"


def _get(url: str, timeout: int = 25, retries: int = 3):
    """429(요청 과다)는 지수적 백오프로 재시도한다."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            print(f"    (조회 실패: {e})", file=sys.stderr)
            return None
        except Exception as e:
            print(f"    (조회 실패: {e})", file=sys.stderr)
            return None
    return None


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", (s or "").lower()).strip()


def _similar(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def search_crossref(query: str, rows: int = 5):
    url = f"{CROSSREF}?query.bibliographic={urllib.parse.quote(query)}&rows={rows}"
    data = _get(url)
    if not data:
        return []
    out = []
    for it in data.get("message", {}).get("items", []):
        out.append({
            "title": (it.get("title") or [""])[0],
            "authors": [f"{a.get('family','')}" for a in it.get("author", [])][:6],
            "year": (it.get("issued", {}).get("date-parts", [[None]])[0] or [None])[0],
            "container": (it.get("container-title") or [""])[0],
            "volume": it.get("volume", ""),
            "page": it.get("page", ""),
            "doi": it.get("DOI", ""),
            "type": it.get("type", ""),
            "retracted": any(u.get("type") == "retraction"
                             for u in (it.get("update-to") or [])),
            "source": "Crossref",
        })
    return out


_OPENALEX_OK = True


def search_openalex(query: str, rows: int = 5):
    global _OPENALEX_OK
    if not _OPENALEX_OK:
        return []
    url = (f"{OPENALEX}?search={urllib.parse.quote(query)}"
           f"&per-page={rows}&mailto=researcher@example.org")
    data = _get(url, retries=2)
    if not data:
        _OPENALEX_OK = False   # 이후 조회는 건너뛰고 Crossref 만 사용
        return []
    out = []
    for it in data.get("results", []):
        auth = [a["author"]["display_name"].split()[-1]
                for a in it.get("authorships", [])][:6]
        loc = (it.get("primary_location") or {}).get("source") or {}
        out.append({
            "title": it.get("title") or "",
            "authors": auth,
            "year": it.get("publication_year"),
            "container": loc.get("display_name", ""),
            "volume": (it.get("biblio") or {}).get("volume", "") or "",
            "page": "",
            "doi": (it.get("doi") or "").replace("https://doi.org/", ""),
            "type": it.get("type", ""),
            "retracted": it.get("is_retracted", False),
            "cited_by": it.get("cited_by_count", 0),
            "source": "OpenAlex",
        })
    return out


def verify(query: str, author: str = None, year: int = None, quiet: bool = False):
    hits = search_crossref(query) + search_openalex(query)
    if not hits:
        return {"verdict": "❌ 없음", "query": query, "best": None,
                "note": "Crossref·OpenAlex 모두에서 검색되지 않음. 허위 인용 의심."}

    for h in hits:
        h["_score"] = _similar(query, h["title"])
    best = max(hits, key=lambda h: h["_score"])

    if best.get("retracted"):
        return {"verdict": "🚫 철회됨", "query": query, "best": best,
                "note": "철회된 논문이다. 절대 인용하지 말 것."}

    author_bad = bool(author) and not any(
        _norm(author) in _norm(a) for a in best["authors"])
    year_bad = bool(year) and bool(best["year"]) and abs(int(year) - int(best["year"])) > 1

    # 제목이 거의 안 맞으면 '찾지 못한 것'으로 본다 — 검색엔진이 엉뚱한 논문을
    # 최선의 후보로 돌려주는 것을 일치로 오인하면 안 된다.
    if best["_score"] < 0.50 or (best["_score"] < 0.75 and (author_bad or year_bad)):
        return {"verdict": "❌ 없음", "query": query, "best": best,
                "note": f"일치하는 문헌을 찾지 못함(최선 후보 유사도 {best['_score']:.2f}). "
                        "허위 인용 의심 — 원문 확인 전까지 논문에 넣지 말 것."}

    problems = []
    if best["_score"] < 0.85:
        problems.append(f"제목 유사도 {best['_score']:.2f}")
    if author_bad:
        problems.append(f"저자 불일치(검색결과: {', '.join(best['authors'][:3])})")
    if year_bad:
        problems.append(f"연도 불일치(검색결과: {best['year']})")

    if not problems:
        return {"verdict": "✅ 일치", "query": query, "best": best, "note": ""}
    return {"verdict": "⚠️ 부분일치", "query": query, "best": best,
            "note": "; ".join(problems) + " → 원문 직접 확인 필요"}


def show(res):
    b = res["best"]
    print(f"\n{res['verdict']}  {res['query'][:80]}")
    if b:
        auth = ", ".join(b["authors"][:4]) or "?"
        print(f"    └ {auth} ({b['year']}). {b['title'][:95]}")
        print(f"      {b['container']} {b['volume']} {b['page']}".rstrip())
        if b["doi"]:
            print(f"      DOI: https://doi.org/{b['doi']}   [{b['source']}]")
    if res["note"]:
        print(f"    ⚑ {res['note']}")


def main():
    ap = argparse.ArgumentParser(description="참고문헌 실재 검증")
    ap.add_argument("--query", help="검증할 제목 또는 서지정보")
    ap.add_argument("--author", help="대조할 제1저자 성(family name)")
    ap.add_argument("--year", type=int, help="대조할 출판연도")
    ap.add_argument("--file", help="한 줄에 한 건씩 담긴 파일 일괄 검증")
    args = ap.parse_args()

    if not args.query and not args.file:
        ap.error("--query 또는 --file 중 하나는 필요합니다")

    results = []
    if args.query:
        results.append(verify(args.query, args.author, args.year))
    if args.file:
        lines = [l.strip() for l in open(args.file, encoding="utf-8")
                 if l.strip() and not l.strip().startswith(("#", "|", ">", "-"))]
        for i, line in enumerate(lines, 1):
            print(f"[{i}/{len(lines)}]", end=" ", flush=True)
            results.append(verify(line))
            time.sleep(0.6)   # API 예의

    for r in results:
        show(r)

    bad = [r for r in results if r["verdict"].startswith(("❌", "🚫"))]
    warn = [r for r in results if r["verdict"].startswith("⚠️")]
    print(f"\n{'='*60}")
    print(f"총 {len(results)}건 · ✅ {len(results)-len(bad)-len(warn)} · "
          f"⚠️ {len(warn)} · ❌🚫 {len(bad)}")
    if bad:
        print("\n❗ 다음 인용은 논문에 넣지 마십시오:")
        for r in bad:
            print(f"   - {r['query'][:75]}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
