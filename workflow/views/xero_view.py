# workflow/views/xero_view.py
import logging
import uuid
import traceback
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from xero_python.accounting import AccountingApi
from xero_python.identity import IdentityApi


from workflow.api.xero.sync import synchronise_xero_data
from workflow.api.xero.xero import (
    api_client,
    exchange_code_for_token,
    get_authentication_url,
    get_token,
    refresh_token,
)

logger = logging.getLogger(__name__)


# Xero Authentication (Step 1: Redirect user to Xero OAuth2 login)
def xero_authenticate(request: HttpRequest) -> HttpResponse:
    state = str(uuid.uuid4())
    request.session["oauth_state"] = state
    authorization_url = get_authentication_url(state)
    return redirect(authorization_url)


# OAuth callback
def xero_oauth_callback(request: HttpRequest) -> HttpResponse:
    code = request.GET.get("code")
    state = request.GET.get("state")
    session_state = request.session.get("oauth_state")

    result = exchange_code_for_token(code, state, session_state)

    if "error" in result:
        return render(
            request, "xero/error_xero_auth.html", {"error_message": result["error"]}
        )

    return redirect("refresh_xero_data")


# Refresh OAuth token and handle redirects
def refresh_xero_token(request: HttpRequest) -> HttpResponse:
    refreshed_token = refresh_token()

    if not refreshed_token:
        return redirect("xero_authenticate")

    return redirect("xero_get_contacts")


# Xero connection success view
def success_xero_connection(request: HttpRequest) -> HttpResponse:
    return render(request, "xero/success_xero_connection.html")


# Get Xero contacts


def refresh_xero_data(request):
    try:
        token = get_token()

        if not token:
            logger.info(
                "User is not authenticated with Xero, redirecting to authentication"
            )
            return redirect(
                "authenticate_xero"
            )  # Redirect to the Xero authentication path

        # If authenticated, proceed with syncing data
        synchronise_xero_data()
        logger.info("Xero data successfully refreshed")

    except Exception as e:
        if "token" in str(e).lower():  # Or check for the specific error code
            logger.error(f"Error while refreshing Xero data: {str(e)}")
            return redirect("authenticate_xero")
        else:
            logger.error(f"Error while refreshing Xero data: {str(e)}")
            traceback.print_exc()
            return render(
                request, "general/generic_error.html", {"error_message": str(e)}
            )

    # After successful sync, redirect to the home page or wherever appropriate
    return redirect("/")


class XeroIndexView(TemplateView):
    """Note this page is currently inaccessible.  We are using a dropdown menu instead.
    Kept as of 2025-01-07 in case we change our mind"""

    template_name = "xero_index.html"
