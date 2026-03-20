from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.api import ModelEvaluationReportSchema, MutationResponseSchema, PipelineStatusResponseSchema
from app.services.admin import AdminService
from app.services.evaluations import EvaluationService

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/pipeline-status", response_model=PipelineStatusResponseSchema)
def get_pipeline_status(db: Session = Depends(get_db)):
    return AdminService(db).pipeline_status()


@router.post("/ingest/run", response_model=MutationResponseSchema)
def run_ingest(db: Session = Depends(get_db)):
    return AdminService(db).run_ingest()


@router.post("/seed/reset", response_model=MutationResponseSchema)
def reset_seed(db: Session = Depends(get_db)):
    return AdminService(db).reset_seed()


@router.get("/evaluations", response_model=list[ModelEvaluationReportSchema])
def list_evaluations():
    return EvaluationService().list_reports()


@router.get("/evaluations/{model_name}", response_model=ModelEvaluationReportSchema)
def get_evaluation(model_name: str):
    report = EvaluationService().get_report(model_name)
    if report is None:
        raise HTTPException(status_code=404, detail="Evaluation report not found")
    return report

