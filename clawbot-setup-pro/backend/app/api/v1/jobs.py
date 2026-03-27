import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.device import Device
from app.models.device_command import DeviceCommand
from app.models.job import Job
from app.schemas.jobs import JobCompleteIn, JobProgressIn, JobStartRequest, JobStartResponse, JobStatusResponse
from app.services.auth import get_current_user_id
from app.services.device_auth import get_current_device_id

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/start", response_model=JobStartResponse)
def start_job(
    payload: JobStartRequest,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    device: Device | None = db.query(Device).filter(Device.id == payload.device_id, Device.user_id == user_id).one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="device_not_found")

    # one-at-a-time per device
    active = (
        db.query(Job)
        .filter(Job.device_id == payload.device_id, Job.status.in_(["queued", "running"]))
        .first()
    )
    if active:
        raise HTTPException(status_code=409, detail="job_already_running")

    job_id = str(uuid.uuid4())
    job = Job(
        id=job_id,
        user_id=user_id,
        device_id=payload.device_id,
        status="queued",
        progress="0",
        plan_json=json.dumps(payload.plan),
        result_json=None,
    )
    db.add(job)

    cmd = DeviceCommand(
        id=str(uuid.uuid4()),
        device_id=payload.device_id,
        job_id=job_id,
        kind="run_plan",
        payload_json=json.dumps({"job_id": job_id, "plan": payload.plan}),
        status="queued",
    )
    db.add(cmd)

    db.commit()

    return JobStartResponse(job_id=job_id)


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job(
    job_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    job: Job | None = db.query(Job).filter(Job.id == job_id, Job.user_id == user_id).one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")

    result = json.loads(job.result_json) if job.result_json else None
    return JobStatusResponse(
        job_id=job.id,
        device_id=job.device_id,
        status=job.status,
        progress=int(job.progress),
        result=result,
    )


@router.post("/{job_id}/progress")
def job_progress(
    job_id: str,
    payload: JobProgressIn,
    device_id: str = Depends(get_current_device_id),
    db: Session = Depends(get_db),
):
    job: Job | None = db.query(Job).filter(Job.id == job_id, Job.device_id == device_id).one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")

    job.status = "running"
    job.progress = str(max(0, min(payload.progress, 100)))
    db.commit()

    return {"ok": True}


@router.post("/{job_id}/complete")
def job_complete(
    job_id: str,
    payload: JobCompleteIn,
    device_id: str = Depends(get_current_device_id),
    db: Session = Depends(get_db),
):
    job: Job | None = db.query(Job).filter(Job.id == job_id, Job.device_id == device_id).one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")

    if payload.status not in ("succeeded", "failed"):
        raise HTTPException(status_code=400, detail="bad_status")

    job.status = payload.status
    job.progress = "100" if payload.status == "succeeded" else job.progress
    job.result_json = json.dumps(payload.result) if payload.result is not None else None
    db.commit()

    return {"ok": True}
