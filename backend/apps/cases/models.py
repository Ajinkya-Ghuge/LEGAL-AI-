"""
Cases app models.
Central entity — everything else hangs off a Case.
"""
from django.db import models
from django.utils import timezone


class Case(models.Model):
    """
    Core legal case record.
    Covers MACT, property disputes, consumer cases, criminal matters, etc.
    """

    # ── Case type choices (Indian legal context) ──────────────────────────
    MACT            = "MACT"
    PROPERTY        = "PROPERTY"
    CRIMINAL        = "CRIMINAL"
    CIVIL           = "CIVIL"
    CONSUMER        = "CONSUMER"
    LABOUR          = "LABOUR"
    FAMILY          = "FAMILY"
    OTHER           = "OTHER"

    CASE_TYPE_CHOICES = [
        (MACT,     "Motor Accident Claims (MACT)"),
        (PROPERTY, "Property Dispute"),
        (CRIMINAL, "Criminal"),
        (CIVIL,    "Civil"),
        (CONSUMER, "Consumer"),
        (LABOUR,   "Labour / Employment"),
        (FAMILY,   "Family / Matrimonial"),
        (OTHER,    "Other"),
    ]

    # ── Status choices ────────────────────────────────────────────────────
    ACTIVE   = "ACTIVE"
    PENDING  = "PENDING"
    CLOSED   = "CLOSED"
    STAYED   = "STAYED"

    STATUS_CHOICES = [
        (ACTIVE,  "Active"),
        (PENDING, "Pending"),
        (CLOSED,  "Closed"),
        (STAYED,  "Stayed"),
    ]

    # ── Core fields ───────────────────────────────────────────────────────
    title           = models.CharField(max_length=255)
    case_no         = models.CharField(max_length=100, blank=True)
    case_type       = models.CharField(max_length=20, choices=CASE_TYPE_CHOICES, default=MACT)
    status          = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    description     = models.TextField(blank=True)

    # ── Client / Petitioner ───────────────────────────────────────────────
    client_name     = models.CharField(max_length=255)
    client_age      = models.CharField(max_length=20, blank=True)
    client_address  = models.TextField(blank=True)
    father_name     = models.CharField(max_length=255, blank=True)
    occupation      = models.CharField(max_length=100, blank=True)

    # ── Accident / Incident details ───────────────────────────────────────
    accident_date   = models.DateField(null=True, blank=True)
    accident_place  = models.CharField(max_length=255, blank=True)
    vehicle_no      = models.CharField(max_length=50, blank=True)
    fir_no          = models.CharField(max_length=100, blank=True)
    hospital        = models.CharField(max_length=255, blank=True)
    tribunal        = models.CharField(max_length=255, blank=True)

    # ── Financial ─────────────────────────────────────────────────────────
    claim_amount    = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    # ── Injuries (stored as JSON list) ────────────────────────────────────
    injuries        = models.JSONField(default=list, blank=True)

    # ── Compensation breakdown (JSON list of {head, amount}) ──────────────
    compensation    = models.JSONField(default=list, blank=True)

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at      = models.DateTimeField(default=timezone.now)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Case"
        verbose_name_plural = "Cases"

    def __str__(self):
        return f"{self.case_no} — {self.title}" if self.case_no else self.title

    @property
    def claim_amount_display(self):
        if self.claim_amount:
            return f"₹ {self.claim_amount:,.0f}/-"
        return "Not specified"
