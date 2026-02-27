"""Config routes - serve editable configuration like exam slots."""

from fastapi import APIRouter, HTTPException
import json
import os
import logging

logger = logging.getLogger("config_routes")

router = APIRouter(prefix="/config", tags=["config"])

EXAM_SLOTS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exam_slots.json")


@router.get("/exam-slots")
async def get_exam_slots():
    """
    Return exam centre / date / time slot configuration.
    Reads fresh from exam_slots.json on every request so edits take effect immediately.
    """
    try:
        with open(EXAM_SLOTS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        logger.error("exam_slots.json not found")
        raise HTTPException(status_code=500, detail="Exam slots configuration not found")
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in exam_slots.json: {e}")
        raise HTTPException(status_code=500, detail="Exam slots configuration is invalid")
