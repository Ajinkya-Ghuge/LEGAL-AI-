"""
Cases views — CRUD + search + stats.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q

from .models import Case
from .serializers import CaseListSerializer, CaseDetailSerializer


class CasePagination(PageNumberPagination):
    page_size            = 20
    page_size_query_param = "page_size"
    max_page_size        = 100


class CaseViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for Cases.

    GET    /api/cases/              — list (paginated, searchable)
    POST   /api/cases/              — create
    GET    /api/cases/<id>/         — retrieve
    PUT    /api/cases/<id>/         — full update
    PATCH  /api/cases/<id>/         — partial update
    DELETE /api/cases/<id>/         — delete
    GET    /api/cases/stats/        — dashboard stats
    GET    /api/cases/<id>/summary/ — case summary with related counts
    """
    queryset         = Case.objects.all()
    pagination_class = CasePagination
    filter_backends  = [filters.SearchFilter, filters.OrderingFilter]
    search_fields    = ["title", "case_no", "client_name", "description"]
    ordering_fields  = ["created_at", "updated_at", "title", "status"]
    ordering         = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return CaseListSerializer
        return CaseDetailSerializer

    def get_queryset(self):
        qs = Case.objects.all()

        # Filter by status
        status_filter = self.request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter.upper())

        # Filter by case_type
        case_type = self.request.query_params.get("case_type")
        if case_type:
            qs = qs.filter(case_type=case_type.upper())

        return qs

    @action(detail=False, methods=["get"], url_path="stats")
    def stats(self, request):
        """Dashboard statistics — total, by status, by type."""
        total   = Case.objects.count()
        by_status = {
            s.lower(): Case.objects.filter(status=s).count()
            for s, _ in Case.STATUS_CHOICES
        }
        by_type = {
            t.lower(): Case.objects.filter(case_type=t).count()
            for t, _ in Case.CASE_TYPE_CHOICES
            if Case.objects.filter(case_type=t).exists()
        }
        return Response({
            "total":     total,
            "by_status": by_status,
            "by_type":   by_type,
        })

    @action(detail=True, methods=["get"], url_path="summary")
    def summary(self, request, pk=None):
        """Case summary with counts of related documents, timeline events, drafts."""
        case = self.get_object()
        serializer = CaseDetailSerializer(case)
        data = serializer.data

        # Attach related counts
        data["document_count"]  = case.documents.count()
        data["timeline_count"]  = case.timeline_events.count()
        data["draft_count"]     = case.drafts.count()
        data["has_summary"]     = hasattr(case, "medical_summary")

        return Response(data)
