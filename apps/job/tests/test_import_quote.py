import io

import pandas as pd
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
import django

django.setup()

from apps.job.models import Job


@pytest.fixture()
def job(db):
    return Job.objects.create(name="Test", charge_out_rate=10)


def create_excel(valid=True, quantity=1):
    primary = pd.DataFrame(
        [
            {
                "Description": "Part A",
                "quantity": quantity,
                "thickness": 1.5,
                "Materials": "SS316",
                "Labour /laser (inhouse)": 5,
                "fold cost": 1,
                "fold set up fee": 1,
                "hole costs": 2,
                "welding cost": 3,
                "Materials cost": 10,
                "Tube (RHS/SHS/pipe)": 0,
                "Prep (detail/finish)": 0,
                "CLEAR": "",
            }
        ]
    )

    if not valid:
        primary = primary.drop(columns=["fold cost"])

    materials = pd.DataFrame({"thickness": [1.5], "Materials": ["SS316"]})

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        primary.to_excel(writer, sheet_name="Primary Details", index=False)
        materials.to_excel(writer, sheet_name="Materials", index=False)
    buffer.seek(0)
    return buffer


def test_valid_import(job):
    client = APIClient()
    buffer = create_excel()
    url = reverse("jobs:import_quote", args=[job.id])
    response = client.post(url, {"file": buffer}, format="multipart")
    assert response.status_code == 201
    data = response.json()
    assert data["parts_created"] == 1
    assert data["total_material_cost"] == "10"


def test_missing_columns(job):
    client = APIClient()
    buffer = create_excel(valid=False)
    url = reverse("jobs:import_quote", args=[job.id])
    response = client.post(url, {"file": buffer}, format="multipart")
    assert response.status_code == 400


def test_zero_quantity(job):
    client = APIClient()
    buffer = create_excel(quantity=0)
    url = reverse("jobs:import_quote", args=[job.id])
    response = client.post(url, {"file": buffer}, format="multipart")
    assert response.status_code == 400

