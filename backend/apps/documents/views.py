"""
Documents views.

POST /api/documents/upload/   — upload file + auto-extract PDF text
POST /api/documents/process/  — (re)process an existing document
GET  /api/documents/          — list all documents (filterable by case)
GET  /api/documents/<id>/     — retrieve single document
DELETE /api/documents/<id>/   — delete document
"""
import os
import logging

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.cases.models import Case
from .models import Document
from .serializers import (
    DocumentSerializer,
    DocumentUploadSerializer,
    DocumentProcessSerializer,
)
from .services import extract_pdf

logger = logging.getLogger(__name__)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    CRUD for Documents + upload + process actions.
    """
    queryset        = Document.objects.select_related("case").all()
    serializer_class = DocumentSerializer
    parser_classes  = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields   = ["original_name", "extracted_text"]
    ordering_fields = ["uploaded_at", "pages"]
    ordering        = ["-uploaded_at"]

    def get_queryset(self):
        qs = Document.objects.select_related("case").all()
        case_id = self.request.query_params.get("case_id")
        if case_id:
            qs = qs.filter(case_id=case_id)
        return qs

    # ── POST /api/documents/upload/ ───────────────────────────────────────
    @action(detail=False, methods=["post"], url_path="upload",
            parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        """
        Upload a document and immediately extract text if it's a PDF.

        Form fields:
            case_id  (int, required)
            file     (file, required)
            doc_type (str, optional)
        """
        serializer = DocumentUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        case_id  = serializer.validated_data["case_id"]
        file     = serializer.validated_data["file"]
        doc_type = serializer.validated_data.get("doc_type", Document.DOC_TYPE_OTHER)

        # Validate case exists
        try:
            case = Case.objects.get(pk=case_id)
        except Case.DoesNotExist:
            return Response(
                {"error": f"Case with id={case_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create document record
        doc = Document.objects.create(
            case          = case,
            file          = file,
            original_name = file.name,
            doc_type      = doc_type,
        )

        # Auto-extract if PDF
        if file.name.lower().endswith(".pdf"):
            result = extract_pdf(doc.file.path)
            if result["success"]:
                doc.pages             = result["pages"]
                doc.extracted_text    = result["full_text"]
                doc.page_texts        = result["page_texts"]
                doc.processing_status = Document.PROCESSING_DONE
                
                # Trigger simple RAG ingestion for this PDF
                try:
                    from apps.web.simple_rag import SimpleCaseRAG
                    rag = SimpleCaseRAG(case.id)
                    rag.ingest_pdf(doc.file.path, doc.id, doc.original_name)
                    logger.info(f"✅ Simple RAG ingestion complete for document {doc.id} in case {case.id}")
                except Exception as e:
                    logger.error(f"❌ Simple RAG ingestion failed for document {doc.id}: {str(e)}")
            else:
                doc.processing_status = Document.PROCESSING_FAILED
                doc.processing_error  = result["error"]
            doc.save()

        return Response(
            DocumentSerializer(doc).data,
            status=status.HTTP_201_CREATED,
        )

    # ── POST /api/documents/process/ ─────────────────────────────────────
    @action(detail=False, methods=["post"], url_path="process")
    def process(self, request):
        """
        (Re)process an existing document — extract text from PDF.

        Body: { "document_id": <int> }
        """
        serializer = DocumentProcessSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        doc_id = serializer.validated_data["document_id"]
        try:
            doc = Document.objects.get(pk=doc_id)
        except Document.DoesNotExist:
            return Response(
                {"error": f"Document with id={doc_id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not doc.file.name.lower().endswith(".pdf"):
            return Response(
                {"error": "Only PDF files can be processed for text extraction."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = extract_pdf(doc.file.path)

        if result["success"]:
            doc.pages             = result["pages"]
            doc.extracted_text    = result["full_text"]
            doc.page_texts        = result["page_texts"]
            doc.processing_status = Document.PROCESSING_DONE
            doc.processing_error  = ""
        else:
            doc.processing_status = Document.PROCESSING_FAILED
            doc.processing_error  = result["error"]

        doc.save()

        return Response({
            "success":  result["success"],
            "document": DocumentSerializer(doc).data,
            "message":  (
                f"Extracted {result['pages']} pages successfully."
                if result["success"]
                else f"Extraction failed: {result['error']}"
            ),
        })

    # ── GET /api/documents/<id>/view-source/ ──────────────────────────────
    @action(detail=True, methods=["get"], url_path="view-source")
    def view_source(self, request, pk=None):
        """
        View source text in PDF with highlighting.
        
        Query params:
            page (int, optional): Specific page number (1-indexed)
            text (str, optional): Text snippet to highlight
        """
        from .pdf_viewer import PDFSourceViewer
        
        doc = self.get_object()
        page_num = request.GET.get('page')
        search_text = request.GET.get('text', '')
        
        if not doc.file:
            return Response(
                {"error": "Document file not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        try:
            with PDFSourceViewer(doc.file.path) as viewer:
                if search_text:
                    # Find text in document
                    page_num_int = int(page_num) - 1 if page_num else None
                    results = viewer.find_text_location(search_text, page_num_int)
                    
                    return Response({
                        "success": True,
                        "document_id": doc.id,
                        "document_name": doc.original_name,
                        "search_text": search_text,
                        "matches": results,
                        "total_matches": len(results)
                    })
                else:
                    # Get page content
                    if page_num:
                        page_data = viewer.get_page_content(int(page_num))
                        return Response({
                            "success": True,
                            "document_id": doc.id,
                            "document_name": doc.original_name,
                            "page_data": page_data
                        })
                    else:
                        return Response(
                            {"error": "Either 'page' or 'text' parameter required"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
        except Exception as e:
            logger.exception("Error viewing source: %s", str(e))
            return Response(
                {"error": f"Failed to view source: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
