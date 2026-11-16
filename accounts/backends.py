from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q


class FlexibleLoginBackend(ModelBackend):
    """Log in with username, email, or mobile number."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None
        User = get_user_model()
        users = User.objects.filter(
            Q(username__iexact=username) | Q(email__iexact=username) | Q(mobile_number=username)
        )
        if users.count() != 1:
            return None
        user = users.first()
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
