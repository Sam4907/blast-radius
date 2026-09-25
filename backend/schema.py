import json
from typing import Any, Dict, List, TypedDict  # Added Any here


class BlastRadiusImpact(TypedDict):
    direct: List[str]
    indirect: List[str]


class AnalysisResultSchema(TypedDict):
    target: str
    nodes: List[str]
    edges: List[List[str]]
    blast_radius: BlastRadiusImpact  # Typed strictly to match the dict
    ai_report: str