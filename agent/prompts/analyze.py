def get_analyze_prompt(message: str, context: str) -> str:
    """Generate a prompt to analyze a user message and extract issue information.

    Args:
        message: The latest user message.
        context: Previous conversation context (formatted message history).

    Returns:
        The analysis prompt string.
    """
    return f"""\
아래 사용자의 메시지를 분석하여 GitHub 이슈 정보를 추출하세요.

## 이전 대화 맥락
{context}

## 최신 메시지
{message}

## 추출할 정보

다음 정보를 JSON 형식으로 추출하세요. 메시지에서 파악할 수 없는 항목은 null로 설정하세요.

```json
{{
    "issue_title": "이슈 제목 (간결하고 명확하게)",
    "issue_description": "이슈 설명 (상세하게)",
    "issue_type": "bug | feature | improvement | question",
    "affected_domain": "auth | member | retrospect | ai | webhook | config | other",
    "severity": "critical | major | minor",
    "steps_to_reproduce": "재현 단계 (버그인 경우)",
    "expected_behavior": "기대 동작 (버그인 경우)",
    "actual_behavior": "실제 동작 (버그인 경우)",
    "environment_info": "환경 정보 (OS, 브라우저 등)",
    "labels": ["라벨1", "라벨2"]
}}
```

## 도메인 판단 기준

- **auth**: 로그인, 회원가입, JWT, OAuth, 토큰, 인증, 인가 관련
- **member**: 프로필, 회원 정보, 탈퇴, 닉네임 관련
- **retrospect**: 회고방, 회고, 답변, 댓글, 좋아요, 참고자료, PDF, 초대코드, KPT/4L/5F/PMI/FREE 관련
- **ai**: AI 분석, 어시스턴트, OpenAI, 프롬프트 관련
- **webhook**: Discord/GitHub 웹훅, 알림 관련
- **config**: 환경변수, DB 설정, CORS, 미들웨어 관련
- **other**: 위 도메인에 해당하지 않는 경우

## 심각도 판단 기준

- **critical**: 서비스 전체 장애, 데이터 손실, 보안 취약점
- **major**: 주요 기능 동작 불가, 사용자 경험 심각한 저하
- **minor**: 사소한 UI 문제, 오타, 개선 사항

## 라벨 자동 부여 규칙

- issue_type에 따라: bug → "bug", feature → "enhancement",
  improvement → "improvement", question → "question"
- affected_domain 값을 라벨에 추가 (예: "domain:retrospect")
- severity가 critical이면 "priority:critical" 추가

JSON만 출력하세요. 추가 설명은 불필요합니다."""
