# backend/src/app/email.py
import smtplib
import httpx
import logging
import os
from email.message import EmailMessage
from starlette.config import Config

logger = logging.getLogger(__name__)
config = Config(".env")  # Load environment variables


async def verify_friendly_captcha(solution: str) -> bool:
    """Verify Friendly Captcha solution with proper error handling"""
    if not solution:
        return False

    # Skip verification in debug mode with test solution
    if os.getenv('DEBUG', 'false').lower() in ('true', '1', 't') and solution == "TEST_SOLUTION":
        logger.warning("DEBUG MODE: Skipping captcha verification")
        return True

    try:
        data = {
            "solution": solution,
            "secret": os.getenv("FRIENDLY_CAPTCHA_SECRET"),
            "sitekey": os.getenv("FRIENDLY_CAPTCHA_SITE_KEY")
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.friendlycaptcha.com/api/v1/siteverify",
                json=data,
                timeout=10.0
            )
            result = response.json()
            logger.debug(f"CAPTCHA API response: {result}")

            if not response.is_success or not result.get("success"):
                logger.warning(f"CAPTCHA verification failed: {result.get('errors', [])}")
                return False

            return True
    except Exception as e:
        logger.error(f"Captcha verification error: {str(e)}")
        return False


async def send_email(to: str, subject: str, body: str) -> bool:
    """Send email using configured SMTP server"""
    try:
        # Get configuration with defaults
        smtp_config = {
            'host': config("SMTP_SERVER", default="smtp.protonmail.ch"),
            'port': config("SMTP_PORT", default=587, cast=int),
            'timeout': config("SMTP_TIMEOUT", default=10, cast=int),
            'creds': config("PROTON_SMTP_CREDENTIALS")
        }

        logger.debug(f"SMTP Config: {smtp_config['host']}:{smtp_config['port']}")

        # Create message
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = config("DEFAULT_FROM_EMAIL", default="green@tymyrddin.dev")
        msg["To"] = to

        # Connect and send
        with smtplib.SMTP(
                host=smtp_config['host'],
                port=smtp_config['port'],
                timeout=smtp_config['timeout']
        ) as server:
            server.set_debuglevel(1)  # Enable verbose logging
            server.ehlo()
            server.starttls()
            server.ehlo()

            if smtp_config['creds']:
                user, passwd = smtp_config['creds'].split(":", 1)
                server.login(user, passwd)

            server.send_message(msg)
            return True

    except Exception as e:
        logger.error(f"Email failed: {str(e)}", exc_info=True)
        return False
