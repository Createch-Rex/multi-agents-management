from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import FastAPI, Response, Request
from api.router import api_router
from utils import common
import config
import os

app = FastAPI(docs_url=None)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(GZipMiddleware)

app.include_router(api_router, prefix="/v1/api")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    if not common.check_status():
        return Response(status_code=404, content="Content Not Found")
    response = await call_next(request)
    return response


@app.get("/static/{path:path}")
async def static_file(path: str):
    if path:
        file_path = os.path.join(config.STATIC_DIR, path)
        if os.path.exists(file_path):
            return FileResponse(file_path, headers={"Access-Control-Allow-Origin": "*", "Cache-Control": "max-age=-1"})
    return Response(status_code=404, content="Content Not Found")


@app.get("/health_check")
async def keep_alive():
    return Response(status_code=200)


@app.get("/{path:path}")
async def spa_web_route(path: str):
    if path:
        file_path = os.path.join(config.WEB_DIR, 'browser', path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
    index_path = os.path.join(config.WEB_DIR, 'browser', 'index.html')
    if os.path.isfile(index_path):
        return FileResponse(index_path, headers={"Access-Control-Allow-Origin": "*"})
    return Response(status_code=404, content="Content Not Found")


@app.get("")
async def spa_route():
    return RedirectResponse('/')
