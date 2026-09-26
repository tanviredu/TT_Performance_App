from urllib.parse import urlencode

from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .exports import export_equipment_hours_to_excel
from .forms import HourEntryForm, ReportFilterForm
from .models import Equipment, EquipmentHourRecord
from .services import get_reading_bounds, create_hour_record


def entry(request: HttpRequest) -> HttpResponse:
    form = HourEntryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            record = create_hour_record(
                operator=form.cleaned_data["operator"],
                equipment_id=form.cleaned_data["equipment"].pk,
                total_hours=form.cleaned_data["total_hours"],
            )
        except (ValidationError, IntegrityError) as error:
            message = (
                error.messages[0]
                if isinstance(error, ValidationError)
                else "এই তথ্যটি ইতোমধ্যে জমা হয়েছে। অনুগ্রহ করে তথ্য যাচাই করুন।"
            )
            form.add_error(None, message)
        else:
            return redirect("equipment:success", record_id=record.pk)

    bounds = None
    selected_equipment = form.data.get("equipment") if form.is_bound else None
    if selected_equipment and not form.errors.get("equipment"):
        equipment = Equipment.objects.filter(
            pk=selected_equipment, is_active=True
        ).first()
        if equipment:
            try:
                bounds = get_reading_bounds(equipment)
            except ValidationError:
                bounds = None
    return render(
        request,
        "equipment/entry.html",
        {"form": form, "bounds": bounds},
    )


def success(request: HttpRequest, record_id: int) -> HttpResponse:
    record = get_object_or_404(
        EquipmentHourRecord.objects.select_related("operator", "equipment"),
        pk=record_id,
    )
    return render(request, "equipment/success.html", {"record": record})


def latest_reading(request: HttpRequest, equipment_id: int) -> JsonResponse:
    equipment = get_object_or_404(Equipment, pk=equipment_id, is_active=True)
    try:
        bounds = get_reading_bounds(equipment)
    except ValidationError as error:
        return JsonResponse({"configured": False, "message": error.messages[0]})
    return JsonResponse(
        {
            "configured": True,
            "previous": str(bounds.previous),
            "maximum": str(bounds.maximum),
        }
    )


def _filtered_records(request: HttpRequest):
    form = ReportFilterForm(request.GET or None)
    queryset = EquipmentHourRecord.objects.select_related(
        "operator", "equipment"
    ).order_by("-created_at", "-id")
    if form.is_valid():
        data = form.cleaned_data
        if data.get("from_date"):
            queryset = queryset.filter(date__gte=data["from_date"])
        if data.get("to_date"):
            queryset = queryset.filter(date__lte=data["to_date"])
        if data.get("equipment"):
            queryset = queryset.filter(equipment=data["equipment"])
        if data.get("operator"):
            queryset = queryset.filter(operator=data["operator"])
    return form, queryset


@staff_member_required
def report(request: HttpRequest) -> HttpResponse:
    form, queryset = _filtered_records(request)
    page_obj = Paginator(queryset, 25).get_page(request.GET.get("page"))
    return render(
        request,
        "equipment/report.html",
        {
            "form": form,
            "page_obj": page_obj,
            "export_url": f"{reverse('equipment:export_excel')}?{urlencode(request.GET)}",
        },
    )


@staff_member_required
def export_excel(request: HttpRequest) -> HttpResponse:
    _, records = _filtered_records(request)
    return export_equipment_hours_to_excel(records, filename_prefix="equipment_hours")