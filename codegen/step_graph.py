from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
import json

@dataclass
class Step:
    id: str
    intent: str
    pre_refs: List[str] = field(default_factory=list)
    post_refs: List[str] = field(default_factory=list)
    invariant_refs: List[str] = field(default_factory=list)
    evidence_hooks: List[str] = field(default_factory=list)
    parents: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict) -> "Step":
        return cls(
            id=data.get("id", ""),
            intent=data.get("intent", ""),
            pre_refs=data.get("pre_refs", []) or [],
            post_refs=data.get("post_refs", []) or [],
            invariant_refs=data.get("invariant_refs", []) or [],
            evidence_hooks=data.get("evidence_hooks", []) or [],
            parents=data.get("parents", []) or [],
            children=data.get("children", []) or [],
        )

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "intent": self.intent,
            "pre_refs": self.pre_refs,
            "post_refs": self.post_refs,
            "invariant_refs": self.invariant_refs,
            "evidence_hooks": self.evidence_hooks,
            "parents": self.parents,
            "children": self.children,
        }

@dataclass
class StepGraph:
    steps: List[Step]
    edges: List[Tuple[str, str]] = field(default_factory=list)  # (parent, child)
    order: List[str] = field(default_factory=list)  # optional linearization
    version: int = 1

    @classmethod
    def from_json(cls, raw: str) -> "StepGraph":
        data = json.loads(raw)
        return cls.from_dict(data)

    @classmethod
    def from_dict(cls, data: Dict) -> "StepGraph":
        steps = [Step.from_dict(s) for s in data.get("steps", [])]
        edges = [tuple(e) for e in data.get("edges", [])]
        order = data.get("order", [])
        return cls(steps=steps, edges=edges, order=order, version=data.get("version", 1))

    def to_dict(self) -> Dict:
        return {
            "version": self.version,
            "steps": [s.to_dict() for s in self.steps],
            "edges": self.edges,
            "order": self.order,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

class StepGraphValidationError(Exception):
    pass

class StepGraphValidator:
    @staticmethod
    def validate(graph: StepGraph, pre_ids: Set[str], post_ids: Set[str], invariant_ids: Set[str]):
        issues = []
        id_set = set()
        for s in graph.steps:
            if not s.id:
                issues.append("Step id empty")
            if s.id in id_set:
                issues.append(f"Duplicate step id {s.id}")
            id_set.add(s.id)
            if not s.intent:
                issues.append(f"Step {s.id} intent empty")
            for r in s.pre_refs:
                if r not in pre_ids:
                    issues.append(f"Step {s.id} unknown pre_ref {r}")
            for r in s.post_refs:
                if r not in post_ids:
                    issues.append(f"Step {s.id} unknown post_ref {r}")
            for r in s.invariant_refs:
                if r not in invariant_ids:
                    issues.append(f"Step {s.id} unknown invariant_ref {r}")
        # edge endpoints
        step_ids = {s.id for s in graph.steps}
        for a, b in graph.edges:
            if a not in step_ids:
                issues.append(f"Edge parent {a} not a step id")
            if b not in step_ids:
                issues.append(f"Edge child {b} not a step id")
        # order if present must cover all
        if graph.order:
            if set(graph.order) != step_ids:
                issues.append("Order does not cover exactly all step ids")
        if issues:
            raise StepGraphValidationError("; ".join(issues))
