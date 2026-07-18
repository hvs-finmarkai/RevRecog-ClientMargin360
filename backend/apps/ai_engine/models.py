"""
AI Engine app models - AIRecommendation, AIModel, AIPrediction,
PromptLog, ContractParsing.
Manages AI/ML models, recommendations, predictions, and document parsing.
"""

import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.users.models import BaseModel


# =============================================================================
# AI Model Registry
# =============================================================================

class AIModel(BaseModel):
    """Registry of AI/ML models used in the system."""

    class ModelType(models.TextChoices):
        CLASSIFICATION = "classification", "Classification"
        REGRESSION = "regression", "Regression"
        NLP = "nlp", "Natural Language Processing"
        ANOMALY = "anomaly", "Anomaly Detection"
        RECOMMENDATION = "recommendation", "Recommendation"
        FORECASTING = "forecasting", "Forecasting"
        CLUSTERING = "clustering", "Clustering"

    class StatusChoices(models.TextChoices):
        TRAINING = "training", "Training"
        ACTIVE = "active", "Active"
        DEPRECATED = "deprecated", "Deprecated"
        FAILED = "failed", "Failed"
        STAGING = "staging", "Staging"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=50)
    model_type = models.CharField(
        max_length=20,
        choices=ModelType.choices,
    )
    endpoint = models.URLField(
        max_length=500,
        blank=True,
        default="",
        help_text="API endpoint for model inference",
    )
    config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Model configuration parameters",
    )
    is_active = models.BooleanField(default=True)
    last_trained = models.DateTimeField(null=True, blank=True)
    accuracy_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Model accuracy score (0-1)",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.STAGING,
    )
    description = models.TextField(blank=True, default="")
    training_data_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Information about training data",
    )
    metrics = models.JSONField(
        default=dict,
        blank=True,
        help_text="Model performance metrics",
    )

    class Meta:
        ordering = ["-last_trained"]
        verbose_name = "AI Model"
        verbose_name_plural = "AI Models"
        unique_together = ["name", "version"]
        indexes = [
            models.Index(fields=["name", "version"]),
            models.Index(fields=["model_type", "is_active"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.name} v{self.version} ({self.get_model_type_display()})"


# =============================================================================
# AI Recommendation Model
# =============================================================================

class AIRecommendation(BaseModel):
    """AI-generated recommendations for clients and contracts."""

    class RecommendationType(models.TextChoices):
        REPRICE = "reprice", "Repricing"
        EXPAND = "expand", "Expansion Opportunity"
        RESTRUCTURE = "restructure", "Restructure"
        EXIT = "exit", "Exit/Terminate"
        OPTIMIZE = "optimize", "Optimize Operations"
        UPSELL = "upsell", "Upsell"
        RETENTION = "retention", "Retention Action"
        RISK_MITIGATION = "risk_mitigation", "Risk Mitigation"

    class PriorityChoices(models.TextChoices):
        CRITICAL = "critical", "Critical"
        HIGH = "high", "High"
        MEDIUM = "medium", "Medium"
        LOW = "low", "Low"

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending Review"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        IMPLEMENTED = "implemented", "Implemented"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
        related_name="ai_recommendations",
        null=True,
        blank=True,
    )
    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.CASCADE,
        related_name="ai_recommendations",
        null=True,
        blank=True,
    )
    recommendation_type = models.CharField(
        max_length=20,
        choices=RecommendationType.choices,
        db_index=True,
    )
    title = models.CharField(max_length=300)
    description = models.TextField()
    expected_impact_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Expected financial impact (positive = revenue gain)",
    )
    expected_impact_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        help_text="Expected percentage impact",
    )
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="AI confidence score (0-1)",
    )
    priority = models.CharField(
        max_length=10,
        choices=PriorityChoices.choices,
        default=PriorityChoices.MEDIUM,
    )
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        db_index=True,
    )
    generated_at = models.DateTimeField(auto_now_add=True)
    model_version = models.CharField(
        max_length=100,
        blank=True,
        default="",
        help_text="AI model version that generated this",
    )
    reasoning = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed reasoning/factors as JSON",
    )
    action_items = models.JSONField(
        default=list,
        blank=True,
        help_text="Suggested action items",
    )
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_recommendations",
    )
    accepted_at = models.DateTimeField(null=True, blank=True)
    implementation_notes = models.TextField(blank=True, default="")
    actual_impact_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Actual financial impact after implementation",
    )

    class Meta:
        ordering = ["-generated_at"]
        verbose_name = "AI Recommendation"
        verbose_name_plural = "AI Recommendations"
        indexes = [
            models.Index(fields=["client", "status"]),
            models.Index(fields=["contract", "status"]),
            models.Index(fields=["recommendation_type", "status"]),
            models.Index(fields=["priority", "status"]),
            models.Index(fields=["generated_at"]),
            models.Index(fields=["confidence_score"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_recommendation_type_display()})"


# =============================================================================
# AI Prediction Model
# =============================================================================

class AIPrediction(BaseModel):
    """Individual predictions made by AI models."""

    class PredictionType(models.TextChoices):
        CHURN_RISK = "churn_risk", "Churn Risk"
        PAYMENT_DELAY = "payment_delay", "Payment Delay"
        REVENUE_FORECAST = "revenue_forecast", "Revenue Forecast"
        MARGIN_TREND = "margin_trend", "Margin Trend"
        LEAKAGE_RISK = "leakage_risk", "Leakage Risk"
        CONTRACT_VALUE = "contract_value", "Contract Value Prediction"
        COLLECTION_DATE = "collection_date", "Collection Date"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(
        AIModel,
        on_delete=models.CASCADE,
        related_name="predictions",
    )
    input_data = models.JSONField(
        default=dict,
        help_text="Input features/data used for prediction",
    )
    output_data = models.JSONField(
        default=dict,
        help_text="Prediction output/result",
    )
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Prediction confidence (0-1)",
    )
    prediction_type = models.CharField(
        max_length=20,
        choices=PredictionType.choices,
        db_index=True,
    )
    entity_type = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text="Type of entity (client, contract, invoice, etc.)",
    )
    entity_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="ID of the entity being predicted",
    )
    actual_outcome = models.JSONField(
        default=dict,
        blank=True,
        help_text="Actual outcome for model validation",
    )
    is_correct = models.BooleanField(
        null=True,
        blank=True,
        help_text="Whether prediction was correct (populated after outcome)",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "AI Prediction"
        verbose_name_plural = "AI Predictions"
        indexes = [
            models.Index(fields=["model", "prediction_type"]),
            models.Index(fields=["prediction_type"]),
            models.Index(fields=["entity_type", "entity_id"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["confidence"]),
        ]

    def __str__(self):
        return f"{self.get_prediction_type_display()} by {self.model.name} (conf: {self.confidence})"


# =============================================================================
# Prompt Log Model
# =============================================================================

class PromptLog(models.Model):
    """Logs all AI/LLM prompts and responses for audit and optimization."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    model = models.ForeignKey(
        AIModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prompt_logs",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prompt_logs",
    )
    prompt_text = models.TextField()
    response_text = models.TextField(blank=True, default="")
    tokens_used = models.PositiveIntegerField(
        default=0,
        help_text="Total tokens consumed (prompt + response)",
    )
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    latency_ms = models.PositiveIntegerField(
        default=0,
        help_text="Response latency in milliseconds",
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=6,
        default=0,
        help_text="Estimated cost in USD",
    )
    status = models.CharField(
        max_length=20,
        default="success",
        choices=[
            ("success", "Success"),
            ("error", "Error"),
            ("timeout", "Timeout"),
            ("rate_limited", "Rate Limited"),
        ],
    )
    error_message = models.TextField(blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Prompt Log"
        verbose_name_plural = "Prompt Logs"
        indexes = [
            models.Index(fields=["model", "created_at"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Prompt by {self.user} at {self.created_at} ({self.tokens_used} tokens)"


# =============================================================================
# Contract Parsing Model
# =============================================================================

class ContractParsing(BaseModel):
    """Results of AI-powered contract document parsing."""

    class StatusChoices(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        NEEDS_REVIEW = "needs_review", "Needs Review"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        "contracts.ContractDocument",
        on_delete=models.CASCADE,
        related_name="parsings",
    )
    raw_text = models.TextField(
        blank=True,
        default="",
        help_text="Raw extracted text from document",
    )
    extracted_entities = models.JSONField(
        default=dict,
        blank=True,
        help_text="Extracted entities (dates, amounts, parties, etc.)",
    )
    confidence_scores = models.JSONField(
        default=dict,
        blank=True,
        help_text="Confidence scores per extracted field",
    )
    model_version = models.CharField(max_length=100, blank=True, default="")
    processing_time_ms = models.PositiveIntegerField(
        default=0,
        help_text="Processing time in milliseconds",
    )
    status = models.CharField(
        max_length=15,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    page_count = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, default="")
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_parsings",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    corrections = models.JSONField(
        default=dict,
        blank=True,
        help_text="Manual corrections applied after review",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contract Parsing"
        verbose_name_plural = "Contract Parsings"
        indexes = [
            models.Index(fields=["document"]),
            models.Index(fields=["status"]),
            models.Index(fields=["model_version"]),
        ]

    def __str__(self):
        return f"Parsing of {self.document} - {self.get_status_display()}"

    @property
    def avg_confidence(self):
        """Calculate average confidence across all extracted fields."""
        scores = self.confidence_scores
        if scores and isinstance(scores, dict):
            values = [v for v in scores.values() if isinstance(v, (int, float))]
            return sum(values) / len(values) if values else 0
        return 0
