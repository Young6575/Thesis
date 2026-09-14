#!/usr/bin/env python3
"""참고문헌 실재·철회 검증기.

AI가 만들어낸 '존재하지 않는 논문'과 '철회된 논문'을 잡아내기 위한 도구.
Crossref 와 OpenAlex 에 실제로 질의하여 서지정보를 대조한다.

사용법
------
  # 제목으로 검증
  python3 tools/verify_citations.py --query "Development of the Work Locus of Control Scale" \
      --author Spector --year 1988

  # DOI 로 검증 (가장 정확하고 빠름)
  python3 tools/verify_citations.py --doi 10.1037/0021-9010.88.1.170

  # 참고문헌 파일 일괄 검증 (한 줄에 한 건)
  python3 tools/verify_citations.py --file references/척도_원전_검증완료.md

  # JSON 목록 일괄 검증
  #   [{"title": "...", "doi": "...", "author": "Kim", "year": 2020}, ...]
  python3 tools/verify_citations.py --json refs.json

판정
----
  ✅ 일치      제목·저자·연도 일치 → `[검증됨]` 태그 가능
  ⚠️ 부분일치   찾았으나 일부 불일치 → 원문 직접 확인 필요
  ❌ 없음      검색되지 않음 → 허위 인용 의심. 논문에 넣지 말 것
  🚫 철회됨    Retracted. 절대 인용 금지

주의사항 (실측 확인, 2026-09)
--------------------------
- 철회 정보는 Crossref 의 `update-to` 가 **아니라** `updated-by` 에 담긴다.
  철회 공지문에 `update-to` 가 붙고, 철회된 원논문에 `updated-by` 가 붙는다.
- OpenAlex 는 종량제로 전환되어 `?search=` 목록 조회는 과금·차단된다.
  반면 `/works/doi:{DOI}` 단건 조회는 과금 0 이므로 DOI 를 알 때만 사용한다.
"""
import argparse
import difflib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

MAILTO = "researcher@example.org"      # 본인 이메일로 바꾸면 Crossref polite pool 적용
UA = f"ThesisCitationVerifier/2.0 (mailto:{MAILTO})"
CROSSREF = "https://api.crossref.org/works"
OPENALEX = "https://api.openalex.org/works"


# --------------------------------------------------------------------------- HTTP
def _get(url: str, timeout: int = 30, retries: int = 3):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None                      # 존재하지 않는 DOI — 정상적인 답
            if e.code in (429, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            return None
        except Exception:
            if attempt < retries - 1:
                time.sleep(1.5 * (attempt + 1))
                continue
            return None
    return None


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", " ", (s or "").lower()).strip()


def _similar(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, _norm(a), _norm(b)).ratio()


# ------------------------------------------------------------------- 서지 정규화
def _year(msg: dict):
    for f in ("published-print", "published-online", "issued", "created"):
        parts = (msg.get(f) or {}).get("date-parts") or []
        if parts and parts[0] and parts[0][0]:
            return parts[0][0]
    return None


def _retraction_flags(msg: dict):
    """철회·수정 공지를 수집한다.

    Crossref 는 철회된 **원논문**에 `updated-by` 를 붙인다. (`update-to` 는
    반대로 철회 공지문 쪽에 붙으므로 원논문 검사에 쓰면 절대 걸리지 않는다.)
    """
    flags = []
    for u in (msg.get("updated-by") or []):
        t = (u.get("type") or "").lower()
        if "retract" in t or "withdraw" in t:
            flags.append(f"철회({u.get('DOI', '')})")
        elif "concern" in t:
            flags.append(f"우려표명({u.get('DOI', '')})")
        elif "correction" in t or "erratum" in t:
            flags.append(f"정정({u.get('DOI', '')})")
    title = (msg.get("title") or [""])[0]
    if re.match(r"^\s*(retracted|withdrawn)\b", title, re.I):
        flags.append("제목에 RETRACTED 표기")
    return flags


def _from_crossref(msg: dict) -> dict:
    flags = _retraction_flags(msg)
    return {
        "title": (msg.get("title") or [""])[0],
        "authors": [a.get("family", "") for a in msg.get("author", [])][:6],
        "year": _year(msg),
        "container": (msg.get("container-title") or [""])[0],
        "volume": msg.get("volume", ""),
        "issue": msg.get("issue", ""),
        "page": msg.get("page", ""),
        "doi": msg.get("DOI", ""),
        "retracted": any(f.startswith("철회") or "RETRACTED" in f for f in flags),
        "notices": flags,
        "source": "Crossref",
    }


# ------------------------------------------------------------------------ 조회
def lookup_doi(doi: str):
    """DOI 단건 조회. Crossref 우선, OpenAlex 로 철회 여부를 교차 확인."""
    doi = (doi or "").strip().replace("https://doi.org/", "").lstrip("doi:")
    data = _get(f"{CROSSREF}/{urllib.parse.quote(doi)}?mailto={MAILTO}")
    if not data:
        return None
    rec = _from_crossref(data["message"])

    # OpenAlex DOI 단건 조회는 과금 0 — 철회 플래그를 한 번 더 확인한다.
    oa = _get(f"{OPENALEX}/doi:{urllib.parse.quote(doi)}?mailto={MAILTO}", retries=1)
    if oa and oa.get("is_retracted"):
        rec["retracted"] = True
        if "철회(OpenAlex)" not in rec["notices"]:
            rec["notices"].append("철회(OpenAlex is_retracted)")
    return rec


def search_title(query: str, rows: int = 5):
    """제목 검색. OpenAlex 의 ?search= 는 과금·차단되므로 Crossref 만 쓴다."""
    url = (f"{CROSSREF}?query.bibliographic={urllib.parse.quote(query)}"
           f"&rows={rows}&mailto={MAILTO}")
    data = _get(url)
    if not data:
        return []
    return [_from_crossref(it) for it in data.get("message", {}).get("items", [])]


# ------------------------------------------------------------------------ 판정
def verify(query: str = None, doi: str = None, author: str = None, year: int = None):
    label = doi or query

    if doi:
        best = lookup_doi(doi)
        if not best:
            return {"verdict": "❌ 없음", "query": label, "best": None,
                    "note": "Crossref 에 등록되지 않은 DOI. 허위 인용 강력 의심."}
        hits_note = []
        if query and _similar(query, best["title"]) < 0.55:
            hits_note.append(
                f"DOI 는 실재하나 제목이 다름 — 인용한 제목: '{query[:50]}…' / "
                f"실제: '{best['title'][:50]}…'")
        if best["retracted"]:
            return {"verdict": "🚫 철회됨", "query": label, "best": best,
                    "note": "; ".join(best["notices"]) + " → 절대 인용 금지"}
        if hits_note:
            return {"verdict": "⚠️ 부분일치", "query": label, "best": best,
                    "note": "; ".join(hits_note)}
        return {"verdict": "✅ 일치", "query": label, "best": best,
                "note": "; ".join(best["notices"])}

    hits = search_title(query)
    if not hits:
        return {"verdict": "❌ 없음", "query": label, "best": None,
                "note": "Crossref 에서 검색되지 않음. 허위 인용 의심."}

    for h in hits:
        h["_score"] = _similar(query, h["title"])
    best = max(hits, key=lambda h: h["_score"])

    if best["retracted"]:
        return {"verdict": "🚫 철회됨", "query": label, "best": best,
                "note": "; ".join(best["notices"]) + " → 절대 인용 금지"}

    author_bad = bool(author) and not any(
        _norm(author) in _norm(a) for a in best["authors"])
    year_bad = bool(year) and bool(best["year"]) and abs(int(year) - int(best["year"])) > 1

    # 학위논문에서는 위음성(허위 인용 통과)이 위양성보다 훨씬 위험하므로
    # 제목이 충분히 맞지 않으면 '찾지 못함'으로 판정한다.
    if best["_score"] < 0.50 or (best["_score"] < 0.75 and (author_bad or year_bad)):
        return {"verdict": "❌ 없음", "query": label, "best": best,
                "note": f"일치 문헌 없음(최선 후보 유사도 {best['_score']:.2f}). "
                        "원문 확인 전까지 논문에 넣지 말 것."}

    problems = []
    if best["_score"] < 0.85:
        problems.append(f"제목 유사도 {best['_score']:.2f}")
    if author_bad:
        problems.append(f"저자 불일치(검색결과: {', '.join(best['authors'][:3])})")
    if year_bad:
        problems.append(f"연도 불일치(검색결과: {best['year']})")
    problems += best["notices"]

    if not problems:
        return {"verdict": "✅ 일치", "query": label, "best": best, "note": ""}
    return {"verdict": "⚠️ 부분일치", "query": label, "best": best,
            "note": "; ".join(problems) + " → 원문 직접 확인 필요"}


# ------------------------------------------------------------------------ 출력
def show(res):
    b = res["best"]
    print(f"\n{res['verdict']}  {str(res['query'])[:78]}")
    if b:
        auth = ", ".join(b["authors"][:4]) or "?"
        print(f"    └ {auth} ({b['year']}). {b['title'][:92]}")
        vol = f"{b['container']} {b['volume']}({b['issue']}) {b['page']}".replace("() ", " ")
        print(f"      {vol.strip()}")
        if b["doi"]:
            print(f"      https://doi.org/{b['doi']}")
    if res["note"]:
        print(f"    ⚑ {res['note']}")


def main():
    ap = argparse.ArgumentParser(description="참고문헌 실재·철회 검증")
    ap.add_argument("--query", help="검증할 논문 제목")
    ap.add_argument("--doi", help="검증할 DOI (가장 정확)")
    ap.add_argument("--author", help="대조할 제1저자 성(family name)")
    ap.add_argument("--year", type=int, help="대조할 출판연도")
    ap.add_argument("--file", help="한 줄에 한 건씩 담긴 텍스트 파일")
    ap.add_argument("--json", help="[{title, doi, author, year}] 형식 JSON 파일")
    ap.add_argument("--mailto", help="Crossref polite pool 용 본인 이메일")
    args = ap.parse_args()

    if args.mailto:
        global MAILTO, UA
        MAILTO = args.mailto
        UA = f"ThesisCitationVerifier/2.0 (mailto:{MAILTO})"

    if not any([args.query, args.doi, args.file, args.json]):
        ap.error("--query, --doi, --file, --json 중 하나는 필요합니다")

    results = []
    if args.query or args.doi:
        results.append(verify(args.query, args.doi, args.author, args.year))

    if args.json:
        refs = json.load(open(args.json, encoding="utf-8"))
        for i, r in enumerate(refs, 1):
            print(f"[{i}/{len(refs)}]", end=" ", flush=True)
            results.append(verify(r.get("title"), r.get("doi"),
                                  r.get("author"), r.get("year")))
            time.sleep(0.4)

    if args.file:
        # DOI 가 들어 있는 줄은 DOI 로, 아니면 제목으로 검증한다.
        lines = [l.strip() for l in open(args.file, encoding="utf-8")
                 if l.strip() and not l.strip().startswith(("#", "|", ">", "-", "```"))]
        for i, line in enumerate(lines, 1):
            m = re.search(r"10\.\d{4,9}/[^\s\"'<>]+", line)
            print(f"[{i}/{len(lines)}]", end=" ", flush=True)
            results.append(verify(doi=m.group(0)) if m else verify(query=line))
            time.sleep(0.4)

    for r in results:
        show(r)

    bad = [r for r in results if r["verdict"].startswith(("❌", "🚫"))]
    warn = [r for r in results if r["verdict"].startswith("⚠️")]
    ok = len(results) - len(bad) - len(warn)
    print(f"\n{'=' * 62}")
    print(f"총 {len(results)}건 · ✅ {ok} · ⚠️ {len(warn)} · ❌🚫 {len(bad)}")
    if bad:
        print("\n❗ 다음 인용은 논문에 넣지 마십시오:")
        for r in bad:
            print(f"   - {r['verdict']}  {str(r['query'])[:70]}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
