import json

from fastapi.testclient import TestClient

from Nexamart_BI.backend import main


def test_api_loads_server_context_and_persists_telemetry(tmp_path, monkeypatch):
    context_path = tmp_path / "insight_context.json"
    context_path.write_text(json.dumps({
        "insight_id": "revenue-test",
        "snapshot": {"total_revenue": 100},
        "confidence": {"status": "abstain", "reasons": ["sparse_history"]},
        "drivers": [],
    }), encoding="utf-8")
    monkeypatch.setattr(main, "CONTEXT_PATH", context_path)
    monkeypatch.setattr(main, "DB", tmp_path / "state.db")
    monkeypatch.setattr(main, "API_TOKEN", "")
    monkeypatch.setattr(main, "ROLE_TOKENS", {})
    client = TestClient(main.app)

    response = client.post("/api/generate-insight", json={"persona": "Analyst", "insight_id": "revenue-test", "snapshot": {"total_revenue": 999999}})
    assert response.status_code == 200
    assert response.json()["status"] == "abstained"
    assert response.json()["telemetry"]["model_calls"] == 0

    unknown = client.post("/api/generate-insight", json={"persona": "Analyst", "insight_id": "caller-invented"})
    assert unknown.status_code == 404

    feedback = client.post("/api/log-feedback", json={
        "insight_id": "revenue-test", "user_id": "analyst-1", "persona": "Analyst",
        "predicted_driver": "volume", "corrected_driver": "price_mix",
        "recommendation_rating": "Incorrect / Flawed", "free_text": "verify",
    })
    assert feedback.status_code == 200
    assert feedback.json()["status"] == "persisted"

    telemetry = client.get("/api/telemetry/latest")
    assert telemetry.status_code == 200
    assert telemetry.json()["rows"][0]["status"] == "abstained"

    evaluation = client.get("/api/feedback/evaluation")
    assert evaluation.status_code == 200
    assert evaluation.json()["feedback_count"] == 1
    assert evaluation.json()["by_predicted_driver"]["volume"]["correction_rate"] == 1.0


def test_role_tokens_are_server_checked(tmp_path, monkeypatch):
    context_path = tmp_path / "insight_context.json"
    context_path.write_text(json.dumps({"insight_id": "r", "confidence": {"status": "abstain"}}), encoding="utf-8")
    monkeypatch.setattr(main, "CONTEXT_PATH", context_path)
    monkeypatch.setattr(main, "DB", tmp_path / "state.db")
    monkeypatch.setattr(main, "API_TOKEN", "")
    monkeypatch.setattr(main, "ROLE_TOKENS", {"Executive": "exec-secret"})
    client = TestClient(main.app)

    denied = client.post("/api/generate-insight", json={"persona": "Executive", "insight_id": "r"})
    assert denied.status_code == 401
    allowed = client.post("/api/generate-insight", headers={"X-Nexamart-Token": "exec-secret"}, json={"persona": "Executive", "insight_id": "r"})
    assert allowed.status_code == 200
    assert allowed.json()["status"] == "abstained"


def test_demo_narration_is_persona_specific_and_evidence_cited(tmp_path, monkeypatch):
    context_path = tmp_path / "insight_context.json"
    context_path.write_text(json.dumps({
        "insight_id": "narrative-test",
        "snapshot": {"total_revenue": 100},
        "movement": {"revenue_change_pct": -0.12},
        "confidence": {"status": "proceed", "reasons": []},
        "drivers": [{"evidence_id": "driver-1", "driver": "volume", "effect": -10}],
        "supporting_signals": [{"evidence_id": "signal-1", "signal": "inventory", "value": 2}],
    }), encoding="utf-8")
    monkeypatch.setattr(main, "CONTEXT_PATH", context_path)
    monkeypatch.setattr(main, "DB", tmp_path / "state.db")
    monkeypatch.setattr(main, "API_TOKEN", "")
    monkeypatch.setattr(main, "ROLE_TOKENS", {})
    monkeypatch.setattr(main, "LLM_URL", "")
    monkeypatch.setattr(main, "DEMO_MODE", True)
    client = TestClient(main.app)

    executive = client.post("/api/generate-insight", json={"persona": "Executive", "insight_id": "narrative-test"})
    analyst = client.post("/api/generate-insight", json={"persona": "Analyst", "insight_id": "narrative-test"})
    assert executive.status_code == analyst.status_code == 200
    assert executive.json()["status"] == analyst.json()["status"] == "demo_ok"
    assert executive.json()["narrative"] != analyst.json()["narrative"]
    assert executive.json()["cited_evidence_ids"] == ["driver-1", "signal-1"]


def test_regional_snapshot_is_filtered_on_server(tmp_path, monkeypatch):
    context_path = tmp_path / "insight_context.json"
    context_path.write_text(json.dumps({
        "insight_id": "regional-test",
        "confidence": {"status": "abstain"},
        "regional_snapshot": [
            {"region": "North", "total_revenue": 10},
            {"region": "West", "total_revenue": 20},
        ],
    }), encoding="utf-8")
    monkeypatch.setattr(main, "CONTEXT_PATH", context_path)
    monkeypatch.setattr(main, "DB", tmp_path / "state.db")
    monkeypatch.setattr(main, "API_TOKEN", "shared-secret")
    monkeypatch.setattr(main, "ROLE_TOKENS", {})
    client = TestClient(main.app)

    response = client.get("/api/regional-snapshot", params={"persona": "Analyst", "insight_id": "regional-test"}, headers={"X-Nexamart-Token": "shared-secret"})
    assert response.status_code == 200
    assert [row["region"] for row in response.json()["rows"]] == ["North"]
