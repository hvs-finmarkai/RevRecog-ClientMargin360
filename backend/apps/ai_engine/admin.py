"""AI Engine admin configuration."""
from django.contrib import admin
from .models import AIProcessingJob, AIModel, EmbeddingDocument


@admin.register(AIProcessingJob)
class AIProcessingJobAdmin(admin.ModelAdmin):
    list_display = ["job_type", "status", "confidence_score", "processing_time_seconds", "created_at"]
    list_filter = ["job_type", "status"]
    readonly_fields = ["input_data", "output_data"]


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ["name", "model_type", "version", "provider", "is_active", "accuracy_score"]
    list_filter = ["model_type", "provider", "is_active"]


@admin.register(EmbeddingDocument)
class EmbeddingDocumentAdmin(admin.ModelAdmin):
    list_display = ["title", "source_type", "source_id", "chunk_count", "created_at"]
    list_filter = ["source_type"]
