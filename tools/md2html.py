#!/usr/bin/env python3
"""마크다운 문서를 옆 패널에서 바로 열리는 HTML 로 변환한다.

마크다운 파일(.md)은 미리보기가 안 되고 내려받기만 뜨는 환경이 있어,
읽어야 할 문서는 HTML 로 만들어 전달한다. 인쇄도 깔끔하게 된다.

사용법
    python3 tools/md2html.py survey/02_설문지_배포본.md
    python3 tools/md2html.py docs/06_교수님_재승인_안건.md -o /tmp/안건.html
    python3 tools/md2html.py docs/*.md -d /tmp/html/      # 여러 개 한꺼번에

변환본은 저장소에 커밋하지 않는다. 원본은 `.md` 하나뿐이어야 한다.
"""
import argparse
import html
import pathlib
import re

CSS = """
:root{--fg:#1a1a1a;--muted:#5c5c5c;--line:#e0ddd6;--bg:#fdfcfa;--accent:#8b5e34;
      --mark:#fff8e6;--markline:#e8c97a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
     font-family:"Pretendard","Apple SD Gothic Neo","Malgun Gothic",-apple-system,sans-serif;
     line-height:1.75;font-size:16px}
.wrap{max-width:820px;margin:0 auto;padding:48px 24px 96px}
h1{font-size:1.75rem;line-height:1.35;margin:0 0 .5em;letter-spacing:-.02em}
h2{font-size:1.3rem;margin:2.2em 0 .7em;padding-bottom:.35em;
   border-bottom:2px solid var(--line);letter-spacing:-.01em}
h3{font-size:1.08rem;margin:1.8em 0 .5em;color:var(--accent)}
h4{font-size:1rem;margin:1.4em 0 .4em}
p{margin:.7em 0}
hr{border:0;border-top:1px solid var(--line);margin:2.2em 0}
table{border-collapse:collapse;width:100%;margin:1.1em 0;font-size:.93rem}
th,td{border:1px solid var(--line);padding:9px 11px;text-align:left;vertical-align:top}
th{background:#f4f1ea;font-weight:600}
tr:nth-child(even) td{background:#faf8f4}
blockquote{margin:1.2em 0;padding:.9em 1.1em;background:var(--mark);
           border-left:4px solid var(--markline);border-radius:0 6px 6px 0}
blockquote p:first-child{margin-top:0}blockquote p:last-child{margin-bottom:0}
code{background:#f0ede6;padding:.12em .4em;border-radius:4px;font-size:.88em;
     font-family:"SF Mono",Menlo,Consolas,monospace}
pre{background:#2d2a26;color:#f0ede6;padding:14px 16px;border-radius:8px;
    overflow-x:auto;font-size:.85rem;line-height:1.6}
pre code{background:none;color:inherit;padding:0}
strong{font-weight:700}
ul,ol{padding-left:1.4em;margin:.7em 0}
li{margin:.3em 0}
.likert{font-size:1.05em;letter-spacing:.35em;color:#444}
@media print{body{background:#fff;font-size:11pt}.wrap{padding:0;max-width:none}
  h2{page-break-after:avoid}table,blockquote{page-break-inside:avoid}}
@media (prefers-color-scheme:dark){
  :root{--fg:#e8e6e1;--muted:#a09a90;--line:#3a3632;--bg:#1c1a18;--accent:#d4a574;
        --mark:#2e2822;--markline:#7a6032}
  th{background:#28241f}tr:nth-child(even) td{background:#221f1c}
  code{background:#2a2622}}
"""

def md2html(md: str) -> str:
    out, i, lines = [], 0, md.split("\n")
    while i < len(lines):
        ln = lines[i]
        # 코드블록
        if ln.startswith("```"):
            j = i + 1
            buf = []
            while j < len(lines) and not lines[j].startswith("```"):
                buf.append(html.escape(lines[j])); j += 1
            out.append("<pre><code>" + "\n".join(buf) + "</code></pre>")
            i = j + 1; continue
        # 표
        if ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:\-|]+\|$", lines[i+1]):
            hdr = [c.strip() for c in ln.strip("|").split("|")]
            rows, j = [], i + 2
            while j < len(lines) and lines[j].startswith("|"):
                rows.append([c.strip() for c in lines[j].strip("|").split("|")]); j += 1
            t = ["<table><thead><tr>"] + [f"<th>{inline(c)}</th>" for c in hdr] + ["</tr></thead><tbody>"]
            for r in rows:
                t += ["<tr>"] + [f"<td>{inline(c)}</td>" for c in r] + ["</tr>"]
            out.append("".join(t) + "</tbody></table>"); i = j; continue
        # 인용
        if ln.startswith(">"):
            buf, j = [], i
            while j < len(lines) and lines[j].startswith(">"):
                buf.append(lines[j].lstrip(">").strip()); j += 1
            inner = md2html("\n".join(buf))
            out.append(f"<blockquote>{inner}</blockquote>"); i = j; continue
        # 제목
        m = re.match(r"^(#{1,4})\s+(.*)", ln)
        if m:
            lv = len(m.group(1)); out.append(f"<h{lv}>{inline(m.group(2))}</h{lv}>"); i += 1; continue
        # 구분선
        if re.match(r"^-{3,}$", ln.strip()):
            out.append("<hr>"); i += 1; continue
        # 번호 목록
        if re.match(r"^\s*\d+\.\s+", ln):
            buf, j = [], i
            while j < len(lines) and re.match(r"^\s*\d+\.\s+", lines[j]):
                buf.append(re.sub(r"^\s*\d+\.\s+", "", lines[j])); j += 1
            out.append("<ol>" + "".join(f"<li>{inline(b)}</li>" for b in buf) + "</ol>")
            i = j; continue
        # 목록
        if re.match(r"^\s*[-*]\s+", ln):
            buf, j = [], i
            while j < len(lines) and re.match(r"^\s*[-*]\s+", lines[j]):
                buf.append(re.sub(r"^\s*[-*]\s+", "", lines[j])); j += 1
            out.append("<ul>" + "".join(f"<li>{inline(b)}</li>" for b in buf) + "</ul>")
            i = j; continue
        if ln.strip():
            cls = ' class="likert"' if ln.strip().startswith("① ② ③") or "　① ② ③" in ln else ""
            out.append(f"<p{cls}>{inline(ln)}</p>")
        i += 1
    return "\n".join(out)


def inline(t: str) -> str:
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"~~([^~]+)~~", r"<del>\1</del>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t.replace("&lt;br&gt;", "<br>").replace("&lt;sub&gt;", "<sub>").replace("&lt;/sub&gt;", "</sub>")


def render(p: pathlib.Path) -> str:
    md = p.read_text(encoding="utf-8")
    title = next((l.lstrip("# ").strip() for l in md.split("\n") if l.startswith("# ")), p.stem)
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>{html.escape(title)}</title><style>{CSS}</style></head>"
            f'<body><div class="wrap">{md2html(md)}</div></body></html>')


def main():
    ap = argparse.ArgumentParser(description="마크다운을 옆 패널에서 열리는 HTML 로 변환한다.")
    ap.add_argument("src", nargs="+", help="변환할 .md 파일 (여러 개 가능)")
    ap.add_argument("-o", "--out", help="출력 파일 경로 (입력이 하나일 때만)")
    ap.add_argument("-d", "--outdir", help="출력 폴더 (여러 개를 한꺼번에 변환할 때)")
    a = ap.parse_args()

    srcs = [pathlib.Path(s) for s in a.src]
    if a.out and len(srcs) > 1:
        ap.error("-o 는 입력이 하나일 때만 쓴다. 여러 개면 -d 를 써라.")
    outdir = pathlib.Path(a.outdir) if a.outdir else None
    if outdir:
        outdir.mkdir(parents=True, exist_ok=True)

    for p in srcs:
        doc = render(p)
        if a.out:
            out = pathlib.Path(a.out)
        elif outdir:
            out = outdir / (p.stem + ".html")
        else:
            out = p.with_suffix(".html")
        out.write_text(doc, encoding="utf-8")
        print(f"생성: {out}  ({len(doc):,} bytes)")


if __name__ == "__main__":
    main()
