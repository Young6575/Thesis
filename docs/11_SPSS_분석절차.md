# SPSS 분석 절차 — 실제 사용 문서

> **2026-09-17 분석 도구를 SPSS 로 확정하였다.**
>
> 이 문서가 **실제로 따를 분석 절차**다. 「분석 계획」 문서는 R(lavaan) 기준으로
> 작성되어 있어 **그대로 쓰지 않는다.** 다만 통계적 논리와 사전 확정 규칙의 근거는
> 그쪽에 남아 있으므로 함께 참고한다.
>
> 통계 용어는 처음 나올 때 한 줄로 풀어 적었다. 더 자세한 것은 문서함 →
> 「참고」 → 「용어사전」.

---

## 0. 먼저 — 확인이 필요한 것 하나

### ⚠️ AMOS 를 쓸 수 있습니까?

SPSS 와 AMOS 는 **다른 프로그램**이다. 같은 회사(IBM) 제품이지만 별도로 설치·구매한다.
지도교수 연구실 관행은 **SPSS + AMOS** 이므로 학교에 AMOS 가 있을 가능성이 높으나,
확인이 필요하다.

**왜 중요한가** — 이것 하나로 분석의 한 단계가 통째로 달라진다.

| | SPSS 만 | SPSS + AMOS |
|---|---|---|
| 요인 구조 확인 | **탐색적 요인분석(EFA)** | **확인적 요인분석(CFA)** |
| 하는 일 | 문항들이 **몇 개 덩어리로 묶이는지 찾아본다** | 이론이 예측한 대로 묶이는지 **맞춰 본다** |
| 모형 적합도(CFI·RMSEA) | ❌ 산출 불가 | ✅ 산출 |
| AVE·개념신뢰도(CR) | ❌ 표준 방식으로는 불가 | ✅ 산출 |
| 통제위치 1요인 vs 2요인 **비교 검정** | ❌ 불가 (눈으로 판단) | ✅ **Δχ² 로 통계적 검정** |

> ⭐ **마지막 줄이 결정적이다.**
>
> 통제위치를 내적·외적으로 **나누어 채점하는 것**이 이 논문 최대 쟁점이다.
> 역방향 문항을 철회한 뒤로 이 쟁점의 방어 수단은 두 가지만 남았는데,
> 그중 하나가 **1요인 대 2요인 비교**다. AMOS 가 없으면 이 비교를 통계적으로
> 검정하지 못하고 "요인분석 결과 2개로 나뉘었다"는 서술에 그친다.

**권장**: 가능하면 AMOS 를 확보한다. 학교 전산실·도서관·연구실 라이선스를 확인하시라.
없더라도 논문은 성립한다. 아래 절차는 **SPSS 만으로 끝까지 가는 것을 기준**으로
작성하였고, AMOS 가 있으면 추가할 부분을 ⊕ 로 표시하였다.

---

## 1. 필요한 것 — 설치

### (1) SPSS 본체
버전은 상관없다. 22 이상이면 아래 절차가 모두 된다.

### (2) PROCESS 매크로 — **반드시 필요하다**

매개효과와 조절효과를 검증하는 도구다. Andrew Hayes 교수가 무료로 배포한다.

- 내려받는 곳: `processmacro.org` → Download
- 설치: 압축을 풀면 `PROCESS vX.X for SPSS.spd` 파일이 있다.
  SPSS 에서 **유틸리티 > 사용자 정의 대화상자 > 사용자 정의 대화상자 설치**로 연다.
- 설치되면 **분석 > 회귀분석 > PROCESS** 메뉴가 생긴다.

> PROCESS 가 없으면 매개효과의 신뢰구간(부트스트랩)을 낼 수 없다.
> 예전 방식(Baron & Kenny 3단계)은 현재 학계에서 권장되지 않으므로,
> 반드시 설치하시라.

### (3) ⊕ AMOS (있는 경우)
확인적 요인분석과 측정모형 적합도 산출에 쓴다.

---

## 2. 표본 수 — 몇 명을 받아야 하는가

**결론: 최소 300명, 목표 400명.**

근거를 계산하였다. 검정력 .80, 유의수준 .05 기준이다.
(검정력 = 실제로 효과가 있을 때 그것을 찾아낼 확률. 통상 .80 이상을 요구한다.)

| 무엇을 검정하나 | 효과크기 가정 | 필요 표본 |
|---|---|---|
| **조절효과(상호작용항)** | f² = .02 (작음) | **395명** |
| 조절효과 | f² = .035 | 227명 |
| 주효과·매개경로 (내적·외적 동시) | f² = .02 | 485명 |
| 주효과·매개경로 | f² = .05 | 196명 |
| **경력 3집단 비교** | 집단당 100명 | **300명** |

> **왜 조절효과가 가장 많은 표본을 요구하는가** — 상호작용 효과는 원래 크기가 작게
> 나온다. 두 변수를 곱해서 만든 항이라 측정오차가 누적되기 때문이다. 본 연구의
> 핵심 가설(H4·H5)이 모두 조절효과이므로 여기에 맞추어야 한다.

**따라서 목표는 400명**이다. 300명 미만이면 조절효과가 있어도 못 찾을 수 있다.

> ⚠️ **기존 계획(600명)은 R 구조방정식 기준이었다.** SPSS 위계적 회귀에서는
> 그만큼 필요하지 않다. 지도교수 연구실 관행(160~300명)보다는 조금 많은 수준이다.
>
> ⚠️ **불성실 응답 제외를 감안하여 회수 목표는 더 잡는다.** 통상 10~20% 를 제외하게
> 되므로, 최종 400명을 확보하려면 **450~500부 회수**를 목표로 한다.

---

## 3. 자료 정제 — 분석 전에 할 일

### 3.1 불성실 응답 제외

주의점검 문항을 쓰지 않으므로 세 기준으로 판정한다.
**임계값은 자료를 보기 전에 아래로 확정한다. 결과를 보고 바꾸지 않는다.**

| 기준 | 임계값 | SPSS 에서 |
|---|---|---|
| **직선 응답** | 52문항 전체의 표준편차가 **0.30 미만** | 변환 > 변수 계산 → `SD.52(Q8 TO Q59)` |
| **응답 소요시간** | **5분 미만** | 플랫폼이 기록한 시간 변수로 판정 |
| **필수 문항 결측** | 한 척도에서 **20% 이상** 결측 | 변환 > 변수 계산 → `NMISS(...)` |

> **직선 응답이란** 모든 문항에 같은 값(예: 전부 ③)을 찍는 것이다. 문항을 읽지 않은
> 응답일 가능성이 높다. 표준편차가 0에 가까우면 그런 경우다.
>
> ⚠️ 응답 소요시간 5분은 **52문항 기준으로 문항당 5초 남짓**이다. 읽고 답하기에
> 물리적으로 부족한 수준으로 잡았다. 실제 파일럿에서 평균 소요시간이 나오면
> 그 값의 **1/3 지점**으로 조정하되, **본조사 자료를 보기 전에** 확정한다.

**SPSS 구문**

```spss
* ── 불성실 응답 판정 변수 만들기 ──.
COMPUTE sd_all  = SD(Q8 TO Q59).
COMPUTE n_miss  = NMISS(Q8 TO Q59).
COMPUTE careless = 0.
IF (sd_all < 0.30) careless = 1.
IF (duration < 300) careless = 1.        /* 초 단위. 300초 = 5분 */
IF (n_miss > 10)    careless = 1.        /* 52문항의 약 20% */
EXECUTE.

FREQUENCIES VARIABLES = careless.        /* 몇 명이 걸리는지 확인 */

* ── 제외 ──.
SELECT IF (careless = 0).
EXECUTE.
```

> ⚠️ **제외 인원을 단계별로 기록해 두었다가 논문 4장 표로 만든다.**
> 주의점검 문항이라는 객관적 기준이 없으므로, **어떤 기준으로 몇 명을 뺐는지**
> 투명하게 밝히는 것이 방어가 된다.

### 3.2 역채점 — **하지 않는다**

역방향 문항을 철회하였으므로 **6에서 빼는 변환이 없다.** 모든 응답값을 그대로 쓴다.

> ⚠️ 예전 문서에 남아 있는 역채점 구문을 실행하지 마시라. 결과가 뒤집힌다.

### 3.3 변수 만들기

각 척도의 문항 평균을 낸다.

```spss
COMPUTE INT  = MEAN(Q8,Q9,Q10,Q11,Q14,Q18,Q21,Q22).        /* 내적 통제위치 8 */
COMPUTE EXT  = MEAN(Q12,Q13,Q15,Q16,Q17,Q19,Q20,Q23).      /* 외적 통제위치 8 */
COMPUTE PFSB = MEAN(Q24 TO Q28).                            /* 긍정적 피드백 추구 5 */
COMPUTE NFSB = MEAN(Q29 TO Q33).                            /* 부정적 피드백 추구 5 */
COMPUTE EMC  = MEAN(Q34 TO Q41).                            /* 지각된 실책관리풍토 8 */
COMPUTE SCB  = MEAN(Q42 TO Q59).                            /* 안전시민행동 18 */
VARIABLE LABELS
  INT '내적 통제위치' EXT '외적 통제위치'
  PFSB '긍정적 피드백 추구행동' NFSB '부정적 피드백 추구행동'
  EMC '지각된 실책관리풍토' SCB '안전시민행동'.
EXECUTE.
```

> ⚠️ **통제위치 문항 번호에 주의하라.** 내적과 외적이 설문지에서 번갈아 배치되어
> 있어 `Q8 TO Q15` 처럼 범위로 지정하면 **엉뚱한 문항이 섞인다.**
> 반드시 위처럼 하나씩 나열하시라. 실제로 그런 사고가 있었다.

안전시민행동은 6개 차원별로도 만든다.

```spss
COMPUTE SCB_help = MEAN(Q42,Q43,Q54).   /* 지원 */
COMPUTE SCB_voic = MEAN(Q44,Q45,Q55).   /* 발언 */
COMPUTE SCB_stew = MEAN(Q46,Q47,Q56).   /* 책무 */
COMPUTE SCB_whis = MEAN(Q48,Q49,Q57).   /* 고발 */
COMPUTE SCB_civi = MEAN(Q50,Q51,Q58).   /* 참여 */
COMPUTE SCB_chan = MEAN(Q52,Q53,Q59).   /* 변화주도 */
EXECUTE.
```

---

## 4. 1단계 — 표본의 일반적 특성

**메뉴**: 분석 > 기술통계량 > 빈도분석

성별·연령·계급·직무분야·직무경력·근무형태의 빈도와 비율을 낸다.
→ 논문 〈표 4-1〉

> ⚠️ **경력 3집단의 크기를 반드시 확인하라.** 한 집단이 50명 아래로 내려가면
> 다집단 비교의 검정력이 부족하다. 그 경우 **연속형 경력변수(Q5-1) 분석을
> 주 결과로** 삼고 3집단 비교는 보조로 제시한다.

---

## 5. 2단계 — 타당도

### 5.1 탐색적 요인분석 (EFA)

**"이 문항들이 정말 몇 개 덩어리로 묶이는가"를 확인하는 분석이다.**

**메뉴**: 분석 > 차원 축소 > 요인분석

| 설정 | 무엇을 고를까 | 왜 |
|---|---|---|
| 요인추출 | **주축 요인추출**(principal axis factoring) | 구성개념을 재는 척도에는 주성분분석보다 적합하다 |
| 회전 | **직접 오블리민**(oblimin) | 요인들이 서로 상관이 있다고 보기 때문이다. 베리맥스는 요인 간 상관을 0으로 가정한다 |
| 요인 수 | 고유값 > 1 **과** 스크리 도표를 함께 본다 | 하나만 쓰면 요인 수를 과대추정하기 쉽다 |
| 출력 | KMO·Bartlett 검정, 회전된 요인행렬, 요인상관행렬 | |

**판정 기준 (사전 확정)**

- KMO ≥ .70, Bartlett 검정 유의 → 요인분석에 적합한 자료
- 요인부하량 ≥ .50 → 해당 요인에 속함
- 교차부하(두 요인 모두에 .40 이상) 문항 → 제거 검토. **제거하면 반드시 보고**

### 5.2 ★ 통제위치 요인 구조 — 최대 쟁점

**통제위치 16문항만 따로 요인분석한다.**

```spss
FACTOR
  /VARIABLES Q8 Q9 Q10 Q11 Q14 Q18 Q21 Q22 Q12 Q13 Q15 Q16 Q17 Q19 Q20 Q23
  /PRINT INITIAL KMO EXTRACTION ROTATION FSCORE
  /PLOT EIGEN
  /CRITERIA FACTORS(2) ITERATE(50)
  /EXTRACTION PAF
  /ROTATION OBLIMIN.
```

**보고할 것**

1. **2요인이 실제로 나왔는가** — 고유값과 스크리 도표
2. **내적 8문항이 한 요인에, 외적 8문항이 다른 요인에 묶였는가** — 회전된 요인행렬
3. **두 요인의 상관** — 요인상관행렬. 상관이 −1에 가까우면 사실상 하나다

> ⚠️ **예상대로 나오지 않으면 그 사실을 그대로 보고한다.** 2요인으로 깨끗하게
> 나뉘지 않으면 **16문항 총점을 쓰는 분석 결과를 함께 제시**하고, 연구모형의
> 해당 부분을 수정한다. 결과를 보고 문항을 골라내어 억지로 2요인을 만들면 안 된다.

> ⊕ **AMOS 가 있으면** — 1요인 모형과 2요인 모형을 각각 만들어 χ²·CFI·RMSEA 를
> 비교하고, **Δχ² 검정**으로 2요인이 유의하게 우월한지 판정한다.
> 이것이 가장 강한 근거다.

### 5.3 판별타당도

SPSS 만으로는 AVE 를 표준 방식으로 내기 어렵다. 대신 다음을 제시한다.

- **요인 간 상관계수**가 지나치게 높지 않은지(통상 .85 미만)
- 각 문항이 **자기 요인에만** 높게 부하되는지

> ⊕ AMOS 가 있으면 AVE 와 개념신뢰도(CR)를 산출하고,
> **√AVE > 구성개념 간 상관** 기준으로 판별타당도를 제시한다(Fornell-Larcker).

---

## 6. 3단계 — 신뢰도

**"같은 것을 재는 문항들이 서로 일관되게 움직이는가"를 보는 지표다.**

**메뉴**: 분석 > 척도분석 > 신뢰도 분석

각 척도별로 Cronbach's α 를 낸다. **.70 이상**이면 수용한다.

```spss
RELIABILITY /VARIABLES=Q8 Q9 Q10 Q11 Q14 Q18 Q21 Q22
  /SCALE('내적 통제위치') /MODEL=ALPHA /SUMMARY=TOTAL.
RELIABILITY /VARIABLES=Q12 Q13 Q15 Q16 Q17 Q19 Q20 Q23
  /SCALE('외적 통제위치') /MODEL=ALPHA /SUMMARY=TOTAL.
RELIABILITY /VARIABLES=Q24 TO Q28 /SCALE('긍정적 피드백추구') /MODEL=ALPHA /SUMMARY=TOTAL.
RELIABILITY /VARIABLES=Q29 TO Q33 /SCALE('부정적 피드백추구') /MODEL=ALPHA /SUMMARY=TOTAL.
RELIABILITY /VARIABLES=Q34 TO Q41 /SCALE('지각된 실책관리풍토') /MODEL=ALPHA /SUMMARY=TOTAL.
RELIABILITY /VARIABLES=Q42 TO Q59 /SCALE('안전시민행동 전체') /MODEL=ALPHA /SUMMARY=TOTAL.
```

**안전시민행동은 6개 차원별 α 도 반드시 보고한다.** 차원당 3문항이므로 α 가
낮게 나올 수 있는데, 그것 자체를 숨기지 말고 보고한다.

### ★ 사전 확정 규칙 — 금전 문항 점검

`/SUMMARY=TOTAL` 이 출력하는 **수정된 항목-전체 상관**을 본다.

| 문항 | 확인할 것 |
|---|---|
| Q13 · Q19 · Q23 | 표준편차, 항목-전체 상관, 제거 시 α |

> **규칙**: 기여도가 낮더라도 **제거 전후 결과를 모두 보고**한다.
> 결과를 보고 골라서 빼면 안 된다. 이것은 교수님 결정으로 확정된 사항이다.

---

## 7. 4단계 — 기술통계와 상관관계

**메뉴**: 분석 > 기술통계량 > 기술통계 (평균·표준편차·왜도·첨도)
**메뉴**: 분석 > 상관분석 > 이변량 상관계수 (Pearson)

→ 논문 〈표 4-7〉

> ⚠️ **안전시민행동의 천장효과를 반드시 확인하라.**
> 평균이 4.5를 넘고 왜도가 −1 보다 작으면(크게 음수이면) 응답이 한쪽으로 몰려
> 분산이 사라진 것이다. 그러면 이후 분석에서 관계가 안 나온다.
> 그런 경우 **그 사실을 5장 한계에 명시**한다.

### 공통방법편의 진단 — Harman 단일요인 검정

**모든 문항을 한꺼번에 요인분석**하여, 회전하지 않은 상태에서 **첫 번째 요인이
전체 분산의 50% 미만**을 설명하는지 본다.

```spss
FACTOR /VARIABLES Q8 TO Q59
  /PRINT INITIAL EXTRACTION
  /CRITERIA FACTORS(1)
  /EXTRACTION PC
  /ROTATION NOROTATE.
```

> ⚠️ **Harman 검정은 약한 검정이다.** "문제없었다"로 끝내면 안 된다.
> 본 연구가 **설계 단계에서 적용한 절차적 통제**(무기명, 척도별 응답형식 분리,
> 문항 순서 무작위화)를 함께 기술하고, 마커변수를 쓰지 않아 방법분산을 수치로
> 추정하지 못한 점을 **5장 한계**에 적는다.

---

## 8. 5단계 — 가설 검증

### 8.0 먼저 — 평균중심화

조절효과를 볼 때 **곱하기 항(상호작용항)** 을 만드는데, 그냥 곱하면 원래 변수와
지나치게 높은 상관이 생겨 결과가 불안정해진다. 그래서 각 변수에서 평균을 빼 둔다.

```spss
* 기술통계로 평균을 먼저 확인한 뒤, 그 값을 넣는다.
DESCRIPTIVES VARIABLES=INT EXT PFSB NFSB EMC.

COMPUTE cINT  = INT  - 3.21.     /* ← 실제 평균으로 바꿀 것 */
COMPUTE cEXT  = EXT  - 2.98.
COMPUTE cPFSB = PFSB - 3.45.
COMPUTE cNFSB = NFSB - 3.12.
COMPUTE cEMC  = EMC  - 3.33.
EXECUTE.

* 상호작용항.
COMPUTE NFSBxEMC = cNFSB * cEMC.
COMPUTE PFSBxEMC = cPFSB * cEMC.
EXECUTE.
```

> PROCESS 를 쓰면 `center` 옵션으로 자동 처리되므로, 직접 위계적 회귀를 돌릴 때만
> 필요하다.

---

### 8.1 H0 — 총효과 (위계적 회귀)

**메뉴**: 분석 > 회귀분석 > 선형 → **블록(Block)** 기능 사용

| 블록 | 넣을 변수 |
|---|---|
| 1 | 통제변수 (성별, 연령, 계급, 직무분야, 근무형태) |
| 2 | 내적 통제위치, 외적 통제위치 |

**종속변수**: 안전시민행동(SCB)

```spss
REGRESSION /STATISTICS COEFF OUTS R ANOVA CHANGE
  /DEPENDENT SCB
  /METHOD=ENTER sex age rank job shift
  /METHOD=ENTER INT EXT.
```

`/STATISTICS ... CHANGE` 를 넣어야 **R² 변화량(ΔR²)** 이 출력된다. 이것이 핵심이다.

> ⚠️ **총효과가 유의하지 않아도 매개 검증을 중단하지 않는다.**
> 이 모형은 내적 경로(−)와 외적 경로(+)가 서로 상쇄되어 총효과가 0에 가까워지는
> 것이 오히려 예측되는 바이다.

---

### 8.2 H1 — 통제위치 → 피드백 추구행동 (a경로)

종속변수를 바꾸어 같은 방식으로 두 번 돌린다.

```spss
REGRESSION /STATISTICS COEFF OUTS R ANOVA CHANGE
  /DEPENDENT PFSB
  /METHOD=ENTER sex age rank job shift /METHOD=ENTER INT EXT.

REGRESSION /STATISTICS COEFF OUTS R ANOVA CHANGE
  /DEPENDENT NFSB
  /METHOD=ENTER sex age rank job shift /METHOD=ENTER INT EXT.
```

→ 논문 〈표 4-10〉의 2×2 표를 이 결과로 채운다.

> ⭐ **이 2×2 표가 본 연구의 핵심 증거다.**
> 내적 → 긍정(+) 강 / 내적 → 부정(−) / 외적 → 부정(+) 강 / 외적 → 긍정 약
> 이라는 **비대칭 교차 패턴**이 나오면, 통제위치가 하나의 연속선이 아니라
> 두 개의 차원임을 보여주는 근거가 된다.
> 응답 습관(묵종편향)은 모든 문항에 같은 방향으로 작용하므로 **이런 비대칭을
> 만들어 낼 수 없다.** 역방향 문항을 철회한 뒤 남은 가장 강한 방어다.

**H1-5 (탐색) — 곡선 관계**

```spss
COMPUTE cINT2 = cINT * cINT.
EXECUTE.
REGRESSION /STATISTICS COEFF OUTS R ANOVA CHANGE
  /DEPENDENT NFSB
  /METHOD=ENTER sex age rank job shift
  /METHOD=ENTER cINT
  /METHOD=ENTER cINT2.
```

3블록의 ΔR² 이 유의하면 곡선 관계가 있다는 뜻이다.

---

### 8.3 H2 — 피드백 추구행동 → 안전시민행동 (b경로)

```spss
REGRESSION /STATISTICS COEFF OUTS R ANOVA CHANGE
  /DEPENDENT SCB
  /METHOD=ENTER sex age rank job shift
  /METHOD=ENTER PFSB NFSB.
```

### ★ H2-2 — "부정적이 긍정적보다 크다"를 어떻게 검정하는가

두 표준화계수(β)를 눈으로 비교하는 것만으로는 **주장이 성립하지 않는다.**
차이가 통계적으로 유의한지 검정해야 한다. SPSS 에서는 다음 방법을 쓴다.

**합·차 변환법** — 두 변수의 합과 차를 새 변수로 만들어 회귀에 넣으면,
**차이 변수의 계수가 곧 두 계수의 차이**를 검정한다.

```spss
COMPUTE FSB_sum  = PFSB + NFSB.
COMPUTE FSB_diff = NFSB - PFSB.
EXECUTE.

REGRESSION /STATISTICS COEFF OUTS R ANOVA
  /DEPENDENT SCB
  /METHOD=ENTER sex age rank job shift FSB_sum FSB_diff.
```

`FSB_diff` 의 계수가 **유의한 양수**이면, 부정적 피드백 추구의 효과가 긍정적보다
유의하게 크다는 뜻이다. 이 결과를 H2-2 의 근거로 보고한다.

**H2-3 (탐색)** — 안전시민행동 6개 차원을 각각 종속변수로 하여 6번 돌리고,
어느 차원에서 관계가 강한지 비교한다.

---

### 8.4 H3 — 매개효과 (PROCESS **Model 4**)

**메뉴**: 분석 > 회귀분석 > PROCESS

| 칸 | 넣을 것 |
|---|---|
| Y variable | SCB |
| X variable | INT (그 다음 EXT 로 한 번 더) |
| Mediator(s) M | **PFSB, NFSB 둘 다** ← 병렬 매개 |
| Covariates | sex, age, rank, job, shift |
| Model number | **4** |
| Bootstrap samples | **5000** |
| Confidence intervals | 95 |
| Options | ☑ Show total effect model · ☑ Pairwise contrasts of indirect effects |

**읽는 법**

- 출력의 **Indirect effect(s) of X on Y** 표를 본다
- **BootLLCI 와 BootULCI** 가 신뢰구간의 하한·상한이다
- **이 구간이 0을 포함하지 않으면 매개효과가 유의**하다
- `(C1)` 로 표시된 줄이 **두 매개효과의 차이**(H3-3) 검정이다

> **"완전매개/부분매개"라는 표현은 조심해서 쓰라.** 직접효과가 유의하지 않다고
> 해서 완전매개라고 단정하면 안 된다. **간접효과의 유의성과 크기를 중심으로**
> 기술하는 것이 현재 학계 권장 방식이다.

---

### 8.5 H4 — 지각된 실책관리풍토의 조절 (PROCESS **Model 14**)

**Model 14 는 b경로(매개변수 → 종속변수)를 조절하는 모형이다.** 본 연구 가설과 맞는다.

| 칸 | 넣을 것 |
|---|---|
| Y | SCB |
| X | EXT (그 다음 INT) |
| Mediator M | NFSB |
| Moderator W | **EMC** |
| Model number | **14** |
| Bootstrap | 5000 |
| Options | ☑ Generate code for visualizing interactions · ☑ Mean center for products |

**읽는 법**

- **Index of moderated mediation** 을 반드시 보고한다. 이것이 조절된 매개의
  핵심 통계량이다. 신뢰구간이 0을 포함하지 않으면 유의하다
- **Conditional indirect effects** 표에서 EMC 가 낮을 때·평균일 때·높을 때의
  간접효과를 본다 → H4-3
- 상호작용이 유의하면 **단순기울기 그림**을 그린다 (PROCESS 가 그림용 구문을 출력해 준다)

**H4-2 (판별가설)** — 매개변수를 PFSB 로 바꾸어 한 번 더 돌리고, 조절효과가
NFSB 쪽보다 약한지 비교한다.

**H4-4** — INT 로 돌린 결과의 조절된 매개지수가 EXT 쪽보다 작은지 비교한다.

---

### 8.6 H5 — 직무경력의 조절

경력이 **3집단**(범주형)이므로 처리가 조금 다르다.

#### (1) 더미변수 만들기

```spss
* 기준집단 = 저경력(5년 이하).
COMPUTE ten_mid  = (tenure = 2).      /* 6~15년 */
COMPUTE ten_high = (tenure = 3).      /* 16년 이상 */
EXECUTE.
```

#### (2) H5-1 — a경로 조절 (위계적 회귀)

```spss
COMPUTE cEXT_mid  = cEXT * ten_mid.
COMPUTE cEXT_high = cEXT * ten_high.
COMPUTE cINT_mid  = cINT * ten_mid.
COMPUTE cINT_high = cINT * ten_high.
EXECUTE.

REGRESSION /STATISTICS COEFF OUTS R ANOVA CHANGE
  /DEPENDENT NFSB
  /METHOD=ENTER sex age rank job shift
  /METHOD=ENTER cINT cEXT ten_mid ten_high
  /METHOD=ENTER cINT_mid cINT_high cEXT_mid cEXT_high.
```

3블록의 **ΔR² 이 유의하면 경력이 조절한다**는 뜻이다.
개별 계수를 보면 어느 집단에서 관계가 다른지 알 수 있다.

#### (3) H5-2 — b경로 조절 + ★ 함수형태 판별

```spss
COMPUTE cNFSB_mid  = cNFSB * ten_mid.
COMPUTE cNFSB_high = cNFSB * ten_high.
EXECUTE.

REGRESSION /STATISTICS COEFF OUTS R ANOVA CHANGE
  /DEPENDENT SCB
  /METHOD=ENTER sex age rank job shift
  /METHOD=ENTER cNFSB ten_mid ten_high
  /METHOD=ENTER cNFSB_mid cNFSB_high.
```

**★ 함수형태는 연속형 경력변수로 판별한다.**

```spss
* Q5-1 (연 단위 경력) 을 쓴다. 3구간 범주화는 정보를 버려 곡선을 못 잡는다.
COMPUTE cTEN  = tenure_yr - 12.4.      /* ← 실제 평균으로 */
COMPUTE cTEN2 = cTEN * cTEN.
COMPUTE NFSBxTEN  = cNFSB * cTEN.
COMPUTE NFSBxTEN2 = cNFSB * cTEN2.
EXECUTE.

REGRESSION /STATISTICS COEFF OUTS R ANOVA CHANGE
  /DEPENDENT SCB
  /METHOD=ENTER sex age rank job shift
  /METHOD=ENTER cNFSB cTEN cTEN2
  /METHOD=ENTER NFSBxTEN
  /METHOD=ENTER NFSBxTEN2.
```

| 결과 | 판정 |
|---|---|
| 4블록만 유의 (`NFSBxTEN`) | **H5-2b 단조 패턴** — 경력이 길수록 효과가 일정하게 변한다 |
| 5블록도 유의 (`NFSBxTEN2`) | **H5-2a 역U자** — 중간경력에서 정점 |

> ⚠️ **역U자가 안 나오는 것은 실패가 아니다.** 선행연구 조사 결과 역U자를 검정한
> 연구가 한 편도 없었고, 오히려 **단조 패턴을 지지하는 대규모 증거**가 있다.
> 어느 쪽이 나오든 그대로 보고하면 된다. 그래서 두 가설을 미리 나누어 두었다.

#### (4) H5-3 — 집단별 조절된 매개

경력 집단별로 PROCESS Model 4 를 따로 돌려 간접효과를 비교한다.

```spss
SORT CASES BY tenure.
SPLIT FILE LAYERED BY tenure.
* → 이 상태에서 PROCESS Model 4 실행.
SPLIT FILE OFF.
```

> ⚠️ 집단별로 나누어 돌린 간접효과의 **차이를 통계적으로 검정하는 것은 아니다.**
> 기술적 비교이며, 공식 검정은 위 (2)·(3)의 상호작용항 ΔR² 이 담당한다.
> 논문에는 이 구분을 분명히 적는다.
>
> ⚠️ PROCESS 버전에 따라 **다범주 조절변수(multicategorical moderator)** 를
> 직접 지원하기도 한다. 쓰는 버전의 설명서를 확인하시라. 지원되면 더 깔끔하다.

#### (5) H5-4 — 독립성

H4 의 PROCESS Model 14 를 돌릴 때 **공변량(Covariates)에 경력 더미 2개를 추가**하고,
조절된 매개지수가 여전히 유의한지 확인한다.

---

## 9. 가설 ↔ 분석 대응표 (한눈에)

| 가설 | 무엇을 보나 | SPSS 에서 |
|---|---|---|
| **H0-1·H0-2** | 통제위치 → 안전시민행동 총효과 | 위계적 회귀 2블록 |
| **H1-1 ~ H1-4** | 통제위치 → 피드백 추구 (2×2 패턴) | 위계적 회귀 ×2 |
| **H1-5** | 내적통제의 곡선 관계 | 위계적 회귀 + 2차항 |
| **H2-1·H2-2** | 피드백 추구 → 안전시민행동 | 위계적 회귀 + **합·차 변환법** |
| **H2-3** | 안전시민행동 차원별 차이 | 위계적 회귀 ×6 |
| **H3-1 ~ H3-3** | 매개효과 | **PROCESS Model 4** (병렬 매개, 부트스트랩 5000) |
| **H4-1·H4-2** | 실책관리풍토의 b경로 조절 | **PROCESS Model 14** |
| **H4-3·H4-4** | 조절된 매개 | **PROCESS Model 14** — 조절된 매개지수 |
| **H5-1a·H5-1b** | 경력의 a경로 조절 | 위계적 회귀 + 더미×상호작용 |
| **H5-2** | 경력의 b경로 조절 | 위계적 회귀 + 더미×상호작용 |
| **H5-2a·H5-2b** | 함수형태(역U자 vs 단조) | 위계적 회귀 + **연속형 경력 2차항** |
| **H5-3** | 집단별 간접효과 | 파일분할 + PROCESS Model 4 |
| **H5-4** | 두 조절효과의 독립성 | Model 14 + 경력 공변량 |

---

## 10. 결과표 만들 때

지도교수님이 검토하시기 좋도록 **SPSS 출력 형태를 그대로 살린 표**로 만든다.

- 위계적 회귀표: 블록별 **β, t, R², ΔR², F** 를 세로로 쌓는다
- 유의도 표기: `* p<.05, ** p<.01, *** p<.001`
- 매개효과표: **B, SE, BootLLCI, BootULCI** (β 가 아니라 비표준화계수 B 를 쓴다)
- 조절효과 그림: ±1 표준편차 단순기울기 그래프

---

## 11. 무엇이 바뀌었나 — 기존 계획과의 차이

| | 기존 (R 기준) | 확정 (SPSS) |
|---|---|---|
| 도구 | R + lavaan | **SPSS + PROCESS** |
| 요인 구조 | 확인적 요인분석 | **탐색적 요인분석** (⊕ AMOS 있으면 CFA) |
| 적합도 지수 | CFI·RMSEA·SRMR | **산출 안 함** (⊕ AMOS 시 산출) |
| AVE·CR | 산출 | **산출 안 함** — α 와 요인부하량으로 대체 |
| 매개·조절 | 구조방정식 | **PROCESS 매크로** |
| 경로계수 비교 | Δχ² 등가제약 | **합·차 변환법** |
| 다집단 비교 | 다집단 구조방정식 | **더미변수 상호작용** |
| **목표 표본** | 600명 | **400명** (최소 300) |

> **성립하는가** — 성립한다. 국내 경영학 학위논문의 표준적 구성이며,
> 지도교수 연구실 관행과도 맞는다.
>
> **다만 한 가지 한계가 생긴다** — 통제위치 2요인 구조를 **통계적으로 검정**하지
> 못하고 요인분석 결과를 **서술**하는 데 그친다. AMOS 를 확보하면 해결된다.

---

*작성 2026-09-17 · 분석 도구 SPSS 확정 반영*
