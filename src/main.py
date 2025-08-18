
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api import web_routes, statistics, member_details

app = FastAPI()


app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
app.include_router(web_routes.router)
app.include_router(statistics.router, prefix="/api/v1")
app.include_router(member_details.router, prefix="/api/v1")

@app.get("/api/hello")
def read_root():
    return {"Hello": "World"}