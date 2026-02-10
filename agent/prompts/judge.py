def get_judge_prompt(
    title: str,
    description: str,
    issue_type: str,
    affected_domain: str,
) -> str:
    """Generate a prompt to judge whether an issue can be auto-resolved by AI.

    Args:
        title: Issue title.
        description: Issue description.
        issue_type: Type of issue (bug/feature/improvement/question).
        affected_domain: Affected domain area.

    Returns:
        The judgment prompt string.
    """
    return f"""\
아래 GitHub 이슈가 AI(claude-code-action)로 자동 해결 가능한지 판단하세요.

## 이슈 정보

- **제목**: {title}
- **설명**: {description}
- **유형**: {issue_type}
- **도메인**: {affected_domain}

## 판단 기준

### 자동 해결 가능 (auto_resolve: true)
- 오타 수정, 문자열 변경
- 간단한 버그 수정 (off-by-one, null 체크 누락, 조건문 오류)
- 설정값 변경 (환경변수, CORS 도메인 추가, timeout 조정)
- 에러 메시지 개선
- 로깅 추가
- 간단한 유효성 검증 추가
- 문서 업데이트 (README, 주석)
- 단순한 CRUD 엔드포인트 추가 (기존 패턴 따라가는 경우)
- 기존 코드의 리팩토링 (명확한 before/after가 있는 경우)

### 자동 해결 불가 (auto_resolve: false)
- 복잡한 아키텍처 변경 (레이어 구조 변경, 새로운 미들웨어 도입)
- 새로운 외부 서비스 연동 (새로운 OAuth 프로바이더, 결제 시스템)
- DB 스키마 대규모 변경 (테이블 추가, 관계 변경)
- 보안 관련 중요 변경 (인증 플로우 변경, 권한 체계 수정)
- 성능 최적화 (쿼리 최적화, 캐싱 전략)
- 비즈니스 로직의 근본적인 변경
- 요구사항이 모호하거나 추가 논의가 필요한 경우

### 조건부 가능 (상세 스펙이 있으면 가능)
- 새로운 API 엔드포인트 (기존 handler/service 패턴이 명확한 경우)
- 새로운 DTO 추가 (필드가 명확히 정의된 경우)
- 에러 핸들링 패턴 추가 (기존 AppError 패턴 따르는 경우)

## Moalog 프로젝트 특성

- Rust/Axum 프로젝트이므로 타입 시스템이 엄격함
- SeaORM 엔티티 변경은 마이그레이션 필요
- handler → service → entity 레이어 구조를 따름
- 에러는 AppError enum에 변형 추가 필요

## 출력 형식

```json
{{
    "auto_resolve": true | false,
    "confidence": "high | medium | low",
    "reason": "판단 근거를 한국어로 1~2문장으로 설명"
}}
```

- **confidence 기준**:
  - high: 확실히 자동 해결 가능/불가능한 경우
  - medium: 조건부로 가능하거나, 상세 스펙에 따라 달라지는 경우
  - low: 판단이 어렵거나 추가 정보가 필요한 경우

JSON만 출력하세요."""
