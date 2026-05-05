"""
Timeline app models.
Medical visit timeline + AI-generated medical summary.
"""
from django.db import models
from django.utils import timezone
from apps.cases.models import Case


class TimelineEvent(models.Model):
    """
    A single medical visit / event in the case timeline.
    Matches the UI reference (Emergency, Specialist Consult, Chiropractic, etc.)
    """

    # ── Tag / visit type choices ──────────────────────────────────────────
    EMERGENCY        = "EMERGENCY"
    SPECIALIST       = "SPECIALIST"
    CHIROPRACTIC     = "CHIROPRACTIC"
    SURGERY          = "SURGERY"
    FOLLOW_UP        = "FOLLOW_UP"
    DISCHARGE        = "DISCHARGE"
    PHYSIOTHERAPY    = "PHYSIOTHERAPY"
    INVESTIGATION    = "INVESTIGATION"
    OTHER            = "OTHER"

    TAG_CHOICES = [
        (EMERGENCY,     "Emergency"),
        (SPECIALIST,    "Specialist Consult"),
        (CHIROPRACTIC,  "Chiropractic"),
        (SURGERY,       "Surgery"),
        (FOLLOW_UP,     "Follow Up"),
        (DISCHARGE,     "Discharge"),
        (PHYSIOTHERAPY, "Physiotherapy"),
        (INVESTIGATION, "Investigation / Scan"),
        (OTHER,         "Other"),
    ]

    case        = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="timeline_events")
    date        = models.DateField()
    title       = models.CharField(max_length=255)          # facility / event name
    doctor      = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    tag         = models.CharField(max_length=20, choices=TAG_CHOICES, default=OTHER)
    medications = models.JSONField(default=list, blank=True)  # ["Gabapentin", ...]
    order       = models.PositiveIntegerField(default=0)      # for manual sorting

    created_at  = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["date", "order"]
        verbose_name = "Timeline Event"
        verbose_name_plural = "Timeline Events"

    def __str__(self):
        return f"{self.date} — {self.title} ({self.get_tag_display()})"


class MedicalSummary(models.Model):
    """
    AI-generated medical summary for a case.
    One-to-one with Case.
    """
    case        = models.OneToOneField(Case, on_delete=models.CASCADE, related_name="medical_summary")

    # ── Structured fields ─────────────────────────────────────────────────
    injuries    = models.JSONField(default=list)    # ["Fracture of Right Femur", ...]
    treatments  = models.JSONField(default=list)    # [{"type": "Surgery", "detail": "ORIF"}, ...]
    medications = models.JSONField(default=list)    # ["Gabapentin 300mg", ...]
    icd_codes   = models.JSONField(default=list)    # [{"code": "S72.0", "desc": "..."}, ...]

    # ── Financial ─────────────────────────────────────────────────────────
    economic_damages     = models.JSONField(default=dict)  # {medical: X, income_loss: Y, ...}
    non_economic_damages = models.JSONField(default=dict)  # {pain: X, disability: Y, ...}

    # ── Free-text AI output ───────────────────────────────────────────────
    notes           = models.TextField(blank=True)   # full AI report text
    ai_raw_output   = models.TextField(blank=True)   # raw Gemini response

    # ── Missing documents checklist ───────────────────────────────────────
    missing_docs    = models.JSONField(default=list)  # ["FIR", "Disability Certificate", ...]

    # ── Lawyer insights ───────────────────────────────────────────────────
    case_strength   = models.CharField(max_length=20, blank=True)  # "Strong" / "Moderate" / "Weak"
    legal_strategy  = models.TextField(blank=True)

    created_at  = models.DateTimeField(default=timezone.now)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Medical Summary"
        verbose_name_plural = "Medical Summaries"

    def __str__(self):
        return f"Medical Summary — Case {self.case_id}"
