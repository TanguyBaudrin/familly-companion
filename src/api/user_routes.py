from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from src.core import services
from src.data.database import get_db

router = APIRouter()

@router.post("/api/users/register")
async def register_user(request: Request, db: Session = Depends(get_db), username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    user_data = {
        "username": username,
        "email": email,
        "password": password
    }
    services.create_user(db, user_data)
    return RedirectResponse(url="/", status_code=303)
