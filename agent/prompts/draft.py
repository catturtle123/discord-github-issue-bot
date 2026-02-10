def get_draft_prompt(
    title: str,
    description: str,
    issue_type: str,
    affected_domain: str,
    severity: str,
    steps: str,
    expected: str,
    actual: str,
    env_info: str,
    labels_text: str,
) -> str:
    """Generate a prompt to create a GitHub issue draft.

    Args:
        title: Issue title.
        description: Issue description.
        issue_type: Type of issue.
        affected_domain: Affected domain area.
        severity: Issue severity.
        steps: Steps to reproduce (for bugs).
        expected: Expected behavior (for bugs).
        actual: Actual behavior (for bugs).
        env_info: Environment information.
        labels_text: Comma-separated labels string.

    Returns:
        The draft generation prompt string.
    """
    return f"""\
아래 정보를 바탕으로 GitHub 이슈 초안을 작성하세요.

## 수집된 정보
- 제목: {title}
- 설명: {description}
- 유형: {issue_type}
- 도메인: {affected_domain}
- 심각도: {severity}
- 재현 단계: {steps or "해당 없음"}
- 기대 동작: {expected or "해당 없음"}
- 실제 동작: {actual or "해당 없음"}
- 환경 정보: {env_info or "해당 없음"}
- 라벨: {labels_text}

## 출력 형식

```json
{{
    "draft_title": "이슈 제목",
    "draft_body": "이슈 본문 (마크다운 형식, 한국어)"
}}
```

## 규칙
- 한국어로 작성하세요.
- 이슈 본문은 마크다운 형식으로 작성하세요.
- 기술 용어는 원어 그대로 사용하세요.
- 버그인 경우 재현 단계, 기대 동작, 실제 동작을 포함하세요.
- feature/improvement인 경우 배경, 제안, 기대 효과를 포함하세요.

JSON만 출력하세요."""
