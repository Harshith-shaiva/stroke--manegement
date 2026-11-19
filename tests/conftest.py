# tests/conftest.py
# Shared pytest fixtures for the Stroke Risk Monitoring API test suite.

import pytest
from app import create_app


# ── App / client fixtures ─────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def app():
    """Create a Flask test application (no live watsonx calls)."""
    flask_app = create_app("config.TestingConfig")
    flask_app.config.update(
        WATSONX_API_KEY="test-key",
        WATSONX_URL="https://us-south.ml.cloud.ibm.com",
        WATSONX_PROJECT_ID="746c612f-47a6-4d52-96df-87c9aa25f468",
    )
    return flask_app


@pytest.fixture()
def client(app):
    """Flask test client."""
    return app.test_client()


# ── Reusable JSON payloads ────────────────────────────────────────────────────

@pytest.fixture()
def patient_payload():
    return {
        "name": "Jane Smith",
        "age": 62,
        "gender": "Female",
        "medical_history": "Type 2 diabetes, atrial fibrillation",
        "bp_systolic": 158,
        "bp_diastolic": 95,
        "blood_glucose": 138.0,
        "cholesterol": 224.0,
        "bmi": 29.4,
        "smoking_status": "Former smoker",
        "activity_level": "Sedentary",
    }


@pytest.fixture()
def bp_payload():
    return {
        "current": {
            "systolic": 182,
            "diastolic": 122,
            "timestamp": "2024-11-19T08:30:00Z",
        },
        "history": [
            {"systolic": 145, "diastolic": 95, "timestamp": "2024-11-18T08:00:00Z"},
            {"systolic": 150, "diastolic": 98, "timestamp": "2024-11-17T08:00:00Z"},
            {"systolic": 148, "diastolic": 96, "timestamp": "2024-11-16T08:00:00Z"},
        ],
    }


@pytest.fixture()
def trends_payload():
    return {
        "glucose_latest": 132.0,
        "glucose_avg": 118.0,
        "glucose_change_pct": 11.9,
        "cholesterol_latest": 215.0,
        "cholesterol_avg": 205.0,
        "cholesterol_change_pct": 4.9,
        "bmi_latest": 30.5,
        "bmi_avg": 29.8,
        "bmi_change_pct": 2.3,
    }


@pytest.fixture()
def lifestyle_payload(patient_payload):
    return {**patient_payload, "risk_level": "High"}


@pytest.fixture()
def emergency_payload():
    return {"symptoms_text": "Sudden face drooping on the left side, arm weakness, slurred speech"}


@pytest.fixture()
def report_payload():
    return {
        "hospital_name": "City General Hospital",
        "report_text": (
            "Patient admitted 2024-11-10. Diagnosed with hypertension (BP 165/105). "
            "History of TIA. Prescribed amlodipine 5mg. Fasting glucose 142 mg/dL. "
            "Total cholesterol 230 mg/dL. Advised lifestyle changes."
        ),
    }


# ── Mock Granite response stubs ───────────────────────────────────────────────

MOCK_STROKE_RISK = {
    "risk_score": 72,
    "risk_level": "High",
    "key_factors": ["Hypertension", "Type 2 diabetes", "Atrial fibrillation"],
    "summary": "Patient presents multiple high-risk factors.",
    "recommendation": "Refer to cardiologist immediately.",
    "disclaimer": "IMPORTANT: This system is a health-risk monitoring and decision-support tool ONLY.",
}

MOCK_BP = {
    "classification": "Hypertensive Crisis",
    "trend": "Worsening",
    "trend_summary": "BP has been steadily rising over three days.",
    "requires_immediate_attention": True,
    "action": "Call emergency services or go to A&E immediately.",
    "disclaimer": "IMPORTANT: This system is a health-risk monitoring and decision-support tool ONLY.",
}

MOCK_TRENDS = {
    "glucose_trend": "Worsening",
    "cholesterol_trend": "Worsening",
    "bmi_trend": "Worsening",
    "alerts": ["Glucose above diabetic threshold", "Cholesterol above elevated threshold"],
    "overall_trend": "Worsening",
    "narrative": "All three markers are trending in the wrong direction.",
    "recommendation": "Urgent GP referral for medication review.",
    "disclaimer": "IMPORTANT: This system is a health-risk monitoring and decision-support tool ONLY.",
}

MOCK_LIFESTYLE = {
    "diet": {
        "advice": "Adopt a DASH diet to lower blood pressure.",
        "foods_to_increase": ["Leafy greens", "Berries"],
        "foods_to_reduce": ["Salt", "Processed foods"],
    },
    "exercise": {
        "advice": "Start with low-impact cardio.",
        "suggested_activities": ["Walking", "Swimming"],
        "weekly_target": "150 minutes moderate aerobic",
    },
    "smoking": {"advice": "Maintain non-smoking status."},
    "stress_management": {"advice": "Practice mindfulness 10 minutes daily."},
    "medication_adherence": {"advice": "Take all prescribed medications at the same time each day."},
    "priority_action": "Reduce sodium intake immediately.",
    "disclaimer": "IMPORTANT: This system is a health-risk monitoring and decision-support tool ONLY.",
}

MOCK_EMERGENCY = {
    "urgency": "EMERGENCY",
    "matched_warning_signs": ["Face drooping", "Arm weakness", "Slurred speech"],
    "fast_flags": {"face": True, "arm": True, "speech": True},
    "rationale": "All three FAST criteria are present, indicating a likely stroke.",
    "immediate_instruction": "Call 999 / 112 immediately. Do not drive yourself.",
    "emergency_message": "CALL EMERGENCY SERVICES IMMEDIATELY. Do not drive yourself. Note the time symptoms started.",
    "disclaimer": "This tool does NOT diagnose stroke.",
}

MOCK_REPORT = {
    "hospital_name": "City General Hospital",
    "key_diagnoses": ["Hypertension", "TIA"],
    "relevant_medications": ["Amlodipine 5mg"],
    "bp_readings_found": ["165/105"],
    "glucose_readings_found": ["142 mg/dL"],
    "cholesterol_readings_found": ["230 mg/dL"],
    "cardiovascular_history": "History of transient ischaemic attack.",
    "summary": "Patient has multiple cardiovascular risk factors.",
    "disclaimer": "IMPORTANT: This system is a health-risk monitoring and decision-support tool ONLY.",
}
