from django.contrib import admin
from .models import AIModel, AIRecommendation, AIPrediction, PromptLog, ContractParsing


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'version', 'is_active']
    list_filter = ['model_type', 'is_active']
    search_fields = ['name']


@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ['model', 'recommendation_type', 'confidence', 'created_at']
    list_filter = ['recommendation_type']
    search_fields = ['model__name']


@admin.register(AIPrediction)
class AIPredictionAdmin(admin.ModelAdmin):
    list_display = ['model', 'prediction_type', 'confidence', 'created_at']
    list_filter = ['prediction_type']
    search_fields = ['model__name']


@admin.register(PromptLog)
class PromptLogAdmin(admin.ModelAdmin):
    list_display = ['model', 'user', 'prompt_type', 'created_at']
    list_filter = ['prompt_type']
    search_fields = ['user__email']


@admin.register(ContractParsing)
class ContractParsingAdmin(admin.ModelAdmin):
    list_display = ['contract', 'status', 'parsed_at']
    list_filter = ['status']
    search_fields = ['contract__name']
