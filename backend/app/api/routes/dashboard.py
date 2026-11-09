from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.dashboard import DashboardSummary, CategorySpending
from app.services import dashboard_service
from app.schemas.dashboard import MonthlyTrend

router = APIRouter(
    prefix="/api/dashboard",
    tags=["Dashboard"]
)


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    return dashboard_service.get_dashboard_summary(db)


@router.get("/category-spending", response_model=list[CategorySpending])
def get_category_spending(db: Session = Depends(get_db)):
    return dashboard_service.get_category_spending(db)

@router.get("/monthly-trends", response_model=list[MonthlyTrend])
def get_monthly_trends(db: Session = Depends(get_db)):
    return dashboard_service.get_monthly_trends(db)