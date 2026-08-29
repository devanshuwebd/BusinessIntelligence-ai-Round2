from pathlib import Path
import hmac
import json
import os
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Literal

import requests
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="NexaMart Intelligence API", version="2.2")
ROOT = Path(__file__).resolve().parents[1]
DB = Path(os.getenv("NEXAMART_STATE_DB", ROOT / "gold_layer" / "nexamart_state.db"))
CONTEXT_PATH = Path(os.getenv("NEXAMART_CONTEXT_PATH", ROOT / "gold_layer" / "insight_context.json"))
LLM_URL = os.getenv("NEXAMART_LLM_URL", "")
LLM_TOKEN = os.getenv("NEXAMART_LLM_TOKEN", "")
LLM_MODEL = os.getenv("NEXAMART_LLM_MODEL", "qwen2.5:7b")
DEMO_MODE = os.getenv("NEXAMART_DEMO_MODE", "1" if os.getenv("NEXAMART_ENV", "development") != "production" else "0") == "1"
API_TOKEN = os.getenv("NEXAMART_API_TOKEN", "")
INPUT_COST_PER_1K = float(os.getenv("NEXAMART_LLM_INPUT_COST_PER_1K", "0"))
OUTPUT_COST_PER_1K = float(os.getenv("NEXAMART_LLM_OUTPUT_COST_PER_1K", "0"))
try:
    ROLE_TOKENS = json.loads(os.getenv("NEXAMART_ROLE_TOKENS", "{}"))
except json.JSONDecodeError as exc:
    raise RuntimeError("NEXAMART_ROLE_TOKENS must be valid JSON") from exc
if os.getenv("NEXAMART_ENV", "development") == "production" and not API_TOKEN and not ROLE_TOKENS:
    raise RuntimeError("Configure NEXAMART_API_TOKEN or NEXAMART_ROLE_TOKENS in production")
ROLE_REGIONS = {"Executive": {"North", "South", "East", "West", "Central"}, "Analyst": {"North", "South", "East"}}


class InsightRequest(BaseModel):
    persona: Literal["Executive", "Analyst"]
    insight_id: str = Field(min_length=1, max_length=200)


class FeedbackRequest(BaseModel):
    insight_id: str = Field(min_length=1, max_length=200)
    user_id: str = Field(min_length=1, max_length=200)
    persona: Literal["Executive", "Analyst"]
    predicted_driver: str = ""
    corrected_driver: str = ""
    recommendation_rating: str = ""
    free_text: str = Field(default="", max_length=2000)
    evidence_version: str = "pipeline_v2"


def connection():
    DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS insight_feedback (feedback_id TEXT PRIMARY KEY, insight_id TEXT NOT NULL, user_id TEXT NOT NULL, persona TEXT NOT NULL, predicted_driver TEXT, corrected_driver TEXT, recommendation_rating TEXT, free_text TEXT, created_at TEXT, evidence_version TEXT);
    CREATE TABLE IF NOT EXISTS runtime_telemetry (request_id TEXT PRIMARY KEY, insight_id TEXT, model TEXT, model_calls INTEGER, latency_ms REAL, prompt_tokens INTEGER, completion_tokens INTEGER, total_tokens INTEGER, estimated_cost_usd REAL, status TEXT, created_at TEXT);
    """)
    conn.commit()
    return conn


def auth(token: str | None, persona: str | None = None):
    if ROLE_TOKENS:
        expected = ROLE_TOKENS.get(persona or "")
        if not expected or token is None or not hmac_compare(token, expected):
            raise HTTPException(status_code=401, detail="Unauthorized role token")
    elif API_TOKEN and (token is None or not hmac_compare(token, API_TOKEN)):
        raise HTTPException(status_code=401, detail="Unauthorized API token")


def hmac_compare(left: str, right: str) -> bool:
    return hmac.compare_digest(left, right)


def load_context(insight_id: str) -> dict[str, Any]:
    try:
        context = json.loads(CONTEXT_PATH.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=503, detail="Server insight context is unavailable") from exc
    if context.get("insight_id") != insight_id:
        raise HTTPException(status_code=404, detail="Unknown insight_id; use a server-generated insight reference")
    return context


def context_evidence(context: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = list(context.get("drivers", [])) + list(context.get("supporting_signals", [])) + list(context.get("policy_evidence", []))
    lineage = context.get("lineage")
    if lineage:
        evidence.append({"evidence_id": "lineage", **lineage})
    return [item for item in evidence if item.get("evidence_id")]


def feedback_learning() -> dict[str, Any]:
    conn = connection()
    rows = conn.execute("SELECT predicted_driver, corrected_driver, recommendation_rating FROM insight_feedback").fetchall()
    conn.close()
    by_driver: dict[str, dict[str, int]] = {}
    for row in rows:
        driver = row["predicted_driver"] or "unknown"
        record = by_driver.setdefault(driver, {"feedback_count": 0, "correction_count": 0, "positive_rating_count": 0})
        record["feedback_count"] += 1
        if row["corrected_driver"] and row["corrected_driver"] != driver:
            record["correction_count"] += 1
        if row["recommendation_rating"] == "Correct / Accurate":
            record["positive_rating_count"] += 1
    for record in by_driver.values():
        record["correction_rate"] = round(record["correction_count"] / record["feedback_count"], 4) if record["feedback_count"] else 0
        record["needs_expert_review"] = record["correction_rate"] >= 0.5 and record["feedback_count"] >= 2
    return {"feedback_count": len(rows), "by_predicted_driver": by_driver, "purpose": "calibration signal only; never replaces deterministic KPI evidence"}


def save_telemetry(row):
    conn = connection()
    conn.execute("INSERT OR REPLACE INTO runtime_telemetry VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", tuple(row[k] for k in ["request_id", "insight_id", "model", "model_calls", "latency_ms", "prompt_tokens", "completion_tokens", "total_tokens", "estimated_cost_usd", "status", "created_at"]))
    conn.commit()
    conn.close()


def write_telemetry(request_id, insight_id, started, status, model_calls, prompt_tokens=0, completion_tokens=0):
    total = prompt_tokens + completion_tokens
    cost = (prompt_tokens / 1000) * INPUT_COST_PER_1K + (completion_tokens / 1000) * OUTPUT_COST_PER_1K
    latency = round((time.perf_counter() - started) * 1000, 2)
    telemetry = {"request_id": request_id, "model": LLM_MODEL, "model_calls": model_calls, "latency_ms": latency, "prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens, "total_tokens": total, "estimated_cost_usd": round(cost, 8)}
    save_telemetry({**telemetry, "insight_id": insight_id, "estimated_cost_usd": round(cost, 8), "status": status, "created_at": datetime.now(timezone.utc).isoformat()})
    return telemetry


@app.get("/api/health")
def health():
    return {"status": "ok", "llm_configured": bool(LLM_URL), "demo_mode": DEMO_MODE, "server_context": CONTEXT_PATH.exists(), "role_tokens_configured": bool(ROLE_TOKENS), "state_db": str(DB)}


@app.get("/api/regional-snapshot")
def regional_snapshot(persona: Literal["Executive", "Analyst"], insight_id: str, x_nexamart_token: str | None = Header(default=None)):
    auth(x_nexamart_token, persona)
    context = load_context(insight_id)
    allowed = ROLE_REGIONS[persona]
    rows = [row for row in context.get("regional_snapshot", []) if row.get("region") in allowed]
    return {"persona": persona, "insight_id": insight_id, "regions": sorted(allowed), "rows": rows, "authorization_mode": "server_role_entitlement" if ROLE_TOKENS else "demo_role_entitlement"}


@app.post("/api/generate-insight")
def generate_insight(req: InsightRequest, x_nexamart_token: str | None = Header(default=None)):
    auth(x_nexamart_token, req.persona)
    request_id, started = str(uuid.uuid4()), time.perf_counter()
    context = load_context(req.insight_id)
    gate = context.get("confidence", {})
    if gate.get("status") != "proceed":
        telemetry = write_telemetry(request_id, req.insight_id, started, "abstained", 0)
        return {"status": "abstained", "insight_id": req.insight_id, "narrative": "There is not enough reliable evidence to explain this movement yet.", "cited_evidence_ids": [], "reasons": gate.get("reasons", ["confidence_gate_failed"]), "telemetry": telemetry}
    if not LLM_URL and DEMO_MODE:
        evidence = context_evidence(context)
        cited = [item["evidence_id"] for item in evidence[:2]]
        driver = context.get("drivers", [{}])[0].get("driver", "the observed drivers")
        change = context.get("movement", {}).get("revenue_change_pct")
        change_text = f"{float(change) * 100:.1f}%" if isinstance(change, (int, float)) else "the recorded amount"
        if req.persona == "Executive":
            narrative = f"Revenue changed by {change_text}; the leading evidence-linked signal is {driver}. Review the gated action list before making a decision."
        else:
            narrative = f"Revenue changed by {change_text}. The deterministic decomposition ranks {driver} first; supporting signals are observational, not causal, and the confidence gate is {gate.get('status')}."
        telemetry = write_telemetry(request_id, req.insight_id, started, "demo_ok", 0)
        return {"status": "demo_ok", "insight_id": req.insight_id, "narrative": narrative, "cited_evidence_ids": cited, "reasons": ["llm_not_configured_demo_mode"], "telemetry": telemetry}
    if not LLM_URL:
        telemetry = write_telemetry(request_id, req.insight_id, started, "not_configured", 0)
        return {"status": "error", "insight_id": req.insight_id, "narrative": "Insight generation is unavailable because NEXAMART_LLM_URL is not configured.", "reasons": ["llm_not_configured"], "telemetry": telemetry}

    evidence = context_evidence(context)
    allowed_ids = {str(item["evidence_id"]) for item in evidence}
    if not allowed_ids:
        telemetry = write_telemetry(request_id, req.insight_id, started, "invalid_evidence", 0)
        return {"status": "error", "insight_id": req.insight_id, "narrative": "No server evidence is available; the service will not generate an untraceable explanation.", "reasons": ["missing_server_evidence"], "telemetry": telemetry}

    payload = {
        "persona": req.persona,
        "snapshot": context.get("snapshot", {}),
        "movement": context.get("movement", {}),
        "drivers": context.get("drivers", []),
        "supporting_signals": context.get("supporting_signals", []),
        "actions": context.get("actions", []),
        "evidence": evidence,
        "confidence": gate,
        "feedback_learning": feedback_learning(),
        "rules": ["Use only server-supplied values", "Do not calculate new numbers", "Do not claim causality when causal is false", "Return JSON with narrative and cited_evidence_ids", "Cite only supplied evidence IDs", "Executive: concise decision summary; Analyst: include methods and uncertainty"],
    }
    prompt_tokens = completion_tokens = 0
    try:
        response = requests.post(LLM_URL, headers={"Authorization": f"Bearer {LLM_TOKEN}"} if LLM_TOKEN else {}, json={"model": LLM_MODEL, "prompt": json.dumps(payload, default=str), "stream": False, "format": "json", "options": {"temperature": 0.1}}, timeout=30)
        response.raise_for_status()
        body = response.json()
        parsed = json.loads(body.get("response", "{}"))
        narrative = parsed.get("narrative")
        cited = parsed.get("cited_evidence_ids")
        if not isinstance(narrative, str) or not narrative.strip() or not isinstance(cited, list) or not cited or not set(map(str, cited)).issubset(allowed_ids):
            raise ValueError("model_output_not_evidence_bounded")
        prompt_tokens, completion_tokens = int(body.get("prompt_eval_count") or 0), int(body.get("eval_count") or 0)
        telemetry = write_telemetry(request_id, req.insight_id, started, "ok", 1, prompt_tokens, completion_tokens)
        return {"status": "ok", "insight_id": req.insight_id, "narrative": narrative.strip(), "cited_evidence_ids": list(map(str, cited)), "telemetry": telemetry}
    except (requests.RequestException, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        telemetry = write_telemetry(request_id, req.insight_id, started, "error", 1, prompt_tokens, completion_tokens)
        return {"status": "error", "insight_id": req.insight_id, "narrative": "No explanation was generated because the insight service failed or returned untraceable output.", "reasons": [type(exc).__name__], "telemetry": telemetry}


@app.post("/api/log-feedback")
def log_feedback(req: FeedbackRequest, x_nexamart_token: str | None = Header(default=None)):
    auth(x_nexamart_token, req.persona)
    load_context(req.insight_id)
    feedback_id = str(uuid.uuid4())
    conn = connection()
    conn.execute("INSERT INTO insight_feedback VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (feedback_id, req.insight_id, req.user_id, req.persona, req.predicted_driver, req.corrected_driver, req.recommendation_rating, req.free_text, datetime.now(timezone.utc).isoformat(), req.evidence_version))
    conn.commit()
    conn.close()
    return {"status": "persisted", "feedback_id": feedback_id, "insight_id": req.insight_id}


@app.get("/api/feedback/evaluation")
def feedback_evaluation(x_nexamart_token: str | None = Header(default=None)):
    auth(x_nexamart_token)
    return feedback_learning()


@app.get("/api/telemetry/latest")
def latest_telemetry(x_nexamart_token: str | None = Header(default=None)):
    auth(x_nexamart_token)
    conn = connection()
    rows = [dict(row) for row in conn.execute("SELECT * FROM runtime_telemetry ORDER BY created_at DESC LIMIT 20").fetchall()]
    conn.close()
    return {"rows": rows}
