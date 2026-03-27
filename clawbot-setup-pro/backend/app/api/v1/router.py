from fastapi import APIRouter

from app.api.v1 import auth, devices, entitlements, billing, pairing, jobs, device_poll, devtools

api_router = APIRouter(prefix="/v1")
api_router.include_router(auth.router)
api_router.include_router(entitlements.router)
api_router.include_router(devices.router)
api_router.include_router(pairing.router)
api_router.include_router(device_poll.router)
api_router.include_router(billing.router)
api_router.include_router(jobs.router)
api_router.include_router(devtools.router)
