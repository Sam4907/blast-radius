from typing import TypedDict, List, Dict, Any


class AnalysisResultSchema(TypedDict):
    target: str
    nodes: List[str]
    edges: List[List[str]]
    blast_radius: Dict[str, Any]
    ai_report: str