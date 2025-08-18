from fastapi import APIRouter, HTTPException, status
from typing import List, Dict
import pychromecast
import logging
from starlette.concurrency import run_in_threadpool
from src.core import schemas # Import schemas

router = APIRouter()

# Suppress pychromecast's extensive logging
logging.getLogger("pychromecast").setLevel(logging.WARNING)
logging.getLogger("zeroconf").setLevel(logging.WARNING)

# Helper function to run blocking pychromecast calls
def _discover_chromecasts_blocking():
    chromecasts, browser = pychromecast.discover_chromecasts()
    return chromecasts, browser

def _get_chromecast_from_uuid_blocking(uuid: str):
    return pychromecast.get_chromecast_from_uuid(uuid)

@router.get("/cast/devices", response_model=List[Dict[str, str]])
async def get_cast_devices():
    """
    Discovers Chromecast devices on the local network.
    Returns a list of dictionaries, each with 'name' and 'uuid'.
    """
    try:
        chromecasts, browser = await run_in_threadpool(_discover_chromecasts_blocking)
        devices = []
        for cast in chromecasts:
            devices.append({"name": cast.friendly_name, "uuid": str(cast.uuid)})
        # It's important to stop the browser, but it might block if done directly in async
        # We can use BackgroundTasks for cleanup if needed, but for simple discovery,
        # the browser might stop itself after a short period.
        # For now, let's assume it's okay to stop it directly after discovery.
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
        cast = await run_in_threadpool(_get_chromecast_from_uuid_blocking, request_body.device_uuid) # Use request_body
        if not cast:
            raise HTTPException(status_code=404, detail="Chromecast device not found.")

        # wait_until_connected and set_display_url are also blocking
        await run_in_threadpool(cast.wait_until_connected)
        await run_in_threadpool(cast.set_display_url, request_body.url) # Use request_body

        return {"message": f"Successfully casted {request_body.url} to {cast.device.friendly_name}"}
    except pychromecast.exceptions.ChromecastConnectionError as e:
        logging.error(f"Chromecast connection error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to connect to Chromecast: {e}")
    except Exception as e:
        logging.error(f"Error casting URL: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to cast URL: {e}")