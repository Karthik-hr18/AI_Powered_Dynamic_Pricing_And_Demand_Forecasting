import pytest
from fastapi import HTTPException, status
from httpx import AsyncClient, ASGITransport

from app.core.constants import UserRole
from app.domains.auth.dependencies import require_role
from app.domains.auth.models import UserDocument
from app.main import app


@pytest.fixture(autouse=True)
async def clean_users_collection():
    """Autouse fixture to clean the users collection before and after each test."""
    await UserDocument.find_all().delete()
    yield
    await UserDocument.find_all().delete()


@pytest.fixture
def transport():
    """Provides an ASGI transport wrapper around the FastAPI app."""
    return ASGITransport(app=app)


@pytest.mark.asyncio
async def test_auth_sync_new_retailer_success(transport):
    """Verify that posting to /sync creates a new RETAILER profile with a business name."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": "Bearer mock-token-retailer_uid_123"}
        payload = {
            "role": "RETAILER",
            "business_name": "Karthik's Retail Shop"
        }
        
        response = await client.post("/api/v1/auth/sync", json=payload, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["firebase_uid"] == "retailer_uid_123"
        assert data["email"] == "retailer_uid_123@example.com"
        assert data["role"] == "RETAILER"
        assert data["business_name"] == "Karthik's Retail Shop"
        assert data["is_email_verified"] is True
        assert data["is_active"] is True


@pytest.mark.asyncio
async def test_auth_sync_new_retailer_missing_business_name(transport):
    """Verify that registering a RETAILER without a business_name fails schema validation."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": "Bearer mock-token-retailer_uid_invalid"}
        payload = {
            "role": "RETAILER"
        }
        
        response = await client.post("/api/v1/auth/sync", json=payload, headers=headers)
        assert response.status_code == 422
        assert "business_name is required when role is RETAILER" in response.text


@pytest.mark.asyncio
async def test_auth_sync_new_admin_success(transport):
    """Verify that an ADMIN profile can be synced without requiring a business name."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": "Bearer mock-token-admin_uid_456"}
        payload = {
            "role": "ADMIN"
        }
        
        response = await client.post("/api/v1/auth/sync", json=payload, headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["firebase_uid"] == "admin_uid_456"
        assert data["role"] == "ADMIN"
        assert data["business_name"] is None


@pytest.mark.asyncio
async def test_auth_sync_existing_user_updates_login_time(transport):
    """Verify that re-syncing an existing user updates their timestamps rather than creating duplicates."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        headers = {"Authorization": "Bearer mock-token-sync_user_789"}
        payload = {"role": "ADMIN"}
        
        # First sync
        res1 = await client.post("/api/v1/auth/sync", json=payload, headers=headers)
        assert res1.status_code == 200
        user1_id = res1.json()["id"]

        # Second sync
        res2 = await client.post("/api/v1/auth/sync", json=payload, headers=headers)
        assert res2.status_code == 200
        assert res2.json()["id"] == user1_id  # Should point to the exact same MongoDB document


@pytest.mark.asyncio
async def test_get_me_protected_route(transport):
    """Verify that /me returns the current profile when authenticated and 403 when anonymous."""
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Anonymous request should fail
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401

        # 2. Authenticated request should succeed
        headers = {"Authorization": "Bearer mock-token-profile_user"}
        await client.post("/api/v1/auth/sync", json={"role": "ADMIN"}, headers=headers)
        
        response = await client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 200
        assert response.json()["firebase_uid"] == "profile_user"


@pytest.mark.asyncio
async def test_role_authorization_guards():
    """Verify that require_role dependency correctly allows or rejects users based on their MongoDB role."""
    admin_checker = require_role([UserRole.ADMIN])
    retailer_checker = require_role([UserRole.RETAILER])

    admin_user = UserDocument(
        firebase_uid="uid_adm",
        email="admin@test.com",
        role=UserRole.ADMIN,
        is_email_verified=True
    )
    
    retailer_user = UserDocument(
        firebase_uid="uid_ret",
        email="ret@test.com",
        role=UserRole.RETAILER,
        business_name="Test Store",
        is_email_verified=True
    )

    # 1. Admin accessing admin-only endpoint: Success
    res1 = admin_checker(admin_user)
    assert res1 == admin_user

    # 2. Retailer accessing admin-only endpoint: Raises 403 Forbidden
    with pytest.raises(HTTPException) as exc_info:
        admin_checker(retailer_user)
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert "Access forbidden" in exc_info.value.detail

    # 3. Retailer accessing retailer endpoint: Success
    res2 = retailer_checker(retailer_user)
    assert res2 == retailer_user
