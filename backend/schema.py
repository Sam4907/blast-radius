import json
from typing import Dict, List, TypedDict


class BlastRadiusImpact(TypedDict):
    direct: List[str]
    indirect: List[str]


class AnalysisResultSchema(TypedDict):
    target: str
    nodes: List[str]
    edges: List[List[str]]  # List of [caller, callee] pairs
    blast_radius: BlastRadiusImpact
    ai_report: str


def validate_analysis_payload(payload: dict) -> bool:
    """Validates that an analysis output dictionary adheres to the required schema."""
    required_keys = {"target", "nodes", "edges", "blast_radius"}
    if not required_keys.issubset(payload.keys()):
        return False

    blast_radius = payload.get("blast_radius", {})
    if "direct" not in blast_radius or "indirect" not in blast_radius:
        return False

    return True