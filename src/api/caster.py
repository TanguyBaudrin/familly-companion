from fastapi import APIRouter, HTTPException, status
from typing import List, Dict
import pychromecast
import logging
import uuid
from starlette.concurrency import run_in_threadpool
from src.core import schemas # Import schemas

# Pour DashCast
from pychromecast.controllers.dashcast import DashCastController

router = APIRouter()

# Suppress pychromecast's extensive logging
logging.getLogger("pychromecast").setLevel(logging.WARNING)
logging.getLogger("zeroconf").setLevel(logging.WARNING)

logging.getLogger("pychromecast").setLevel(logging.WARNING)
logging.getLogger("zeroconf").setLevel(logging.WARNING)

# Helper function to run blocking pychromecast calls
def _discover_chromecasts_blocking():
    chromecasts, _ = pychromecast.get_chromecasts()
    return chromecasts, _

def _get_chromecast_from_uuid_blocking(uuid_str: str):
    chromecasts, _ = pychromecast.get_chromecasts()
    target_uuid = uuid.UUID(uuid_str)
    found_cast = None
    for cast in chromecasts:
        if cast.uuid == target_uuid:
            found_cast = cast
            break
    return found_cast

@router.get("/cast/devices", response_model=List[Dict[str, str]])
async def get_cast_devices():
    """
    Discovers Chromecast devices on the local network.
    Returns a list of dictionaries, each with 'name' and 'uuid'.
    """
    try:
        chromecasts, _browser = await run_in_threadpool(_discover_chromecasts_blocking)
        devices = []
        for cast in chromecasts:
            # cast.name est le nom convivial, cast.uuid l'identifiant
            devices.append({"name": cast.name, "uuid": str(cast.uuid)})
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
        cast = await run_in_threadpool(_get_chromecast_from_uuid_blocking, request_body.device_uuid)
        if not cast:
            raise HTTPException(status_code=404, detail="Chromecast device not found.")

        # Attendre la connexion
        await run_in_threadpool(cast.wait)

        if getattr(request_body, "is_webpage", False):
            # Utiliser DashCast pour caster une page web
            dashcast = DashCastController()
            cast.register_handler(dashcast)
            await run_in_threadpool(dashcast.load_url, request_body.url)
            return {"message": f"Successfully casted web page {request_body.url} to {cast.name}"}
        else:
            # Utiliser play_media pour caster une vidéo/flux
            await run_in_threadpool(cast.media_controller.play_media, request_body.url, "video/mp4")
            await run_in_threadpool(cast.media_controller.block_until_active)
            return {"message": f"Successfully casted {request_body.url} to {cast.name}"}
    except pychromecast.error.ChromecastConnectionError as e:
        logging.error(f"Chromecast connection error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to connect to Chromecast: {e}")
    except Exception as e:
        logging.error(f"Error casting URL: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to cast URL: {e}")