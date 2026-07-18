from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOrganizationMember(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.organization is not None
        )

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        user_org = request.user.organization
        if not user_org:
            return False
        if hasattr(obj, "organization_id"):
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


class IsFinanceManager(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.role:
            return False
        return request.user.role.name == "Finance Manager"


class IsAccountsExecutive(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.role:
            return False
        return request.user.role.name == "Accounts Executive"


class IsOperationsHead(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.role:
            return False
        return request.user.role.name == "Operations Head"


class IsClientPartner(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.role:
            return False
        return request.user.role.name == "Client Partner"

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if hasattr(obj, "client") and hasattr(obj.client, "assigned_partner_id"):
            return obj.client.assigned_partner_id == request.user.id
        return True


class CanManageContracts(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.role:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role.name in ["Admin", "Finance Manager"]


class CanManageInvoices(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.role:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role.name in ["Admin", "Finance Manager", "Accounts Executive"]


class CanViewProfitability(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class CanManageLeakage(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.role:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.role.name in ["Admin", "Finance Manager"]


class CanApproveInvoice(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.role:
            return False
        return request.user.role.name in ["Admin", "Finance Manager"]

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if hasattr(obj, "created_by_id") and obj.created_by_id == request.user.id:
            return False
        if hasattr(obj, "created_by") and obj.created_by == request.user:
            return False
        return True


class CanDeleteRecord(BasePermission):
    def has_permission(self, request, view):
        if request.method != "DELETE":
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.role:
            return False
        return request.user.role.name == "Admin"


class IsSameOrganization(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        user_org = request.user.organization
        if not user_org:
            return False
        obj_org_id = None
        if hasattr(obj, "organization_id"):
            obj_org_id = obj.organization_id
        elif hasattr(obj, "organization"):
            obj_org_id = obj.organization.id if obj.organization else None
        elif hasattr(obj, "client") and hasattr(obj.client, "organization_id"):
            obj_org_id = obj.client.organization_id
        elif hasattr(obj, "contract") and obj.contract and hasattr(obj.contract, "organization_id"):
            obj_org_id = obj.contract.organization_id
        elif hasattr(obj, "invoice") and hasattr(obj.invoice, "organization_id"):
            obj_org_id = obj.invoice.organization_id
        if obj_org_id is None:
            return False
        return obj_org_id == user_org.id
