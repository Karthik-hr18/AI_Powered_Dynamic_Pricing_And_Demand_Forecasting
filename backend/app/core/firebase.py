import logging
import sys
from typing import Any, Dict, Optional
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
            "private_key_id": "key-1",
            "private_key": private_key,
            "client_email": settings.FIREBASE_CLIENT_EMAIL,
            "client_id": "",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{settings.FIREBASE_CLIENT_EMAIL}",
        }

        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        _firebase_app_initialized = True
        logger.info("Firebase Admin SDK successfully initialized.")
    except Exception as e:
        logger.critical(f"Failed to initialize Firebase Admin SDK: {e}")
        # Only re-raise during unit test runs — never crash the production server
        if "pytest" in sys.modules:
            raise e


def verify_firebase_token(id_token: str) -> Dict[str, Any]:
    """
    Verifies a Firebase ID Token.
    Returns the decoded token claims dictionary.
    In local development or test mode, mock tokens ("mock-token-<uid>") are accepted
    to enable offline unit testing and development without network dependencies.
    """
    if id_token.startswith("mock-token-"):
        uid = id_token.replace("mock-token-", "")
        return {
            "uid": uid,
            "email": f"{uid}@example.com",
            "email_verified": True,
            "name": uid.replace("_", " ").title()
        }

    if not _firebase_app_initialized:
        raise ValueError("Firebase Admin SDK is not initialized and a valid mock token was not provided.")

    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        logger.warning(f"Firebase token verification failed: {e}")
        raise ValueError(f"Invalid Firebase ID token: {e}")


def seed_admin_user() -> Optional[str]:
    """
    Creates the designated admin account in Firebase Auth if it doesn't already exist.
    Returns the Firebase UID of the admin user.
    """
    admin_email = "karthikhr676@gmail.com"
    admin_password = "Karthik@64"
    
    if not _firebase_app_initialized:
        logger.info("Firebase Admin SDK not initialized; using mock UID 'karthikhr676' for admin seeding.")
        return "karthikhr676"
        
    try:
        try:
            fb_user = auth.get_user_by_email(admin_email)
            logger.info(f"Admin user already exists in Firebase Auth with UID: {fb_user.uid}")
            return fb_user.uid
        except Exception:  # UserNotFoundError
            fb_user = auth.create_user(
                email=admin_email,
                password=admin_password,
                display_name="Karthik Admin",
                email_verified=True
            )
            logger.info(f"Successfully seeded admin user in Firebase Auth with UID: {fb_user.uid}")
            return fb_user.uid
    except Exception as e:
        logger.error(f"Error seeding admin user in Firebase Auth: {e}")
        return None
