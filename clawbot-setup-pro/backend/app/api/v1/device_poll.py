import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.device_command import DeviceCommand
from app.services.device_auth import get_current_device_id

router = APIRouter(prefix="/devices", tags=["devices"])


@router.post("/{device_id}/poll")
def poll(device_id: str, authed_device_id: str = Depends(get_current_device_id), db: Session = Depends(get_db)):
    if authed_device_id != device_id:
        return {"commands": []}

    cmd: DeviceCommand | None = (
        db.query(DeviceCommand)
        .filter(DeviceCommand.device_id == device_id, DeviceCommand.status == "queued")
        .order_by(DeviceCommand.created_at.asc())
        .first()
    )

    if not cmd:
        return {"commands": []}

    cmd.status = "delivered"
    db.commit()

    return {
        "commands": [
            {
                "id": cmd.id,
                "job_id": cmd.job_id,
                "kind": cmd.kind,
                "payload": json.loads(cmd.payload_json),
            }
        ]
    }
