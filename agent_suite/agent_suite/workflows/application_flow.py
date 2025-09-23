"""LangGraph workflow orchestrating the Agent Suite pipeline."""

from __future__ import annotations

from typing import Any, Dict, List, TypedDict

from langgraph.graph import END, StateGraph

from agent_suite.agents import (
    AgentContext,
    CommunicationsAgent,
    JobDescriptionParserAgent,
    ProfileAgent,
    ResumeAgent,
    SearchAgent,
    SenderAgent,
    TrackerAgent,
)


class ApplicationState(TypedDict, total=False):
    """Shared state flowing through the workflow graph."""

    profile: Dict[str, Any]
    jobs: List[Dict[str, Any]]
    parsed_jobs: List[Dict[str, Any]]
    resumes: List[Dict[str, Any]]
    communications: List[Dict[str, Any]]
    submissions: List[Dict[str, Any]]
    dashboard: List[Dict[str, Any]]
    auto_send: bool
    review_status: str


class ApplicationWorkflow:
    """Build and execute the Agent Suite LangGraph workflow."""

    def __init__(self) -> None:
        self._context = AgentContext()
        self._profile_agent = ProfileAgent()
        self._search_agent = SearchAgent()
        self._parser_agent = JobDescriptionParserAgent()
        self._resume_agent = ResumeAgent()
        self._comms_agent = CommunicationsAgent()
        self._sender_agent = SenderAgent()
        self._tracker_agent = TrackerAgent()
        self._graph = self._build_graph()

    def _build_graph(self) -> StateGraph[ApplicationState]:
        graph: StateGraph[ApplicationState] = StateGraph(ApplicationState)

        graph.add_node("profile_agent", self._profile_node)
        graph.add_node("search_agent", self._search_node)
        graph.add_node("jd_parser_agent", self._jd_parser_node)
        graph.add_node("resume_agent", self._resume_node)
        graph.add_node("communications_agent", self._communications_node)
        graph.add_node("human_review", self._human_review_node)
        graph.add_node("sender_agent", self._sender_node)
        graph.add_node("tracker_agent", self._tracker_node)

        graph.set_entry_point("profile_agent")
        graph.add_edge("profile_agent", "search_agent")
        graph.add_edge("search_agent", "jd_parser_agent")
        graph.add_edge("jd_parser_agent", "resume_agent")
        graph.add_edge("resume_agent", "communications_agent")
        graph.add_edge("communications_agent", "human_review")
        graph.add_conditional_edges(
            "human_review",
            self._review_decision,
            {
                "auto": "sender_agent",
                "pending": END,
            },
        )
        graph.add_edge("sender_agent", "tracker_agent")
        graph.add_edge("tracker_agent", END)

        return graph

    async def run(self, initial_state: ApplicationState) -> ApplicationState:
        """Execute the workflow asynchronously."""

        compiled = self._graph.compile()
        result_state: ApplicationState = await compiled.ainvoke(initial_state)
        return result_state

    async def _profile_node(self, state: ApplicationState) -> ApplicationState:
        profile_data = state.get("profile", {})
        result = await self._profile_agent.arun(profile_data, self._context)
        state["profile"] = result.output
        return state

    async def _search_node(self, state: ApplicationState) -> ApplicationState:
        result = await self._search_agent.arun(state, self._context)
        state["jobs"] = result.output
        return state

    async def _jd_parser_node(self, state: ApplicationState) -> ApplicationState:
        result = await self._parser_agent.arun(state.get("jobs", []), self._context)
        state["parsed_jobs"] = result.output
        return state

    async def _resume_node(self, state: ApplicationState) -> ApplicationState:
        result = await self._resume_agent.arun(state.get("parsed_jobs", []), self._context)
        state["resumes"] = result.output
        return state

    async def _communications_node(self, state: ApplicationState) -> ApplicationState:
        result = await self._comms_agent.arun(state.get("resumes", []), self._context)
        state["communications"] = result.output
        return state

    async def _human_review_node(self, state: ApplicationState) -> ApplicationState:
        if not state.get("auto_send", True):
            state["review_status"] = "pending"
        else:
            state["review_status"] = "auto"
        return state

    def _review_decision(self, state: ApplicationState) -> str:
        return "auto" if state.get("review_status") == "auto" else "pending"

    async def _sender_node(self, state: ApplicationState) -> ApplicationState:
        result = await self._sender_agent.arun(state.get("communications", []), self._context)
        state["submissions"] = result.output
        return state

    async def _tracker_node(self, state: ApplicationState) -> ApplicationState:
        result = await self._tracker_agent.arun(state.get("submissions", []), self._context)
        state["dashboard"] = result.output
        return state


__all__ = ["ApplicationWorkflow", "ApplicationState"]
