# app/services/__init__.py
from .prompts import (
    stroke_risk_assessment_prompt,
    blood_pressure_monitoring_prompt,
    health_risk_trend_prompt,
    lifestyle_advisory_prompt,
    emergency_symptom_alert_prompt,
    hospital_report_summary_prompt,
)
from .agents import (
    assess_stroke_risk,
    monitor_blood_pressure,
    analyse_health_trends,
    get_lifestyle_advice,
    assess_emergency_symptoms,
    summarise_hospital_report,
)

__all__ = [
    # Prompt builders
    "stroke_risk_assessment_prompt",
    "blood_pressure_monitoring_prompt",
    "health_risk_trend_prompt",
    "lifestyle_advisory_prompt",
    "emergency_symptom_alert_prompt",
    "hospital_report_summary_prompt",
    # Agent functions
    "assess_stroke_risk",
    "monitor_blood_pressure",
    "analyse_health_trends",
    "get_lifestyle_advice",
    "assess_emergency_symptoms",
    "summarise_hospital_report",
]
