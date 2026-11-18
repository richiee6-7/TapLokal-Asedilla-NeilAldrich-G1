from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, RedirectView, TemplateView

from accounts.forms import StaffCreationForm
from accounts.mixins import ResidentRequiredMixin, StaffRequiredMixin
from accounts.models import CustomUser
from reports.models import HazardReport, ReportStatus


class DashboardView(LoginRequiredMixin, RedirectView):
    """Send each user to the dashboard of their own role."""

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.role == CustomUser.Role.STAFF:
            return reverse_lazy("admin_panel")
        return reverse_lazy("resident_dashboard")


class ResidentDashboardView(ResidentRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reports = HazardReport.objects.filter(reported_by=self.request.user)
        context["total_reports"] = reports.count()
        context["pending_reports"] = reports.filter(status=ReportStatus.PENDING).count()
        context["in_review_reports"] = reports.filter(status=ReportStatus.IN_REVIEW).count()
        context["resolved_reports"] = reports.filter(status=ReportStatus.RESOLVED).count()
        context["recent_reports"] = reports.select_related("hazard_type")[:5]
        return context


# ---------- Custom admin panel (staff only; Django admin is not used) ----------
class AdminPanelView(StaffRequiredMixin, TemplateView):
    template_name = "dashboard/admin_panel.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = CustomUser.objects
        context["total_users"] = users.count()
        context["total_residents"] = users.filter(role=CustomUser.Role.RESIDENT).count()
        context["total_staff"] = users.filter(role=CustomUser.Role.STAFF).count()
        context["inactive_users"] = users.filter(is_active=False).count()
        return context


class ManageUsersView(StaffRequiredMixin, ListView):
    model = CustomUser
    template_name = "dashboard/manage_users.html"
    context_object_name = "users"

    def get_queryset(self):
        qs = CustomUser.objects.order_by("-created_at")
        q = self.request.GET.get("q", "").strip()
        role = self.request.GET.get("role", "")
        if q:
            qs = qs.filter(
                Q(username__icontains=q) | Q(full_name__icontains=q)
                | Q(email__icontains=q) | Q(mobile_number__icontains=q)
            )
        if role in CustomUser.Role.values:
            qs = qs.filter(role=role)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["role"] = self.request.GET.get("role", "")
        return context


class CreateStaffView(StaffRequiredMixin, CreateView):
    form_class = StaffCreationForm
    template_name = "dashboard/create_staff.html"
    success_url = reverse_lazy("manage_users")

    def form_valid(self, form):
        messages.success(self.request, "Staff account created.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Could not create the account. Please fix the errors below.")
        return super().form_invalid(form)


class ToggleUserActiveView(StaffRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        target = get_object_or_404(CustomUser, pk=pk)
        if target == request.user:
            messages.error(request, "You cannot deactivate your own account.")
        else:
            target.is_active = not target.is_active
            target.save(update_fields=["is_active"])
            state = "activated" if target.is_active else "deactivated"
            messages.success(request, f"{target.username} was {state}.")
        return redirect("manage_users")


class SetUserRoleView(StaffRequiredMixin, View):
    http_method_names = ["post"]

    def post(self, request, pk):
        target = get_object_or_404(CustomUser, pk=pk)
        new_role = request.POST.get("role")
        if target == request.user:
            messages.error(request, "You cannot change your own role.")
        elif new_role not in CustomUser.Role.values:
            messages.error(request, "Invalid role.")
        elif target.is_superuser:
            messages.error(request, "Superuser accounts always stay as staff.")
        else:
            target.role = new_role
            target.save(update_fields=["role"])
            messages.success(request, f"{target.username} is now {target.get_role_display()}.")
        return redirect("manage_users")
