import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def serve_frontend():
    with open(os.path.join("app", "static", "schedulerfrontend.html"), "r") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)
