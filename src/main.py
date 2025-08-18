
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api import web_routes

app = FastAPI()


app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
app.include_router(web_routes.router)

@app.get("/api/hello")
def read_root():
    return {"Hello": "World"}