import logging

from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib import messages

from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView
from django_tables2 import SingleTableView

from workflow.api.xero.sync import single_sync_client, sync_client_to_xero
from workflow.api.xero.xero import get_valid_token

from workflow.forms import ClientForm
from workflow.models import Client

# from workflow.tables import ClientTable

logger = logging.getLogger(__name__)


class ClientListView(SingleTableView):
    model = Client
    template_name = "clients/list_clients.html"


class ClientUpdateView(UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "clients/update_client.html"
    success_url = reverse_lazy("list_clients")

    def form_valid(self, form):
        response = super().form_valid(form)

        # Simple token check before attempting sync
        token = get_valid_token()
        if not token:
            messages.warning(self.request, "Xero authentication required.")
            return redirect("authenticate_xero")

        try:
            sync_client_to_xero(self.object)
            messages.success(self.request, "Client synced to Xero successfully")
        except Exception as e:
            messages.error(self.request, "Failed to sync to Xero")
            return render(
                self.request,
                "general/generic_error.html",
                {"error_message": f"Failed to sync client to Xero: {str(e)}"},
            )

        return response


def ClientSearch(request):
    query = request.GET.get("q", "")
    if query and len(query) >= 3:  # Only search when the query is 3+ characters
        clients = Client.objects.filter(Q(name__icontains=query))[
            :10
        ]  # Adjust fields as needed
        results = [{"id": client.id, "name": client.name} for client in clients]
    else:
        results = []

    return JsonResponse({"results": results})


def all_clients(request):
    """
    API endpoint to return all clients as JSON for AJAX table population.
    """
    clients = Client.objects.values(
        "id", "name", "email", "phone", "address", "is_account_customer"
    )
    return JsonResponse(list(clients), safe=False)


def AddClient(request):
    if request.method == "GET":
        # Check for stub creation mode
        if request.GET.get("mode") == "redirect":
            name = request.GET.get("name", "")
            client = (
                Client.objects.create(name=name) if name else Client.objects.create()
            )
            return redirect("update_client", pk=client.id)

        # Default: Serve the add client form
        name = request.GET.get("name", "")
        form = ClientForm(initial={"name": name}) if name else ClientForm()
        return render(request, "clients/add_client.html", {"form": form})

    elif request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client = Client(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                phone=form.cleaned_data["phone"],
                address=form.cleaned_data["address"],
                xero_last_modified="2000-01-01 00:00:00+00:00",
            )
            client.save()

            # Sync with Xero
            try:
                sync_client_to_xero(client)
                single_sync_client(client_identifier=client.id, delete_local=False)
                return render(request, "clients/client_added_success.html")
            except Exception as e:
                logger.error(f"Failed to sync client {client.name} to Xero: {str(e)}")
                return render(
                    request, "clients/client_added_failure.html", {"error": str(e)}
                )
        else:
            return render(request, "clients/add_client.html", {"form": form})
