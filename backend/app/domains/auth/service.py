import logging
from datetime import datetime
from typing import Optional

from app.core.constants import UserRole
from app.domains.auth.models import UserDocument
from app.domains.auth.schemas import UserSyncRequest

logger = logging.getLogger("app.domains.auth.service")

# The one and only admin account. No one else may register with this email.
ADMIN_EMAIL = "karthikhr676@gmail.com"


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

    # Determine role: admin email always gets ADMIN, everything else RETAILER
    is_admin_email = email_lower == ADMIN_EMAIL.lower()

    # 1. Check if user already exists in MongoDB
    user = await UserDocument.find_one(UserDocument.firebase_uid == firebase_uid)

    if user:
        # Update mutable parameters from Firebase and client request
        user.email = email_lower
        user.is_email_verified = email_verified
        user.last_login_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()

        # Ensure admin email always retains ADMIN role
        if is_admin_email:
            user.role = UserRole.ADMIN

        # Merge business name if updated or passed in
        if sync_data and sync_data.business_name and not is_admin_email:
            user.business_name = sync_data.business_name

        # Enforce validation schemas on update
        await user.save()
        logger.info(f"Synchronized existing user session: {email_lower}")
    else:
        # 2. Register new profile linked to Firebase UID
        if is_admin_email:
            # Admin account — always seeded as ADMIN, no business_name required
            role = UserRole.ADMIN
            business_name = None
        else:
            # Ordinary retailer registration
            role = UserRole.RETAILER
            business_name = None

            if sync_data:
                business_name = sync_data.business_name

            if not business_name:
                business_name = "Pending Sync"

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


async def seed_admin_to_mongo(firebase_uid: str) -> None:
    """
    Ensures the admin user document exists in MongoDB.
    Called once at application startup after Firebase seeding.
    """
    existing = await UserDocument.find_one(UserDocument.firebase_uid == firebase_uid)
    if existing:
        # Guarantee role is ADMIN even if it somehow got corrupted
        if existing.role != UserRole.ADMIN:
            existing.role = UserRole.ADMIN
            await existing.save()
        logger.info("Admin user already exists in MongoDB.")
        return

    user = UserDocument(
        firebase_uid=firebase_uid,
        email=ADMIN_EMAIL.lower(),
        role=UserRole.ADMIN,
        business_name=None,
        is_email_verified=True,
        is_active=True,
        last_login_at=datetime.utcnow()
    )
    await user.insert()
    logger.info(f"Seeded admin user into MongoDB with UID: {firebase_uid}")
