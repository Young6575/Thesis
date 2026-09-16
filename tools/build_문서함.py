#!/usr/bin/env python3
"""연구 문서를 한 페이지짜리 「연구 문서함」으로 묶는다.

옆 패널에서 바로 열리는 페이지를 만든다. 웹(claude.ai)에서는 파일을 보내면
내려받기 카드로만 뜨므로, 읽을 문서는 이렇게 묶어 아티팩트로 올린다.

    python3 tools/build_문서함.py /tmp/문서함.html

만든 뒤에는 **기존 아티팩트를 갱신**한다. 새로 올리면 주소가 바뀐다.
    https://claude.ai/artifact/1QojziYRZ778QiYbw3DLVN

새 문서를 추가하려면 아래 DOCS 목록에 한 줄 넣으면 된다.
"""
import html
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import md2html as M

if len(sys.argv) < 2:
    sys.exit("사용법: python3 tools/build_문서함.py <출력.html>")
OUT = pathlib.Path(sys.argv[1])

# ─────────────────────────────────────────────────────────────
# 문서 목록 — (경로, 구역, 짧은 이름, 등급라벨, 등급종류)
#
# 등급종류는 CLAUDE.md §3-2 문서 신뢰도 등급을 따른다.
#   hot     지금 손대야 하는 것
#   wait    결재·회신 대기
#   ok      확정본 — 다른 문서와 충돌하면 이것이 맞다
#   draft   AI 초고 — 논문에 그대로 옮기면 안 된다
#   check   서지는 확인했으나 원문 미확인
#   neutral 참고
# ─────────────────────────────────────────────────────────────
DOCS = [
    ("docs/06_교수님_재승인_안건.md",           "지금 — 설문 배포 전", "교수님 재승인 안건",   "결재 대기", "wait"),
    ("survey/02_설문지_배포본.md",              "지금 — 설문 배포 전", "설문지 배포본",        "배포 직전", "hot"),
    ("docs/08_연구수행_표준절차_체크리스트.md", "지금 — 설문 배포 전", "연구 수행 절차 점검",  "진행 중",   "wait"),

    ("docs/_확정사항.md",                       "확정 · 근거",         "확정사항",             "확정",      "ok"),
    ("references/척도_원전_검증완료.md",        "확정 · 근거",         "척도 원전 검증",       "확정",      "ok"),
    ("docs/07_직무경력_절단점_근거.md",         "확정 · 근거",         "직무경력 절단점 근거", "근거자료",  "ok"),

    ("docs/00_연구개요.md",                     "연구 설계",           "연구 개요",            "초고",      "draft"),
    ("docs/01_연구모형_가설.md",                "연구 설계",           "연구모형 · 가설",      "초고",      "draft"),
    ("docs/02_조작적정의_측정도구.md",          "연구 설계",           "조작적 정의 · 측정도구", "초고",    "draft"),
    ("docs/03_분석계획.md",                     "연구 설계",           "분석 계획",            "초고",      "draft"),

    ("docs/04_이론적배경_문헌노트.md",          "이론 · 문헌",         "이론적 배경 문헌노트", "초고",      "draft"),
    ("references/문헌매트릭스.md",              "이론 · 문헌",         "문헌 매트릭스",        "누적 중",   "neutral"),
    ("docs/09_지도교수_연구분석.md",            "이론 · 문헌",         "지도교수 연구 분석",   "원문 미확인", "check"),

    ("docs/초안/Spector_메일_초안.md",          "보낼 것",             "Spector 교수 메일",    "미발송",    "wait"),
    ("docs/초안/IRB_연구대상자_설명문_동의서.md", "보낼 것",           "연구 설명문 · 동의서", "초안",      "neutral"),

    ("docs/용어사전.md",                        "참고",                "용어사전",             "참고",      "neutral"),
    ("docs/05_AI연구도구_리서치.md",            "참고",                "AI 연구도구 조사",     "참고",      "neutral"),
]

RAW_HTML = re.compile(
    r"^\s*(?:</?details\b[^>]*>|<summary\b[^>]*>.*</summary>|</?summary>)\s*$", re.I)


def convert(md: str) -> str:
    """md2html 을 쓰되, <details>/<summary> 는 원문 그대로 통과시킨다."""
    chunks, buf = [], []
    for ln in md.split("\n"):
        if RAW_HTML.match(ln):
            chunks.append(("md", "\n".join(buf))); buf = []
            chunks.append(("raw", ln.strip()))
        else:
            buf.append(ln)
    chunks.append(("md", "\n".join(buf)))
    body = "".join(c if k == "raw" else M.md2html(c) for k, c in chunks)
    for mark, cls in (("[x] ", "chk done"), ("[X] ", "chk done"), ("[ ] ", "chk")):
        body = body.replace(f"<li>{mark}", f'<li class="{cls}">')
    return body


def split_title(md: str):
    lines = md.split("\n")
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            return ln[2:].strip(), "\n".join(lines[i + 1:])
    return "제목 없음", md


# ── 표지에 쓸 숫자는 문항 뱅크에서 직접 읽는다 (손으로 적으면 어긋난다) ──
bank = json.loads((ROOT / "survey/item_bank.json").read_text(encoding="utf-8"))
n_items = len(bank["items"])
by_var = {}
for it in bank["items"]:
    by_var[it["var"]] = by_var.get(it["var"], 0) + 1
extra = bank.get("administered_extra", [])
n_attn = len([i for i in extra if i.get("var") == "ATTN"])
n_rated = n_items + 7 + n_attn          # 연구변수 + 일반적 사항 7 + 주의점검

COVER = f"""
<article class="pane" id="cover">
  <header class="dochead">
    <p class="eyebrow">표지 · <span class="chip hot">설문 배포 직전</span></p>
    <h1>소방공무원의 통제위치가 안전시민행동에 미치는 영향</h1>
    <p class="sub">피드백 추구행동의 매개효과와 지각된 실책관리풍토 · 직무경력의 조절효과</p>
  </header>
  <div class="doc">

    <div class="callout">
      <p class="calloutlab">이 논문이 하려는 말</p>
      <p><strong>“내적 통제위치는 좋고 외적 통제위치는 나쁘다”는 통념에 대한 반론.</strong>
      극도의 불확실성과 높은 팀 상호의존성을 가진 소방 현장에서는 내적 통제성향이
      <strong>항상</strong> 안전에 유리한 것은 아니며, 피드백 추구와 실책관리풍토라는
      조직적 메커니즘에 따라 그 효과가 달라진다.</p>
    </div>

    <h2>연구모형</h2>
    <div class="modelwrap">
      <div class="model">
        <div class="mcol">
          <p class="mrole">독립변수</p>
          <div class="mbox"><b>통제위치</b><span>내적 · 외적</span></div>
        </div>
        <div class="marrow" aria-hidden="true">→</div>
        <div class="mcol">
          <p class="mrole">매개변수</p>
          <div class="mbox"><b>피드백 추구행동</b><span>긍정적 · 부정적</span></div>
        </div>
        <div class="marrow" aria-hidden="true">→</div>
        <div class="mcol">
          <p class="mrole">종속변수</p>
          <div class="mbox"><b>안전시민행동</b><span>6차원</span></div>
        </div>
      </div>
      <div class="mods">
        <p class="mrole">조절변수 — 위 두 경로에 작용</p>
        <div class="mbox mod"><b>지각된 실책관리풍토</b><span>개인 지각 수준</span></div>
        <div class="mbox mod"><b>직무경력</b><span>3집단 · ≤5년 / 6–15년 / ≥16년</span></div>
      </div>
    </div>

    <h2>측정도구</h2>
    <table>
      <thead><tr><th>구분</th><th>변수</th><th>원척도</th><th>문항</th></tr></thead>
      <tbody>
        <tr><td>독립</td><td>통제위치 (LOC)</td><td>Spector (1988) WLCS + 역문항 4</td><td>{by_var.get('LOC', 0)}</td></tr>
        <tr><td>매개</td><td>피드백 추구행동 (FSB)</td><td>Ashford &amp; Tsui (1991) 기반</td><td>{by_var.get('FSB', 0)}</td></tr>
        <tr><td>조절 1</td><td>지각된 실책관리풍토 (EMC)</td><td>van Dyck 외 (2005) + 역문항 2</td><td>{by_var.get('EMC', 0)}</td></tr>
        <tr><td>조절 2</td><td>직무경력</td><td>인구통계 3구간</td><td>1</td></tr>
        <tr><td>종속</td><td>안전시민행동 (SCB)</td><td>Hofmann 외 (2003) 기반 6차원×3</td><td>{by_var.get('SCB', 0)}</td></tr>
      </tbody>
    </table>
    <p class="note">연구 변수 <b>{n_items}문항</b> · 여기에 일반적 사항 7 + 주의점검 {n_attn} 을 더해
    설문에 실리는 평정 문항은 <b>{n_rated}문항</b>. 전 척도 5점이되 안전시민행동만 빈도형이다.
    <b>마커변수는 쓰지 않는다</b>(2026-09-16 철회 · 숭실대 관행).</p>

    <h2>지금 어디까지 왔나</h2>
    <ol class="steps">
      <li class="done"><b>척도 확정</b> — 지도교수 검토 통과</li>
      <li class="done"><b>설문지 작성</b> — 배포본 완성</li>
      <li class="now"><b>재승인 결재</b> — <span class="chip wait">대기</span> 이것만 끝나면 배포한다</li>
      <li><b>기관 협조 · 파일럿</b> — 배포 경로 확보, 사전조사</li>
      <li><b>자료 수집 → 분석 → 집필</b></li>
    </ol>
    <div class="callout warn">
      <p class="calloutlab">배포 전에만 되돌릴 수 있다</p>
      <p>설문을 뿌리고 나면 문항은 고칠 수 없다. <b>「교수님 재승인 안건」 결재 전에는
      배포하지 않는다.</b> 아직 열려 있는 항목은 R7(피드백추구 역문항) 하나뿐이다.</p>
    </div>

    <h2>왼쪽 목록 보는 법</h2>
    <p>문서 이름 옆의 표시가 <b>그 문서를 얼마나 믿어도 되는지</b>를 뜻한다.</p>
    <ul class="legend">
      <li><span class="chip ok">확정</span> 지도교수 검토를 통과했거나 원전 대조를 마쳤다. 다른 문서와 어긋나면 <b>이쪽이 맞다</b>.</li>
      <li><span class="chip hot">배포 직전</span> <span class="chip wait">결재 대기</span> 지금 손대고 있는 것.</li>
      <li><span class="chip draft">초고</span> <b>AI가 쓴 초안이다. 논문에 그대로 옮기면 안 된다.</b> 영문 문헌은 DOI 확인을 마쳤으나 국내 문헌은 대부분 미검증이다.</li>
      <li><span class="chip check">원문 미확인</span> 서지정보는 확인했으나 논문 본문(PDF)은 아직 못 봤다.</li>
      <li><span class="chip neutral">참고</span> 필요할 때 찾아보는 자료.</li>
    </ul>
  </div>
</article>
"""

# ── 문서 변환 ─────────────────────────────────────────────────
nav, panes, section_now = [], [], None
nav.append('<p class="navhead">표지</p><ul class="navlist">'
           '<li><button class="navitem on" data-t="cover" aria-current="page">'
           '<span class="navname">연구 한눈에 보기</span></button></li></ul>')

for n, (rel, section, short, label, kind) in enumerate(DOCS):
    src = ROOT / rel
    if not src.exists():
        print(f"  ⚠️ 없음, 건너뜀: {rel}")
        continue
    full_title, body_md = split_title(src.read_text(encoding="utf-8"))
    did = f"d{n}"
    if section != section_now:
        if section_now is not None:
            nav.append("</ul>")
        nav.append(f'<p class="navhead">{html.escape(section)}</p><ul class="navlist">')
        section_now = section
    nav.append(
        f'<li><button class="navitem" data-t="{did}" aria-current="false">'
        f'<span class="navname">{html.escape(short)}</span>'
        f'<span class="chip {kind}">{html.escape(label)}</span></button></li>')
    # 무거운 본문은 <template> 에 담아 둔다. 열 때 꺼내 붙이므로 첫 화면이 빠르다.
    panes.append(
        f'<template data-pane="{did}">'
        f'<article class="pane" id="{did}">'
        f'<header class="dochead"><p class="eyebrow">{html.escape(section)} · '
        f'<span class="chip {kind}">{html.escape(label)}</span></p>'
        f'<h1>{html.escape(full_title)}</h1>'
        f'<p class="src">{html.escape(rel)}</p></header>'
        f'<div class="doc">{convert(body_md)}</div></article></template>')
nav.append("</ul>")

CSS = r"""
:root{
  --ground:#eef1f4; --surface:#ffffff; --sink:#e3e8ed;
  --ink:#0f1b24; --body:#30404d; --muted:#65788a; --rule:#d2dae1;
  --accent:#12626f; --accent-soft:#dfeef0; --accent-line:#8fc2c8;
  --warn:#8a5209; --warn-soft:#f8efdd;
  --ok:#1c6b4a;   --ok-soft:#e0f0e8;
  --hot:#8f3520;  --hot-soft:#f8e6e0;
  --draft:#5a4b86; --draft-soft:#ebe7f5;
  --codebg:#e9edf1; --prebg:#16222c; --prefg:#dfe7ee;
  --shadow:0 1px 2px rgba(15,27,36,.05), 0 10px 30px -22px rgba(15,27,36,.5);
}
@media (prefers-color-scheme:dark){ :root:not([data-theme="light"]){
  --ground:#0d1318; --surface:#141d24; --sink:#1b262e;
  --ink:#e9eff4; --body:#bfccd6; --muted:#8395a4; --rule:#28343d;
  --accent:#63b6c2; --accent-soft:#123034; --accent-line:#2b5f68;
  --warn:#d9a94f; --warn-soft:#2e2717;
  --ok:#6cbd95;   --ok-soft:#142b21;
  --hot:#dd8b73;  --hot-soft:#2e1a14;
  --draft:#b5a6e0; --draft-soft:#221d33;
  --codebg:#1d2830; --prebg:#0a1016; --prefg:#cfdae3;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 30px -22px rgba(0,0,0,.9);
}}
:root[data-theme="dark"]{
  --ground:#0d1318; --surface:#141d24; --sink:#1b262e;
  --ink:#e9eff4; --body:#bfccd6; --muted:#8395a4; --rule:#28343d;
  --accent:#63b6c2; --accent-soft:#123034; --accent-line:#2b5f68;
  --warn:#d9a94f; --warn-soft:#2e2717;
  --ok:#6cbd95;   --ok-soft:#142b21;
  --hot:#dd8b73;  --hot-soft:#2e1a14;
  --draft:#b5a6e0; --draft-soft:#221d33;
  --codebg:#1d2830; --prebg:#0a1016; --prefg:#cfdae3;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 30px -22px rgba(0,0,0,.9);
}

*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:var(--ground);color:var(--body);
  font-family:"IBM Plex Sans KR",-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;
  font-size:15.5px;line-height:1.78;-webkit-font-smoothing:antialiased;
  /* 한국어는 어절 단위로 끊는다. 없으면 단어 한가운데서 줄이 바뀐다 */
  word-break:keep-all;overflow-wrap:break-word}
.doc code,.doc pre,.src{word-break:break-all}

.shell{display:grid;grid-template-columns:292px minmax(0,1fr);min-height:100%}

/* ── 왼쪽 목록 ───────────────────────────── */
.rail{background:var(--surface);border-right:1px solid var(--rule);
  position:sticky;top:env(safe-area-inset-top,0px);align-self:start;
  max-height:100vh;overflow-y:auto;padding-block:26px 40px;padding-inline:20px}
.brand{display:block;margin:0 0 3px;font-family:"Gowun Batang",serif;
  font-size:1.12rem;font-weight:700;color:var(--ink);letter-spacing:-.01em;line-height:1.4}
.brandsub{margin:0 0 20px;font-size:.75rem;color:var(--muted);line-height:1.6}
.navhead{margin:20px 0 7px;font-size:.69rem;font-weight:600;letter-spacing:.12em;
  color:var(--muted)}
.navhead:first-of-type{margin-top:0}
.navlist{list-style:none;margin:0;padding:0;display:grid;gap:2px}
.navitem{width:100%;display:flex;align-items:center;justify-content:space-between;gap:9px;
  background:none;border:0;border-radius:6px;padding:7px 9px;cursor:pointer;text-align:left;
  font:inherit;font-size:.86rem;color:var(--body);line-height:1.45}
.navitem:hover{background:var(--sink);color:var(--ink)}
.navitem.on{background:var(--accent-soft);color:var(--ink);font-weight:600;
  box-shadow:inset 2px 0 0 var(--accent)}
.navitem:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.navname{min-width:0}

.chip{flex:none;font-size:.66rem;font-weight:600;padding:2px 7px;border-radius:999px;
  white-space:nowrap;background:var(--sink);color:var(--muted)}
.chip.ok{background:var(--ok-soft);color:var(--ok)}
.chip.wait{background:var(--warn-soft);color:var(--warn)}
.chip.hot{background:var(--hot-soft);color:var(--hot)}
.chip.draft{background:var(--draft-soft);color:var(--draft)}
.chip.check{background:var(--sink);color:var(--body)}

/* ── 본문 ───────────────────────────────── */
.stage{padding-block:40px 120px;padding-inline:clamp(16px,4vw,56px);min-width:0}
.pane{max-width:70ch;margin:0 auto}
#cover{max-width:76ch}

.dochead{margin:0 0 34px;padding-bottom:20px;border-bottom:2px solid var(--rule)}
.eyebrow{margin:0 0 10px;font-size:.72rem;letter-spacing:.09em;color:var(--muted);
  display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.dochead h1{margin:0;font-family:"Gowun Batang",serif;font-weight:700;color:var(--ink);
  font-size:clamp(1.4rem,1.05rem + 1.35vw,1.92rem);line-height:1.42;letter-spacing:-.015em;
  text-wrap:balance}
.dochead .sub{margin:.55em 0 0;font-size:.95rem;color:var(--muted);line-height:1.6}
.src{margin:12px 0 0;font-family:"IBM Plex Mono",ui-monospace,monospace;
  font-size:.72rem;color:var(--muted)}

.doc h2{margin:2.5em 0 .7em;font-family:"Gowun Batang",serif;font-size:1.2rem;font-weight:700;
  color:var(--ink);letter-spacing:-.01em;line-height:1.45;text-wrap:balance;
  padding-bottom:.3em;border-bottom:1px solid var(--rule)}
.doc h3{margin:2em 0 .5em;font-size:1.01rem;font-weight:600;color:var(--accent);line-height:1.5}
.doc h4{margin:1.6em 0 .4em;font-size:.93rem;font-weight:600;color:var(--ink)}
.doc p{margin:.75em 0}
.doc strong,.doc b{font-weight:600;color:var(--ink)}
.doc a{color:var(--accent);text-underline-offset:3px}
.doc hr{border:0;border-top:1px solid var(--rule);margin:2.6em 0}
.doc ul,.doc ol{padding-left:1.35em;margin:.75em 0}
.doc li{margin:.32em 0}
.doc li::marker{color:var(--muted)}
.doc li.chk{list-style:none;margin-left:-1.35em;padding-left:1.6em;position:relative}
.doc li.chk::before{content:"☐";position:absolute;left:0;color:var(--warn);font-size:1.05em}
.doc li.chk.done::before{content:"☑";color:var(--ok)}
.doc li.chk.done{color:var(--muted)}

.doc blockquote{margin:1.4em 0;padding:.95em 1.15em;background:var(--accent-soft);
  border-left:3px solid var(--accent-line);border-radius:0 6px 6px 0}
.doc blockquote p:first-child{margin-top:0}
.doc blockquote p:last-child{margin-bottom:0}

.doc code{font-family:"IBM Plex Mono",ui-monospace,monospace;font-size:.85em;
  background:var(--codebg);color:var(--ink);padding:.1em .38em;border-radius:4px}
.doc pre{background:var(--prebg);color:var(--prefg);padding:15px 17px;border-radius:9px;
  overflow-x:auto;font-size:.82rem;line-height:1.65;margin:1.3em 0}
.doc pre code{background:none;color:inherit;padding:0;font-size:inherit}

.doc table{border-collapse:collapse;width:100%;font-size:.88rem;margin:0}
.doc th,.doc td{border:1px solid var(--rule);padding:8px 11px;text-align:left;
  vertical-align:top;line-height:1.6}
.doc th{background:var(--sink);color:var(--ink);font-weight:600;white-space:nowrap}
.doc td{font-variant-numeric:tabular-nums}
.tablewrap{overflow-x:auto;margin:1.4em 0;border-radius:8px;box-shadow:var(--shadow);
  background:var(--surface)}

.doc details{margin:1.3em 0;padding:.8em 1.05em;background:var(--surface);
  border:1px solid var(--rule);border-radius:8px}
.doc summary{cursor:pointer;font-weight:600;color:var(--ink);font-size:.92rem}
.doc summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}

.doc .likert{margin:.2em 0 1.15em;padding-left:.2em;color:var(--accent);
  font-size:.94em;word-spacing:.12em;font-variant-numeric:tabular-nums}

/* ── 표지 전용 ──────────────────────────── */
.callout{margin:1.6em 0;padding:1.05em 1.25em;background:var(--accent-soft);
  border:1px solid var(--accent-line);border-radius:9px}
.callout.warn{background:var(--warn-soft);border-color:var(--warn)}
.calloutlab{margin:0 0 .45em!important;font-size:.7rem;font-weight:700;letter-spacing:.1em;
  color:var(--accent)}
.callout.warn .calloutlab{color:var(--warn)}
.callout p:last-child{margin-bottom:0}

.modelwrap{margin:1.5em 0}
.model{display:flex;align-items:stretch;gap:10px;flex-wrap:wrap}
.mcol{flex:1 1 170px;min-width:0;display:flex;flex-direction:column;gap:6px}
.mrole{margin:0!important;font-size:.69rem;font-weight:600;letter-spacing:.1em;color:var(--muted)}
.mbox{flex:1;background:var(--surface);border:1px solid var(--rule);border-radius:8px;
  padding:12px 14px;display:flex;flex-direction:column;gap:3px;box-shadow:var(--shadow)}
.mbox b{color:var(--ink);font-size:.95rem;line-height:1.4}
.mbox span{font-size:.79rem;color:var(--muted);line-height:1.5}
.marrow{align-self:center;color:var(--accent);font-size:1.3rem;flex:none;padding-top:1.1em}
.mods{margin-top:12px;display:flex;gap:10px;flex-wrap:wrap}
.mods .mrole{flex-basis:100%;margin-bottom:-2px!important}
.mbox.mod{flex:1 1 210px;border-style:dashed;border-color:var(--accent-line);box-shadow:none}

.note{font-size:.87rem;color:var(--muted);line-height:1.7}
.note b{color:var(--ink)}

.steps{list-style:none;padding:0!important;margin:1.2em 0!important;display:grid;gap:8px;
  counter-reset:step}
.steps li{margin:0;position:relative;padding:9px 13px 9px 42px;border-radius:8px;
  background:var(--surface);border:1px solid var(--rule);counter-increment:step;
  font-size:.92rem;line-height:1.6}
.steps li::before{content:counter(step);position:absolute;left:13px;top:9px;
  width:20px;height:20px;border-radius:50%;background:var(--sink);color:var(--muted);
  font-size:.72rem;font-weight:700;display:grid;place-items:center}
.steps li.done{color:var(--muted)}
.steps li.done::before{content:"✓";background:var(--ok-soft);color:var(--ok)}
.steps li.now{border-color:var(--warn);background:var(--warn-soft)}
.steps li.now::before{background:var(--warn);color:var(--surface)}

.legend{list-style:none;padding:0!important;display:grid;gap:9px;margin:1em 0!important}
.legend li{margin:0;font-size:.89rem;line-height:1.65}
.legend .chip{margin-right:5px;vertical-align:1px}

/* ── 좁은 화면 ──────────────────────────── */
@media (max-width:900px){
  .shell{grid-template-columns:1fr}
  .rail{position:sticky;top:0;max-height:none;border-right:0;
    border-bottom:1px solid var(--rule);padding-block:14px;z-index:5;
    padding-top:calc(14px + env(safe-area-inset-top,0px))}
  .brandsub{display:none}
  .brand{margin-bottom:10px;font-size:.98rem}
  .navhead{display:none}
  .navlist{display:flex;gap:6px;overflow-x:auto;padding-bottom:3px}
  .navlist+.navhead+.navlist{margin-top:6px}
  .navitem{width:auto;white-space:nowrap;border:1px solid var(--rule);padding:5px 11px}
  .navitem.on{box-shadow:none;border-color:var(--accent-line)}
  .navitem .chip{display:none}
  .stage{padding-block:26px 90px}
  .marrow{display:none}
  .model{flex-direction:column}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media print{
  .rail{display:none}.shell{display:block}.stage{padding:0}
  body{background:#fff;font-size:10.5pt}
  .doc h2{page-break-after:avoid}.doc table,.doc blockquote{page-break-inside:avoid}
}
"""

JS = r"""
(function(){
  var stage = document.querySelector('.stage');
  var items = Array.prototype.slice.call(document.querySelectorAll('.navitem'));
  var KEY = 'thesis-doc';
  var built = {};

  function dress(pane){
    // 넓은 표는 표 안에서만 가로로 밀리게 감싼다 (페이지가 옆으로 새지 않도록)
    pane.querySelectorAll('table').forEach(function(t){
      if (t.parentElement && t.parentElement.classList.contains('tablewrap')) return;
      var w = document.createElement('div');
      w.className = 'tablewrap';
      t.parentNode.insertBefore(w, t);
      w.appendChild(t);
    });
  }

  function ensure(id){
    if (built[id]) return built[id];
    var el = document.getElementById(id);
    if (!el){
      var tpl = document.querySelector('template[data-pane="' + id + '"]');
      if (!tpl) return null;
      el = tpl.content.firstElementChild.cloneNode(true);
      dress(el);
      stage.appendChild(el);
    }
    built[id] = el;
    return el;
  }

  function show(id, remember){
    var el = ensure(id);
    if (!el) return;
    stage.querySelectorAll('.pane').forEach(function(p){ p.hidden = (p !== el); });
    items.forEach(function(b){
      var on = b.dataset.t === id;
      b.classList.toggle('on', on);
      b.setAttribute('aria-current', on ? 'page' : 'false');
    });
    window.scrollTo(0, 0);
    if (stage.scrollTop) stage.scrollTop = 0;
    if (remember){ try { localStorage.setItem(KEY, id); } catch (e) {} }
  }

  items.forEach(function(b){
    b.addEventListener('click', function(){ show(b.dataset.t, true); });
  });

  dress(document.getElementById('cover'));
  try {
    var last = localStorage.getItem(KEY);
    if (last && last !== 'cover' &&
        document.querySelector('template[data-pane="' + last + '"]')) show(last, false);
  } catch (e) {}
})();
"""

page = f"""<title>소방 안전행동 연구 문서함</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Sans+KR:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
<div class="shell">
  <nav class="rail" aria-label="문서 목록">
    <span class="brand">소방공무원 통제위치 ·<br>안전시민행동 연구</span>
    <p class="brandsub">박사학위논문 작업 문서. 설문 배포 직전 단계.</p>
    {''.join(nav)}
  </nav>
  <main class="stage">
    {COVER}
    {''.join(panes)}
  </main>
</div>
<script>{JS}</script>
"""

OUT.write_text(page, encoding="utf-8")
print(f"생성: {OUT}  ({len(page):,} chars, 문서 {len(panes)}개)")
