from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_viewer, require_analyst
from app.models.user import User
from app.schemas.summary import FinancialSummary
from app.services.summary import get_summary

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get("/", response_model=FinancialSummary)
def financial_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_viewer),
):
    """
    Returns financial summary for the current user.
    - Viewers see their own data only.
    - Analysts and Admins see aggregate data across all users.
    """
    return get_summary(db, current_user)
