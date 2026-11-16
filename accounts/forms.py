from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction

from .models import CustomUser, ResidentProfile


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css = "form-check-input"
            elif isinstance(widget, forms.Select):
                css = "form-select"
            else:
                css = "form-control"
            widget.attrs["class"] = f"{widget.attrs.get('class', '')} {css}".strip()

    def is_valid(self):
        valid = super().is_valid()
        for name in self.errors:
            if name in self.fields:
                widget = self.fields[name].widget
                widget.attrs["class"] = f"{widget.attrs.get('class', '')} is-invalid".strip()
        return valid


class UniqueEmailMixin:
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class CustomUserCreationForm(UniqueEmailMixin, BootstrapFormMixin, UserCreationForm):
    """Resident registration. Password is hashed by UserCreationForm."""

    purok = forms.CharField(max_length=50)
    street_address = forms.CharField(max_length=255)

    field_order = ["username", "full_name", "email", "mobile_number",
                   "purok", "street_address", "password1", "password2"]

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "full_name", "email", "mobile_number")

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.Role.RESIDENT
        user.save()
        ResidentProfile.objects.create(
            user=user,
            purok=self.cleaned_data["purok"],
            street_address=self.cleaned_data["street_address"],
        )
        return user


class StaffCreationForm(UniqueEmailMixin, BootstrapFormMixin, UserCreationForm):
    """Used by the custom admin panel to add staff accounts."""

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("username", "full_name", "email", "mobile_number")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = CustomUser.Role.STAFF
        user.save()
        return user


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    """Edits the logged-in user's details (+ purok/address for residents)."""

    purok = forms.CharField(max_length=50)
    street_address = forms.CharField(max_length=255)

    class Meta:
        model = CustomUser
        fields = ("full_name", "email", "mobile_number")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resident_profile = ResidentProfile.objects.filter(user=self.instance).first()
        if self.resident_profile:
            self.fields["purok"].initial = self.resident_profile.purok
            self.fields["street_address"].initial = self.resident_profile.street_address
        else:  # staff have no resident profile
            del self.fields["purok"]
            del self.fields["street_address"]

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit)
        if self.resident_profile:
            self.resident_profile.purok = self.cleaned_data["purok"]
            self.resident_profile.street_address = self.cleaned_data["street_address"]
            self.resident_profile.save()
        return user


class StyledAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.CharField(label="Username, email, or mobile number")
    error_messages = {
        "invalid_login": "Invalid credentials. Please check your login and password.",
        "inactive": "This account is inactive.",
    }
