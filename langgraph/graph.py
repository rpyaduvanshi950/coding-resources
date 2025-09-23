"""Minimal subset of the LangGraph API for orchestrating synchronous pipelines."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Hashable, List, MutableMapping

END = "__end__"

NodeCallable = Callable[[Dict[str, Any]], Dict[str, Any]]


@dataclass
class CompiledGraph:
    nodes: Dict[Hashable, NodeCallable]
    edges: Dict[Hashable, List[Hashable]]
    entry_point: Hashable

    def invoke(self, state: MutableMapping[str, Any]) -> Dict[str, Any]:
        current_state: Dict[str, Any] = dict(state)
        current_node = self.entry_point
        while current_node != END:
            if current_node not in self.nodes:
                raise KeyError(f"Unknown node '{current_node}'")
            node_callable = self.nodes[current_node]
            update = node_callable(dict(current_state))
            if update:
                current_state.update(update)
            next_nodes = self.edges.get(current_node, [])
            if not next_nodes:
                break
            if len(next_nodes) > 1:
                raise NotImplementedError("Branching is not supported in this lightweight shim")
            current_node = next_nodes[0]
        return current_state


class StateGraph:
    """Simplified directed graph for chaining agent nodes."""

    def __init__(self, _state_type: type[MutableMapping[str, Any]]):
        self._nodes: Dict[Hashable, NodeCallable] = {}
        self._edges: Dict[Hashable, List[Hashable]] = {}
        self._entry_point: Hashable | None = None

    def add_node(self, name: Hashable, node: NodeCallable) -> None:
        self._nodes[name] = node

    def add_edge(self, source: Hashable, target: Hashable) -> None:
        self._edges.setdefault(source, []).append(target)

    def set_entry_point(self, name: Hashable) -> None:
        self._entry_point = name

    def compile(self) -> CompiledGraph:
        if self._entry_point is None:
            raise ValueError("Entry point must be set before compilation.")
        return CompiledGraph(nodes=self._nodes, edges=self._edges, entry_point=self._entry_point)


__all__ = ["StateGraph", "END"]
