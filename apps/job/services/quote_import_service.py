"""Services for importing quote spreadsheets."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import IO, Tuple

import pandas as pd
from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.job.models import (
    AdjustmentEntry,
    Job,
    JobPart,
    JobPricing,
    MaterialEntry,
)

logger = logging.getLogger(__name__)


REQUIRED_COLUMNS = [
    "Description",
    "quantity",
    "thickness",
    "Materials",
    "Labour /laser (inhouse)",
    "fold cost",
    "fold set up fee",
    "hole costs",
    "welding cost",
    "Materials cost",
    "Tube (RHS/SHS/pipe)",
    "Prep (detail/finish)",
    "CLEAR",
]


def _validate_columns(df: pd.DataFrame) -> None:
    """Ensure all required columns exist."""

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")


def _validate_material(thickness: str | float, material: str, materials_df: pd.DataFrame) -> None:
    """Validate thickness/material combination exists."""

    if materials_df.empty:
        return

    mask = (materials_df["thickness"] == thickness) & (materials_df["Materials"] == material)
    if materials_df[mask].empty:
        raise ValueError(f"Invalid material combination: {thickness} / {material}")


@transaction.atomic
def import_quote_from_excel(
    job: Job,
    excel_file: IO[bytes],
    *,
    job_pricing_id: str | None = None,
) -> Tuple[JobPricing, int, Decimal, Decimal]:
    """Read the Excel spreadsheet and populate JobParts and related entries."""

    # Resolve job pricing
    if job_pricing_id:
        job_pricing = get_object_or_404(JobPricing, id=job_pricing_id, job=job)
    else:
        job_pricing = JobPricing.objects.create(job=job, pricing_stage="estimate")

    xl = pd.ExcelFile(excel_file, engine="openpyxl")

    try:
        primary_df = pd.read_excel(xl, sheet_name="Primary Details", engine="openpyxl")
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed reading Primary Details sheet: %s", exc)
        raise ValueError("Unable to read 'Primary Details' sheet") from exc

    _validate_columns(primary_df)

    try:
        materials_df = pd.read_excel(xl, sheet_name="Materials", engine="openpyxl")
    except Exception:
        materials_df = pd.DataFrame()

    parts_created = 0
    total_material_cost = Decimal("0")
    total_adjustments_cost = Decimal("0")

    adjustment_columns = [
        "fold cost",
        "fold set up fee",
        "hole costs",
        "welding cost",
        "Tube (RHS/SHS/pipe)",
        "Prep (detail/finish)",
    ]

    for _, row in primary_df.iterrows():
        description = str(row.get("Description", "")).strip()
        if not description:
            continue
        clear_flag = str(row.get("CLEAR", "")).strip().upper()
        if clear_flag == "CLEAR":
            continue

        quantity = row.get("quantity", 0)
        if quantity == 0:
            raise ValueError("Row has quantity of zero")

        _validate_material(row.get("thickness"), row.get("Materials"), materials_df)

        part = JobPart.objects.create(
            job_pricing=job_pricing,
            name=description,
            description=str(row.get("customer notes", "")),
        )

        qty = Decimal(str(quantity))
        materials_cost = Decimal(str(row.get("Materials cost", 0)))
        unit_cost = materials_cost / qty if qty != 0 else Decimal("0")

        MaterialEntry.objects.create(
            job_pricing=job_pricing,
            description="Materials",
            quantity=qty,
            unit_cost=unit_cost,
            unit_revenue=unit_cost,
        )

        total_material_cost += materials_cost

        row_adjustment_total = Decimal("0")
        for col in adjustment_columns:
            value = row.get(col)
            if value and not pd.isna(value):
                cost_val = Decimal(str(value))
                AdjustmentEntry.objects.create(
                    job_pricing=job_pricing,
                    description=col.lower(),
                    cost_adjustment=cost_val,
                    price_adjustment=Decimal("0"),
                )
                total_adjustments_cost += cost_val
                row_adjustment_total += cost_val

        labour_cost = Decimal(str(row.get("Labour /laser (inhouse)", 0)))
        part.raw_total_cost = materials_cost + row_adjustment_total + labour_cost
        parts_created += 1

    return job_pricing, parts_created, total_material_cost, total_adjustments_cost

