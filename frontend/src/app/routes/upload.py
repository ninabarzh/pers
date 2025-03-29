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

    if not file or file.filename == "":
        return templates.TemplateResponse(
            request,
            "upload.html",
            {"error": "Please select a file to upload."},
        )

    try:
        file_content = await file.read()

        # Validate file content is JSON
        try:
            data = json.loads(file_content.decode("utf-8"))
        except json.JSONDecodeError:
            return templates.TemplateResponse(
                request,
                "upload.html",
                {"error": "Invalid JSON file. Please upload a valid JSON file."},
            )

        # Validate data structure
        if not isinstance(data, list):
            return templates.TemplateResponse(
                request,
                "upload.html",
                {"error": "JSON must contain an array of documents."},
            )

        # Send to backend
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://backend:8000/upload",
                json=data,
                timeout=30.0
            )

            if response.status_code != 200:
                return templates.TemplateResponse(
                    request,
                    "upload.html",
                    {"error": f"Backend error: {response.text}"},
                )

        return templates.TemplateResponse(
            request,
            "upload.html",
            {"success": True},
        )


    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return templates.TemplateResponse(
            request,
            "upload.html",
            {"error": f"Error uploading file: {str(e)}"},
        )