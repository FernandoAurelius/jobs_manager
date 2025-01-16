import logging
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.core.cache import cache
from xero_python.api_client import ApiClient, Configuration
from xero_python.api_client.oauth2 import OAuth2Token
from xero_python.identity import IdentityApi
from xero_python.api_client.oauth2 import TokenApi

logger = logging.getLogger(__name__)

XERO_SCOPES = [
    "offline_access",
    "openid",
    "profile",
    "email",
    "accounting.contacts",
    "accounting.transactions",
    "accounting.reports.read",
    "accounting.settings",
    "accounting.journals.read",
]

api_client = ApiClient(
    Configuration(
        oauth2_token=OAuth2Token(
            client_id=settings.XERO_CLIENT_ID,
            client_secret=settings.XERO_CLIENT_SECRET,
        ),
    ),
)


@api_client.oauth2_token_getter
def get_token() -> Optional[Dict[str, Any]]:
    """Get token from cache."""
    return cache.get("xero_token")


@api_client.oauth2_token_saver
def store_token(token: Dict[str, Any]) -> None:
    """Store token in cache with 29 minute timeout."""
    logger.info(f"Storing token: {token}")
    cache.set("xero_token", token, timeout=1740)  # 29 minutes


def refresh_token() -> Optional[Dict[str, Any]]:
    """Refresh the token using the refresh_token."""
    token = get_token()
    if not token or "refresh_token" not in token:
        logger.error("No valid token to refresh")
        return None

    token_api = TokenApi(api_client)
    refreshed_token = token_api.refresh_token(token)
    refreshed_dict = refreshed_token.to_dict()
    store_token(refreshed_dict)
    return refreshed_dict


def get_valid_token() -> Optional[Dict[str, Any]]:
    """Get a valid token, refreshing if needed."""
    token = get_token()
    if not token:
        return None

    expires_at = token.get("expires_at")
    if expires_at:
        expires_at_datetime = datetime.fromtimestamp(expires_at, tz=timezone.utc)
        if datetime.now(timezone.utc) > expires_at_datetime:
            token = refresh_token()
    return token


def get_authentication_url(state: str) -> str:
    """Get the URL for initial Xero OAuth."""
    return f"https://login.xero.com/identity/connect/authorize?{urlencode({
        'response_type': 'code',
        'client_id': settings.XERO_CLIENT_ID,
        'redirect_uri': settings.XERO_REDIRECT_URI,
        'scope': ' '.join(XERO_SCOPES),
        'state': state,
    })}"


def get_tenant_id_from_connections() -> str:
    """Get tenant ID using current token."""
    identity_api = IdentityApi(api_client)
    connections = identity_api.get_connections()
    if not connections:
        raise Exception("No Xero tenants found.")
    return connections[0].tenant_id


def exchange_code_for_token(
    code: str, state: str, session_state: str
) -> Dict[str, Any]:
    """Exchange OAuth code for token and store it."""
    if state != session_state:
        raise ValueError("OAuth state mismatch")

    # Get initial token
    response = requests.post(
        "https://identity.xero.com/connect/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.XERO_REDIRECT_URI,
            "client_id": settings.XERO_CLIENT_ID,
            "client_secret": settings.XERO_CLIENT_SECRET,
        },
    )
    response.raise_for_status()
    token_data = response.json()

    # Store token
    store_token(token_data)

    # Get and store tenant ID separately
    tenant_id = get_tenant_id_from_connections()
    cache.set("xero_tenant_id", tenant_id)

    return {"success": True}


def get_tenant_id() -> str:
    """
    Retrieve the tenant ID from cache, refreshing or re-authenticating as needed.
    """
    tenant_id = cache.get(
        "xero_tenant_id"
    )  # Step 1: Try to retrieve the tenant ID from the cache.
    token = (
        get_valid_token()
    )  # Step 2: Ensure a valid token exists, refreshing if necessary.

    if not token:
        raise Exception(
            "No valid Xero token found. Please complete the authorization workflow."
        )

    if (
        not tenant_id
    ):  # Step 3: If tenant ID is missing, fetch it using the current token.
        try:
            tenant_id = get_tenant_id_from_connections()
            cache.set(
                "xero_tenant_id", tenant_id
            )  # Cache the tenant ID for future use.
        except Exception as e:
            raise Exception(f"Failed to fetch tenant ID: {str(e)}")

    return tenant_id
