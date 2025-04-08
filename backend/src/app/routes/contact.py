# backend/src/app/routes/contact.py
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.datastructures import FormData
from ..email import send_email, verify_friendly_captcha
import os
import logging
import re
from typing import Dict, Any, Pattern, Union

logger = logging.getLogger(__name__)

async def validate_form_data(form_data: Union[Dict[str, Any], FormData]) -> Dict[str, Any]:
    """Validate and sanitize form inputs"""
    required = {
        'name': {'min': 2, 'max': 100},
        'email': {'pattern': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')},
        'message': {'min': 10, 'max': 2000},
        'frc-captcha-solution': {},
        'consent': {}
    }

    errors: Dict[str, str] = {}
    data: Dict[str, str] = {}

    # Convert FormData to dict if needed
    if isinstance(form_data, FormData):
        form_data = dict(form_data)

    for field, rules in required.items():
        value = form_data.get(field, '').strip()

        if not value:
            errors[field] = "This field is required"
            continue

        if field == 'email' and not rules['pattern'].match(value):  # type: ignore
            errors[field] = "Invalid email format"
        elif 'min' in rules and len(value) < rules['min']:
            errors[field] = f"Must be at least {rules['min']} characters"
        elif 'max' in rules and len(value) > rules['max']:
            errors[field] = f"Must be less than {rules['max']} characters"
        else:
            data[field] = value

    return {'data': data, 'errors': errors} if not errors else {'errors': errors}

async def contact_post(request: Request):
    """Process contact form submission"""
    try:
        form_data = await request.form()
        validation = await validate_form_data(form_data)

        if 'errors' in validation:
            return JSONResponse(
                {"status": "error", "errors": validation['errors']},
                status_code=400
            )

        # Verify friendly captcha
        if not await verify_friendly_captcha(validation['data']['frc-captcha-solution']):
            logger.warning(f"Failed Friendly Captcha from IP: {request.client.host}")
            return JSONResponse(
                {"status": "error", "detail": "CAPTCHA verification failed"},
                status_code=400
            )

        # Send email
        email_body = f"""
        New Contact Submission
        {'-' * 40}
        Name: {validation['data']['name']}
        Email: {validation['data']['email']}
        Message:
        {validation['data']['message']}
        {'-' * 40}
        """

        success = await send_email(
            to=os.getenv("CONTACT_RECIPIENT", "green@tymyrddin.dev"),
            subject=f"New contact from {validation['data']['name']}",
            body=email_body
        )

        if not success:
            raise RuntimeError("Email sending failed")

        return JSONResponse({"status": "success"})

    except Exception as e:
        logger.error(f"Contact form error: {str(e)}", exc_info=True)
        return JSONResponse(
            {"status": "error", "detail": "Message could not be sent"},
            status_code=500
        )
