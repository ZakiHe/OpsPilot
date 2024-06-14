# Generated by Django 4.2.7 on 2024-06-07 16:38

import django.core.validators
import django_minio_backend.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FileKnowledge",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255, verbose_name="文件名称")),
                (
                    "file",
                    models.FileField(
                        storage=django_minio_backend.models.MinioBackend(bucket_name="munchkin-private"),
                        upload_to=django_minio_backend.models.iso_date_prefix,
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=[
                                    "md",
                                    "docx",
                                    "xlsx",
                                    "csv",
                                    "pptx",
                                    "pdf",
                                    "txt",
                                ]
                            )
                        ],
                        verbose_name="文件",
                    ),
                ),
            ],
            options={
                "verbose_name": "文件知识",
                "verbose_name_plural": "文件知识",
            },
        ),
        migrations.CreateModel(
            name="KnowledgeBaseFolder",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                (
                    "name",
                    models.CharField(max_length=255, unique=True, verbose_name="名称"),
                ),
                ("description", models.TextField(verbose_name="描述")),
                (
                    "train_status",
                    models.IntegerField(
                        choices=[(0, "待训练"), (1, "处理中"), (2, "完成"), (3, "失败")],
                        default=0,
                        verbose_name="状态",
                    ),
                ),
                ("train_progress", models.FloatField(default=0, verbose_name="训练进度")),
                (
                    "enable_general_parse",
                    models.BooleanField(default=True, verbose_name="分块解析"),
                ),
                (
                    "general_parse_chunk_size",
                    models.IntegerField(default=1000, verbose_name="分块大小"),
                ),
                (
                    "general_parse_chunk_overlap",
                    models.IntegerField(default=100, verbose_name="分块重叠"),
                ),
                (
                    "enable_vector_search",
                    models.BooleanField(default=True, verbose_name="向量检索"),
                ),
                (
                    "vector_search_weight",
                    models.FloatField(default=0.1, verbose_name="向量检索权重"),
                ),
                ("rag_k", models.IntegerField(default=5, verbose_name="返回结果数量")),
                (
                    "rag_num_candidates",
                    models.IntegerField(default=1000, verbose_name="候选数量"),
                ),
                (
                    "enable_text_search",
                    models.BooleanField(default=True, verbose_name="文本检索"),
                ),
                (
                    "text_search_weight",
                    models.FloatField(default=0.9, verbose_name="文本检索权重"),
                ),
                (
                    "enable_rerank",
                    models.BooleanField(default=False, verbose_name="启用Rerank"),
                ),
                (
                    "rerank_top_k",
                    models.IntegerField(default=5, verbose_name="Rerank返回结果数量"),
                ),
            ],
            options={
                "verbose_name": "知识库",
                "verbose_name_plural": "知识库",
            },
        ),
    ]
