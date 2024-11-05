from workflow.models.company_defaults import CompanyDefaults


def get_company_defaults():
    """Retrieve the single CompanyDefaults instance, or create it if it doesn't exist."""
    defaults, created = CompanyDefaults.objects.get_or_create(
        defaults={
            "time_markup": 0.0,
            "materials_markup": 0.0,
            "charge_out_rate": 105.00,
            "wage_rate": 32.00,
        }
    )
    return defaults
