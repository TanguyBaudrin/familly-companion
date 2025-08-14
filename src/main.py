from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api import web_routes, user_routes, auth_routes

app = FastAPI()

app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
app.include_router(web_routes.router)
app.include_router(user_routes.router)
app.include_router(auth_routes.router)

@app.get("/api/hello")
def read_root():
    return {"Hello": "World"}