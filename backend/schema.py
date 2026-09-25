import json
from typing import Dict, List, TypedDict


class BlastRadiusImpact(TypedDict):
    direct: List[str]
    indirect: List[str]


class AnalysisResultSchema(TypedDict):
    target: str
    nodes: List[str]
    edges: List[List[str]]
    blast_radius: Dict[str, Any]
    ai_report: str
