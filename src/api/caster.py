from fastapi import APIRouter, HTTPException, status
from typing import List, Dict
import pychromecast
import logging
import uuid
from starlette.concurrency import run_in_threadpool
from src.core import schemas # Import schemas

router = APIRouter()

# Suppress pychromecast's extensive logging
logging.getLogger("pychromecast").setLevel(logging.WARNING)
logging.getLogger("zeroconf").setLevel(logging.WARNING)

CASTS = pychromecast.get_chromecasts()

@router.get("/cast/devices", response_model=List[Dict[str, str]])
async def get_cast_devices():
    """
    Discovers Chromecast devices on the local network.
    Returns a list of dictionaries, each with 'name' and 'uuid'.
    """
    try:
        devices = []
        for cast in CASTS:
            devices.append({"name": cast.friendly_name, "uuid": str(cast.uuid)})
        return devices
    except Exception as e:
        logging.error(f"Error discovering Chromecasts: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to discover devices: {e}")

@router.post("/cast/start", status_code=status.HTTP_200_OK)
async def start_cast(request_body: schemas.CastRequest): # Modified signature
    """
    Starts casting a URL to a specific Chromecast device.
    """
    try:
        target_uuid = uuid.UUID(request_body.device_uuid)
        cast = next((c for c in CASTS if c.uuid == target_uuid), None)

        if not cast:
            raise HTTPException(status_code=404, detail="Chromecast device not found.")

        # wait_until_connected and set_display_url are also blocking
        await run_in_threadpool(cast.wait_until_connected)
        await run_in_threadpool(cast.set_display_url, request_body.url) # Use request_body

        return {"message": f"Successfully casted {request_body.url} to {cast.device.friendly_name}"}
    except pychromecast.error.ChromecastConnectionError as e:
        logging.error(f"Chromecast connection error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to connect to Chromecast: {e}")
    except Exception as e:
        logging.error(f"Error casting URL: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to cast URL: {e}")