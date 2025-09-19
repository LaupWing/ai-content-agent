from __future__ import annotations
import os, requests
from typing import Dict, Any

API_BASE = os.getenv("LARAVEL_API_BASE_URL", "http://localhost:8000/api").rstrip("/")
TIMEOUT = float(os.getenv("API_TIMEOUT_SECONDS", "12.0"))

def api_workouts_today(whatsapp_id: str) -> Dict[str, Any]:
    """Return today's planned workout for the user.

    Args:
        whatsapp_id (str): WhatsApp ID of the user.

    Returns:
        dict: Plan meta + today's exercises.
    """
    print('here is the whatsapp id----------------:')
    print(whatsapp_id)
    print('end of whatsapp id----------------:')
    r = requests.get(f"{API_BASE}/workouts/today", params={"whatsapp_id": whatsapp_id}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def api_workouts_schema(whatsapp_id: str) -> Dict[str, Any]:
    """Return the user's full workout plan/schema.

    Args:
        whatsapp_id (str): WhatsApp ID.

    Returns:
        dict: Plan with days and exercises.
    """
    r = requests.get(f"{API_BASE}/workouts/schema", params={"whatsapp_id": whatsapp_id}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def api_workouts_log_by_id(whatsapp_id: str, exercise_id: int, sets: int, reps: int, weight: float, unit: str) -> Dict[str, Any]:
    """Log a set for a predefined exercise by exercise_id.

    The 'unit' must be "kg" or "lb". If the user logged bodyweight, pass weight=0 and unit="kg".

    Args:
        whatsapp_id (str): WhatsApp ID.
        exercise_id (int): ID of the exercise from /exercises.
        sets (int): Number of sets performed.
        reps (int): Reps per set.
        weight (float): Weight value as provided by the user (not converted).
        unit (str): "kg" or "lb".

    Returns:
        dict: The created log payload and display echo.
    """
    payload = {
        "whatsapp_id": whatsapp_id,
        "exercise_id": exercise_id,
        "sets": sets,
        "reps": reps,
        "weight": weight,   # Laravel converts to weight_kg internally
        "notes": None
    }
    r = requests.post(f"{API_BASE}/workouts/log", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def api_workouts_log_by_name(whatsapp_id: str, exercise_name: str, sets: int, reps: int, weight: float, unit: str) -> Dict[str, Any]:
    """Log a set using a free-text exercise name (when no ID match).

    Args:
        whatsapp_id (str): WhatsApp ID.
        exercise_name (str): Exercise name to attach to the log.
        sets (int): Sets performed.
        reps (int): Reps per set.
        weight (float): Weight value as provided by the user. Use 0 for bodyweight.
        unit (str): "kg" or "lb".

    Returns:
        dict: The created log payload and display echo.
    """
    payload = {
        "whatsapp_id": whatsapp_id,
        "exercise_name": exercise_name,
        "sets": sets,
        "reps": reps,
        "weight": weight,   # Laravel converts to weight_kg internally
        "notes": None
    }
    r = requests.post(f"{API_BASE}/workouts/log", json=payload, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def api_workouts_logs_today(whatsapp_id: str) -> Dict[str, Any]:
    """List today's workout logs for the user.

    Args:
        whatsapp_id (str): WhatsApp ID.

    Returns:
        dict: {date, logs:[...]}
    """
    r = requests.get(f"{API_BASE}/workouts/logs/today", params={"whatsapp_id": whatsapp_id}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def api_workouts_delete_log(whatsapp_id: str, log_id: int) -> Dict[str, Any]:
    """Delete a specific workout log.

    Args:
        whatsapp_id (str): WhatsApp ID.
        log_id (int): The log ID to delete.

    Returns:
        dict: {"deleted": true}
    """
    r = requests.delete(f"{API_BASE}/workouts/log/{log_id}", params={"whatsapp_id": whatsapp_id}, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()
