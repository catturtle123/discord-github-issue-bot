"""Tests for agent.graph module."""

from unittest.mock import patch

from langgraph.graph import END

from agent.graph import _route_after_check, create_graph
from agent.state import IssueState


class TestRouteAfterCheck:
    """Tests for the _route_after_check routing function."""

    def test_routes_to_ask_question_when_insufficient(self) -> None:
        state: IssueState = {"completeness_status": "insufficient"}
        assert _route_after_check(state) == "ask_question"

    def test_routes_to_generate_draft_when_sufficient(self) -> None:
        state: IssueState = {"completeness_status": "sufficient"}
        assert _route_after_check(state) == "generate_draft"

    def test_routes_to_end_when_confirmed(self) -> None:
        state: IssueState = {"completeness_status": "confirmed"}
        assert _route_after_check(state) == END

    def test_defaults_to_ask_question_when_missing(self) -> None:
        state: IssueState = {}
        assert _route_after_check(state) == "ask_question"


class TestCreateGraph:
    """Tests for graph creation and compilation."""

    @patch("agent.graph.analyze")
    @patch("agent.graph.check_completeness")
    @patch("agent.graph.ask_question")
    @patch("agent.graph.generate_draft")
    def test_graph_compiles_successfully(
        self,
        mock_draft: object,
        mock_ask: object,
        mock_check: object,
        mock_analyze: object,
    ) -> None:
        graph = create_graph()
        assert graph is not None

    @patch("agent.graph.analyze")
    @patch("agent.graph.check_completeness")
    @patch("agent.graph.ask_question")
    @patch("agent.graph.generate_draft")
    def test_graph_has_expected_nodes(
        self,
        mock_draft: object,
        mock_ask: object,
        mock_check: object,
        mock_analyze: object,
    ) -> None:
        graph = create_graph()
        # CompiledStateGraph stores node names in its nodes dict
        node_names = set(graph.nodes.keys())
        expected = {"analyze", "check_completeness", "ask_question", "generate_draft"}
        assert expected.issubset(node_names)
