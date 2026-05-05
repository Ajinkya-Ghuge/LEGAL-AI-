"""
Drafts app models.
Versioned legal document drafts with AI generation.
"""
from django.db import models
from django.utils import timezone
from apps.cases.models import Case


class Draft(models.Model):
    """
    A versioned legal document draft.
    Each save creates a new version — old versions are preserved.
    """

    # ── Draft type choices (Indian legal documents) ───────────────────────
    CLAIM_PETITION  = "CLAIM_PETITION"
    LEGAL_NOTICE    = "LEGAL_NOTICE"
    AFFIDAVIT       = "AFFIDAVIT"
    COMPENSATION    = "COMPENSATION"
    WRITTEN_ARGS    = "WRITTEN_ARGS"
    VAKALATNAMA     = "VAKALATNAMA"
    REPLY           = "REPLY"
    OTHER           = "OTHER"

    DRAFT_TYPE_CHOICES = [
        (CLAIM_PETITION, "Claim Petition u/s 166 MV Act"),
        (LEGAL_NOTICE,   "Legal Notice"),
        (AFFIDAVIT,      "Affidavit"),
        (COMPENSATION,   "Statement of Compensation"),
        (WRITTEN_ARGS,   "Written Arguments"),
        (VAKALATNAMA,    "Vakalatnama"),
        (REPLY,          "Reply / Written Statement"),
        (OTHER,          "Other"),
    ]

    STATUS_DRAFT     = "DRAFT"
    STATUS_REVIEW    = "REVIEW"
    STATUS_FINAL     = "FINAL"
    STATUS_ARCHIVED  = "ARCHIVED"

    STATUS_CHOICES = [
        (STATUS_DRAFT,    "Draft"),
        (STATUS_REVIEW,   "Under Review"),
        (STATUS_FINAL,    "Final"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    case        = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="drafts")
    title       = models.CharField(max_length=255)
    draft_type  = models.CharField(max_length=20, choices=DRAFT_TYPE_CHOICES, default=OTHER)
    content     = models.TextField()                  # HTML content from editor
    version     = models.PositiveIntegerField(default=1)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_DRAFT)

    # ── AI generation metadata ────────────────────────────────────────────
    ai_generated = models.BooleanField(default=False)
    ai_prompt    = models.TextField(blank=True)

    # ── Ref number (e.g. 2024-882-CP) ────────────────────────────────────
    ref_no      = models.CharField(max_length=100, blank=True)

    created_at  = models.DateTimeField(default=timezone.now)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-version", "-created_at"]
        verbose_name = "Draft"
        verbose_name_plural = "Drafts"

    def __str__(self):
        return f"{self.title} v{self.version} (Case {self.case_id})"

    def save_new_version(self, new_content: str) -> "Draft":
        """Create a new version of this draft with updated content."""
        return Draft.objects.create(
            case         = self.case,
            title        = self.title,
            draft_type   = self.draft_type,
            content      = new_content,
            version      = self.version + 1,
            status       = self.STATUS_DRAFT,
            ai_generated = False,
            ref_no       = self.ref_no,
        )
