"""
AI Engine app serializers - AIRecommendationSerializer, AIModelSerializer,
AIPredictionSerializer, PromptLogSerializer, ContractParsingSerializer.
"""

from rest_framework import serializers

from .models import AIModel, AIPrediction, AIRecommendation, ContractParsing, PromptLog


# =============================================================================
# AI Model Serializer
# =============================================================================

class AIModelSerializer(serializers.ModelSerializer):
    """Serializer for AIModel model."""

    model_type_display = serializers.CharField(
        source="get_model_type_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    prediction_count = serializers.SerializerMethodField()

    class Meta:
        model = AIModel
        fields = [
            "id", "name", "version",
            "model_type", "model_type_display",
            "endpoint", "config", "is_active",
            "last_trained", "accuracy_score",
            "status", "status_display",
            "description", "training_data_info", "metrics",
            "prediction_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_prediction_count(self, obj):
        return obj.predictions.count()

    def validate(self, attrs):
        name = attrs.get("name", getattr(self.instance, "name", None))
        version = attrs.get("version", getattr(self.instance, "version", None))

        if name and version:
            qs = AIModel.objects.filter(name=name, version=version)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "An AI model with this name and version already exists."
                )
        return attrs


# =============================================================================
# AI Recommendation Serializer
# =============================================================================

class AIRecommendationSerializer(serializers.ModelSerializer):
    """Serializer for AIRecommendation model."""

    client_name = serializers.CharField(
        source="client.name", read_only=True, default=None
    )
    contract_number = serializers.CharField(
        source="contract.contract_number", read_only=True, default=None
    )
    recommendation_type_display = serializers.CharField(
        source="get_recommendation_type_display", read_only=True
    )
    priority_display = serializers.CharField(
        source="get_priority_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    accepted_by_name = serializers.SerializerMethodField()
    roi_estimate = serializers.SerializerMethodField()

    class Meta:
        model = AIRecommendation
        fields = [
            "id", "client", "client_name",
            "contract", "contract_number",
            "recommendation_type", "recommendation_type_display",
            "title", "description",
            "expected_impact_amount", "expected_impact_pct",
            "confidence_score", "priority", "priority_display",
            "status", "status_display",
            "generated_at", "model_version",
            "reasoning", "action_items",
            "accepted_by", "accepted_by_name", "accepted_at",
            "implementation_notes", "actual_impact_amount",
            "roi_estimate",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "generated_at", "confidence_score",
            "accepted_by", "accepted_at",
            "created_at", "updated_at",
        ]

    def get_accepted_by_name(self, obj):
        if obj.accepted_by:
            return obj.accepted_by.get_full_name()
        return None

    def get_roi_estimate(self, obj):
        """Calculate estimated ROI if actual impact is available."""
        if obj.actual_impact_amount and obj.expected_impact_amount:
            return round(
                (obj.actual_impact_amount / obj.expected_impact_amount) * 100, 2
            )
        return None


# =============================================================================
# AI Prediction Serializer
# =============================================================================

class AIPredictionSerializer(serializers.ModelSerializer):
    """Serializer for AIPrediction model."""

    model_name = serializers.CharField(source="model.name", read_only=True)
    model_version = serializers.CharField(source="model.version", read_only=True)
    prediction_type_display = serializers.CharField(
        source="get_prediction_type_display", read_only=True
    )
    accuracy_label = serializers.SerializerMethodField()

    class Meta:
        model = AIPrediction
        fields = [
            "id", "model", "model_name", "model_version",
            "input_data", "output_data", "confidence",
            "prediction_type", "prediction_type_display",
            "entity_type", "entity_id",
            "actual_outcome", "is_correct",
            "accuracy_label",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "model_name", "model_version",
            "created_at", "updated_at",
        ]

    def get_accuracy_label(self, obj):
        if obj.is_correct is None:
            return "pending"
        return "correct" if obj.is_correct else "incorrect"


# =============================================================================
# Prompt Log Serializer
# =============================================================================

class PromptLogSerializer(serializers.ModelSerializer):
    """Serializer for PromptLog model."""

    model_name = serializers.CharField(
        source="model.name", read_only=True, default=None
    )
    user_email = serializers.CharField(
        source="user.email", read_only=True, default=None
    )
    total_tokens = serializers.SerializerMethodField()

    class Meta:
        model = PromptLog
        fields = [
            "id", "model", "model_name",
            "user", "user_email",
            "prompt_text", "response_text",
            "tokens_used", "prompt_tokens", "completion_tokens",
            "latency_ms", "cost",
            "status", "error_message", "metadata",
            "total_tokens", "created_at",
        ]
        read_only_fields = [
            "id", "tokens_used", "prompt_tokens",
            "completion_tokens", "latency_ms", "cost",
            "status", "error_message", "created_at",
        ]

    def get_total_tokens(self, obj):
        return obj.prompt_tokens + obj.completion_tokens


# =============================================================================
# Contract Parsing Serializer
# =============================================================================

class ContractParsingSerializer(serializers.ModelSerializer):
    """Serializer for ContractParsing model."""

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    document_name = serializers.CharField(
        source="document.file_name", read_only=True
    )
    avg_confidence = serializers.SerializerMethodField()
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ContractParsing
        fields = [
            "id", "document", "document_name",
            "raw_text", "extracted_entities", "confidence_scores",
            "model_version", "processing_time_ms",
            "status", "status_display",
            "page_count", "error_message",
            "reviewed_by", "reviewed_by_name", "reviewed_at",
            "corrections", "avg_confidence",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "raw_text", "extracted_entities",
            "confidence_scores", "processing_time_ms",
            "status", "page_count", "error_message",
            "reviewed_at", "created_at", "updated_at",
        ]

    def get_avg_confidence(self, obj):
        return obj.avg_confidence

    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name()
        return None
