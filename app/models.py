# app/models.py
# Request / response dataclasses for the Stroke Risk Monitoring API.
# Using dataclasses + __post_init__ validation keeps this dependency-free.

from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Request models
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class PatientProfile:
    """Shared patient profile used by Agent 1 and Agent 4."""
    age: int
    gender: str
    bmi: float
    smoking_status: str          # e.g. "Current smoker", "Non-smoker", "Former smoker"
    activity_level: str          # e.g. "Sedentary", "Moderate", "Active"
    bp_systolic: int
    bp_diastolic: int
    blood_glucose: float         # mg/dL fasting
    cholesterol: float           # mg/dL total
    name: Optional[str] = None
    medical_history: Optional[str] = None
    risk_level: Optional[str] = None  # pre-computed by Agent 1; used by Agent 4

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "medical_history": self.medical_history,
            "bp_systolic": self.bp_systolic,
            "bp_diastolic": self.bp_diastolic,
            "blood_glucose": self.blood_glucose,
            "cholesterol": self.cholesterol,
            "bmi": self.bmi,
            "smoking_status": self.smoking_status,
            "activity_level": self.activity_level,
            "risk_level": self.risk_level,
        }


@dataclass
class BPReading:
    """A single blood pressure reading."""
    systolic: int
    diastolic: int
    timestamp: str               # ISO-8601 string, e.g. "2024-11-19T08:30:00Z"

    def to_dict(self) -> dict:
        return {
            "systolic": self.systolic,
            "diastolic": self.diastolic,
            "timestamp": self.timestamp,
        }


@dataclass
class HealthMetrics:
    """Trend metrics for Agent 3."""
    glucose_latest: float
    glucose_avg: float
    glucose_change_pct: float
    cholesterol_latest: float
    cholesterol_avg: float
    cholesterol_change_pct: float
    bmi_latest: float
    bmi_avg: float
    bmi_change_pct: float

    def to_dict(self) -> dict:
        return {
            "glucose_latest": self.glucose_latest,
            "glucose_avg": self.glucose_avg,
            "glucose_change_pct": self.glucose_change_pct,
            "cholesterol_latest": self.cholesterol_latest,
            "cholesterol_avg": self.cholesterol_avg,
            "cholesterol_change_pct": self.cholesterol_change_pct,
            "bmi_latest": self.bmi_latest,
            "bmi_avg": self.bmi_avg,
            "bmi_change_pct": self.bmi_change_pct,
        }


@dataclass
class EmergencySymptomRequest:
    """Payload for Agent 5."""
    symptoms_text: str


@dataclass
class HospitalReportRequest:
    """Payload for the report upload endpoint."""
    report_text: str
    hospital_name: str


# ─────────────────────────────────────────────────────────────────────────────
# Lightweight response envelope
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class AgentResponse:
    """Standard API envelope wrapping any agent's JSON payload."""
    agent: str
    success: bool
    data: dict = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "agent": self.agent,
            "success": self.success,
            "data": self.data,
            "error": self.error,
        }
