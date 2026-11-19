# app/services/agents.py
# High-level agent functions.
# Each function builds a prompt, calls the Granite model, and returns
# the parsed JSON dict.  All config is injected via the `cfg` dict so
# the functions stay testable without live credentials.

import logging
from .prompts import (
    stroke_risk_assessment_prompt,
    blood_pressure_monitoring_prompt,
    health_risk_trend_prompt,
    lifestyle_advisory_prompt,
    emergency_symptom_alert_prompt,
    hospital_report_summary_prompt,
)
from .watsonx_client import generate_json

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _creds(cfg: dict) -> tuple[str, str, str]:
    """Extract (api_key, url, project_id) from the app config dict."""
    return (
        cfg["WATSONX_API_KEY"],
        cfg["WATSONX_URL"],
        cfg["WATSONX_PROJECT_ID"],
    )


# ---------------------------------------------------------------------------
# Agent 1 — Stroke Risk Assessment
# ---------------------------------------------------------------------------

def assess_stroke_risk(patient: dict, cfg: dict) -> dict:
    """
    Assess overall stroke risk for a patient.

    Args:
        patient: dict with keys name, age, gender, medical_history,
                 bp_systolic, bp_diastolic, blood_glucose, cholesterol,
                 bmi, smoking_status, activity_level.
        cfg:     Flask app.config dict (must contain WATSONX_* keys).

    Returns:
        Parsed JSON dict with risk_score, risk_level, key_factors,
        summary, recommendation, disclaimer.
    """
    prompt = stroke_risk_assessment_prompt(patient)
    logger.info("Agent 1 — Stroke Risk Assessment for patient: %s", patient.get("name"))
    return generate_json(prompt, *_creds(cfg))


# ---------------------------------------------------------------------------
# Agent 2 — Blood Pressure Monitoring
# ---------------------------------------------------------------------------

def monitor_blood_pressure(current: dict, history: list, cfg: dict) -> dict:
    """
    Classify a BP reading and analyse the recent trend.

    Args:
        current: dict with keys systolic, diastolic, timestamp.
        history: list of dicts with keys timestamp, systolic, diastolic
                 (most recent last; only the last 10 are used).
        cfg:     Flask app.config dict.

    Returns:
        Parsed JSON dict with classification, trend, trend_summary,
        requires_immediate_attention, action, disclaimer.
    """
    prompt = blood_pressure_monitoring_prompt(current, history)
    logger.info(
        "Agent 2 — BP Monitoring: %s/%s mmHg at %s",
        current.get("systolic"),
        current.get("diastolic"),
        current.get("timestamp"),
    )
    result = generate_json(prompt, *_creds(cfg))

    if result.get("requires_immediate_attention"):
        logger.warning(
            "IMMEDIATE ATTENTION required — BP %s/%s mmHg classified as: %s",
            current.get("systolic"),
            current.get("diastolic"),
            result.get("classification"),
        )

    return result


# ---------------------------------------------------------------------------
# Agent 3 — Health Risk Trend Analysis
# ---------------------------------------------------------------------------

def analyse_health_trends(metrics: dict, cfg: dict) -> dict:
    """
    Analyse longitudinal trends in glucose, cholesterol, and BMI.

    Args:
        metrics: dict with keys glucose_latest, glucose_avg,
                 glucose_change_pct, cholesterol_latest, cholesterol_avg,
                 cholesterol_change_pct, bmi_latest, bmi_avg,
                 bmi_change_pct.
        cfg:     Flask app.config dict.

    Returns:
        Parsed JSON dict with per-metric trends, alerts list,
        overall_trend, narrative, recommendation, disclaimer.
    """
    prompt = health_risk_trend_prompt(metrics)
    logger.info("Agent 3 — Health Risk Trend Analysis")
    return generate_json(prompt, *_creds(cfg))


# ---------------------------------------------------------------------------
# Agent 4 — Lifestyle Advisory
# ---------------------------------------------------------------------------

def get_lifestyle_advice(patient: dict, cfg: dict) -> dict:
    """
    Generate a personalised lifestyle health plan.

    Args:
        patient: dict with keys age, gender, bmi, smoking_status,
                 activity_level, risk_level, bp_systolic, bp_diastolic,
                 blood_glucose, cholesterol.
        cfg:     Flask app.config dict.

    Returns:
        Parsed JSON dict with diet, exercise, smoking,
        stress_management, medication_adherence, priority_action,
        disclaimer.
    """
    prompt = lifestyle_advisory_prompt(patient)
    logger.info("Agent 4 — Lifestyle Advisory for patient age %s", patient.get("age"))
    return generate_json(prompt, *_creds(cfg))


# ---------------------------------------------------------------------------
# Agent 5 — Emergency Symptom Alert
# ---------------------------------------------------------------------------

def assess_emergency_symptoms(symptoms_text: str, cfg: dict) -> dict:
    """
    Assess reported symptoms for stroke / brain haemorrhage warning signs.

    Args:
        symptoms_text: Free-text description of symptoms from the patient.
        cfg:           Flask app.config dict.

    Returns:
        Parsed JSON dict with urgency, matched_warning_signs, fast_flags,
        rationale, immediate_instruction, emergency_message, disclaimer.
    """
    prompt = emergency_symptom_alert_prompt(symptoms_text)
    logger.warning("Agent 5 — Emergency Symptom Alert triggered")
    result = generate_json(prompt, *_creds(cfg))

    if result.get("urgency") == "EMERGENCY":
        logger.critical(
            "STROKE EMERGENCY: %s | Signs: %s",
            result.get("rationale"),
            result.get("matched_warning_signs"),
        )

    return result


# ---------------------------------------------------------------------------
# Report Summary (Hospital Report Upload Service)
# ---------------------------------------------------------------------------

def summarise_hospital_report(report_text: str, hospital_name: str, cfg: dict) -> dict:
    """
    Extract stroke-relevant information from a hospital report.

    Args:
        report_text:   Raw text of the hospital report (first 3000 chars used).
        hospital_name: Name of the issuing hospital.
        cfg:           Flask app.config dict.

    Returns:
        Parsed JSON dict with hospital_name, key_diagnoses,
        relevant_medications, bp_readings_found, glucose_readings_found,
        cholesterol_readings_found, cardiovascular_history, summary,
        disclaimer.
    """
    prompt = hospital_report_summary_prompt(report_text, hospital_name)
    logger.info("Report Summary — hospital: %s", hospital_name)
    return generate_json(prompt, *_creds(cfg))
