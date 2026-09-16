#!/usr/bin/env python3
"""연구 문서들을 한 페이지짜리 아티팩트로 묶는다.

옆 패널에서 바로 열리는 「연구 문서함」 페이지를 만든다.
웹(claude.ai)에서는 파일을 보내면 내려받기 카드로만 뜨므로,
읽을 문서는 이렇게 묶어 아티팩트로 올린다.

    python3 tools/build_문서함.py /tmp/문서함.html

만든 뒤에는 **기존 아티팩트를 갱신**한다. 새로 올리면 주소가 바뀐다.
    https://claude.ai/artifact/1QojziYRZ778QiYbw3DLVN
"""
import html
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import md2html as M

# 저장소를 더럽히지 않도록 출력 경로는 반드시 밖으로 받는다.
if len(sys.argv) < 2:
    sys.exit("사용법: python3 tools/build_문서함.py <출력.html>")
OUT = pathlib.Path(sys.argv[1])

# (파일, 구역, 상태라벨, 상태종류)
DOCS = [
    ("docs/06_교수님_재승인_안건.md",            "지금 할 일", "결재 대기", "wait"),
    ("docs/08_연구수행_표준절차_체크리스트.md",  "지금 할 일", "진행 중",   "wait"),
    ("survey/02_설문지_배포본.md",               "설문",       "배포 직전", "hot"),
    ("docs/_확정사항.md",                        "확정·근거",  "확정",      "ok"),
    ("docs/07_직무경력_절단점_근거.md",          "확정·근거",  "근거자료",  "ok"),
    ("docs/09_지도교수_연구분석.md",             "확정·근거",  "서지 확인", "ok"),
    ("docs/용어사전.md",                         "참고",       "참고",      "neutral"),
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
    # 체크박스 목록을 실제 체크 표시로
    body = body.replace("<li>[x] ", '<li class="chk done">').replace("<li>[ ] ", '<li class="chk">')
    body = body.replace("<li>[X] ", '<li class="chk done">')
    return body


def split_title(md: str):
    lines = md.split("\n")
    title, rest = None, []
    for i, ln in enumerate(lines):
        if title is None and ln.startswith("# "):
            title = ln[2:].strip()
            rest = lines[i + 1:]
            break
    return (title or "제목 없음"), "\n".join(rest)


SHORT = {
    "docs/06_교수님_재승인_안건.md": "교수님 재승인 안건",
    "docs/08_연구수행_표준절차_체크리스트.md": "연구 수행 절차 체크리스트",
    "survey/02_설문지_배포본.md": "설문지 배포본",
    "docs/_확정사항.md": "확정사항",
    "docs/07_직무경력_절단점_근거.md": "직무경력 절단점 근거",
    "docs/09_지도교수_연구분석.md": "지도교수 연구 분석",
    "docs/용어사전.md": "용어사전",
}

nav_html, panes, section_now = [], [], None
for n, (rel, section, status, kind) in enumerate(DOCS):
    md = (ROOT / rel).read_text(encoding="utf-8")
    full_title, body_md = split_title(md)
    short = SHORT[rel]
    did = f"d{n}"
    if section != section_now:
        if section_now is not None:
            nav_html.append("</ul>")
        nav_html.append(f'<p class="navhead">{html.escape(section)}</p><ul class="navlist">')
        section_now = section
    nav_html.append(
        f'<li><button class="navitem{" on" if n == 0 else ""}" data-t="{did}" '
        f'aria-current="{"page" if n == 0 else "false"}">'
        f'<span class="navname">{html.escape(short)}</span>'
        f'<span class="chip {kind}">{html.escape(status)}</span></button></li>')
    panes.append(
        f'<article class="pane" id="{did}"{"" if n == 0 else " hidden"}>'
        f'<header class="dochead"><p class="eyebrow">{html.escape(section)} · '
        f'<span class="chip {kind}">{html.escape(status)}</span></p>'
        f'<h1>{html.escape(full_title)}</h1>'
        f'<p class="src">{html.escape(rel)}</p></header>'
        f'<div class="doc">{convert(body_md)}</div></article>')
nav_html.append("</ul>")

CSS = r"""
:root{
  --ground:#eef1f4; --surface:#ffffff; --sink:#e3e8ed;
  --ink:#0f1b24; --body:#30404d; --muted:#65788a; --rule:#d2dae1;
  --accent:#12626f; --accent-soft:#dfeef0; --accent-line:#8fc2c8;
  --warn:#8a5209; --warn-soft:#f8efdd;
  --ok:#1c6b4a;   --ok-soft:#e0f0e8;
  --hot:#8f3520;  --hot-soft:#f8e6e0;
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
  --codebg:#1d2830; --prebg:#0a1016; --prefg:#cfdae3;
  --shadow:0 1px 2px rgba(0,0,0,.4), 0 10px 30px -22px rgba(0,0,0,.9);
}

*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:var(--ground);color:var(--body);
  font-family:"IBM Plex Sans KR",-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;
  font-size:15.5px;line-height:1.78;-webkit-font-smoothing:antialiased}

/* ── 뼈대 ───────────────────────────────── */
.shell{display:grid;grid-template-columns:288px minmax(0,1fr);min-height:100%}

.rail{background:var(--surface);border-right:1px solid var(--rule);
  position:sticky;top:env(safe-area-inset-top,0px);align-self:start;
  max-height:100vh;overflow-y:auto;padding-block:26px 34px;padding-inline:20px}
.brand{display:block;margin:0 0 4px;font-family:"Gowun Batang",serif;
  font-size:1.16rem;font-weight:700;color:var(--ink);letter-spacing:-.01em;line-height:1.35}
.brandsub{margin:0 0 18px;font-size:.76rem;color:var(--muted);line-height:1.6}

.facts{display:grid;gap:1px;background:var(--rule);border:1px solid var(--rule);
  border-radius:7px;overflow:hidden;margin:0 0 22px}
.fact{background:var(--surface);padding:8px 11px;display:flex;justify-content:space-between;
  align-items:baseline;gap:10px}
.fact dt{margin:0;font-size:.74rem;color:var(--muted);letter-spacing:.02em}
.fact dd{margin:0;font-size:.82rem;color:var(--ink);font-weight:600;
  font-variant-numeric:tabular-nums;text-align:right}

.navhead{margin:18px 0 7px;font-size:.68rem;font-weight:600;letter-spacing:.14em;
  color:var(--muted);text-transform:none}
.navhead:first-of-type{margin-top:0}
.navlist{list-style:none;margin:0;padding:0;display:grid;gap:2px}
.navitem{width:100%;display:flex;align-items:center;justify-content:space-between;gap:9px;
  background:none;border:0;border-radius:6px;padding:7px 9px;cursor:pointer;text-align:left;
  font:inherit;font-size:.87rem;color:var(--body);line-height:1.45}
.navitem:hover{background:var(--sink);color:var(--ink)}
.navitem.on{background:var(--accent-soft);color:var(--ink);font-weight:600;
  box-shadow:inset 2px 0 0 var(--accent)}
.navitem:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
.navname{min-width:0}

.chip{flex:none;font-size:.66rem;font-weight:600;letter-spacing:.02em;
  padding:2px 7px;border-radius:999px;white-space:nowrap;
  background:var(--sink);color:var(--muted)}
.chip.ok{background:var(--ok-soft);color:var(--ok)}
.chip.wait{background:var(--warn-soft);color:var(--warn)}
.chip.hot{background:var(--hot-soft);color:var(--hot)}

.stage{padding-block:40px 120px;padding-inline:clamp(16px,4vw,56px);min-width:0}
.pane{max-width:70ch;margin:0 auto}

.dochead{margin:0 0 34px;padding-bottom:20px;border-bottom:2px solid var(--rule)}
.eyebrow{margin:0 0 10px;font-size:.72rem;letter-spacing:.1em;color:var(--muted);
  display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.dochead h1{margin:0;font-family:"Gowun Batang",serif;font-weight:700;color:var(--ink);
  font-size:clamp(1.42rem,1.1rem + 1.3vw,1.95rem);line-height:1.4;letter-spacing:-.015em;
  text-wrap:balance}
.src{margin:12px 0 0;font-family:"IBM Plex Mono",ui-monospace,monospace;
  font-size:.73rem;color:var(--muted)}

/* ── 문서 본문 ──────────────────────────── */
.doc h2{margin:2.5em 0 .7em;font-family:"Gowun Batang",serif;font-size:1.22rem;font-weight:700;
  color:var(--ink);letter-spacing:-.01em;line-height:1.45;text-wrap:balance;
  padding-bottom:.3em;border-bottom:1px solid var(--rule)}
.doc h3{margin:2em 0 .5em;font-size:1.02rem;font-weight:600;color:var(--accent);line-height:1.5}
.doc h4{margin:1.6em 0 .4em;font-size:.93rem;font-weight:600;color:var(--ink);
  letter-spacing:.02em}
.doc p{margin:.75em 0}
.doc strong{font-weight:600;color:var(--ink)}
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

/* 응답 보기 줄: 문항 아래 한 칸 들여 조용하게 */
.doc .likert{margin:.2em 0 1.15em;padding-left:.2em;color:var(--accent);
  font-size:.94em;word-spacing:.12em;font-variant-numeric:tabular-nums}

/* ── 좁은 화면 ──────────────────────────── */
@media (max-width:900px){
  .shell{grid-template-columns:1fr}
  .rail{position:sticky;top:0;max-height:none;border-right:0;
    border-bottom:1px solid var(--rule);padding-block:14px;z-index:5;
    padding-top:calc(14px + env(safe-area-inset-top,0px))}
  .brandsub,.facts{display:none}
  .brand{margin-bottom:10px;font-size:1rem}
  .navhead{display:none}
  .navlist{display:flex;gap:6px;overflow-x:auto;padding-bottom:3px;
    scrollbar-width:thin}
  .navitem{width:auto;white-space:nowrap;border:1px solid var(--rule);padding:5px 11px}
  .navitem.on{box-shadow:none;border-color:var(--accent-line)}
  .navitem .chip{display:none}
  .stage{padding-block:26px 90px}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media print{
  .rail{display:none}.shell{display:block}.stage{padding:0}
  .pane[hidden]{display:block!important}
  body{background:#fff;font-size:10.5pt}
  .doc h2{page-break-after:avoid}.doc table,.doc blockquote{page-break-inside:avoid}
}
"""

JS = r"""
(function(){
  var items = Array.prototype.slice.call(document.querySelectorAll('.navitem'));
  var panes = Array.prototype.slice.call(document.querySelectorAll('.pane'));
  var KEY = 'thesis-doc';

  function show(id, remember){
    panes.forEach(function(p){ p.hidden = (p.id !== id); });
    items.forEach(function(b){
      var on = b.dataset.t === id;
      b.classList.toggle('on', on);
      b.setAttribute('aria-current', on ? 'page' : 'false');
    });
    document.querySelector('.stage').scrollTop = 0;
    window.scrollTo(0, 0);
    if (remember) { try { localStorage.setItem(KEY, id); } catch (e) {} }
  }

  items.forEach(function(b){
    b.addEventListener('click', function(){ show(b.dataset.t, true); });
  });

  try {
    var last = localStorage.getItem(KEY);
    if (last && document.getElementById(last)) show(last, false);
  } catch (e) {}

  // 넓은 표는 가로로만 스크롤되게 감싼다 (페이지 전체가 옆으로 밀리지 않도록)
  document.querySelectorAll('.doc table').forEach(function(t){
    if (t.parentElement && t.parentElement.classList.contains('tablewrap')) return;
    var w = document.createElement('div');
    w.className = 'tablewrap';
    t.parentNode.insertBefore(w, t);
    w.appendChild(t);
  });
})();
"""

page = f"""<title>소방 안전행동 연구 문서함</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Gowun+Batang:wght@400;700&family=IBM+Plex+Sans+KR:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
<div class="shell">
  <nav class="rail" aria-label="문서 목록">
    <span class="brand">소방공무원 통제위치·<br>안전시민행동 연구</span>
    <p class="brandsub">박사학위논문 작업 문서. 설문 배포 직전 단계.</p>
    <dl class="facts">
      <div class="fact"><dt>연구 변수 문항</dt><dd>58</dd></div>
      <div class="fact"><dt>평정 문항 합계</dt><dd>63</dd></div>
      <div class="fact"><dt>응답 척도</dt><dd>5점</dd></div>
      <div class="fact"><dt>안전시민행동</dt><dd>6차원 × 3</dd></div>
      <div class="fact"><dt>배포 차단 요건</dt><dd>결재 1건</dd></div>
    </dl>
    {''.join(nav_html)}
  </nav>
  <main class="stage">
    {''.join(panes)}
  </main>
</div>
<script>{JS}</script>
"""

OUT.write_text(page, encoding="utf-8")
print(f"생성: {OUT}  ({len(page):,} chars)")
