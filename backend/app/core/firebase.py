import logging
import sys
from typing import Any, Dict
import firebase_admin
from firebase_admin import auth, credentials

from app.core.config import settings

logger = logging.getLogger("app.core.firebase")

_firebase_app_initialized = False


def initialize_firebase() -> None:
    """
    Initializes the Firebase Admin SDK using settings credentials.
    Permits graceful warning fallback during local development or unit testing
    when Firebase environment variables are omitted or carry default placeholders.
    """
    global _firebase_app_initialized
    if _firebase_app_initialized:
        return

    # Check for empty or placeholder configuration values
    has_config = (
        settings.FIREBASE_PROJECT_ID and 
        "placeholder" not in settings.FIREBASE_PROJECT_ID and
        settings.FIREBASE_CLIENT_EMAIL and
        settings.FIREBASE_PRIVATE_KEY
    )

    if not has_config:
        logger.warning(
            "Firebase credentials are not fully configured. "
            "Falling back to local Mock verification for development/testing."
        )
        return

    try:
        # Standardize private key formats (handling double-escaped newlines in env files)
        private_key = settings.FIREBASE_PRIVATE_KEY
        if private_key:
            # Strip quotes and decode escaped newlines
            private_key = private_key.strip('"').replace("\\n", "\n")

        cred_dict = {
            "type": "service_account",
            "project_id": settings.FIREBASE_PROJECT_ID,
            "private_key": private_key,
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "token_url": "https://oauth2.googleapis.com/token",
        }
        
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        _firebase_app_initialized = True
        logger.info("Firebase Admin SDK successfully initialized.")
    except Exception as e:
        logger.critical(f"Failed to initialize Firebase Admin SDK: {e}")
        # Allow running in dev or test environments to prevent startup crash
        if settings.APP_ENV not in ["development", "test"] and "pytest" not in sys.modules:
            raise e


def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """
    Verifies a Firebase ID Token.
    Returns the decoded token claims dictionary.
    In local development or test mode, mock tokens ("mock-token-<uid>") are accepted
    to enable offline unit testing and development without network dependencies.
    """
    if not _firebase_app_initialized:
        # Local mock mode
        if id_token.startswith("mock-token-"):
            uid = id_token.replace("mock-token-", "")
            return {
                "uid": uid,
                "email": f"{uid}@example.com",
                "email_verified": True,
                "name": uid.replace("_", " ").title()
            }
        raise ValueError("Firebase Admin SDK is not initialized and a valid mock token was not provided.")

    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        raise ValueError(f"Invalid Firebase ID token: {e}")
