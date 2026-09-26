from django.urls import path

from . import views

app_name = "equipment"

urlpatterns = [
    path("", views.entry, name="entry"),
    path("success/<int:record_id>/", views.success, name="success"),
    path("equipment/<int:equipment_id>/latest/", views.latest_reading, name="latest"),
    path("reports/", views.report, name="report"),
    path("reports/export/", views.export_excel, name="export_excel"),
]