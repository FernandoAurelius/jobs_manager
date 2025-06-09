from django import template
from django.core.cache import cache
from datetime import datetime, timedelta, timezone

from apps.workflow.models import CompanyDefaults
from apps.workflow.api.xero.xero import get_token

register = template.Library()

# List of entities in the order they should be processed
XERO_ENTITIES = [
    "accounts",
    "contacts",
    "invoices",
    "bills",
    "quotes",
    "credit_notes",
    "purchase_orders",
    "stock",
    "journals",
]


@register.simple_tag
def get_xero_action():
    """
    Returns the appropriate Xero action based on connection state.
    Returns:
        dict: Contains 'action_text' (str) and 'url_name' (str)
    """
    token = (
        get_token()
    )  # Use the API's get_token function instead of direct cache access

    if not token or not token.get("access_token"):
        return {"action_text": "Connect to Xero", "url_name": "api_xero_authenticate"}

    expires_at = token.get("expires_at")
    if expires_at and datetime.fromtimestamp(
        expires_at, tz=timezone.utc
    ) < datetime.now(timezone.utc):
        return {"action_text": "Reconnect to Xero", "url_name": "api_xero_authenticate"}

    return {"action_text": "Disconnect from Xero", "url_name": "xero_disconnect"}


@register.simple_tag
def check_xero_sync_needed():
    """
    Checks if Xero sync is needed (hasn't been run in over 24 hours)
    or if deep sync is needed (hasn't been run in over 30 days).
    Returns:
        dict: Contains 'needed' (bool) and 'message' (str)
    """
    try:
        company_defaults = CompanyDefaults.objects.first()
        now = datetime.now(timezone.utc)

        if not company_defaults or not company_defaults.last_xero_sync:
            return {"needed": True, "message": "Xero data has never been synchronized"}

        # Check regular sync (24 hours)
        if now - company_defaults.last_xero_sync > timedelta(days=1):
            return {
                "needed": True,
                "message": "Xero data is outdated, please contact Corrin",
            }

        # Check deep sync (30 days)
        if not company_defaults.last_xero_deep_sync or (
            now - company_defaults.last_xero_deep_sync > timedelta(days=30)
        ):
            return {
                "needed": True,
                "message": "Deep Xero sync needed (looking back 90 days)",
            }

        return {"needed": False, "message": None}
    except Exception:
        return {"needed": False, "message": None}


@register.simple_tag
def get_xero_entities():
    return XERO_ENTITIES


@register.filter
def replace(value, arg):
    """Replace hyphens and underscores with spaces and capitalize words"""
    return value.replace("-", " ").replace("_", " ").title()
