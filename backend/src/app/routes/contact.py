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
    required = {
        'name': {'min': 2, 'max': 100},
        'email': {'pattern': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')},
        'message': {'min': 10, 'max': 2000},
        'consent': {},
        'frc-captcha-solution': {'optional': False}  # Explicitly mark as required
    }

    errors = {}
    data = {}

    form_dict = dict(form_data) if isinstance(form_data, FormData) else form_data

    # Debug: Log all received fields
    print("Received form fields:", form_dict.keys())

    for field, rules in required.items():
        value = form_dict.get(field, '').strip()

        # Skip validation if field is marked optional and empty
        if rules.get('optional') and not value:
            continue

        # Special handling for consent checkbox
        if field == 'consent':
            if not value or value.lower() not in ('true', 'on', '1'):
                errors[field] = "You must agree before submitting"
            continue

        # Handle empty required fields
        if not value:
            errors[field] = "This field is required"
            continue

        # Store valid values
        data[field] = value

    # Additional debug
    print("Captcha solution present:", 'frc-captcha-solution' in form_dict)

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
