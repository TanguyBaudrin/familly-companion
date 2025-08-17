from fastapi import APIRouter, Request, Depends, HTTPException, Body, status
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from starlette.config import Config
from pydantic import BaseModel

from src.core.config import settings
from src.core import services
from src.data.database import get_db

router = APIRouter()

config = Config()
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid email profile'},
)



@router.get('/login/google')
async def login_google(request: Request):
    redirect_uri = settings.REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/auth/google')
async def auth_google(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = await oauth.google.parse_id_token(request, token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {e}")

    # Check if user already exists by google_id or email
    user = services.get_user_by_google_id(db, user_info['sub'])
    if not user:
        user = services.get_user_by_email(db, user_info['email'])

    if user:
        # Update existing user with Google info if not already linked
        if not user.google_id:
            user.google_id = user_info['sub']
            user.profile_picture = user_info.get('picture')
            db.add(user)
            db.commit()
            db.refresh(user)
    else:
        # Create new user
        user_data = {
            "username": user_info.get('name', user_info['email'].split('@')[0]), # Use name or part of email as username
            "email": user_info['email'],
            "google_id": user_info['sub'],
            "profile_picture": user_info.get('picture')
        }
        user = services.create_user_from_oauth(db, user_data)

    # Store user info in session
    request.session["user"] = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "profile_picture": user.profile_picture
    }
    return RedirectResponse(url="/dashboard")

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")

async def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user
