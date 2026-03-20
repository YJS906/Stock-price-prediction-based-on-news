from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.clusters import ClusterService

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("")
def list_clusters(db: Session = Depends(get_db)):
    return ClusterService(db).list_clusters()


@router.get("/{cluster_id}")
def get_cluster(cluster_id: UUID, db: Session = Depends(get_db)):
    response = ClusterService(db).get_cluster_detail(cluster_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Cluster not found")
    return response

