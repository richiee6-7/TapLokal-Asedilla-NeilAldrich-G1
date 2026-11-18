from django.urls import path

from . import staff_views, views

urlpatterns = [
    # Resident
    path("reports/", views.MyReportsView.as_view(), name="my_reports"),
    path("reports/new/", views.ReportCreateView.as_view(), name="report_create"),
    path("reports/<int:pk>/", views.ReportDetailView.as_view(), name="report_detail"),
    path("reports/<int:pk>/edit/", views.ReportUpdateView.as_view(), name="report_edit"),
    path("reports/<int:pk>/delete/", views.ReportDeleteView.as_view(), name="report_delete"),
    # Staff
    path("admin-panel/reports/", staff_views.StaffReportListView.as_view(), name="staff_reports"),
    path("admin-panel/reports/<int:pk>/", staff_views.StaffReportDetailView.as_view(), name="staff_report_detail"),
    path("admin-panel/hazard-types/", staff_views.HazardTypeListView.as_view(), name="hazard_types"),
    path("admin-panel/hazard-types/new/", staff_views.HazardTypeCreateView.as_view(), name="hazard_type_create"),
    path("admin-panel/hazard-types/<int:pk>/edit/", staff_views.HazardTypeUpdateView.as_view(), name="hazard_type_edit"),
    path("admin-panel/hazard-types/<int:pk>/toggle/", staff_views.HazardTypeToggleView.as_view(), name="hazard_type_toggle"),
]
