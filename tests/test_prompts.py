# tests/test_prompts.py
# Unit tests for all 6 Granite prompt-builder functions.
# Verifies structure, required fields, and safety constraints — no live API calls.

import pytest
from app.services.prompts import (
    stroke_risk_assessment_prompt,
    blood_pressure_monitoring_prompt,
    health_risk_trend_prompt,
    lifestyle_advisory_prompt,
    emergency_symptom_alert_prompt,
    hospital_report_summary_prompt,
    DISCLAIMER,
)


PATIENT = {
    "name": "Jane Smith",
    "age": 62,
    "gender": "Female",
    "medical_history": "Atrial fibrillation",
    "bp_systolic": 158,
    "bp_diastolic": 95,
    "blood_glucose": 138.0,
    "cholesterol": 224.0,
    "bmi": 29.4,
    "smoking_status": "Former smoker",
    "activity_level": "Sedentary",
}

BP_CURRENT = {"systolic": 182, "diastolic": 122, "timestamp": "2024-11-19T08:30:00Z"}
BP_HISTORY = [
    {"systolic": 145, "diastolic": 95, "timestamp": "2024-11-18T08:00:00Z"},
]

METRICS = {
    "glucose_latest": 132.0, "glucose_avg": 118.0, "glucose_change_pct": 11.9,
    "cholesterol_latest": 215.0, "cholesterol_avg": 205.0, "cholesterol_change_pct": 4.9,
    "bmi_latest": 30.5, "bmi_avg": 29.8, "bmi_change_pct": 2.3,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _has_chat_template(prompt: str) -> bool:
    return "<|system|>" in prompt and "<|user|>" in prompt and "<|assistant|>" in prompt


# ── Agent 1 ───────────────────────────────────────────────────────────────────

class TestStrokeRiskPrompt:
    def test_returns_string(self):
        assert isinstance(stroke_risk_assessment_prompt(PATIENT), str)

    def test_chat_template_present(self):
        assert _has_chat_template(stroke_risk_assessment_prompt(PATIENT))

    def test_contains_patient_name(self):
        assert "Jane Smith" in stroke_risk_assessment_prompt(PATIENT)

    def test_contains_bp_values(self):
        p = stroke_risk_assessment_prompt(PATIENT)
        assert "158" in p and "95" in p

    def test_disclaimer_injected(self):
        assert DISCLAIMER in stroke_risk_assessment_prompt(PATIENT)

    def test_json_schema_present(self):
        p = stroke_risk_assessment_prompt(PATIENT)
        assert "risk_score" in p
        assert "risk_level" in p
        assert "key_factors" in p

    def test_missing_optional_name_defaults(self):
        patient_no_name = {k: v for k, v in PATIENT.items() if k != "name"}
        p = stroke_risk_assessment_prompt(patient_no_name)
        assert "Unknown" in p


# ── Agent 2 ───────────────────────────────────────────────────────────────────

class TestBPMonitoringPrompt:
    def test_returns_string(self):
        assert isinstance(blood_pressure_monitoring_prompt(BP_CURRENT, BP_HISTORY), str)

    def test_chat_template_present(self):
        assert _has_chat_template(blood_pressure_monitoring_prompt(BP_CURRENT, BP_HISTORY))

    def test_current_reading_present(self):
        p = blood_pressure_monitoring_prompt(BP_CURRENT, BP_HISTORY)
        assert "182" in p and "122" in p

    def test_history_reading_present(self):
        p = blood_pressure_monitoring_prompt(BP_CURRENT, BP_HISTORY)
        assert "145" in p

    def test_empty_history_fallback(self):
        p = blood_pressure_monitoring_prompt(BP_CURRENT, [])
        assert "No prior readings available" in p

    def test_only_last_10_history_used(self):
        # Build 15 readings; only the last 10 should appear in prompt
        history = [
            {"systolic": 100 + i, "diastolic": 70 + i, "timestamp": f"2024-11-{i+1:02d}T08:00:00Z"}
            for i in range(15)
        ]
        p = blood_pressure_monitoring_prompt(BP_CURRENT, history)
        # Reading 0 (systolic=100) should NOT appear; reading 14 (systolic=114) SHOULD
        assert "100" not in p
        assert "114" in p

    def test_disclaimer_injected(self):
        assert DISCLAIMER in blood_pressure_monitoring_prompt(BP_CURRENT, BP_HISTORY)

    def test_requires_immediate_attention_field_present(self):
        p = blood_pressure_monitoring_prompt(BP_CURRENT, BP_HISTORY)
        assert "requires_immediate_attention" in p


# ── Agent 3 ───────────────────────────────────────────────────────────────────

class TestHealthRiskTrendPrompt:
    def test_returns_string(self):
        assert isinstance(health_risk_trend_prompt(METRICS), str)

    def test_chat_template_present(self):
        assert _has_chat_template(health_risk_trend_prompt(METRICS))

    def test_glucose_values_present(self):
        p = health_risk_trend_prompt(METRICS)
        assert "132.0" in p and "118.0" in p

    def test_all_trend_fields_in_schema(self):
        p = health_risk_trend_prompt(METRICS)
        for field in ("glucose_trend", "cholesterol_trend", "bmi_trend", "alerts", "overall_trend"):
            assert field in p

    def test_disclaimer_injected(self):
        assert DISCLAIMER in health_risk_trend_prompt(METRICS)


# ── Agent 4 ───────────────────────────────────────────────────────────────────

class TestLifestyleAdvisoryPrompt:
    def test_returns_string(self):
        assert isinstance(lifestyle_advisory_prompt(PATIENT), str)

    def test_chat_template_present(self):
        assert _has_chat_template(lifestyle_advisory_prompt(PATIENT))

    def test_all_categories_in_schema(self):
        p = lifestyle_advisory_prompt(PATIENT)
        for field in ("diet", "exercise", "smoking", "stress_management",
                      "medication_adherence", "priority_action"):
            assert field in p

    def test_disclaimer_injected(self):
        assert DISCLAIMER in lifestyle_advisory_prompt(PATIENT)

    def test_guidelines_sourced(self):
        p = lifestyle_advisory_prompt(PATIENT)
        assert "WHO" in p and "AHA" in p and "NHS" in p


# ── Agent 5 ───────────────────────────────────────────────────────────────────

class TestEmergencyAlertPrompt:
    def test_returns_string(self):
        assert isinstance(emergency_symptom_alert_prompt("face drooping"), str)

    def test_chat_template_present(self):
        assert _has_chat_template(emergency_symptom_alert_prompt("face drooping"))

    def test_symptoms_text_injected(self):
        p = emergency_symptom_alert_prompt("arm weakness and slurred speech")
        assert "arm weakness and slurred speech" in p

    def test_fast_flags_in_schema(self):
        p = emergency_symptom_alert_prompt("face drooping")
        assert "fast_flags" in p
        assert '"face"' in p and '"arm"' in p and '"speech"' in p

    def test_emergency_escalation_rule_present(self):
        p = emergency_symptom_alert_prompt("headache")
        assert "EMERGENCY" in p

    def test_never_downplay_instruction_present(self):
        p = emergency_symptom_alert_prompt("mild headache")
        assert "Never downplay" in p or "never downplay" in p.lower()

    def test_disclaimer_in_schema(self):
        p = emergency_symptom_alert_prompt("dizziness")
        assert "does NOT diagnose stroke" in p


# ── Report Summary ────────────────────────────────────────────────────────────

class TestHospitalReportPrompt:
    REPORT = "BP 165/105. Diagnosed with hypertension. Glucose 142 mg/dL."

    def test_returns_string(self):
        assert isinstance(hospital_report_summary_prompt(self.REPORT, "City General"), str)

    def test_chat_template_present(self):
        assert _has_chat_template(hospital_report_summary_prompt(self.REPORT, "City General"))

    def test_hospital_name_injected(self):
        p = hospital_report_summary_prompt(self.REPORT, "City General")
        assert "City General" in p

    def test_report_truncated_at_3000_chars(self):
        long_report = "x" * 5000
        p = hospital_report_summary_prompt(long_report, "Test Hospital")
        # The prompt should contain exactly 3000 x's, not 5000
        assert "x" * 3000 in p
        assert "x" * 3001 not in p

    def test_all_schema_fields_present(self):
        p = hospital_report_summary_prompt(self.REPORT, "City General")
        for field in ("key_diagnoses", "relevant_medications", "bp_readings_found",
                      "glucose_readings_found", "cholesterol_readings_found",
                      "cardiovascular_history", "summary"):
            assert field in p

    def test_disclaimer_injected(self):
        assert DISCLAIMER in hospital_report_summary_prompt(self.REPORT, "City General")
