def get_ask_prompt(conversation: str, missing_text: str) -> str:
    """Generate a prompt to create follow-up questions for missing issue info.

    Args:
        conversation: Formatted conversation history.
        missing_text: Bulleted list of missing information items.

    Returns:
        The follow-up question prompt string.
    """
    return f"""\
아래 대화를 바탕으로, 이슈 생성에 필요한 추가 정보를 요청하는 후속 질문을 생성하세요.

## 대화 내용
{conversation}

## 부족한 정보
{missing_text}

## 규칙
- 한국어로 질문하세요.
- 최대 2~3개의 질문만 하세요.
- 친절하지만 간결하게 작성하세요.
- Moalog 프로젝트의 도메인 맥락을 고려하여 질문하세요.
- 질문만 출력하세요. 추가 설명은 불필요합니다."""
