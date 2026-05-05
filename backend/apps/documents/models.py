"""
Documents app models.
Handles uploaded PDFs and their extracted text.
"""
import os
from django.db import models
from django.utils import timezone
from apps.cases.models import Case


def document_upload_path(instance, filename):
    """Store documents under media/cases/<case_id>/docs/<filename>"""
    return f"cases/{instance.case_id}/docs/{filename}"


class Document(models.Model):
    """
    A PDF or document file attached to a case.
    Text is extracted page-by-page via PyMuPDF on upload.
    """

    DOC_TYPE_CASE_FILE   = "CASE_FILE"
    DOC_TYPE_MEDICAL     = "MEDICAL"
    DOC_TYPE_FIR         = "FIR"
    DOC_TYPE_INSURANCE   = "INSURANCE"
    DOC_TYPE_COURT_ORDER = "COURT_ORDER"
    DOC_TYPE_EVIDENCE    = "EVIDENCE"
    DOC_TYPE_OTHER       = "OTHER"

    DOC_TYPE_CHOICES = [
        (DOC_TYPE_CASE_FILE,   "Case File"),
        (DOC_TYPE_MEDICAL,     "Medical Record"),
        (DOC_TYPE_FIR,         "FIR / Police Report"),
        (DOC_TYPE_INSURANCE,   "Insurance Document"),
        (DOC_TYPE_COURT_ORDER, "Court Order / Judgment"),
        (DOC_TYPE_EVIDENCE,    "Evidence"),
        (DOC_TYPE_OTHER,       "Other"),
    ]

    PROCESSING_PENDING  = "PENDING"
    PROCESSING_DONE     = "DONE"
    PROCESSING_FAILED   = "FAILED"

    PROCESSING_CHOICES = [
        (PROCESSING_PENDING, "Pending"),
        (PROCESSING_DONE,    "Done"),
        (PROCESSING_FAILED,  "Failed"),
    ]

    case            = models.ForeignKey(Case, on_delete=models.CASCADE, related_name="documents")
    file            = models.FileField(upload_to=document_upload_path)
    original_name   = models.CharField(max_length=255, blank=True)
    doc_type        = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES, default=DOC_TYPE_OTHER)

    # ── Extraction results ────────────────────────────────────────────────
    pages           = models.PositiveIntegerField(default=0)
    extracted_text  = models.TextField(blank=True)   # full text dump
    page_texts      = models.JSONField(default=list)  # [{page: 1, text: "..."}, ...]
    processing_status = models.CharField(
        max_length=10, choices=PROCESSING_CHOICES, default=PROCESSING_PENDING
    )
    processing_error = models.TextField(blank=True)

    uploaded_at     = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-uploaded_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self):
        return f"{self.original_name or self.file.name} (Case: {self.case_id})"

    @property
    def file_size_kb(self):
        try:
            return round(self.file.size / 1024, 1)
        except Exception:
            return 0

    @property
    def filename(self):
        return os.path.basename(self.file.name) if self.file else ""
