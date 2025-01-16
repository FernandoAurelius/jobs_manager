from django.views.generic import TemplateView


class ReportsIndexView(TemplateView):
    template_name = "reports/reports_index.html"


class CompanyProfitAndLossView(TemplateView):
    """Note this page is currently inaccessible.  We are using a dropdown menu instead.
    Kept as of 2025-01-07 in case we change our mind"""

    template_name = "reports/report_company_profit_and_loss.html"
