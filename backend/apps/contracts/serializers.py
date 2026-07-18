"""
Contracts app serializers - ContractListSerializer, ContractDetailSerializer,
ContractCreateSerializer, ContractTermSerializer, PerformanceObligationSerializer,
ContractDocumentSerializer, ContractAmendmentSerializer, ContractVersionSerializer.
"""

from django.utils import timezone
from rest_framework import serializers

from .models import (
    Contract,
    ContractAmendment,
    ContractDocument,
    ContractTerm,
    ContractVersion,
    PerformanceObligation,
)


# =============================================================================
# Contract Term Serializer
# =============================================================================

class ContractTermSerializer(serializers.ModelSerializer):
    """Serializer for ContractTerm model."""

    term_type_display = serializers.CharField(
        source="get_term_type_display", read_only=True
    )
    escalation_frequency_display = serializers.CharField(
        source="get_escalation_frequency_display", read_only=True
    )

    class Meta:
        model = ContractTerm
        fields = [
            "id", "contract", "term_type", "term_type_display",
            "description", "value", "unit",
            "escalation_rate", "escalation_frequency",
            "escalation_frequency_display",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        escalation_rate = attrs.get("escalation_rate")
        escalation_frequency = attrs.get("escalation_frequency")

        if escalation_rate and not escalation_frequency:
            raise serializers.ValidationError(
                {"escalation_frequency": "Escalation frequency is required when escalation rate is set."}
            )
        return attrs


# =============================================================================
# Performance Obligation Serializer
# =============================================================================

class PerformanceObligationSerializer(serializers.ModelSerializer):
    """Serializer for PerformanceObligation model."""

    recognition_pattern_display = serializers.CharField(
        source="get_recognition_pattern_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = PerformanceObligation
        fields = [
            "id", "contract", "description",
            "standalone_price", "allocation_amount",
            "recognition_pattern", "recognition_pattern_display",
            "status", "status_display",
            "satisfaction_criteria", "expected_completion_date",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        allocation_amount = attrs.get("allocation_amount", 0)
        standalone_price = attrs.get("standalone_price", 0)

        if allocation_amount > standalone_price * 2:
            raise serializers.ValidationError(
                {"allocation_amount": "Allocation amount seems unusually high relative to standalone price."}
            )
        return attrs


# =============================================================================
# Contract Document Serializer
# =============================================================================

class ContractDocumentSerializer(serializers.ModelSerializer):
    """Serializer for ContractDocument model."""

    document_type_display = serializers.CharField(
        source="get_document_type_display", read_only=True
    )
    reviewed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ContractDocument
        fields = [
            "id", "contract", "document_type", "document_type_display",
            "file_url", "file_name", "file_size",
            "ocr_text", "extracted_data", "confidence_score",
            "reviewed_by", "reviewed_by_name", "reviewed_at",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "ocr_text", "extracted_data", "confidence_score",
            "reviewed_at", "created_at", "updated_at",
        ]

    def get_reviewed_by_name(self, obj):
        if obj.reviewed_by:
            return obj.reviewed_by.get_full_name()
        return None


# =============================================================================
# Contract Amendment Serializer
# =============================================================================

class ContractAmendmentSerializer(serializers.ModelSerializer):
    """Serializer for ContractAmendment model."""

    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = ContractAmendment
        fields = [
            "id", "contract", "amendment_number", "description",
            "effective_date", "value_change", "new_terms",
            "status", "status_display",
            "approved_by", "approved_by_name", "approved_at",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "approved_by", "approved_at", "created_at", "updated_at",
        ]

    def get_approved_by_name(self, obj):
        if obj.approved_by:
            return obj.approved_by.get_full_name()
        return None

    def validate_effective_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "Effective date cannot be in the past."
            )
        return value


# =============================================================================
# Contract Version Serializer
# =============================================================================

class ContractVersionSerializer(serializers.ModelSerializer):
    """Serializer for ContractVersion model."""

    class Meta:
        model = ContractVersion
        fields = [
            "id", "contract", "version_number",
            "changes_summary", "effective_date", "snapshot_data",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# =============================================================================
# Contract List Serializer (Read - Lightweight)
# =============================================================================

class ContractListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for contract list views."""

    client_name = serializers.CharField(source="client.name", read_only=True)
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    billing_model_display = serializers.CharField(
        source="get_billing_model_display", read_only=True
    )
    is_active = serializers.BooleanField(read_only=True)
    remaining_value = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = Contract
        fields = [
            "id", "contract_number", "title", "client", "client_name",
            "billing_model", "billing_model_display",
            "currency", "total_value", "monthly_value",
            "start_date", "end_date", "status", "status_display",
            "is_active", "remaining_value",
            "asc606_compliant", "created_at",
        ]
        read_only_fields = ["id", "contract_number", "created_at"]


# =============================================================================
# Contract Detail Serializer (Read - Full)
# =============================================================================

class ContractDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for contract with nested objects."""

    client_name = serializers.CharField(source="client.name", read_only=True)
    organization_name = serializers.CharField(
        source="organization.name", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    billing_model_display = serializers.CharField(
        source="get_billing_model_display", read_only=True
    )
    payment_terms_display = serializers.CharField(
        source="get_payment_terms_display", read_only=True
    )
    is_active = serializers.BooleanField(read_only=True)
    remaining_value = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    terms = ContractTermSerializer(many=True, read_only=True)
    performance_obligations = PerformanceObligationSerializer(many=True, read_only=True)
    documents = ContractDocumentSerializer(many=True, read_only=True)
    amendments = ContractAmendmentSerializer(many=True, read_only=True)
    versions = ContractVersionSerializer(many=True, read_only=True)

    class Meta:
        model = Contract
        fields = [
            "id", "organization", "organization_name",
            "client", "client_name", "contract_number", "title",
            "billing_model", "billing_model_display",
            "currency", "total_value", "monthly_value",
            "start_date", "end_date", "auto_renewal", "renewal_term_months",
            "payment_terms", "payment_terms_display",
            "status", "status_display", "is_active",
            "asc606_compliant", "signed_date", "document_url",
            "description", "notes", "remaining_value",
            "terms", "performance_obligations", "documents",
            "amendments", "versions",
            "created_at", "updated_at", "created_by", "updated_by",
        ]
        read_only_fields = [
            "id", "contract_number", "created_at", "updated_at",
            "created_by", "updated_by",
        ]


# =============================================================================
# Contract Create Serializer (Write)
# =============================================================================

class ContractCreateSerializer(serializers.ModelSerializer):
    """Write serializer for creating/updating contracts with nested writes."""

    terms = ContractTermSerializer(many=True, required=False)
    performance_obligations = PerformanceObligationSerializer(many=True, required=False)

    class Meta:
        model = Contract
        fields = [
            "id", "organization", "client", "title",
            "billing_model", "currency", "total_value", "monthly_value",
            "start_date", "end_date", "auto_renewal", "renewal_term_months",
            "payment_terms", "status", "asc606_compliant",
            "signed_date", "document_url", "description", "notes",
            "terms", "performance_obligations",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError(
                {"end_date": "End date must be after start date."}
            )

        total_value = attrs.get("total_value", 0)
        if total_value <= 0:
            raise serializers.ValidationError(
                {"total_value": "Total value must be greater than zero."}
            )

        return attrs

    def create(self, validated_data):
        terms_data = validated_data.pop("terms", [])
        obligations_data = validated_data.pop("performance_obligations", [])

        contract = Contract.objects.create(**validated_data)

        for term_data in terms_data:
            term_data.pop("contract", None)
            ContractTerm.objects.create(contract=contract, **term_data)

        for obligation_data in obligations_data:
            obligation_data.pop("contract", None)
            PerformanceObligation.objects.create(contract=contract, **obligation_data)

        return contract

    def update(self, instance, validated_data):
        terms_data = validated_data.pop("terms", None)
        obligations_data = validated_data.pop("performance_obligations", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if terms_data is not None:
            instance.terms.all().delete()
            for term_data in terms_data:
                term_data.pop("contract", None)
                ContractTerm.objects.create(contract=instance, **term_data)

        if obligations_data is not None:
            instance.performance_obligations.all().delete()
            for obligation_data in obligations_data:
                obligation_data.pop("contract", None)
                PerformanceObligation.objects.create(contract=instance, **obligation_data)

        return instance
