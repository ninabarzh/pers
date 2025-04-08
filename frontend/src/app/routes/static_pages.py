from starlette.templating import Jinja2Templates
from starlette.requests import Request
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
        "now": datetime.now()  # For last updated dates
    }

async def about(request: Request):
    context = get_base_context(request, "about")
    return templates.TemplateResponse(
        "about.html",
        {**context, "meta_title": "About Us - Pers"}
    )

async def contact(request: Request):
    context = get_base_context(request, "contact")
    return templates.TemplateResponse(
        "contact.html",
        {**context, "meta_title": "Contact Us - Pers"}
    )

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
