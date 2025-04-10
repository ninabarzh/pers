# frontend/src/app/routes/static_pages.py
from starlette.templating import Jinja2Templates
from starlette.requests import Request
from starlette.responses import JSONResponse
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "../templates"))

def get_base_context(request: Request, active_page: str = ""):
    """Shared context for all pages"""
    return {
        "request": request,
        "active_page": active_page,
        "now": datetime.now(),  # For last updated dates
        "FRIENDLY_CAPTCHA_SITE_KEY": os.getenv("FRIENDLY_CAPTCHA_SITE_KEY")  # Add hCaptcha key to base
    }


async def about(request: Request):
    context = get_base_context(request, "about")
    return templates.TemplateResponse(
        "about.html",
        {**context, "meta_title": "About Us - Pers"}
    )


async def contact(request: Request):
    """Handle GET requests for contact page"""
    context = {
        "request": request,
        "active_page": "contact",
        "FRIENDLY_CAPTCHA_SITE_KEY": os.getenv("FRIENDLY_CAPTCHA_SITE_KEY"),
        "csrf_token": request.cookies.get("csrftoken", ""),
        "BACKEND_URL": os.getenv("BACKEND_URL", "http://localhost:8000")  # Add this line
    }
    return templates.TemplateResponse("contact.html", context)


async def privacy(request: Request):
    context = get_base_context(request, "privacy")
    return templates.TemplateResponse(
        "privacy.html",
        {**context, "meta_title": "Privacy Policy - Pers"}
    )


async def terms(request: Request):
    context = get_base_context(request, "terms")
    return templates.TemplateResponse(
        "terms.html",
        {**context, "meta_title": "Terms of Service - Pers"}
    )
