# 박사학위논문 프로젝트

**소방공무원의 통제위치가 안전시민행동에 미치는 영향**
— 피드백 추구행동의 매개효과와 지각된 실책관리풍토·직무경력의 조절효과

---

## 지금 어디까지 왔나

| 단계 | 상태 |
|---|---|
| 연구모형·변수 확정 | ✅ 완료 |
| 척도 47문항 확정 (교수님 검토) | ✅ 완료 |
| 설문지 배포본 작성 | ✅ 완료 |
| IRB / 기관 승인 | ⬜ 확인 필요 |
| 설문 배포·자료수집 | ⬜ 진행 예정 |
| 통계분석 | ⬜ |
| 논문 집필 (1~5장) | ⬜ |
| 심사 대응 | ⬜ |

---

## 폴더 안내

| 폴더 | 내용 |
|---|---|
| `CLAUDE.md` | **프로젝트 메모리.** 모든 Claude 세션에 자동 주입된다. 연구 배경을 다시 설명할 필요 없음 |
| `docs/_확정사항.md` | **확정 사항 원천.** AI가 쓴 다른 문서와 충돌하면 이 문서가 맞다 |
| `docs/` | 연구개요 · 가설 · 조작적정의 · 분석계획 · 문헌노트 · AI도구 리서치 |
| `survey/` | 척도 총괄표(xlsx) · 문항 뱅크(json/csv) · 설문지 배포본 · 생성 스크립트 |
| `data/` | 설문 원자료 (수집 후). `data/raw/` 는 **커밋되지 않음** |
| `analysis/` | R / Python 분석 스크립트 |
| `references/` | 참고문헌 (검증 상태 태그 포함) |
| `.claude/agents/` | 전문 서브에이전트 |
| `.claude/skills/` | 반복 작업 절차 (슬래시 명령) |

---

## 설문지 다시 만들기

문항은 `survey/item_bank.json` 이 **단일 원천**이다. 문항을 고칠 때는 이 파일만 고친다.

```bash
python3 survey/build_survey.py              # 변수 블록 배치 (기본)
python3 survey/build_survey.py --shuffle    # 무작위 배치 (공통방법편향 완화)
```

---

## 인용 검증 (반드시 할 것)

AI가 찾아준 참고문헌을 **그대로 논문에 넣지 않는다.** 실재를 확인한다.

```bash
curl -s "https://api.crossref.org/works?query.bibliographic=Spector+Work+Locus+of+Control+Scale&rows=3" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);[print(i['title'][0],'|',i.get('DOI')) for i in d['message']['items']]"
```

참고문헌에는 `[검증됨]` / `[미검증]` 태그를 붙이고, **`[미검증]` 은 논문 본문에 인용하지 않는다.**
