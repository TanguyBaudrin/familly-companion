
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.api import web_routes, statistics, member_details, caster

app = FastAPI()


app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
app.include_router(web_routes.router)
app.include_router(statistics.router, prefix="/api/v1")
app.include_router(member_details.router, prefix="/api/v1")
app.include_router(caster.router, prefix="/api/v1")

@app.get("/api/hello")
def read_root():
    return {"Hello": "World"}

# TEMPORARY DEBUG ENDPOINT
@app.get("/debug/routes")
def debug_routes():
    routes_list = []
    for route in app.routes:
        routes_list.append({"path": route.path, "name": route.name, "methods": route.methods if hasattr(route, 'methods') else []})
    return routes_list
# END TEMPORARY DEBUG ENDPOINT