---
name: 모형점검
description: 연구모형·가설·문서 간 정합성을 기계적으로 점검한다. 문서를 고친 뒤나 교수님께 보내기 전에 "점검해줘", "일관성 확인", "모순 없나" 라고 할 때 사용한다.
---

# 연구모형·문서 정합성 점검

가설 번호가 문서마다 다른 뜻을 가리키는 사고가 **실제로 발생했다.**
문서를 고칠 때마다 이 점검을 돌린다.

## 자동 점검

```bash
# ① 가설 라벨 — 정본은 docs/01_연구모형_가설.md
for f in docs/0[0234]*.md; do
  printf "%-34s " "$(basename $f)"
  grep -oE "H[1-9]-[0-9][ab]?" "$f" | sort -u | tr '\n' ' '; echo
done

# ② 문항 수 — 46 + 직무경력 1 = 47 이 전 문서 동일해야 한다
python3 -c "
import json; b=json.load(open('survey/item_bank.json'))
from collections import Counter
c=Counter(i['var'] for i in b['items'])
print('item_bank:', dict(c), '합계', sum(c.values()))
print('제안 문항:', len(b.get('proposed_items',[])))
"
grep -rn "47문항\|46문항\|12문항\|16문항" docs/*.md | head

# ③ 변수명 표기 통일 — '지각된 실책관리풍토'
grep -rc "실책관리풍토" docs/*.md
grep -rn "Van Dyck" docs/*.md | head   # 정규 표기는 소문자 van Dyck

# ④ 설문지가 문항 뱅크와 동기화되어 있는가
python3 survey/build_survey.py && git diff --stat survey/
```

## 논리 점검 — 사람이 판단할 것

1. **핵심 주장이 관철되는가** — "내적통제가 항상 좋은 건 아니다"가
   2장~5장에 일관되게 흐르는가? 어디선가 "내적통제=좋음"으로 되돌아가지 않는가?
2. **가설과 분석방법이 맞는가** — 매개는 Model 4, a경로 조절은 Model 7,
   b경로 조절된 매개는 Model 14. 가설표와 분석계획의 모형 번호가 일치하는가?
3. **`_확정사항.md` 와 충돌하는 권고가 있는가** — 있다면 그것은 연구자가
   혼자 실행할 일이 아니라 **지도교수 재승인 안건**이다.
   `docs/06_교수님_재승인_안건.md` 로 옮긴다.
4. **[미검증] 문헌이 본문 논거로 쓰이고 있는가** — 쓰이면 안 된다.

## 깊은 검토가 필요하면

`thesis-critic` 에이전트에 위임한다. 독립된 맥락에서 심사위원 관점으로 본다.
이 스킬은 **기계적 정합성**, 그 에이전트는 **논리적 결함**을 본다.
