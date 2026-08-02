import logging
from datetime import datetime
from typing import Optional

from app.core.constants import UserRole
from app.domains.auth.models import UserDocument
from app.domains.auth.schemas import UserSyncRequest

logger = logging.getLogger("app.domains.auth.service")


async def sync_firebase_user(
    decoded_token: dict,
    sync_data: Optional[UserSyncRequest] = None
) -> UserDocument:
    """
    Synchronizes a verified Firebase user with the MongoDB database.
    Creates a new profile if they do not exist, otherwise updates relevant claims
    (such as email verification status and last login timestamp).
    """
    firebase_uid = decoded_token.get("uid")
    email = decoded_token.get("email")
    email_verified = decoded_token.get("email_verified", False)

    if not firebase_uid or not email:
        raise ValueError("Invalid Firebase token payload: uid and email are required.")

    email_lower = email.lower()
    
    # 1. Check if user already exists in MongoDB
    user = await UserDocument.find_one(UserDocument.firebase_uid == firebase_uid)

    if user:
        # Update mutable parameters from Firebase and client request
        user.email = email_lower
        user.is_email_verified = email_verified
        user.last_login_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        
        # Merge business name if updated or passed in
        if sync_data and sync_data.business_name:
            user.business_name = sync_data.business_name
            
        # Enforce validation schemas on update
        await user.save()
        logger.info(f"Synchronized existing user session: {email_lower}")
    else:
        # 2. Register new profile linked to Firebase UID
        role = UserRole.RETAILER
        business_name = None
        
        if sync_data:
            role = sync_data.role
            business_name = sync_data.business_name

        user = UserDocument(
            firebase_uid=firebase_uid,
            email=email_lower,
            role=role,
            business_name=business_name,
            is_email_verified=email_verified,
            is_active=True,
            last_login_at=datetime.utcnow()
        )
        
        # Enforce schemas checks (e.g. business name for RETAILER) and insert
        await user.insert()
        logger.info(f"Created new MongoDB profile for Firebase UID: {firebase_uid} ({email_lower})")

    return user
