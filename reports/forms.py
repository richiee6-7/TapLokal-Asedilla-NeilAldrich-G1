from django import forms
from django.core.files.uploadedfile import UploadedFile
from django.db.models import Q

from accounts.forms import BootstrapFormMixin

from .models import HazardReport, HazardType, ReportStatus

MAX_PHOTO_MB = 5


class HazardReportForm(BootstrapFormMixin, forms.ModelForm):
    photo = forms.ImageField(
        required=False,
        label="Photo (optional)",
        widget=forms.FileInput(attrs={"accept": "image/*"}),
        help_text=f"JPG or PNG, up to {MAX_PHOTO_MB} MB.",
    )

    class Meta:
        model = HazardReport
        fields = ["hazard_type", "street_address", "description",
                  "latitude", "longitude", "photo"]
        labels = {
            "hazard_type": "Hazard type",
            "street_address": "Street address of the hazard",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
        }
        error_messages = {
            "latitude": {"required": "Please pin the hazard location on the map."},
            "longitude": {"required": "Please pin the hazard location on the map."},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only active hazard types can be chosen (BR-10); keep the current one on edit.
        types = Q(is_active=True)
        if self.instance.pk:
            types |= Q(pk=self.instance.hazard_type_id)
        self.fields["hazard_type"].queryset = HazardType.objects.filter(types)
        self.fields["hazard_type"].empty_label = "Select a hazard type"

    def clean_street_address(self):
        value = self.cleaned_data["street_address"].strip()
        if len(value) < 5:
            raise forms.ValidationError("Please enter the street address (at least 5 characters).")
        return value

    def clean_description(self):
        value = self.cleaned_data["description"].strip()
        if len(value) < 10:
            raise forms.ValidationError("Please describe the hazard (at least 10 characters).")
        return value

    def clean_photo(self):
        photo = self.cleaned_data.get("photo")
        if isinstance(photo, UploadedFile) and photo.size > MAX_PHOTO_MB * 1024 * 1024:
            raise forms.ValidationError(f"The photo must be {MAX_PHOTO_MB} MB or smaller.")
        return photo


class ReportFilterForm(BootstrapFormMixin, forms.Form):
    """Search/filter by keyword, status, type, and date (used by both roles)."""

    q = forms.CharField(required=False, label="Keyword")
    status = forms.ChoiceField(
        required=False, choices=[("", "All statuses")] + ReportStatus.choices
    )
    hazard_type = forms.ModelChoiceField(
        required=False, queryset=HazardType.objects.all(), empty_label="All types"
    )
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))

    def filter(self, queryset, search_reporter=False):
        if not self.is_bound or not self.is_valid():
            return queryset
        data = self.cleaned_data
        if data["q"]:
            q = data["q"]
            cond = (Q(description__icontains=q) | Q(street_address__icontains=q)
                    | Q(hazard_type__name__icontains=q))
            if search_reporter:
                cond |= (Q(reported_by__full_name__icontains=q)
                         | Q(reported_by__username__icontains=q))
            queryset = queryset.filter(cond)
        if data["status"]:
            queryset = queryset.filter(status=data["status"])
        if data["hazard_type"]:
            queryset = queryset.filter(hazard_type=data["hazard_type"])
        if data["date_from"]:
            queryset = queryset.filter(created_at__date__gte=data["date_from"])
        if data["date_to"]:
            queryset = queryset.filter(created_at__date__lte=data["date_to"])
        return queryset
