# backend/src/app/routes/contact.py
from starlette.requests import Request
from starlette.responses import JSONResponse
from ..email import send_email, verify_friendly_captcha
import os
import logging

logger = logging.getLogger(__name__)


async def contact_post(request: Request):
    """Simplified contact handler with explicit validation"""
    try:
        form_data = await request.form()

        logger.debug("CSRF Token: %s", form_data.get('csrf_token'))
        logger.debug("SMTP Config: %s:%s",
                     os.getenv('SMTP_SERVER'),
                     os.getenv('SMTP_PORT'))

        # Debug mode bypass
        debug_mode = os.getenv('DEBUG', 'false').lower() in ('true', '1', 't')
        test_solution = debug_mode and form_data.get('frc-captcha-solution') == 'TEST_SOLUTION'

        # Verify captcha unless in debug mode with test solution
        if not test_solution:
            if not await verify_friendly_captcha(form_data['frc-captcha-solution']):
                logger.error("Captcha verification failed")
                return JSONResponse(
                    {"status": "error", "error": "Captcha verification failed"},
                    status_code=400
                )

        # 1. Verify all required fields exist
        required_fields = {
            'name': str,
            'email': str,
            'message': str,
            'consent': str,
            'csrf_token': str,
            'frc-captcha-solution': str
        }

        missing_fields = [
            field for field in required_fields
            if field not in form_data or not form_data[field].strip()
        ]

        if missing_fields:
            logger.error("Missing fields: %s", missing_fields)
            return JSONResponse(
                {"status": "error", "missing_fields": missing_fields},
                status_code=400
            )

        # 2. Verify consent
        if form_data['consent'].lower() not in ['on', 'true', '1']:
            logger.error("Consent not given")
            return JSONResponse(
                {"status": "error", "error": "Consent required"},
                status_code=400
            )

        # 3. Handle captcha (skip in dev with TEST_SOLUTION)
        if (os.getenv('DEBUG', 'false').lower() not in ('true', '1', 't') or
                form_data['frc-captcha-solution'] != 'TEST_SOLUTION'):

            if not await verify_friendly_captcha(form_data['frc-captcha-solution']):
                logger.error("Captcha verification failed")
                return JSONResponse(
                    {"status": "error", "error": "Captcha verification failed"},
                    status_code=400
                )

        # 4. Send email
        email_sent = await send_email(
            to=os.getenv("CONTACT_RECIPIENT", "green@tymyrddin.dev"),
            subject=f"New contact from {form_data['name']}",
            body=f"""New Contact Submission
                   {'-' * 40}
                   Name: {form_data['name']}
                   Email: {form_data['email']}
                   Message: {form_data['message']}
                   {'-' * 40}"""
        )

        if not email_sent:
            raise RuntimeError("Email sending failed")

        return JSONResponse({"status": "success"})

    except Exception as e:
        logger.error("Error processing contact form: %s", str(e), exc_info=True)
        return JSONResponse(
            {"status": "error", "detail": str(e)},
            status_code=500
        )
