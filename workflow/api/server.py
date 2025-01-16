from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import os


@login_required
def get_env_variable(request):
    var_name = request.GET.get("var_name")
    if not var_name:
        return JsonResponse({"error": "Missing variable name"}, status=400)

    # Retrieve the variable from the environment
    value = os.getenv(var_name)
    if value is None:
        return JsonResponse({"error": f"Variable {var_name} not found"}, status=404)

    return JsonResponse({"value": value})
