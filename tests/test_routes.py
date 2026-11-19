# tests/test_routes.py
# Integration tests for all Flask API routes.
# All watsonx.ai calls are mocked — no live credentials needed.

import json
import pytest
from unittest.mock import patch

from tests.conftest import (
    MOCK_STROKE_RISK,
    MOCK_BP,
    MOCK_TRENDS,
    MOCK_LIFESTYLE,
    MOCK_EMERGENCY,
    MOCK_REPORT,
)

MOCK_TARGET = "app.services.agents.generate_json"


# ─────────────────────────────────────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────────────────────────────────────

def test_health_check(client):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


# ─────────────────────────────────────────────────────────────────────────────
# Agent 1 — Stroke Risk Assessment
# ─────────────────────────────────────────────────────────────────────────────

class TestStrokeRiskRoute:
    URL = "/api/v1/assess/stroke-risk"

    def test_success(self, client, patient_payload):
        with patch(MOCK_TARGET, return_value=MOCK_STROKE_RISK):
            r = client.post(self.URL, json=patient_payload)
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is True
        assert body["agent"] == "stroke_risk_assessment"
        assert body["data"]["risk_score"] == 72
        assert body["data"]["risk_level"] == "High"

    def test_missing_required_field(self, client, patient_payload):
        del patient_payload["age"]
        r = client.post(self.URL, json=patient_payload)
        assert r.status_code == 400
        assert "age" in r.get_json()["error"]

    def test_non_json_body(self, client):
        r = client.post(self.URL, data="not json", content_type="text/plain")
        assert r.status_code == 400

    def test_agent_error_returns_500(self, client, patient_payload):
        with patch(MOCK_TARGET, side_effect=RuntimeError("API down")):
            r = client.post(self.URL, json=patient_payload)
        assert r.status_code == 500
        assert r.get_json()["success"] is False

    def test_invalid_json_from_model_returns_500(self, client, patient_payload):
        with patch(MOCK_TARGET, side_effect=ValueError("non-JSON output")):
            r = client.post(self.URL, json=patient_payload)
        assert r.status_code == 500


# ─────────────────────────────────────────────────────────────────────────────
# Agent 2 — Blood Pressure Monitoring
# ─────────────────────────────────────────────────────────────────────────────

class TestBPMonitoringRoute:
    URL = "/api/v1/monitor/blood-pressure"

    def test_success(self, client, bp_payload):
        with patch(MOCK_TARGET, return_value=MOCK_BP):
            r = client.post(self.URL, json=bp_payload)
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is True
        assert body["data"]["classification"] == "Hypertensive Crisis"
        assert body["data"]["requires_immediate_attention"] is True

    def test_missing_current_field(self, client, bp_payload):
        del bp_payload["current"]["systolic"]
        r = client.post(self.URL, json=bp_payload)
        assert r.status_code == 400

    def test_empty_history_accepted(self, client, bp_payload):
        bp_payload["history"] = []
        with patch(MOCK_TARGET, return_value=MOCK_BP):
            r = client.post(self.URL, json=bp_payload)
        assert r.status_code == 200

    def test_missing_current_block(self, client):
        with patch(MOCK_TARGET, return_value=MOCK_BP):
            r = client.post(self.URL, json={"history": []})
        assert r.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# Agent 3 — Health Risk Trend Analysis
# ─────────────────────────────────────────────────────────────────────────────

class TestTrendsRoute:
    URL = "/api/v1/analyse/trends"

    def test_success(self, client, trends_payload):
        with patch(MOCK_TARGET, return_value=MOCK_TRENDS):
            r = client.post(self.URL, json=trends_payload)
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is True
        assert body["data"]["overall_trend"] == "Worsening"
        assert len(body["data"]["alerts"]) == 2

    def test_missing_field(self, client, trends_payload):
        del trends_payload["glucose_latest"]
        r = client.post(self.URL, json=trends_payload)
        assert r.status_code == 400
        assert "glucose_latest" in r.get_json()["error"]


# ─────────────────────────────────────────────────────────────────────────────
# Agent 4 — Lifestyle Advisory
# ─────────────────────────────────────────────────────────────────────────────

class TestLifestyleRoute:
    URL = "/api/v1/advise/lifestyle"

    def test_success(self, client, lifestyle_payload):
        with patch(MOCK_TARGET, return_value=MOCK_LIFESTYLE):
            r = client.post(self.URL, json=lifestyle_payload)
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is True
        assert "diet" in body["data"]
        assert "priority_action" in body["data"]

    def test_optional_risk_level_accepted(self, client, patient_payload):
        # risk_level is optional in Agent 4 request
        with patch(MOCK_TARGET, return_value=MOCK_LIFESTYLE):
            r = client.post(self.URL, json=patient_payload)
        assert r.status_code == 200

    def test_missing_bmi_returns_400(self, client, lifestyle_payload):
        del lifestyle_payload["bmi"]
        r = client.post(self.URL, json=lifestyle_payload)
        assert r.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# Agent 5 — Emergency Symptom Alert
# ─────────────────────────────────────────────────────────────────────────────

class TestEmergencyRoute:
    URL = "/api/v1/alert/emergency"

    def test_emergency_urgency(self, client, emergency_payload):
        with patch(MOCK_TARGET, return_value=MOCK_EMERGENCY):
            r = client.post(self.URL, json=emergency_payload)
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is True
        assert body["data"]["urgency"] == "EMERGENCY"
        assert body["data"]["fast_flags"]["face"] is True
        assert body["data"]["fast_flags"]["arm"] is True
        assert body["data"]["fast_flags"]["speech"] is True

    def test_empty_symptoms_text_returns_400(self, client):
        r = client.post(self.URL, json={"symptoms_text": ""})
        assert r.status_code == 400

    def test_missing_symptoms_text_returns_400(self, client):
        r = client.post(self.URL, json={})
        assert r.status_code == 400


# ─────────────────────────────────────────────────────────────────────────────
# Hospital Report Summary
# ─────────────────────────────────────────────────────────────────────────────

class TestReportSummaryRoute:
    URL = "/api/v1/report/summarise"

    def test_success(self, client, report_payload):
        with patch(MOCK_TARGET, return_value=MOCK_REPORT):
            r = client.post(self.URL, json=report_payload)
        assert r.status_code == 200
        body = r.get_json()
        assert body["success"] is True
        assert body["data"]["hospital_name"] == "City General Hospital"
        assert "Hypertension" in body["data"]["key_diagnoses"]

    def test_missing_report_text_returns_400(self, client):
        r = client.post(self.URL, json={"hospital_name": "Test Hospital"})
        assert r.status_code == 400

    def test_missing_hospital_name_returns_400(self, client):
        r = client.post(self.URL, json={"report_text": "Some report text."})
        assert r.status_code == 400

    def test_empty_report_text_returns_400(self, client):
        r = client.post(self.URL, json={"report_text": "", "hospital_name": "Test"})
        assert r.status_code == 400
