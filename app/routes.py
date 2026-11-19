# app/routes.py
# Flask Blueprint — REST API routes for all five Stroke Risk Monitoring agents.
#
# Endpoints:
#   GET  /                               ← web UI
#   POST /api/v1/assess/stroke-risk
#   POST /api/v1/monitor/blood-pressure
#   POST /api/v1/analyse/trends
#   POST /api/v1/advise/lifestyle
#   POST /api/v1/alert/emergency
#   POST /api/v1/report/summarise

import logging
from flask import Blueprint, request, jsonify, current_app, render_template

from .models import (
    AgentResponse,
    PatientProfile,
    BPReading,
    HealthMetrics,
    EmergencySymptomRequest,
    HospitalReportRequest,
)
from .services.agents import (
    assess_stroke_risk,
    monitor_blood_pressure,
    analyse_health_trends,
    get_lifestyle_advice,
    assess_emergency_symptoms,
    summarise_hospital_report,
)

logger = logging.getLogger(__name__)

bp = Blueprint("api", __name__, url_prefix="/api/v1")

# ── Web UI ────────────────────────────────────────────────────────────────────
ui_bp = Blueprint("ui", __name__)

@ui_bp.route("/")
def index():
    return render_template("login.html")

@ui_bp.route("/patient")
def patient():
    return render_template("patient.html")

@ui_bp.route("/professional")
def professional():
    return render_template("professional.html")


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _ok(agent_name: str, data: dict):
    return jsonify(AgentResponse(agent=agent_name, success=True, data=data).to_dict()), 200


def _err(agent_name: str, message: str, status: int = 500):
    logger.error("[%s] %s", agent_name, message)
    return jsonify(
        AgentResponse(agent=agent_name, success=False, error=message).to_dict()
    ), status


def _require_json():
    """Return parsed JSON body or raise 400."""
    body = request.get_json(silent=True)
    if body is None:
        return None, (jsonify({"error": "Request body must be valid JSON"}), 400)
    return body, None


# ─────────────────────────────────────────────────────────────────────────────
# Agent 1 — Stroke Risk Assessment
# POST /api/v1/assess/stroke-risk
# ─────────────────────────────────────────────────────────────────────────────

@bp.route("/assess/stroke-risk", methods=["POST"])
def route_stroke_risk():
    body, err = _require_json()
    if err:
        return err

    required = ["age", "gender", "bmi", "smoking_status", "activity_level",
                "bp_systolic", "bp_diastolic", "blood_glucose", "cholesterol"]
    missing = [k for k in required if k not in body]
    if missing:
        return _err("stroke_risk_assessment", f"Missing fields: {missing}", 400)

    patient = PatientProfile(
        name=body.get("name"),
        age=body["age"],
        gender=body["gender"],
        medical_history=body.get("medical_history"),
        bmi=body["bmi"],
        smoking_status=body["smoking_status"],
        activity_level=body["activity_level"],
        bp_systolic=body["bp_systolic"],
        bp_diastolic=body["bp_diastolic"],
        blood_glucose=body["blood_glucose"],
        cholesterol=body["cholesterol"],
    )

    try:
        result = assess_stroke_risk(patient.to_dict(), current_app.config)
        return _ok("stroke_risk_assessment", result)
    except (ValueError, RuntimeError) as exc:
        return _err("stroke_risk_assessment", str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Agent 2 — Blood Pressure Monitoring
# POST /api/v1/monitor/blood-pressure
# ─────────────────────────────────────────────────────────────────────────────

@bp.route("/monitor/blood-pressure", methods=["POST"])
def route_blood_pressure():
    body, err = _require_json()
    if err:
        return err

    current_raw = body.get("current", {})
    history_raw = body.get("history", [])

    required = ["systolic", "diastolic", "timestamp"]
    missing = [k for k in required if k not in current_raw]
    if missing:
        return _err("bp_monitoring", f"Missing fields in 'current': {missing}", 400)

    current = BPReading(
        systolic=current_raw["systolic"],
        diastolic=current_raw["diastolic"],
        timestamp=current_raw["timestamp"],
    )
    history = [
        BPReading(
            systolic=r["systolic"],
            diastolic=r["diastolic"],
            timestamp=r["timestamp"],
        ).to_dict()
        for r in history_raw
        if all(k in r for k in ("systolic", "diastolic", "timestamp"))
    ]

    try:
        result = monitor_blood_pressure(current.to_dict(), history, current_app.config)
        return _ok("bp_monitoring", result)
    except (ValueError, RuntimeError) as exc:
        return _err("bp_monitoring", str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Agent 3 — Health Risk Trend Analysis
# POST /api/v1/analyse/trends
# ─────────────────────────────────────────────────────────────────────────────

@bp.route("/analyse/trends", methods=["POST"])
def route_trends():
    body, err = _require_json()
    if err:
        return err

    required = [
        "glucose_latest", "glucose_avg", "glucose_change_pct",
        "cholesterol_latest", "cholesterol_avg", "cholesterol_change_pct",
        "bmi_latest", "bmi_avg", "bmi_change_pct",
    ]
    missing = [k for k in required if k not in body]
    if missing:
        return _err("health_risk_trends", f"Missing fields: {missing}", 400)

    metrics = HealthMetrics(
        glucose_latest=body["glucose_latest"],
        glucose_avg=body["glucose_avg"],
        glucose_change_pct=body["glucose_change_pct"],
        cholesterol_latest=body["cholesterol_latest"],
        cholesterol_avg=body["cholesterol_avg"],
        cholesterol_change_pct=body["cholesterol_change_pct"],
        bmi_latest=body["bmi_latest"],
        bmi_avg=body["bmi_avg"],
        bmi_change_pct=body["bmi_change_pct"],
    )

    try:
        result = analyse_health_trends(metrics.to_dict(), current_app.config)
        return _ok("health_risk_trends", result)
    except (ValueError, RuntimeError) as exc:
        return _err("health_risk_trends", str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Agent 4 — Lifestyle Advisory
# POST /api/v1/advise/lifestyle
# ─────────────────────────────────────────────────────────────────────────────

@bp.route("/advise/lifestyle", methods=["POST"])
def route_lifestyle():
    body, err = _require_json()
    if err:
        return err

    required = ["age", "gender", "bmi", "smoking_status", "activity_level",
                "bp_systolic", "bp_diastolic", "blood_glucose", "cholesterol"]
    missing = [k for k in required if k not in body]
    if missing:
        return _err("lifestyle_advisory", f"Missing fields: {missing}", 400)

    patient = PatientProfile(
        age=body["age"],
        gender=body["gender"],
        bmi=body["bmi"],
        smoking_status=body["smoking_status"],
        activity_level=body["activity_level"],
        bp_systolic=body["bp_systolic"],
        bp_diastolic=body["bp_diastolic"],
        blood_glucose=body["blood_glucose"],
        cholesterol=body["cholesterol"],
        risk_level=body.get("risk_level"),
    )

    try:
        result = get_lifestyle_advice(patient.to_dict(), current_app.config)
        return _ok("lifestyle_advisory", result)
    except (ValueError, RuntimeError) as exc:
        return _err("lifestyle_advisory", str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Agent 5 — Emergency Symptom Alert
# POST /api/v1/alert/emergency
# ─────────────────────────────────────────────────────────────────────────────

@bp.route("/alert/emergency", methods=["POST"])
def route_emergency():
    body, err = _require_json()
    if err:
        return err

    symptoms_text = body.get("symptoms_text", "").strip()
    if not symptoms_text:
        return _err("emergency_alert", "Field 'symptoms_text' is required and cannot be empty.", 400)

    req = EmergencySymptomRequest(symptoms_text=symptoms_text)

    try:
        result = assess_emergency_symptoms(req.symptoms_text, current_app.config)
        return _ok("emergency_alert", result)
    except (ValueError, RuntimeError) as exc:
        return _err("emergency_alert", str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Hospital Report Summary
# POST /api/v1/report/summarise
# ─────────────────────────────────────────────────────────────────────────────

@bp.route("/report/summarise", methods=["POST"])
def route_report_summary():
    body, err = _require_json()
    if err:
        return err

    report_text = body.get("report_text", "").strip()
    hospital_name = body.get("hospital_name", "").strip()

    if not report_text:
        return _err("report_summary", "Field 'report_text' is required.", 400)
    if not hospital_name:
        return _err("report_summary", "Field 'hospital_name' is required.", 400)

    req = HospitalReportRequest(report_text=report_text, hospital_name=hospital_name)

    try:
        result = summarise_hospital_report(req.report_text, req.hospital_name, current_app.config)
        return _ok("report_summary", result)
    except (ValueError, RuntimeError) as exc:
        return _err("report_summary", str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Neighbor Emergency Alert
# POST /api/v1/alert/neighbors
# ─────────────────────────────────────────────────────────────────────────────

# In-memory neighbor registry (replace with a DB in production).
# Each entry: { "name": str, "phone": str, "address": str, "notified_at": str|None }
_NEIGHBORS: list = [
    {"id": "n1", "name": "Ravi Kumar",    "phone": "+91-98765-11111", "address": "Flat 101, same building", "notified_at": None},
    {"id": "n2", "name": "Priya Sharma",  "phone": "+91-98765-22222", "address": "Flat 203, same building", "notified_at": None},
    {"id": "n3", "name": "Anjali Nair",   "phone": "+91-98765-33333", "address": "House next door",         "notified_at": None},
]


@bp.route("/alert/neighbors", methods=["POST"])
def route_alert_neighbors():
    """
    Simulate broadcasting an emergency alert to all registered neighbors.
    Body: { "patient_name": str, "urgency": str, "message": str }
    """
    import datetime
    body, err = _require_json()
    if err:
        return err

    patient_name = body.get("patient_name", "Unknown patient")
    urgency      = body.get("urgency", "EMERGENCY")
    message      = body.get("message", "Stroke emergency — please check on your neighbor.")

    now = datetime.datetime.utcnow().isoformat() + "Z"
    notified = []
    for nb in _NEIGHBORS:
        nb["notified_at"] = now
        notified.append({
            "id":          nb["id"],
            "name":        nb["name"],
            "phone":       nb["phone"],
            "address":     nb["address"],
            "notified_at": now,
            "alert_sent":  True,
            "message_sent": f"🚨 EMERGENCY ALERT: {patient_name} may be having a stroke. "
                            f"Please check on them immediately. ({urgency}) — {message}",
        })
        logger.critical(
            "NEIGHBOR ALERT sent → %s (%s) : %s", nb["name"], nb["phone"], message
        )

    return jsonify({
        "agent":       "neighbor_alert",
        "success":     True,
        "total_notified": len(notified),
        "neighbors_notified": notified,
        "broadcast_at": now,
        "disclaimer":  "This is a simulated notification. In production, integrate SMS (Twilio) or push notification service.",
    }), 200


@bp.route("/alert/neighbors", methods=["GET"])
def route_get_neighbors():
    """Return the current neighbor registry."""
    return jsonify({"neighbors": _NEIGHBORS}), 200


# ─────────────────────────────────────────────────────────────────────────────
# Health check
# ─────────────────────────────────────────────────────────────────────────────

@bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "Stroke Risk Monitoring API"}), 200
