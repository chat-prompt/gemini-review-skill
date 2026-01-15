# Gemini Review Skill - 개발 로그

Claude Code와 함께 진행한 개발 작업 기록입니다.

---

## 2026-01-15 (Day 1)

### 1. 프로젝트 시작 - Gemini 리뷰 스킬 기획

```
"Claude가 짠 코드를 Gemini에게 리뷰시키는" 워크플로우가 새로운 표준으로 자리잡고 있는데
Claude Code로 개발하고, Gemini로 검수하는 방식이거든?
이걸 이 디렉토리에 있는 skill-creator로 만들고 싶어.
```

**Claude 작업:**
- 기존 `skill-creator` 스킬 구조 분석
- Gemini 코드 리뷰 스킬 설계 시작
- bkit 개발 가이드 참고하여 PDCA 방식 적용 검토

---

### 2. 핵심 요구사항 정의

```
하나의 기능이나 단계가 구현되면 그 다음에는 자동으로 무조건 리뷰를 시키게 해줘.
내가 먼저 이야기 하지 않더라도.
gemini api키는 처음 스킬이 동작될 때 물어보게 하고 - 유저가 대답하면 .env에 저장해줘.
모델은 gemini 3.0 flash를 항상 써줘.
방금 짠 코드를 그때그때 리뷰 받는거지.
리뷰 결과는 어떻게 처리할지 니가 정해봐.
```

**Claude 작업:**
- 자동 리뷰 트리거 설계: Edit/Write 도구 사용 후 자동 실행
- API 키 관리 방식 설계: `.env` 파일 저장
- 모델 선정: `gemini-3-flash-preview`
- 리뷰 결과 처리 방식 설계: 번호 선택형 인터랙티브 UI

---

### 3. 스킬 기본 구조 생성

**Claude 작업:**
- 스킬 파일 구조 생성:
  - `skills/gemini-review/SKILL.md` - 스킬 정의 및 사용법
  - `skills/gemini-review/scripts/gemini_review.py` - 리뷰 실행 스크립트
  - `skills/gemini-review/scripts/setup_api_key.py` - API 키 설정 스크립트
  - `skills/gemini-review/references/review-criteria.md` - 리뷰 기준 문서
  - `gemini-review.skill` - 스킬 패키지 파일

---

### 4. 리뷰 UI 개선 및 방법론 도입

```
스킬을 좀 개선하자.
- 특히 가장 수정 필요한 것 위주로 알려주고 - 이 중 수정할 것을 선택하게 하는 UI가 되면 좋겠고.
- 그리고 네가 아는 코드 리뷰 방법론을 도입해서 개선 전략을 세워봐
```

**Claude 작업:**
- **Conventional Comments 방법론 도입:**
  - `issue(blocking)`: 반드시 수정 - 보안 취약점, 버그
  - `issue(non-blocking)`: 수정 권장 - 성능, 에러 핸들링
  - `suggestion`: 개선 제안 - 리팩토링, 패턴
  - `praise`: 잘한 점

- **인터랙티브 선택 UI 구현:**
  - 번호로 이슈 선택 가능
  - `blocking/all/skip` 옵션 제공

---

### 5. Thinking Level 자동 감지

**Claude 작업:**
- 코드 복잡도 기반 자동 분석 깊이 조절:
  - `minimal`: <100줄, 단순 코드 → 빠른 리뷰
  - `medium`: 여러 파일, 복잡한 로직 → 균형잡힌 리뷰 (기본값)
  - `high`: 보안 관련, >500줄 → 심층 분석

---

### 6. 병렬 리뷰 가능성 검토

```
코드 만드는 과정에서 병렬로 계속 봐줄 수도 있어?
```

**Claude 작업:**
- 병렬 리뷰 방식 분석:
  1. **Hook 방식**: Edit/Write 후 자동 트리거 (추천)
  2. **File Watcher**: 파일 변경 감지
  3. **현재 방식**: 순차 실행 (스킬 지침 기반)

---

### 7. Hook vs 스킬 지침 비교

```
hook 방식이랑 지금 방식 차이점은?
```

**Claude 작업:**
- 현재 방식: Claude가 지침 읽고 알아서 실행 (유연함)
- Hook 방식: 시스템이 강제 실행 (100% 보장)
- **결론**: 스킬 지침 방식 유지 (Claude가 결과 직접 처리 가능)

---

### 8. Gemini 리뷰 장점 정리

```
gemini api로 리뷰 시키면 토큰 절약되고, 다른 시각으로 리뷰 가능한거 맞아?
```

**Claude 작업:**
- **토큰 절약**: Gemini가 분석 → Claude는 결과만 처리
- **크로스 체크**: Claude 맹점을 Gemini가 보완
- **비용 효율**: Gemini Flash 저렴 ($0.10/1M input)
- **속도**: Gemini Flash 빠름

---

## 기술 스택

- **Language**: Python 3.x
- **AI Model**: Google Gemini 3.0 Flash
- **Package**: google-genai
- **Framework**: Claude Code Skills System
- **Methodology**: Conventional Comments

---

## 주요 기능

1. **자동 코드 리뷰** - Edit/Write 후 자동 실행
2. **인터랙티브 이슈 선택** - 번호로 선택, blocking/all/skip
3. **Thinking Level 자동 감지** - 복잡도 기반 분석 깊이
4. **Conventional Comments** - 표준 리뷰 방법론
5. **포커스 모드** - security/performance/quality
