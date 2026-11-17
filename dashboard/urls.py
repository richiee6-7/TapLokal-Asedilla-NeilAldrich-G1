from django.urls import path

from .views import (AdminPanelView, CreateStaffView, DashboardView, ManageUsersView,
                    ResidentDashboardView, SetUserRoleView, ToggleUserActiveView)

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("home/", ResidentDashboardView.as_view(), name="resident_dashboard"),
    path("admin-panel/", AdminPanelView.as_view(), name="admin_panel"),
    path("admin-panel/users/", ManageUsersView.as_view(), name="manage_users"),
    path("admin-panel/users/new/", CreateStaffView.as_view(), name="create_staff"),
    path("admin-panel/users/<int:pk>/toggle/", ToggleUserActiveView.as_view(), name="toggle_user_active"),
    path("admin-panel/users/<int:pk>/role/", SetUserRoleView.as_view(), name="set_user_role"),
]
