from django.contrib import admin
from .models import AIModel, AIRecommendation, AIPrediction, PromptLog, ContractParsing

admin.site.register(AIModel)
admin.site.register(AIRecommendation)
admin.site.register(AIPrediction)
admin.site.register(PromptLog)
admin.site.register(ContractParsing)
