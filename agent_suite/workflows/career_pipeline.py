"""LangGraph workflow orchestrating the career assistant agents."""

from __future__ import annotations

from typing import Any, Dict

from langgraph.graph import END, StateGraph

from agent_suite.agents.comms import CommsAgent
from agent_suite.agents.jd_parser import JDParserAgent
from agent_suite.agents.profile import ProfileAgent
from agent_suite.agents.resume import ResumeAgent
from agent_suite.agents.review import ReviewAgent
from agent_suite.agents.search import SearchAgent
from agent_suite.agents.sender import SenderAgent
from agent_suite.agents.tracker import TrackerAgent
from agent_suite.utils.telemetry import span
from agent_suite.workflows.state import CareerState


def build_career_workflow() -> StateGraph:
    """Create and return the compiled LangGraph workflow."""

    graph: StateGraph = StateGraph(dict)

    profile_agent = ProfileAgent()
    search_agent = SearchAgent()
    jd_parser = JDParserAgent()
    resume_agent = ResumeAgent()
    comms_agent = CommsAgent()
    review_agent = ReviewAgent()
    sender_agent = SenderAgent()
    tracker_agent = TrackerAgent()

    def run_agent(agent, state: Dict[str, Any]) -> Dict[str, Any]:
        with span(agent.__class__.__name__):
            result = agent.run(state)
            return result.payload

    graph.add_node("profile", lambda state: run_agent(profile_agent, state))
    graph.add_node("search", lambda state: run_agent(search_agent, state))
    graph.add_node("jd_parser", lambda state: run_agent(jd_parser, state))
    graph.add_node("resume", lambda state: run_agent(resume_agent, state))
    graph.add_node("comms", lambda state: run_agent(comms_agent, state))
    graph.add_node("review", lambda state: run_agent(review_agent, state))
    graph.add_node("sender", lambda state: run_agent(sender_agent, state))
    graph.add_node("tracker", lambda state: run_agent(tracker_agent, state))

    graph.set_entry_point("profile")
    graph.add_edge("profile", "search")
    graph.add_edge("search", "jd_parser")
    graph.add_edge("jd_parser", "resume")
    graph.add_edge("resume", "comms")
    graph.add_edge("comms", "review")
    graph.add_edge("review", "sender")
    graph.add_edge("sender", "tracker")
    graph.add_edge("tracker", END)

    return graph.compile()


def run_pipeline(initial_state: CareerState) -> CareerState:
    """Execute the workflow using the provided initial state."""

    workflow = build_career_workflow()
    result_state = workflow.invoke(initial_state.to_dict())
    return CareerState(**result_state)


__all__ = ["build_career_workflow", "run_pipeline"]
