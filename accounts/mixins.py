from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect

from .models import CustomUser


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Logged-in users only, and only users holding `required_role`."""

    required_role = None

    def test_func(self):
        return self.request.user.role == self.required_role

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, "You are not allowed to open that page.")
            return redirect("dashboard")
        return super().handle_no_permission()


class ResidentRequiredMixin(RoleRequiredMixin):
    required_role = CustomUser.Role.RESIDENT


class StaffRequiredMixin(RoleRequiredMixin):
    required_role = CustomUser.Role.STAFF
