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
        "rank": None,
        "scholarship": None
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
            
            scholarship = None
            if mapping.get("scholarship"):
                try:
                    raw_scholarship = row.get(mapping["scholarship"])
                    
                    # Handle fractional value
                    if isinstance(raw_scholarship, float) and 0 < raw_scholarship < 1:
                        raw_scholarship = raw_scholarship * 100
                                        
                    # print(f"Raw scholarship value: {raw_scholarship} (type: {type(raw_scholarship)})")
                    if pd.notna(raw_scholarship):
                        # Handle "90%" format - strip % and convert to float
                        scholarship_str = str(raw_scholarship).strip().rstrip('%')
                        scholarship = float(scholarship_str)
                except Exception:
                    scholarship = None

            if not name or not phone:
                continue

            entry = StudentResult(
                name=name,
                phone=phone,
                percentage=percentage,
                rank=rank,
                scholarship=scholarship,
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
            "scholarship": r.scholarship,
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


def _get_fuzzy_score(submitted_name: str, db_name: str) -> int:
    """Get fuzzy match score between two names."""
    if not RAPIDFUZZ_AVAILABLE:
        # Fallback
        if submitted_name.lower() in db_name.lower() or db_name.lower() in submitted_name.lower():
            return 100
        return 0
    
    s1 = ' '.join(submitted_name.strip().lower().split())
    s2 = ' '.join(db_name.strip().lower().split())
    return fuzz.token_sort_ratio(s1, s2)


def _fuzzy_name_match(submitted_name: str, db_name: str, threshold: int = 85) -> bool:
    """Check if two names match using fuzzy matching."""
    return _get_fuzzy_score(submitted_name, db_name) >= threshold


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
    
    # Step 1: Find all records by phone number
    all_phone_results = db.query(StudentResult).filter(StudentResult.phone == norm_phone).all()
    
    if not all_phone_results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")
    
    # Step 2: If fuzzy name matching is enabled, verify the name
    result = None
    suggestions = []
    
    if settings.fuzzy_name_match_enabled and name:
        submitted_name = name.strip()
        if submitted_name:
            # Find BEST match (highest score), not just first match above threshold
            best_match = None
            best_score = 0
            
            for r in all_phone_results:
                score = _get_fuzzy_score(submitted_name, r.name)
                if score > best_score:
                    best_score = score
                    best_match = r
                if score < settings.fuzzy_name_threshold and score >= 50:
                    # Include as suggestion if somewhat similar but below threshold
                    suggestions.append({"name": r.name, "phone": r.phone, "score": score})
            
            # Use best match if it meets threshold
            if best_score >= settings.fuzzy_name_threshold:
                result = best_match
            else:
                # Best match didn't meet threshold - add it to suggestions too
                if best_match and best_score >= 50:
                    suggestions.append({"name": best_match.name, "phone": best_match.phone, "score": best_score})
            
            if not result and not suggestions:
                # No match and no suggestions - return all names for this phone as suggestions
                suggestions = [{"name": r.name, "phone": r.phone, "score": 0} for r in all_phone_results]
            
            if not result:
                # Sort suggestions by score descending
                suggestions.sort(key=lambda x: x["score"], reverse=True)
                logger.info(f"Fuzzy name mismatch: submitted='{submitted_name}' - returning {len(suggestions)} suggestions")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, 
                    detail={"message": "Name does not match. Did you mean one of these?", "suggestions": suggestions[:5]}
                )
        else:
            result = all_phone_results[0]
    else:
        result = all_phone_results[0]
    
    logger.info(f"Search success - phone: {norm_phone}, name: {name}")

    # Build scholarship response using value directly from Excel/DB
    scholarship_data = None
    if result.scholarship is not None:
        scholarship_value = int(result.scholarship) if result.scholarship == int(result.scholarship) else result.scholarship
        scholarship_message = f"""🎉 Congratulations!

You have successfully qualified in the NSAT Scholarship Test.

Based on your performance, you have been awarded a scholarship of {scholarship_value}% on SVPS PW Vidyapeeth programs.

To avail your scholarship and secure your admission, please visit the campus with your parents at the earliest.

📍 Venue: SVPS School
Near Ughadmal Balaji, Sawaimadhopur Road, Gangapur City

📞 For more information contact: 9983616223 / 9983616224

⚠️ Scholarship is valid for a limited period and applicable as per institute terms & conditions.

We look forward to welcoming you and helping you achieve your academic goals!"""
        scholarship_data = {
            "scholarship": scholarship_value,
            "message": scholarship_message
        }

    resp = {
        "id": result.id,
        "name": result.name,
        "phone": result.phone,
        "percentage": result.percentage,
        "rank": result.rank,
        "source_file": result.source_file,
        "created_at": result.created_at
    }
    if scholarship_data:
        resp['scholarship'] = scholarship_data
    return resp
