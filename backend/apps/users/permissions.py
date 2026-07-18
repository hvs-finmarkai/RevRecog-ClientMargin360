from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizationMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        user_org = request.user.organization
        if not user_org:
            return False
        if hasattr(obj, "organization_id"):
            return obj.organization_id == user_org.id
        if hasattr(obj, "organization"):
            return obj.organization_id == user_org.id
        if hasattr(obj, "client") and hasattr(obj.client, "organization_id"):
            return obj.client.organization_id == user_org.id
        if hasattr(obj, "contract") and obj.contract and hasattr(obj.contract, "organization_id"):
            return obj.contract.organization_id == user_org.id
        if hasattr(obj, "invoice") and hasattr(obj.invoice, "organization_id"):
            return obj.invoice.organization_id == user_org.id
        return False


class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.role:
            return False
        return request.user.role.name == "Admin"


class IsFinanceRole(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.role:
            return False
        return request.user.role.name in ["Admin", "Finance Manager"]


class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class HasContractAccess(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.role:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role.name in [
            "Admin",
            "Finance Manager",
            "Operations Head",
            "Client Partner",
        ]

    def has_object_permission(self, request, view, obj):
        if not request.user.organization:
            return False
        org_id = request.user.organization.id
        if hasattr(obj, "organization_id"):
            return obj.organization_id == org_id
        if hasattr(obj, "contract") and obj.contract:
            return obj.contract.organization_id == org_id
        return False


class HasInvoiceAccess(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.role:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role.name in [
            "Admin",
            "Finance Manager",
            "Accounts Executive",
        ]

    def has_object_permission(self, request, view, obj):
        if not request.user.organization:
            return False
        org_id = request.user.organization.id
        if hasattr(obj, "organization_id"):
            return obj.organization_id == org_id
        if hasattr(obj, "invoice") and obj.invoice:
            return obj.invoice.organization_id == org_id
        return False
