from apps.core.admin.guarded_admin_base import GuardedAdminBase
from apps.knowledge_mgmt.models import FileKnowledge, KnowledgeBaseFolder, ManualKnowledge, WebPageKnowledge
from apps.knowledge_mgmt.tasks.embed_task import general_embed
from django.contrib import admin, messages
from django.db.models import TextField
from django.http import HttpRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from unfold.contrib.forms.widgets import WysiwygWidget
from unfold.decorators import action

from apps.knowledge_mgmt.tasks.knowledge_integration_task import execute_knowledge_integration


class FileKnowledgeInline(admin.TabularInline):
    model = FileKnowledge
    fieldsets = (
        ("", {"fields": ("title", "file")}),
        ("分块解析", {"fields": ("enable_general_parse", ("general_parse_chunk_size", "general_parse_chunk_overlap"))}),
        ("语义分块解析", {"fields": ("enable_semantic_chunck_parse", "semantic_chunk_parse_embedding_model")}),
        ("Excel解析", {"fields": ("excel_header_row_parse", "excel_full_content_parse")}),
        ("OCR增强", {"fields": ("enable_ocr_parse",)}),
    )
    extra = 0
    readonly_fields = ["title"]


class WebPageKnowledgeInline(admin.TabularInline):
    model = WebPageKnowledge
    fieldsets = (
        ("", {"fields": ("title", "url", "max_depth")}),
        ("分块解析", {"fields": ("enable_general_parse", ("general_parse_chunk_size", "general_parse_chunk_overlap"))}),
        ("语义分块解析", {"fields": ("enable_semantic_chunck_parse", "semantic_chunk_parse_embedding_model")}),
    )
    extra = 0


class ManualKnowledgeInline(admin.StackedInline):
    model = ManualKnowledge
    fieldsets = (
        ("", {"fields": ("title", "content")}),
        ("分块解析", {"fields": ("enable_general_parse", ("general_parse_chunk_size", "general_parse_chunk_overlap"))}),
        ("语义分块解析", {"fields": ("enable_semantic_chunck_parse", "semantic_chunk_parse_embedding_model")}),
    )
    formfield_overrides = {
        TextField: {
            "widget": WysiwygWidget,
        },
    }
    extra = 0


@admin.register(KnowledgeBaseFolder)
class KnowledgeBaseFolderAdmin(GuardedAdminBase):
    def get_list_display(self, request):
        list_display = [
            "name",
            "description",
            "embed_model_link",
            "enable_text_search",
            "enable_vector_search",
            "train_status",
            "train_progress",
        ]
        if request.user.is_superuser:
            list_display.append("owner_name")
        return list_display

    search_fields = ["name"]
    list_display_links = ["name"]
    ordering = ["id"]
    filter_horizontal = ['knowledge_integration']
    actions = ["train_embed", "knowledge_integration_action"]
    actions_list = ["knowledge_integration_action"]
    inlines = [FileKnowledgeInline, WebPageKnowledgeInline, ManualKnowledgeInline]
    readonly_fields = ["train_status"]
    save_as = True

    fieldsets = (
        ("基本信息", {"fields": ("name", "description")}),
        ("知识集成", {"fields": ("knowledge_integration",)}),
        ("Embeding模型", {"fields": ("embed_model",)}),
        ("文本检索", {"fields": ("enable_text_search", "text_search_weight")}),
        ("向量检索", {"fields": ("enable_vector_search", "vector_search_weight", "rag_k", "rag_num_candidates")}),
        ("结果重排", {"fields": ("enable_rerank", "rerank_model", "rerank_top_k")}),
        ("OCR模型", {"fields": ("ocr_model",)}),
    )

    def delete_queryset(self, request, queryset):
        for knowledge in queryset:  # 遍历并使用原生的delete方法, 以调用delete方法同步删除索引
            knowledge.delete()

    @action(description="知识采集", url_path="knowledge_integration_action")
    def knowledge_integration_action(self, request: HttpRequest):
        execute_knowledge_integration.delay()

    @action(description="训练", url_path="train_embed_model")
    def train_embed(self, request: HttpRequest, knowledges):
        # 检查knowledges是否在 处理中
        if any(knowledge.train_status == 1 for knowledge in knowledges):
            messages.error(request, "知识库正在训练中，请稍后再试")
            return redirect(reverse("admin:knowledge_mgmt_knowledgebasefolder_changelist"))

        for knowledge in knowledges:
            general_embed.delay(knowledge.id)

        messages.success(request, "开始训练")
        return redirect(reverse("admin:knowledge_mgmt_knowledgebasefolder_changelist"))

    def embed_model_link(self, obj):
        link = reverse("admin:model_provider_mgmt_embedprovider_change", args=[obj.embed_model.id])
        return format_html('<a href="{}">{}</a>', link, obj.embed_model)

    embed_model_link.short_description = "嵌入模型"
