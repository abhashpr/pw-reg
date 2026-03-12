from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import StudentResult
from config import get_settings
from typing import List, Optional
import pandas as pd
import json
import io
import logging
import re

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False

from routers.admin_routes import get_admin_user

logger = logging.getLogger("results_routes")

router = APIRouter(prefix="/results", tags=["results"])


# Load scholarship rules from backend/configs/scholarships.json if present
_SCHOLARSHIP_RULES = None


def _load_scholarship_rules():
    global _SCHOLARSHIP_RULES
    if _SCHOLARSHIP_RULES is not None:
        return _SCHOLARSHIP_RULES
    try:
        from pathlib import Path
        cfg_path = Path(__file__).resolve().parents[1] / 'configs' / 'scholarships.json'
        if not cfg_path.exists():
            _SCHOLARSHIP_RULES = []
            return _SCHOLARSHIP_RULES

        with open(cfg_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)

        rules = []
        for item in raw:
            pct = item.get('percentage')
            # Accept formats: "range(20-30)", "20-30", or {"min":20,"max":30}
            min_pct = None
            max_pct = None
            if isinstance(pct, str):
                m = re.search(r"range\((\d{1,3})-(\d{1,3})\)", pct)
                if m:
                    min_pct = float(m.group(1))
                    max_pct = float(m.group(2))
                else:
                    m2 = re.search(r"^(\d{1,3})-(\d{1,3})$", pct)
                    if m2:
                        min_pct = float(m2.group(1))
                        max_pct = float(m2.group(2))
            elif isinstance(pct, dict):
                min_pct = float(pct.get('min')) if pct.get('min') is not None else None
                max_pct = float(pct.get('max')) if pct.get('max') is not None else None

            scholarship = item.get('scholarship')
            message = item.get('message')
            if (min_pct is not None or max_pct is not None) and scholarship is not None:
                rules.append({
                    'min': min_pct,
                    'max': max_pct,
                    'scholarship': scholarship,
                    'message': message
                })

        _SCHOLARSHIP_RULES = rules
        return _SCHOLARSHIP_RULES
    except Exception as e:
        logger.warning(f"Failed to load scholarship rules: {e}")
        _SCHOLARSHIP_RULES = []
        return _SCHOLARSHIP_RULES


@router.post("/upload")
async def upload_results(
    excel_file: UploadFile = File(...),
    config_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    _=Depends(get_admin_user)
):
    """Upload an Excel file and optional JSON mapping config. Admin only."""
    try:
        content = await excel_file.read()
        excel_buf = io.BytesIO(content)
        # Read Excel into DataFrame
        df = pd.read_excel(excel_buf)
    except Exception as e:
        logger.error(f"Failed to read Excel file: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Excel file")

    # Default mapping: look for obvious column names
    mapping = {
        "name": None,
        "phone": None,
        "percentage": None,
        "rank": None
    }

    if config_file:
        try:
            cfg_bytes = await config_file.read()
            cfg = json.loads(cfg_bytes.decode())
            # Expect mapping object in config or use flat mapping
            mapping.update(cfg.get("mapping", cfg))
        except Exception as e:
            logger.error(f"Invalid config JSON: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON config")

    # Try to auto-detect columns if mapping values are None
    cols = [c.lower() for c in df.columns]
    for key in list(mapping.keys()):
        if not mapping.get(key):
            # find first column containing the key name
            for c in df.columns:
                if key in c.lower():
                    mapping[key] = c
                    break

    # Ensure required mappings exist
    if not mapping["name"] or not mapping["phone"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Mapping must include at least 'name' and 'phone' columns")

    inserted = 0
    source_filename = excel_file.filename
    for _, row in df.iterrows():
        try:
            name = str(row.get(mapping["name"]) or "").strip()
            raw_phone = row.get(mapping["phone"])
            # Normalize phone to digits-only string. Handle numeric Excel cells.
            if pd.isna(raw_phone):
                phone = ""
            elif isinstance(raw_phone, (int,)) or (isinstance(raw_phone, float) and float(raw_phone).is_integer()):
                phone = str(int(raw_phone))
            else:
                phone = ''.join(re.findall(r"\d+", str(raw_phone)))
            phone = phone.strip()
            percentage = None
            rank = None
            if mapping.get("percentage"):
                try:
                    percentage = float(row.get(mapping["percentage"]) or None)
                except Exception:
                    percentage = None
            if mapping.get("rank"):
                try:
                    rank = int(row.get(mapping["rank"]) or None)
                except Exception:
                    rank = None

            if not name or not phone:
                continue

            entry = StudentResult(
                name=name,
                phone=phone,
                percentage=percentage,
                rank=rank,
                source_file=source_filename
            )
            db.add(entry)
            inserted += 1
        except Exception as e:
            logger.warning(f"Skipping row due to error: {e}")

    db.commit()
    return {"inserted": inserted}


@router.get("/admin", response_model=List[dict])
def list_results_admin(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    """Return all imported results (admin only)."""
    rows = db.query(StudentResult).order_by(StudentResult.id.desc()).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "phone": r.phone,
            "percentage": r.percentage,
            "rank": r.rank,
            "source_file": r.source_file,
            "created_at": r.created_at
        }
        for r in rows
    ]


@router.delete("/admin/truncate")
def truncate_results_admin(db: Session = Depends(get_db), _=Depends(get_admin_user)):
    """Delete all imported results (admin only)."""
    deleted = db.query(StudentResult).delete(synchronize_session=False)
    db.commit()
    return {"deleted": deleted, "message": "All results data removed."}


def _fuzzy_name_match(submitted_name: str, db_name: str, threshold: int = 85) -> bool:
    """Check if two names match using fuzzy matching."""
    if not RAPIDFUZZ_AVAILABLE:
        # Fallback to case-insensitive contains match
        return submitted_name.lower() in db_name.lower() or db_name.lower() in submitted_name.lower()
    
    # Normalize strings (lowercase and remove extra spaces)
    s1 = ' '.join(submitted_name.strip().lower().split())
    s2 = ' '.join(db_name.strip().lower().split())
    
    # Use token_sort_ratio for best results with names (handles word order differences)
    score = fuzz.token_sort_ratio(s1, s2)
    return score >= threshold


@router.get("/search")
def search_result(name: Optional[str] = None, phone: Optional[str] = None, db: Session = Depends(get_db)):
    """Search for a student result by name and/or phone (public).
    
    Strategy:
    1. Filter by phone number first (primary key, fast)
    2. If FUZZY_NAME_MATCH_ENABLED, verify name using fuzzy matching
    3. If fuzzy matching disabled, return result based on phone only
    """
    settings = get_settings()
    
    # Normalize phone search parameter to digits-only string
    norm_phone = ''.join(re.findall(r"\d+", str(phone))) if phone else ""
    
    if not norm_phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Phone number is required")
    
    # Step 1: Find record by phone number (fast, indexed lookup)
    result = db.query(StudentResult).filter(StudentResult.phone == norm_phone).first()
    
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")
    
    # Step 2: If fuzzy name matching is enabled, verify the name
    if settings.fuzzy_name_match_enabled and name:
        submitted_name = name.strip()
        if submitted_name:
            if not _fuzzy_name_match(submitted_name, result.name, settings.fuzzy_name_threshold):
                logger.info(f"Fuzzy name mismatch: submitted='{submitted_name}' vs stored='{result.name}'")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")
    
    logger.info(f"Search success - phone: {norm_phone}, name: {name}")

    # Evaluate scholarship rules (if any)
    scholarship = None
    try:
        rules = _load_scholarship_rules()
        pct = None
        if result.percentage is not None:
            try:
                pct = float(result.percentage)
            except Exception:
                pct = None

        if pct is not None and rules:
            for r in rules:
                minv = r.get('min')
                maxv = r.get('max')
                if minv is None and maxv is None:
                    continue
                match = False
                if minv is None and maxv is not None and pct <= maxv:
                    match = True
                elif maxv is None and minv is not None and pct >= minv:
                    match = True
                elif minv is not None and maxv is not None and (pct >= minv and pct <= maxv):
                    match = True

                if match:
                    scholarship = {"scholarship": r.get('scholarship'), "message": r.get('message')}
                    break
    except Exception:
        scholarship = None

    resp = {
        "id": result.id,
        "name": result.name,
        "phone": result.phone,
        "percentage": result.percentage,
        "rank": result.rank,
        "source_file": result.source_file,
        "created_at": result.created_at
    }
    print(f"Scholarship evaluated: {scholarship}")
    if scholarship:
        resp['scholarship'] = scholarship
    return resp
