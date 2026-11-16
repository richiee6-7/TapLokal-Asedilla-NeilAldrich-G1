from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import FeedbackView, ProfileView, SignUpView, TapLokalLoginView

urlpatterns = [
    path("login/", TapLokalLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("signup/", SignUpView.as_view(), name="signup"),
    path("feedback/", FeedbackView.as_view(), name="feedback"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
