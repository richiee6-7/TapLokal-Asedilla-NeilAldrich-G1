from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from accounts.mixins import ResidentRequiredMixin

from .forms import HazardReportForm, ReportFilterForm
from .models import HazardReport, ReportStatus, StatusHistory


class FilteredReportListMixin:
    """Shared search/filter + pagination for the resident and staff lists."""

    search_reporter = False
    paginate_by = 8
    context_object_name = "reports"

    def get_base_queryset(self):
        raise NotImplementedError

    def get_queryset(self):
        self.filter_form = ReportFilterForm(self.request.GET or None)
        qs = self.get_base_queryset().select_related("hazard_type", "reported_by")
        return self.filter_form.filter(qs, search_reporter=self.search_reporter)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        context["filter_form"] = self.filter_form
        context["query_string"] = params.urlencode()
        return context


class MyReportsView(ResidentRequiredMixin, FilteredReportListMixin, ListView):
    template_name = "reports/my_reports.html"

    def get_base_queryset(self):
        # Residents only ever see their own reports.
        return HazardReport.objects.filter(reported_by=self.request.user)


class ReportCreateView(ResidentRequiredMixin, CreateView):
    form_class = HazardReportForm
    template_name = "reports/report_form.html"

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.reported_by = self.request.user
            response = super().form_valid(form)
            # BR-17: every status is recorded with who set it and when.
            StatusHistory.objects.create(
                report=self.object, status=ReportStatus.PENDING,
                changed_by=self.request.user, remarks="Report submitted",
            )
        messages.success(self.request, f"Hazard report #{self.object.pk} was submitted successfully.")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "The report was not submitted. Please fix the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("report_detail", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Report a hazard"
        return context


class OwnReportMixin:
    def get_queryset(self):
        return HazardReport.objects.filter(reported_by=self.request.user)


class PendingOnlyMixin:
    """BR-11: residents can change a report only while it is PENDING."""

    def dispatch(self, request, *args, **kwargs):
        report = self.get_object()  # 404 if it is not the user's own report
        if not report.is_editable:
            messages.error(request, "Only pending reports can be edited or deleted.")
            return redirect("report_detail", pk=report.pk)
        return super().dispatch(request, *args, **kwargs)


class ReportDetailView(ResidentRequiredMixin, OwnReportMixin, DetailView):
    template_name = "reports/report_detail.html"
    context_object_name = "report"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["history"] = self.object.history.select_related("changed_by")
        return context


class ReportUpdateView(ResidentRequiredMixin, PendingOnlyMixin, OwnReportMixin, UpdateView):
    form_class = HazardReportForm
    template_name = "reports/report_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Hazard report updated successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "The report was not updated. Please fix the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("report_detail", args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = f"Edit report #{self.object.pk}"
        return context


class ReportDeleteView(ResidentRequiredMixin, PendingOnlyMixin, OwnReportMixin, DeleteView):
    template_name = "reports/report_confirm_delete.html"
    context_object_name = "report"
    success_url = reverse_lazy("my_reports")

    def form_valid(self, form):
        report = self.object
        if report.photo:
            report.photo.delete(save=False)
        messages.success(self.request, f"Hazard report #{report.pk} was deleted.")
        return super().form_valid(form)
