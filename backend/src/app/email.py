# backend/src/app/email.py
import smtplib
import ssl
import httpx
import logging
import os
from email.message import EmailMessage
from starlette.config import Config

logger = logging.getLogger(__name__)
config = Config(".env")


async def verify_friendly_captcha(solution: str) -> bool:
    """Verify Friendly Captcha solution with their API"""
    if not solution:
        logger.warning("Empty CAPTCHA solution provided")
        return False

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.friendlycaptcha.com/api/v1/siteverify",
                json={
                    "solution": solution,
                    "secret": os.getenv("FRIENDLY_CAPTCHA_SECRET"),
                    "sitekey": os.getenv("FRIENDLY_CAPTCHA_SITE_KEY")
                },
                timeout=5.0
            )
            result = response.json()

            if not result.get("success"):
                logger.warning(f"Friendly Captcha verification failed: {result.get('errors')}")
                return False
            return True

    except Exception as e:
        logger.error(f"Friendly Captcha API error: {str(e)}")
        return False


async def send_email(to: str, subject: str, body: str) -> bool:
    """Send email using Proton SMTP Bridge

    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Parse credentials (format: "local-username@domain:token")
        creds = config("PROTON_SMTP_CREDENTIALS")
        username, password = creds.split(":", 1)

        # Get SMTP configuration with type-safe defaults
        smtp_server = config("SMTP_SERVER", default="127.0.0.1")  # Local bridge
        smtp_port = int(config("SMTP_PORT", default="1025"))  # Default bridge port
        from_email = config("DEFAULT_FROM_EMAIL", default="green@tymyrddin.dev")

        # Create message
        msg = EmailMessage()
        msg.set_content(body)
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to  # This comes from the function parameter

        # Create secure SSL context
        context = ssl.create_default_context()

        # Connect to SMTP server
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_port == 587:  # For direct Proton SMTP
                server.starttls(context=context)
            server.login(username, password)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {to}")
        return True
    except Exception as e:
        logger.error(f"Email failed to {to}: {str(e)}")
        return False
