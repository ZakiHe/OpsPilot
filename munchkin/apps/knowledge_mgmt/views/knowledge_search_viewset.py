from apps.knowledge_mgmt.models import KnowledgeBaseFolder
from apps.knowledge_mgmt.services.knowledge_search_service import KnowledgeSearchService
from django.http import JsonResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.decorators import action


class KnowledgeSearchViewSet(viewsets.ViewSet):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "knowledgebase_folder_ids": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                ),
                "query": openapi.Schema(type=openapi.TYPE_STRING),
                "metadata": openapi.Schema(type=openapi.TYPE_OBJECT),
                "score_threshold": openapi.Schema(type=openapi.TYPE_NUMBER),
            },
        ),
    )
    @action(methods=["post"], detail=False, url_path="search")
    def search(self, request):
        data = request.data
        knowledgebase_folder_ids = data.get("knowledgebase_folder_ids")
        query = data.get("query")
        metadata = data.get("metadata", {})
        score_threshold = data.get("score_threshold", 0)
        service = KnowledgeSearchService()
        knowledgebase_folders = KnowledgeBaseFolder.objects.filter(id__in=knowledgebase_folder_ids)
        docs = service.search(knowledgebase_folders, query, metadata, score_threshold)
        results = {"data": docs}
        return JsonResponse(results)
