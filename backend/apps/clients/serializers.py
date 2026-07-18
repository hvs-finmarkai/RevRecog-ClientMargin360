"""
Clients app serializers - ClientListSerializer, ClientDetailSerializer,
ClientCreateSerializer, ClientContactSerializer, ClientAddressSerializer,
ClientSegmentSerializer, ClientHealthSerializer.
"""

from rest_framework import serializers

from .models import Client, ClientAddress, ClientContact, ClientSegment


# =============================================================================
# Client Segment Serializer
# =============================================================================

class ClientSegmentSerializer(serializers.ModelSerializer):
    """Serializer for ClientSegment model."""

    client_count = serializers.SerializerMethodField()

    class Meta:
        model = ClientSegment
        fields = [
            "id", "name", "description", "criteria",
            "min_revenue", "max_revenue", "color_code",
            "client_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_client_count(self, obj):
        return obj.clients.filter(is_deleted=False).count()

    def validate(self, attrs):
        min_revenue = attrs.get("min_revenue", 0)
        max_revenue = attrs.get("max_revenue")
        if max_revenue is not None and max_revenue <= min_revenue:
            raise serializers.ValidationError(
                {"max_revenue": "Maximum revenue must be greater than minimum revenue."}
            )
        return attrs


# =============================================================================
# Client Contact Serializer
# =============================================================================

class ClientContactSerializer(serializers.ModelSerializer):
    """Serializer for ClientContact model."""

    class Meta:
        model = ClientContact
        fields = [
            "id", "client", "name", "designation", "email",
            "phone", "is_primary", "is_billing_contact",
            "department", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        is_primary = attrs.get("is_primary", False)
        client = attrs.get("client") or (self.instance.client if self.instance else None)

        if is_primary and client:
            existing_primary = ClientContact.objects.filter(
                client=client, is_primary=True, is_deleted=False
            )
            if self.instance:
                existing_primary = existing_primary.exclude(pk=self.instance.pk)
            if existing_primary.exists():
                raise serializers.ValidationError(
                    {"is_primary": "This client already has a primary contact. Update the existing one first."}
                )
        return attrs


# =============================================================================
# Client Address Serializer
# =============================================================================

class ClientAddressSerializer(serializers.ModelSerializer):
    """Serializer for ClientAddress model."""

    address_type_display = serializers.CharField(
        source="get_address_type_display", read_only=True
    )
    full_address = serializers.CharField(read_only=True)

    class Meta:
        model = ClientAddress
        fields = [
            "id", "client", "address_type", "address_type_display",
            "line1", "line2", "city", "state", "pincode", "country",
            "gstin", "is_default", "full_address",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# =============================================================================
# Client Health Serializer
# =============================================================================

class ClientHealthSerializer(serializers.Serializer):
    """Read-only serializer for client health metrics."""

    client_id = serializers.UUIDField(read_only=True)
    client_name = serializers.CharField(read_only=True)
    health_score = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )
    risk_score = serializers.DecimalField(
        max_digits=5, decimal_places=2, read_only=True
    )
    active_contracts = serializers.IntegerField(read_only=True)
    total_revenue = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    outstanding_amount = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    overdue_invoices = serializers.IntegerField(read_only=True)
    avg_payment_days = serializers.DecimalField(
        max_digits=7, decimal_places=2, read_only=True
    )
    trend = serializers.CharField(read_only=True)


# =============================================================================
# Client List Serializer (Read - Lightweight)
# =============================================================================

class ClientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for client list views."""

    segment_name = serializers.CharField(
        source="segment.name", read_only=True, default=None
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    industry_display = serializers.CharField(
        source="get_industry_display", read_only=True
    )
    active_contracts_count = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            "id", "name", "legal_name", "industry", "industry_display",
            "segment", "segment_name", "status", "status_display",
            "city", "state", "country",
            "contact_person", "email", "phone",
            "health_score", "risk_score", "credit_limit",
            "payment_terms", "active_contracts_count",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_active_contracts_count(self, obj):
        return obj.contracts.filter(
            status="active", is_deleted=False
        ).count()


# =============================================================================
# Client Detail Serializer (Read - Full)
# =============================================================================

class ClientDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer for client with nested objects."""

    segment_detail = ClientSegmentSerializer(source="segment", read_only=True)
    contacts = ClientContactSerializer(many=True, read_only=True)
    addresses = ClientAddressSerializer(many=True, read_only=True)
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )
    industry_display = serializers.CharField(
        source="get_industry_display", read_only=True
    )
    payment_terms_display = serializers.CharField(
        source="get_payment_terms_display", read_only=True
    )
    active_contracts_count = serializers.SerializerMethodField()
    total_contract_value = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            "id", "organization", "name", "legal_name",
            "industry", "industry_display",
            "segment", "segment_detail",
            "gstin", "pan", "address", "city", "state",
            "country", "pincode",
            "contact_person", "email", "phone", "website",
            "payment_terms", "payment_terms_display",
            "credit_limit", "risk_score", "health_score",
            "status", "status_display", "logo_url", "notes",
            "contacts", "addresses",
            "active_contracts_count", "total_contract_value",
            "created_at", "updated_at", "created_by", "updated_by",
        ]
        read_only_fields = [
            "id", "created_at", "updated_at", "created_by", "updated_by",
        ]

    def get_active_contracts_count(self, obj):
        return obj.contracts.filter(
            status="active", is_deleted=False
        ).count()

    def get_total_contract_value(self, obj):
        from django.db.models import Sum
        result = obj.contracts.filter(
            status="active", is_deleted=False
        ).aggregate(total=Sum("total_value"))
        return result["total"] or 0


# =============================================================================
# Client Create Serializer (Write)
# =============================================================================

class ClientCreateSerializer(serializers.ModelSerializer):
    """Write serializer for creating/updating clients with nested writes."""

    contacts = ClientContactSerializer(many=True, required=False)
    addresses = ClientAddressSerializer(many=True, required=False)

    class Meta:
        model = Client
        fields = [
            "id", "organization", "name", "legal_name",
            "industry", "segment", "gstin", "pan",
            "address", "city", "state", "country", "pincode",
            "contact_person", "email", "phone", "website",
            "payment_terms", "credit_limit", "status",
            "logo_url", "notes",
            "contacts", "addresses",
        ]
        read_only_fields = ["id"]

    def validate_gstin(self, value):
        if value:
            qs = Client.objects.filter(gstin=value)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    "A client with this GSTIN already exists."
                )
        return value

    def validate(self, attrs):
        credit_limit = attrs.get("credit_limit", 0)
        if credit_limit < 0:
            raise serializers.ValidationError(
                {"credit_limit": "Credit limit cannot be negative."}
            )
        return attrs

    def create(self, validated_data):
        contacts_data = validated_data.pop("contacts", [])
        addresses_data = validated_data.pop("addresses", [])

        client = Client.objects.create(**validated_data)

        for contact_data in contacts_data:
            contact_data.pop("client", None)
            ClientContact.objects.create(client=client, **contact_data)

        for address_data in addresses_data:
            address_data.pop("client", None)
            ClientAddress.objects.create(client=client, **address_data)

        return client

    def update(self, instance, validated_data):
        contacts_data = validated_data.pop("contacts", None)
        addresses_data = validated_data.pop("addresses", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if contacts_data is not None:
            instance.contacts.all().delete()
            for contact_data in contacts_data:
                contact_data.pop("client", None)
                ClientContact.objects.create(client=instance, **contact_data)

        if addresses_data is not None:
            instance.addresses.all().delete()
            for address_data in addresses_data:
                address_data.pop("client", None)
                ClientAddress.objects.create(client=instance, **address_data)

        return instance
