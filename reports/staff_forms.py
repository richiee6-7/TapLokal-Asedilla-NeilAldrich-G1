from django import forms

from accounts.forms import BootstrapFormMixin

from .models import HazardType, ReportStatus


class StatusUpdateForm(BootstrapFormMixin, forms.Form):
    status = forms.ChoiceField(label="New status")
    remarks = forms.CharField(
        required=False, max_length=255, label="Remarks (optional)",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Crew dispatched to the site"}),
    )

    def __init__(self, *args, report, **kwargs):
        super().__init__(*args, **kwargs)
        self.report = report
        # Only statuses different from the current one can be chosen.
        self.fields["status"].choices = [
            (value, label) for value, label in ReportStatus.choices if value != report.status
        ]


class HazardTypeForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = HazardType
        fields = ["name", "description", "priority_level", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
        labels = {"is_active": "Active (can be selected in new reports)"}

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if HazardType.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A hazard type with this name already exists.")
        return name
