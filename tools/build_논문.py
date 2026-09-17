#!/usr/bin/env python3
"""장별 초고를 한 편의 논문으로 이어 붙인다.

    python3 tools/build_논문.py docs/논문초고/_논문_전체.md

각 장 파일 맨 위의 작업용 안내 상자(> ⚠️ 초고이다 …)는 떼어내고,
표지·목차·초록 자리·참고문헌을 붙여 하나의 문서로 만든다.

장을 고쳤으면 이 스크립트를 다시 돌려 합본을 갱신한다.
"""
import io
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs/논문초고/_논문_전체.md"

CHAPTERS = [
    "docs/논문초고/제1장_서론.md",
    "docs/논문초고/제2장_이론적배경및가설설정.md",
    "docs/논문초고/제3장_연구모형및연구방법.md",
    "docs/논문초고/제4장_제5장_틀.md",
]


def strip_workbox(md: str) -> tuple[str, str]:
    """맨 앞 H1 제목과, 그 뒤에 붙은 작업용 인용 상자를 떼어낸다."""
    lines = md.split("\n")
    title, i = None, 0
    for i, ln in enumerate(lines):
        if ln.startswith("# "):
            title = ln[2:].strip()
            i += 1
            break
    body = lines[i:]
    # 제목 바로 뒤의 인용 상자(>)와 구분선(---)을 건너뛴다
    j = 0
    while j < len(body) and (not body[j].strip() or body[j].startswith(">")):
        j += 1
    while j < len(body) and body[j].strip() in ("---", ""):
        j += 1
    return title or "", "\n".join(body[j:]).rstrip()


def strip_tail(md: str) -> str:
    """꼬리말(*작성 …*)과 '연구자가 채워야 할 것' 표를 떼어낸다."""
    md = re.sub(r"\n---\n+\*작성[^\n]*\*\s*$", "", md)
    md = re.sub(r"\n#{2,3} ▣ [^\n]*\n(?:.*\n)*?(?=\n---\n|\Z)", "\n", md)
    return md.rstrip()


parts = []
todo = []          # ▣ 로 표시된 미완 항목을 모아 뒤에 부록으로 붙인다

for rel in CHAPTERS:
    p = ROOT / rel
    if not p.exists():
        print(f"  ⚠️ 없음, 건너뜀: {rel}")
        continue
    raw = p.read_text(encoding="utf-8")
    title, body = strip_workbox(raw)
    body = strip_tail(body)
    # 4·5장 파일은 본문 안에 자체 H1(제4장/제5장)을 갖고 있다.
    # 래퍼 제목("제4장·제5장 — 틀")을 쓰면 제목이 겹치므로 버린다.
    if body.lstrip().startswith("# "):
        title = None
    parts.append((title, body, rel))
    for m in re.finditer(r"▣\s*\*?\(?([^\n)*]{10,120})", body):
        todo.append((title or "제4·5장", m.group(1).strip()))

TITLE_KO = "소방공무원의 통제위치가 안전시민행동에 미치는 영향"
SUB_KO = "피드백 추구행동의 매개효과와 지각된 실책관리풍토·직무경력의 조절효과"
TITLE_EN = ("The Effect of Locus of Control on Safety Citizenship Behavior "
            "among Firefighters")
SUB_EN = ("The Mediating Role of Feedback-Seeking Behavior and the Moderating "
          "Effects of Perceived Error Management Climate and Job Tenure")

head = f"""# {TITLE_KO}

### {SUB_KO}

**{TITLE_EN}:**
*{SUB_EN}*

---

> # ⚠️ 이것은 초고이다
>
> 지도교수 검토를 받지 않았다. **논문에 그대로 옮기지 말고 반드시 수정하라.**
>
> **제4장과 제5장은 본문을 쓰지 않았다.** 설문을 아직 돌리지 않아 결과가 없기
> 때문이다. 지금 쓰면 없는 결과를 지어내는 것이 된다. 대신 **표의 뼈대와 채울
> 자리**를 만들어 두었다. 자료가 들어오면 그 자리에 수치를 넣으면 된다.
>
> **`▣` 로 표시한 곳**은 연구자가 직접 확인해 채워야 하는 부분이다.
> 확인하지 않은 통계 수치나 미검증 문헌을 넣으면 심사에서 치명적이다.
> 전체 목록을 문서 맨 뒤 「채워야 할 것」에 모아 두었다.
>
> **인용 규칙** — 본문의 영문 문헌은 모두 서지 검증(Crossref DOI 대조)을 마쳤다.
> 다만 구체적 수치(상관계수·α·표본 수)를 인용할 때에는 원문을 직접 확인해야 한다.
> **국내 문헌은 아직 넣지 않았다.** KCI 원문 확인 전에는 인용하지 않는다.

---

## 국문초록

> ▣ *(연구가 끝난 뒤 마지막에 작성한다. 통상 A4 1~2쪽.
> 연구목적 → 연구방법 → 주요 결과 → 시사점 순으로 쓴다.
> 결과가 나와야 쓸 수 있으므로 지금은 비워 둔다.)*

**주제어**: 소방공무원, 통제위치, 피드백 추구행동, 지각된 실책관리풍토,
직무경력, 안전시민행동

---

## ABSTRACT

> ▣ *(국문초록을 작성한 뒤 번역한다.)*

**Keywords**: firefighters, locus of control, feedback-seeking behavior,
perceived error management climate, job tenure, safety citizenship behavior

---

## 목 차

"""

# 목차 — 각 장의 H2·H3 를 긁어 만든다
toc = []
for title, body, _ in parts:
    if title:
        toc.append(f"### {title}\n")
    for ln in body.split("\n"):
        if ln.startswith("# ") and not ln.startswith("##"):
            toc.append(f"\n### {ln[2:].strip()}\n")
        elif ln.startswith("## ") and not ln.startswith("###"):
            toc.append(f"- {ln[3:].strip()}")
        elif ln.startswith("### "):
            toc.append(f"  - {ln[4:].strip()}")
    toc.append("")
head += "\n".join(toc) + "\n---\n\n"

body_all = []
for title, body, rel in parts:
    body_all.append((f"# {title}\n\n{body}" if title else body) + "\n\n---\n")

# 채워야 할 것
todo_lines = ["# 부록 A. 채워야 할 것 — 연구자 확인 사항\n",
              "> `▣` 로 표시한 자리를 모은 것이다. **확인하지 않은 수치나 미검증 문헌을",
              "> 넣으면 안 된다.** 확인할 곳을 함께 적었다.\n",
              "| 장 | 채워야 할 것 |", "|---|---|"]
seen = set()
for ch, item in todo:
    item = re.sub(r"\s+", " ", item).strip().rstrip("*)")
    key = (ch, item[:40])
    if key in seen:
        continue
    seen.add(key)
    todo_lines.append(f"| {ch} | {item} |")

todo_lines += ["""
## 자료 수집 후에 채울 것

| 위치 | 내용 |
|---|---|
| 국문초록 · ABSTRACT | 결과가 나온 뒤 마지막에 작성 |
| 제3장 자료수집 | 조사기간 · 배포 부수 · 회수 부수 · 최종 분석 표본 |
| 제4장 전체 | 모든 표의 빈칸 — SPSS 출력을 옮긴다 |
| 제5장 5.1 · 5.2 | 결과 요약과 시사점 — 결과를 보고 쓴다 |

> **제4장을 채우는 순서**는 문서함 → 「지금 — 설문 배포 전」 → 「SPSS 분석 절차」에
> 단계별로 적어 두었다. 메뉴 경로와 구문을 그대로 따라 하면 된다.

## 반드시 먼저 구해야 할 논문 두 편

지도교수 연구실이 본 연구와 **같은 변수**를 이미 다루었다. 측정문항과 신뢰도를
확인해야 하며, 문체를 맞추는 데에도 필요하다.

- **이미희 · 신호철** — 포용적 리더십이 구성원의 혁신행동에 미치는 영향:
  LMX의 매개효과와 **지각된 실책관리풍토**의 조절효과
- **이원재 · 신호철** (2025) — 상사의 코칭 행동이 직원열의에 미치는 영향:
  권력거리 성향의 조절효과 및 심리적 안전감과 **피드백 추구 행동**의 매개효과
"""]

refs = """
# 참고문헌

> **아래는 서지 검증(Crossref DOI 대조)을 마친 문헌만 담았다.**
> 본문에서 인용한 것과 일치해야 한다. 최종 제출 전에 대조할 것.
>
> ⚠️ **국내 문헌이 아직 없다.** 학위논문으로서 국내 선행연구 인용이 반드시 필요하다.
> KCI 원문을 직접 확인한 뒤 추가한다.

Anseel, F., Beatty, A. S., Shen, W., Lievens, F., & Sackett, P. R. (2015). How are
    we doing after 30 years? A meta-analytic review of the antecedents and outcomes
    of feedback-seeking behavior. *Journal of Management, 41*(1), 318–348.
    https://doi.org/10.1177/0149206313484521

Ashford, S. J. (1986). Feedback-seeking in individual adaptation: A resources
    perspective. *Academy of Management Journal, 29*(3), 465–487.
    https://doi.org/10.2307/256219

Ashford, S. J., & Cummings, L. L. (1983). Feedback as an individual resource:
    Personal strategies of creating information. *Organizational Behavior and Human
    Performance, 32*(3), 370–398. https://doi.org/10.1016/0030-5073(83)90156-3

Ashford, S. J., De Stobbeleir, K., & Nujella, M. (2016). To seek or not to seek:
    Is that the only question? Recent developments in feedback-seeking literature.
    *Annual Review of Organizational Psychology and Organizational Behavior, 3*(1),
    213–239. https://doi.org/10.1146/annurev-orgpsych-041015-062314

Ashford, S. J., & Tsui, A. S. (1991). Self-regulation for managerial effectiveness:
    The role of active feedback seeking. *Academy of Management Journal, 34*(2),
    251–280. https://doi.org/10.2307/256442

Breslin, F. C., Dollack, J., Mahood, Q., Maas, E. T., & Laberge, M. (2019). Are new
    workers at elevated risk for work injury? A systematic review. *Occupational and
    Environmental Medicine, 76*(9), 694–701.
    https://doi.org/10.1136/oemed-2018-105639

Breslin, F. C., & Smith, P. (2006). Trial by fire: A multivariate examination of the
    relation between job tenure and work injuries. *Occupational and Environmental
    Medicine, 63*(1), 27–32. https://doi.org/10.1136/oem.2005.021006

Cigularov, K. P., Chen, P. Y., & Rosecrance, J. (2010). The effects of error
    management climate and safety communication on safety: A multi-level study.
    *Accident Analysis & Prevention, 42*(5), 1498–1506.
    https://doi.org/10.1016/j.aap.2010.01.003

Feldman, D. C. (1976). A contingency theory of socialization. *Administrative
    Science Quarterly, 21*(3), 433–452.

Gould, S., & Hawkins, B. L. (1978). Organizational career stage as a moderator of
    the satisfaction-performance relationship. *Academy of Management Journal,
    21*(3), 434–450. https://doi.org/10.2307/255725

Griffin, M. A., & Neal, A. (2000). Perceptions of safety at work: A framework for
    linking safety climate to safety performance, knowledge, and motivation.
    *Journal of Occupational Health Psychology, 5*(3), 347–358.

Gupta, S., & Prashar, A. (2026). Meta-analytic review of role of career stage in
    newcomers' socialization: Beyond stages model of organizational-socialization.
    *Human Resource Development Review*.
    https://doi.org/10.1177/15344843261435287

Hofmann, D. A., Morgeson, F. P., & Gerras, S. J. (2003). Climate as a moderator of
    the relationship between leader-member exchange and content specific
    citizenship: Safety climate as an exemplar. *Journal of Applied Psychology,
    88*(1), 170–178. https://doi.org/10.1037/0021-9010.88.1.170

Meng, X., & Chan, A. H. S. (2020). Demographic influences on safety consciousness
    and safety citizenship behavior of construction workers. *Safety Science, 129*,
    104835. https://doi.org/10.1016/j.ssci.2020.104835

Morrison, E. W. (1993). Newcomer information seeking: Exploring types, modes,
    sources, and outcomes. *Academy of Management Journal, 36*(3), 557–589.
    https://doi.org/10.2307/256592

Murphy, L. A., Huang, Y. H., Lee, J., Robertson, M. M., & Jeffries, S. (2019). The
    moderating effect of long-haul truck drivers' occupational tenure on the
    relationship between safety climate and driving safety behavior. *Safety
    Science, 120*, 283–289. https://doi.org/10.1016/j.ssci.2019.07.003

Neal, A., & Griffin, M. A. (2006). A study of the lagged relationships among safety
    climate, safety motivation, safety behavior, and accidents at the individual and
    group levels. *Journal of Applied Psychology, 91*(4), 946–953.

Ng, T. W. H., & Feldman, D. C. (2010). Organizational tenure and job performance.
    *Journal of Management, 36*(5), 1220–1250.
    https://doi.org/10.1177/0149206309359809

Nykänen, M., Salmela-Aro, K., Tolvanen, A., & Vuori, J. (2019). Safety self-efficacy
    and internal locus of control as mediators of safety motivation — Randomized
    controlled trial (RCT) study. *Safety Science, 117*, 330–338.
    https://doi.org/10.1016/j.ssci.2019.04.037

Podsakoff, P. M., MacKenzie, S. B., Lee, J. Y., & Podsakoff, N. P. (2003). Common
    method biases in behavioral research: A critical review of the literature and
    recommended remedies. *Journal of Applied Psychology, 88*(5), 879–903.

Rotter, J. B. (1954). *Social learning and clinical psychology.* Prentice-Hall.
    https://doi.org/10.1037/10788-000

Rotter, J. B. (1966). Generalized expectancies for internal versus external control
    of reinforcement. *Psychological Monographs: General and Applied, 80*(1), 1–28.
    https://doi.org/10.1037/h0092976

Rybowiak, V., Garst, H., Frese, M., & Batinic, B. (1999). Error Orientation
    Questionnaire (EOQ): Reliability, validity, and different language equivalence.
    *Journal of Organizational Behavior, 20*(4), 527–547.

Siemsen, E., Roth, A., & Oliva, R. (2010). Common method bias in regression models
    with linear, quadratic, and interaction effects. *Organizational Research
    Methods, 13*(3), 456–476.

Spector, P. E. (1988). Development of the Work Locus of Control Scale. *Journal of
    Occupational Psychology, 61*(4), 335–340.

Super, D. E. (1980). A life-span, life-space approach to career development.
    *Journal of Vocational Behavior, 16*(3), 282–298.
    https://doi.org/10.1016/0001-8791(80)90056-1

van Dyck, C., Frese, M., Baer, M., & Sonnentag, S. (2005). Organizational error
    management culture and its impact on performance: A two-study replication.
    *Journal of Applied Psychology, 90*(6), 1228–1240.
    https://doi.org/10.1037/0021-9010.90.6.1228

Weick, K. E. (1993). The collapse of sensemaking in organizations: The Mann Gulch
    disaster. *Administrative Science Quarterly, 38*(4), 628–652.

You, X., Ji, M., & Han, H. (2013). The effects of risk perception and flight
    experience on airline pilots' locus of control with regard to safety operation
    behaviors. *Accident Analysis & Prevention, 57*, 131–139.
    https://doi.org/10.1016/j.aap.2013.03.036

---

# 부록 B. 설문지

> 전문은 문서함 → 「지금 — 설문 배포 전」 → 「설문지 배포본」에 있다.
> 최종 제출 시 이 자리에 붙여 넣는다.
>
> 연구 변수 **52문항** — 통제위치 16 · 피드백 추구행동 10 ·
> 지각된 실책관리풍토 8 · 안전시민행동 18. 전 척도 5점이되 안전시민행동만 빈도형.

---
"""

doc = head + "\n".join(body_all) + "\n" + "\n".join(todo_lines) + "\n\n---\n" + refs
doc += f"\n*합본 생성 — `tools/build_논문.py`. 장을 고치면 다시 돌려 갱신할 것.*\n"

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(doc, encoding="utf-8")
print(f"생성: {OUT}  ({len(doc):,} chars · 장 {len(parts)}개 · ▣ {len(seen)}건)")
