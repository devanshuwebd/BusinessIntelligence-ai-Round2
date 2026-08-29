from __future__ import annotations

import json
import os
from typing import Any


def build_narrative_payload(kpi_name: str, snapshot: dict[str, Any], drivers: list[dict[str, Any]], evidence: list[dict[str, Any]], persona: str, confidence: dict[str, Any]) -> str:
    return json.dumps({
        "persona": persona, "kpi": kpi_name, "snapshot": snapshot,
        "drivers": drivers, "evidence": evidence, "confidence": confidence,
        "rules": ["Use only supplied values.", "Do not calculate new numbers.", "Do not claim causality when causal is false.", "Cite evidence IDs."],
    }, indent=2, default=str)


def calculate_confidence_score(data_quality: float, evidence_strength: float, history_support: float, contradiction_penalty: float = 0.0) -> float:
    score = (0.4 * data_quality) + (0.4 * evidence_strength) + (0.2 * history_support) - contradiction_penalty
    return round(max(0.0, min(1.0, score)) * 100, 2)


def llm_configured() -> bool:
    return bool(os.getenv("NEXAMART_LLM_URL"))
