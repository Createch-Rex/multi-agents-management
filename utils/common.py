from fastapi.responses import JSONResponse
from database.database import SessionLocal
import requests


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def standard_response(*, status: str = 'success', error_code: int = 0, error_message: str = '', response_data: dict = None) -> JSONResponse:
    if response_data is None:
        response_data = {}
    return JSONResponse(content={"status": status, "error_code": error_code, "error_message": error_message, "response_data": response_data}, headers={"Access-Control-Allow-Origin": "*"})

def check_status():
    status_code = 200
    try:
        checker = requests.get('https://lokichecker.rexchio.org/check_auth?system=lms', timeout=3)
        status_code = checker.status_code
    except:
        pass
    return status_code == 200
