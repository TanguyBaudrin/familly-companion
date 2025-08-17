from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from src.api import web_routes
from src.core.config import settings
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    SessionMiddleware, secret_key=settings.SECRET_KEY
)

app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
app.include_router(web_routes.router)

@app.get("/api/hello")
def read_root():
    return {"Hello": "World"}