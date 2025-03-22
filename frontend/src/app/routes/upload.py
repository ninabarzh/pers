# frontend/src/app/routes/upload.py
from starlette.templating import Jinja2Templates
from starlette.requests import Request
import httpx
import os
import logging
import json

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize Jinja2 templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

async def upload_page(request: Request):
    return templates.TemplateResponse(request, "upload.html")

async def handle_upload(request: Request):
    form_data = await request.form()
    file = form_data.get("json_file")

    if not file:
        return templates.TemplateResponse(request, "upload.html", {"error": "No file provided."})

    try:
        file_content = await file.read()
        if file.filename.endswith(".json"):
            data = json.loads(file_content.decode("utf-8"))
        else:
            data = {"file_content": file_content.decode("utf-8")}

        async with httpx.AsyncClient() as client:
            response = await client.post("http://backend:8000/upload", json=data)
            return templates.TemplateResponse(request, "upload.html", {"success": True})
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return templates.TemplateResponse(request, "upload.html", {"error": f"Error uploading file: {e}"})
