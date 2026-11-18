from django.contrib import messages
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from accounts.mixins import StaffRequiredMixin

from .models import HazardReport, HazardType, ReportStatus, StatusHistory
from .staff_forms import HazardTypeForm, StatusUpdateForm
from .views import FilteredReportListMixin


class StaffReportListView(StaffRequiredMixin, FilteredReportListMixin, ListView):
    template_name = "reports/staff_reports.html"
    search_reporter = True

    def get_base_queryset(self):
        return HazardReport.objects.all()


class StaffReportDetailView(StaffRequiredMixin, DetailView):
    """View a report and update its status (BR-17: every change is logged)."""

    model = HazardReport
    template_name = "reports/staff_report_detail.html"
    context_object_name = "report"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("form", StatusUpdateForm(report=self.object))
        context["history"] = self.object.history.select_related("changed_by")
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = StatusUpdateForm(request.POST, report=self.object)
        if not form.is_valid():
            messages.error(request, "The status was not updated. Please fix the errors below.")
            return self.render_to_response(self.get_context_data(form=form))

        new_status = form.cleaned_data["status"]
        with transaction.atomic():
            report = self.object
            report.status = new_status
            # BR-09: resolved_at is set only while the report is RESOLVED.
            report.resolved_at = timezone.now() if new_status == ReportStatus.RESOLVED else None
            report.save(update_fields=["status", "resolved_at"])
            StatusHistory.objects.create(
                report=report, status=new_status, changed_by=request.user,
                remarks=form.cleaned_data["remarks"],
            )
        messages.success(request, f"Report #{report.pk} is now {report.get_status_display()}.")
        return redirect("staff_report_detail", pk=report.pk)


class HazardTypeListView(StaffRequiredMixin, ListView):
    template_name = "reports/hazard_types.html"
    context_object_name = "hazard_types"

    def get_queryset(self):
        return HazardType.objects.annotate(report_count=Count("reports"))


class HazardTypeCreateView(StaffRequiredMixin, CreateView):
    form_class = HazardTypeForm
    template_name = "reports/hazard_type_form.html"
    success_url = reverse_lazy("hazard_types")

    def form_valid(self, form):
        messages.success(self.request, "Hazard type added.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "The hazard type was not saved. Please fix the errors below.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Add hazard type"
        return context


class HazardTypeUpdateView(StaffRequiredMixin, UpdateView):
    model = HazardType
    form_class = HazardTypeForm
    template_name = "reports/hazard_type_form.html"
    success_url = reverse_lazy("hazard_types")

    def form_valid(self, form):
        messages.success(self.request, "Hazard type updated.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "The hazard type was not saved. Please fix the errors below.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Edit {self.object.name}"
        return context


class HazardTypeToggleView(StaffRequiredMixin, View):
    """BR-10: types are deactivated, never deleted."""

    http_method_names = ["post"]

    def post(self, request, pk):
        hazard_type = get_object_or_404(HazardType, pk=pk)
        hazard_type.is_active = not hazard_type.is_active
        hazard_type.save(update_fields=["is_active"])
        state = "activated" if hazard_type.is_active else "deactivated"
        messages.success(request, f"{hazard_type.name} was {state}.")
        return redirect("hazard_types")
