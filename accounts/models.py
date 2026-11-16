from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

mobile_validator = RegexValidator(
    regex=r"^(09\d{9}|\+639\d{9})$",
    message="Enter a valid PH mobile number (e.g. 09171234567 or +639171234567).",
)


class CustomUser(AbstractUser):
    """`users` table from the SDD. Passwords are hashed by Django's auth system."""

    class Role(models.TextChoices):
        RESIDENT = "RESIDENT", "Resident"
        STAFF = "STAFF", "Barangay Staff"

    first_name = None
    last_name = None

    email = models.EmailField("email address", unique=True)
    mobile_number = models.CharField(max_length=15, unique=True, validators=[mobile_validator])
    full_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.RESIDENT)
    created_at = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ["email", "mobile_number", "full_name"]

    class Meta:
        db_table = "users"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(role__in=["RESIDENT", "STAFF"]),
                name="users_role_valid",
            )
        ]

    def save(self, *args, **kwargs):
        # Accounts made with `createsuperuser` are staff.
        if self.is_superuser:
            self.role = self.Role.STAFF
        super().save(*args, **kwargs)

    def get_full_name(self):
        return self.full_name

    def get_short_name(self):
        return self.full_name

    def __str__(self):
        return self.full_name or self.username


class ResidentProfile(models.Model):
    """`resident_profiles` table from the SDD."""

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="resident_profile")
    purok = models.CharField(max_length=50)
    street_address = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = "resident_profiles"

    def __str__(self):
        return f"Profile of {self.user}"
