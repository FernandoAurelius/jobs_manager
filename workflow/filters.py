import django_filters

from workflow.enums import InvoiceStatus
from workflow.models import Invoice


class InvoiceFilter(django_filters.FilterSet):
    invoice_number = django_filters.CharFilter(
        field_name="number", lookup_expr="icontains", label="Invoice Number"
    )
    client = django_filters.CharFilter(
        field_name="client__name", lookup_expr="icontains", label="Client Name"
    )
    date = django_filters.DateFromToRangeFilter(
        widget=django_filters.widgets.RangeWidget(attrs={"placeholder": "YYYY-MM-DD"})
    )
    status = django_filters.ChoiceFilter(
        choices=InvoiceStatus.choices
    )  # If status is a choice field

    class Meta:
        model = Invoice
        fields = ["invoice_number", "client", "date", "status"]
