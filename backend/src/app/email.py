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
    """Verify Friendly Captcha solution (with hardcoded values for testing)"""
    sitekey = "FCMT61L5M64SR0PR"  # HARDCODED TEST
    secret = "A1OBAUC2NQ6MRBDBA3TF77P4ONS9GUEGDQBFMNLVHTIP4M85C04LHKR47B"  # HARDCODED TEST
    logger.debug(f"Using Sitekey: {sitekey}")

    try:
        # Initialize the HTTP client properly
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.friendlycaptcha.com/api/v1/siteverify",
                json={
                    "solution": solution,
                    "secret": secret,
                    "sitekey": sitekey
                }
            )

            # Debug log the full response
            logger.debug(f"CAPTCHA API response: {response.text}")

            if response.status_code != 200:
                logger.error(f"CAPTCHA API returned HTTP {response.status_code}")
                return False

            return response.json().get("success", False)

    except Exception as e:
        logger.error(f"CAPTCHA verification failed: {str(e)}")
        return False
    # if not solution:
    #     logger.warning("Empty CAPTCHA solution provided")
    #     return False
    #
    # try:
    #     # Configure HTTP client with proper timeout and retry settings
    #     async with httpx.AsyncClient(
    #         timeout=httpx.Timeout(30.0),  # Total operation timeout
    #         limits=httpx.Limits(
    #             max_connections=100,
    #             max_keepalive_connections=20
    #         )
    #     ) as client:
    #         response = await client.post(
    #             "https://api.friendlycaptcha.com/api/v1/siteverify",
    #             json={
    #                 "solution": solution,
    #                 "secret": os.getenv("FRIENDLY_CAPTCHA_SECRET"),
    #                 "sitekey": os.getenv("FRIENDLY_CAPTCHA_SITE_KEY")
    #             }
    #         )
    #
    #         # Check both HTTP status and API response
    #         if response.status_code != 200:
    #             logger.warning(f"CAPTCHA API returned HTTP {response.status_code}")
    #             return False
    #
    #         result = response.json()
    #         if not result.get("success", False):
    #             logger.warning(
    #                 f"CAPTCHA verification failed: {result.get('errors', 'Unknown error')}"
    #             )
    #             return False
    #
    #         return True
    #
    # except httpx.ReadTimeout:
    #     logger.warning("CAPTCHA verification timed out after 30 seconds")
    #     return False
    #
    # except httpx.ConnectError:
    #     logger.warning("Failed to connect to CAPTCHA service")
    #     return False
    #
    # except Exception as e:
    #     logger.error(f"Unexpected CAPTCHA verification error: {str(e)}", exc_info=True)
    #     return False


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
