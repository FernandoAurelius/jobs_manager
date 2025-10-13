"""
RESTful URLs for the purchasing app.
All purchasing functionality is now provided via REST APIs under /purchasing/rest/
"""

from typing import List, Union

from django.urls import URLPattern, URLResolver, include, path

app_name = "purchasing"

# All REST API endpoints are in urls_rest.py
urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path("rest/", include("apps.purchasing.urls_rest")),
]
