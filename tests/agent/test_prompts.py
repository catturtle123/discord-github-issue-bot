"""Tests for agent.prompts modules."""

from agent.prompts.analyze import get_analyze_prompt
from agent.prompts.ask import get_ask_prompt
from agent.prompts.draft import get_draft_prompt
from agent.prompts.judge import get_judge_prompt
from agent.prompts.system import SYSTEM_PROMPT


class TestSystemPrompt:
    """Tests for the system prompt."""

    def test_system_prompt_is_string(self) -> None:
        assert isinstance(SYSTEM_PROMPT, str)

    def test_system_prompt_is_in_korean(self) -> None:
        assert "Moalog" in SYSTEM_PROMPT
        assert "회고" in SYSTEM_PROMPT

    def test_system_prompt_contains_domain_areas(self) -> None:
        assert "auth" in SYSTEM_PROMPT
        assert "member" in SYSTEM_PROMPT
        assert "retrospect" in SYSTEM_PROMPT
        assert "webhook" in SYSTEM_PROMPT
        assert "config" in SYSTEM_PROMPT

    def test_system_prompt_contains_tech_stack(self) -> None:
        assert "Rust" in SYSTEM_PROMPT
        assert "Axum" in SYSTEM_PROMPT
        assert "SeaORM" in SYSTEM_PROMPT

    def test_system_prompt_contains_response_rules(self) -> None:
        assert "한국어" in SYSTEM_PROMPT


class TestAnalyzePrompt:
    """Tests for the analyze prompt template."""

    def test_renders_with_message_and_context(self) -> None:
        result = get_analyze_prompt("로그인이 안됩니다", "없음")
        assert "로그인이 안됩니다" in result
        assert "없음" in result

    def test_contains_json_format(self) -> None:
        result = get_analyze_prompt("test", "context")
        assert "issue_title" in result
        assert "issue_type" in result
        assert "affected_domain" in result

    def test_contains_domain_criteria(self) -> None:
        result = get_analyze_prompt("test", "context")
        assert "auth" in result
        assert "retrospect" in result

    def test_contains_severity_criteria(self) -> None:
        result = get_analyze_prompt("test", "context")
        assert "critical" in result
        assert "major" in result
        assert "minor" in result

    def test_multiline_context(self) -> None:
        context = "[user]: 첫번째 메시지\n[assistant]: 응답"
        result = get_analyze_prompt("두번째 메시지", context)
        assert "첫번째 메시지" in result
        assert "두번째 메시지" in result


class TestJudgePrompt:
    """Tests for the judge prompt template."""

    def test_renders_with_all_params(self) -> None:
        result = get_judge_prompt(
            title="오타 수정",
            description="에러 메시지 오타",
            issue_type="bug",
            affected_domain="config",
        )
        assert "오타 수정" in result
        assert "에러 메시지 오타" in result
        assert "bug" in result
        assert "config" in result

    def test_contains_auto_resolve_criteria(self) -> None:
        result = get_judge_prompt("title", "desc", "bug", "auth")
        assert "auto_resolve" in result
        assert "true" in result
        assert "false" in result

    def test_contains_moalog_specific_criteria(self) -> None:
        result = get_judge_prompt("title", "desc", "bug", "auth")
        assert "Rust" in result
        assert "Axum" in result
        assert "SeaORM" in result

    def test_contains_json_output_format(self) -> None:
        result = get_judge_prompt("title", "desc", "bug", "auth")
        assert "reason" in result


class TestAskPrompt:
    """Tests for the ask prompt template."""

    def test_renders_with_conversation_and_missing(self) -> None:
        result = get_ask_prompt(
            "[user]: 버그 발견",
            "- 이슈 제목\n- 재현 단계",
        )
        assert "버그 발견" in result
        assert "이슈 제목" in result
        assert "재현 단계" in result

    def test_contains_rules(self) -> None:
        result = get_ask_prompt("conversation", "- missing item")
        assert "한국어" in result
        assert "2~3" in result
        assert "Moalog" in result


class TestDraftPrompt:
    """Tests for the draft prompt template."""

    def test_renders_with_all_params(self) -> None:
        result = get_draft_prompt(
            title="Login bug",
            description="Cannot login",
            issue_type="bug",
            affected_domain="auth",
            severity="critical",
            steps="1. Go to login",
            expected="Should login",
            actual="Error 500",
            env_info="Chrome",
            labels_text="bug, domain:auth",
        )
        assert "Login bug" in result
        assert "Cannot login" in result
        assert "bug" in result
        assert "auth" in result
        assert "critical" in result
        assert "1. Go to login" in result
        assert "Chrome" in result
        assert "bug, domain:auth" in result

    def test_handles_empty_optional_fields(self) -> None:
        result = get_draft_prompt(
            title="Feature",
            description="Add export",
            issue_type="feature",
            affected_domain="retrospect",
            severity="minor",
            steps="",
            expected="",
            actual="",
            env_info="",
            labels_text="없음",
        )
        assert "해당 없음" in result
        assert "Feature" in result

    def test_contains_json_output_format(self) -> None:
        result = get_draft_prompt("t", "d", "bug", "auth", "minor", "", "", "", "", "없음")
        assert "draft_title" in result
        assert "draft_body" in result
