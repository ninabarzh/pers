# backend/src/app/email.py
import smtplib
import httpx
import logging
from email.message import EmailMessage
from starlette.config import Config

logger = logging.getLogger(__name__)
config = Config(".env")  # Load environment variables


async def verify_friendly_captcha(solution: str) -> bool:
    """Verify Friendly Captcha solution with proper error handling"""
    if not solution:
        logger.warning("Empty CAPTCHA solution provided")
        return False

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.friendlycaptcha.com/api/v1/siteverify",
                json={
                    "solution": solution,
                    "secret": config("FRIENDLY_CAPTCHA_SECRET"),
                    "sitekey": config("FRIENDLY_CAPTCHA_SITE_KEY")
                }
            )

            logger.debug(f"CAPTCHA API response: {response.text}")

            if response.status_code != 200:
                logger.error(f"CAPTCHA API returned HTTP {response.status_code}")
                return False

            result = response.json()
            if not result.get("success", False):
                logger.warning(f"CAPTCHA verification failed: {result.get('errors', 'Unknown error')}")
            return result["success"]

    except httpx.ReadTimeout:
        logger.error("CAPTCHA verification timed out")
        return False

    except Exception as e:
        logger.error(f"CAPTCHA verification failed: {str(e)}", exc_info=True)
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
