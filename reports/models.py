from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class ReportStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    IN_REVIEW = "IN_REVIEW", "In Review"
    RESOLVED = "RESOLVED", "Resolved"


class HazardType(models.Model):
    """`hazard_types` table from the SDD."""

    PRIORITY_CHOICES = [(1, "1 - High"), (2, "2 - Medium"), (3, "3 - Low")]

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    priority_level = models.SmallIntegerField(choices=PRIORITY_CHOICES, default=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "hazard_types"
        ordering = ["priority_level", "name"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(priority_level__gte=1) & models.Q(priority_level__lte=3),
                name="hazard_types_priority_valid",
            )
        ]

    def __str__(self):
        return self.name


class HazardReport(models.Model):
    """`hazard_reports` table from the SDD."""

    Status = ReportStatus

    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="hazard_reports"
    )
    hazard_type = models.ForeignKey(
        HazardType, on_delete=models.PROTECT, related_name="reports"
    )
    description = models.TextField()
    street_address = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    photo = models.ImageField(upload_to="hazard_photos/", blank=True, null=True)
    status = models.CharField(
        max_length=15, choices=ReportStatus.choices, default=ReportStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "hazard_reports"
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(latitude__gte=-90) & models.Q(latitude__lte=90),
                name="hazard_reports_latitude_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(longitude__gte=-180) & models.Q(longitude__lte=180),
                name="hazard_reports_longitude_valid",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=["PENDING", "IN_REVIEW", "RESOLVED"]),
                name="hazard_reports_status_valid",
            ),
            # BR-09: resolved_at is set only when the status is RESOLVED
            models.CheckConstraint(
                condition=(
                    models.Q(status="RESOLVED", resolved_at__isnull=False)
                    | (~models.Q(status="RESOLVED") & models.Q(resolved_at__isnull=True))
                ),
                name="hazard_reports_resolved_at_consistent",
            ),
        ]

    @property
    def is_editable(self):
        """BR-11: residents may edit/delete only while the report is PENDING."""
        return self.status == ReportStatus.PENDING

    def __str__(self):
        return f"Report #{self.pk} - {self.hazard_type}"


class StatusHistory(models.Model):
    """`status_history` table from the SDD (the document-request link is added
    in the document requests phase)."""

    STATUS_CHOICES = ReportStatus.choices + [("READY_FOR_PICKUP", "Ready for Pickup")]

    report = models.ForeignKey(
        HazardReport, on_delete=models.CASCADE, related_name="history"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="status_changes"
    )
    remarks = models.CharField(max_length=255, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "status_history"
        ordering = ["changed_at", "pk"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    status__in=["PENDING", "IN_REVIEW", "RESOLVED", "READY_FOR_PICKUP"]
                ),
                name="status_history_status_valid",
            )
        ]

    def __str__(self):
        return f"{self.report_id}: {self.status}"
