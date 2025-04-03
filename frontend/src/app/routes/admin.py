# frontend/src/app/routes/admin.py
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


async def admin_dashboard(request: Request):
    """Main admin interface"""
    return templates.TemplateResponse("admin.html", {"request": request})


async def handle_admin_actions(request: Request):
    """Handles all admin operations"""
    form_data = await request.form()

    # File Upload Handling
    if "json_file" in form_data:
        file = form_data["json_file"]

        if not file or file.filename == "":
            return templates.TemplateResponse(
                "admin.html",
                {"request": request, "error": "Please select a file to upload."},
            )

        try:
            file_content = await file.read()

            # Validate JSON
            try:
                data = json.loads(file_content.decode("utf-8"))
            except json.JSONDecodeError:
                return templates.TemplateResponse(
                    "admin.html",
                    {"request": request, "error": "Invalid JSON file"},
                )

            if not isinstance(data, list):
                return templates.TemplateResponse(
                    "admin.html",
                    {"request": request, "error": "JSON must be an array"},
                )

            # Get backend URL from app state
            backend_url = request.app.state.config['BACKEND_URL']

            # Send to backend
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{backend_url}/upload",
                    json=data,
                    timeout=30.0,
                    headers={"Content-Type": "application/json"}  # Explicit content-type
                )
                response.raise_for_status()

            return templates.TemplateResponse(
                "admin.html",
                {"request": request, "success": "File processed successfully"},
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"Backend error: {e.response.text}")
            return templates.TemplateResponse(
                "admin.html",
                {"request": request, "error": f"Backend error: {e.response.text}"},
            )
        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return templates.TemplateResponse(
                "admin.html",
                {"request": request, "error": f"Error: {str(e)}"},
            )

    # Future admin actions can be added here
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "error": "Invalid admin action"},
    )
