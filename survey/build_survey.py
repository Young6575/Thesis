#!/usr/bin/env python3
"""설문지 배포본 생성기.

item_bank.json 을 단일 원천(single source of truth)으로 삼아
배포용 설문지 마크다운을 생성한다.

문항을 수정할 때는 item_bank.json 만 고치고 이 스크립트를 다시 돌린다.
    python3 survey/build_survey.py

옵션:
    --shuffle   척도 문항을 변수 블록 없이 무작위 배치 (공통방법편향 완화용)
                재현성을 위해 --seed 로 난수 시드를 고정한다.
    --with-proposed
                교수님 검토 대기 중인 제안 문항을
                포함한 검토용 설문지를 생성한다. 확정본에는 포함되지 않는다.
"""
import argparse
import json
import pathlib
import random

HERE = pathlib.Path(__file__).parent
BANK = HERE / "item_bank.json"

TITLE = "소방공무원의 통제위치가 안전시민행동에 미치는 영향에 관한 연구"

CONSENT = """\
## 연구 참여 안내 및 동의

안녕하십니까.

본 설문은 **소방공무원의 개인 특성(통제위치)이 안전시민행동에 미치는 영향**과,
그 과정에서 **피드백 추구행동**, **지각된 실책관리풍토**, **직무경력**이 어떤 역할을 하는지
알아보기 위한 박사학위논문 연구의 일환으로 실시됩니다.

- 본 설문에는 **옳고 그른 답이 없습니다.** 평소 느끼시는 대로 솔직하게 응답해 주시면 됩니다.
- 응답 내용은 **통계법 제33조**에 따라 익명으로 처리되며, **연구 목적 외에는 사용되지 않습니다.**
- 성명·연락처 등 **개인을 식별할 수 있는 정보는 수집하지 않습니다.**
- 소속(소방서·센터)을 여쭙는 문항이 있으나, 이는 **집단 단위 통계 분석에만** 사용되며
  개인이나 특정 관서를 식별하는 데 사용되지 않습니다.
- 참여는 자발적이며, 응답 도중 언제든지 중단하실 수 있습니다.
- 소요 시간은 약 **12~15분**입니다.

바쁘신 중에도 시간을 내어 주셔서 진심으로 감사드립니다.

> ☐ 위 내용을 이해하였으며, 연구 참여에 동의합니다.  **(동의하셔야 설문이 진행됩니다)**

---
"""

DEMOGRAPHICS = """\
## Ⅰ. 일반적 사항

해당하는 곳에 표시해 주십시오.

**Q1.** 귀하의 성별은?
　① 남성　② 여성

**Q2.** 귀하의 연령은?
　① 20대　② 30대　③ 40대　④ 50대 이상

**Q2-1.** 만 ( ______ )세

**Q3.** 귀하의 계급은?
　① 소방사　② 소방교　③ 소방장　④ 소방위　⑤ 소방경 이상

**Q4.** 귀하의 주된 근무 분야는?
　① 화재진압　② 구급　③ 구조　④ 기타( 　　　　　 )

**Q5.** 귀하의 소방 분야 **총 근무경력**은 얼마입니까?
　① 5년 이하　② 6년 ~ 15년　③ 16년 이상

**Q5-1.** 위 경력을 연 단위로 적어 주십시오.　( ______ )년 ( ______ )개월

**Q6.** 귀하의 현재 근무 형태는?
　① 3교대　② 2교대　③ 일근(주간)　④ 기타( 　　　　　 )

**Q7.** 최근 1년간 귀하의 **월평균 출동 횟수**는?
　① 10회 미만　② 10~29회　③ 30~49회　④ 50회 이상

**Q7-1.** 귀하가 근무하시는 소방서와 119안전센터(또는 구조대·구급대)를 적어 주십시오.
　　소방서: ____________________　　센터/대: ____________________

> 이 항목은 **집단 단위 통계 분석에만** 사용되며, 개인을 특정하는 데 사용되지 않습니다.

---
"""

LIKERT = """\
> **응답 방법**  다음 문항들을 읽고 평소 생각과 가장 가까운 곳에 표시해 주십시오.
>
> | ① | ② | ③ | ④ | ⑤ |
> |---|---|---|---|---|
> | 전혀 그렇지 않다 | 그렇지 않다 | 보통이다 | 그렇다 | 매우 그렇다 |
"""

# 안전시민행동은 원척도(Hofmann et al., 2003)에 맞추어 빈도형으로 측정한다.
# 태도가 아니라 '행동을 얼마나 자주 하는가'를 재는 개념이기 때문이다.
LIKERT_FREQ = """\
> **응답 방법**  **최근 1년간** 귀하가 실제로 **얼마나 자주** 하셨는지 표시해 주십시오.
>
> | ① | ② | ③ | ④ | ⑤ |
> |---|---|---|---|---|
> | 전혀 하지 않는다 | 드물게 한다 | 가끔 한다 | 자주 한다 | 항상 한다 |
"""

# 척도별 응답 형식
SCALE_ANCHOR = {"SCB": LIKERT_FREQ}

SECTIONS = [
    ("LOC", "Ⅱ. 업무와 관련된 생각",
     "다음은 **일과 직장에 대한 일반적인 생각**을 묻는 문항입니다."),
    ("FSB", "Ⅲ. 업무 수행과 피드백",
     "다음은 귀하가 **상사로부터 업무에 대한 피드백을 구하는 정도**를 묻는 문항입니다.\n"
     "여기서 **상사**란 출동 현장에서 귀하가 직접 지휘를 받는 팀장 또는 선임을 의미합니다."),
    ("EMC", "Ⅳ. 조직의 실수 관리 분위기",
     "다음은 귀하가 **소속 조직(119안전센터·구조대·구급대 등 근무 단위)의**\n"
     "**실수(실책) 대응 분위기를 어떻게 지각하고 있는지**를 묻는 문항입니다.\n"
     "본인의 행동이 아니라 **조직의 분위기**에 대해 응답해 주십시오."),
    ("SCB", "Ⅴ. 안전과 관련된 행동",
     "다음은 귀하가 **현장과 조직에서 안전을 위해 하는 행동**을 묻는 문항입니다.\n"
     "**이 부분은 앞과 응답 방식이 다릅니다.** 그렇게 생각하는지가 아니라,\n"
     "**실제로 얼마나 자주 하시는지**를 표시해 주십시오."),
]


def build(shuffle: bool = False, seed: int = 20260914,
          with_proposed: bool = False) -> str:
    bank = json.loads(BANK.read_text(encoding="utf-8"))
    items = bank["items"]
    proposed = bank.get("proposed_items", []) if with_proposed else []

    label = "검토용 (제안 문항 포함)" if with_proposed else "배포본"
    demo = DEMOGRAPHICS
    if with_proposed:
        # 경력 연속형 병기와 소속 식별 문항은 일반적 사항 절에 들어간다
        q5b = next((i for i in proposed if i["qid"] == "Q5b"), None)
        d8 = next((i for i in proposed if i["qid"] == "D8"), None)
        if q5b:
            demo = demo.replace(
                "　① 5년 이하　② 6년 ~ 15년　③ 16년 이상",
                "　① 5년 이하　② 6년 ~ 15년　③ 16년 이상\n\n"
                "**Q5-1.** 〔제안〕" + q5b["item_ko"])
        if d8:
            demo = demo.replace("---\n", "**Q8.** 〔제안〕" + d8["item_ko"] + "\n\n---\n")

    out = [f"# {TITLE}\n", f"### 설문지 ({label})\n", "---\n", CONSENT, demo]

    if shuffle:
        # ⚠️ 전면 무작위화는 쓰지 않는다.
        # 섹션 지시문이 사라지면 실책관리풍토 문항이 지시대상(조직)을 잃고
        # 개인 행동 자기보고로 읽힌다. "실수 경험을 다른 구성원들과 공유한다" 가
        # 조직 분위기가 아니라 응답자 본인의 행동으로 해석되는 것이다.
        # 그러면 조절변수가 조작적 정의('조직이 지원한다고 지각하는 정도')와
        # 다른 것을 측정하게 되고, 매개변수(피드백추구)와 판별되지도 않는다.
        # 따라서 무작위화는 **척도 블록 내부로 한정**하고 지시문은 유지한다.
        rng = random.Random(seed)
        out.append(
            f"> 문항 배치: 척도 블록 내부 무작위 (난수 시드 `{seed}`).\n"
            "> 블록 순서와 섹션 지시문은 유지한다 — 지시문이 사라지면 조직 수준\n"
            "> 문항이 개인 행동 문항으로 읽혀 변수의 의미가 달라지기 때문이다.\n\n")
        for key, heading, lead in SECTIONS:
            block = [i for i in items if i["var"] == key]
            rng.shuffle(block)
            out.append(f"## {heading}\n")
            out.append(f"{lead}\n\n")
            out.append(SCALE_ANCHOR.get(key, LIKERT))
            out.append("\n")
            for n, it in enumerate(block, 1):
                out.append(f"**{n}.** {it['item_ko']}\n")
                out.append("　① ② ③ ④ ⑤\n\n")
            out.append("---\n\n")
    else:
        for key, heading, lead in SECTIONS:
            block = [i for i in items if i["var"] == key]
            out.append(f"## {heading}\n")
            out.append(f"{lead}\n\n")
            out.append(SCALE_ANCHOR.get(key, LIKERT))
            out.append("\n")
            for idx, it in enumerate(block, 1):
                # 문항 식별자(Q54 등)를 그대로 노출하면 응답자가 추가 문항을
                # 의식하게 되므로, 모든 척도 블록을 일련번호로 표시한다.
                # 식별자와 설문 표시번호의 대응은 survey/item_bank.json 이 관리한다.
                label = f"{idx}"
                out.append(f"**{label}.** {it['item_ko']}\n")
                out.append("　① ② ③ ④ ⑤\n\n")
            out.append("---\n\n")

    if proposed:
        # 제안 문항은 검토용에서 교수님이 한눈에 보시도록 따로 모아 표시한다.
        revs = [i for i in proposed if i["var"] == "REV"]
        if revs:
            out.append("## 〔제안〕 역방향 문항\n")
            out.append("아래는 **역채점** 문항입니다. 실제 배포 시에는 해당 척도 "
                       "블록 안에 섞어서 배치합니다.\n\n")
            out.append(LIKERT)
            out.append("\n")
            cur = None
            for it in revs:
                if it["sub_ko"] != cur:
                    cur = it["sub_ko"]
                    out.append(f"\n**［{cur}］** "
                               f"({it.get('우선순위','')})\n\n")
                out.append(f"**{it['qid']}.** {it['item_ko']}\n")
                out.append(f"　① ② ③ ④ ⑤　　<sub>↔ 짝: {it.get('pair','')}</sub>\n\n")
            out.append("---\n\n")

    out.append("## 설문이 끝났습니다\n\n")
    out.append("응답해 주셔서 진심으로 감사드립니다.\n")
    out.append("귀하의 소중한 의견은 소방공무원의 현장 안전을 높이는 연구 자료로 활용하겠습니다.\n\n")
    out.append("---\n\n")
    out.append(
        f"<sub>연구 변수 {len(items)}문항 + 일반적 사항 7문항(+연속형 2·소속 1) · "
        "통제위치·피드백추구·실책관리풍토는 5점 동의형, "
        "안전시민행동은 5점 빈도형 · "
        "`survey/item_bank.json` 에서 자동 생성</sub>\n")
    return "".join(out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--shuffle", action="store_true",
                    help="척도 문항 무작위 배치 (공통방법편향 완화)")
    ap.add_argument("--seed", type=int, default=20260914)
    ap.add_argument("--with-proposed", action="store_true",
                    help="교수님 검토 대기 중인 제안 문항 포함")
    args = ap.parse_args()

    if args.with_proposed:
        name = "03_설문지_검토용_제안문항포함.md"
    elif args.shuffle:
        name = "02_설문지_배포본_무작위.md"
    else:
        name = "02_설문지_배포본.md"
    (HERE / name).write_text(
        build(args.shuffle, args.seed, args.with_proposed), encoding="utf-8")
    print(f"생성 완료: survey/{name}")
