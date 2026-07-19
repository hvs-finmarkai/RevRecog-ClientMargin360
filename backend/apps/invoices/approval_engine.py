from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from typing import Any, Optional
from datetime import datetime
import uuid


class ApprovalError(Exception):
    pass


class UnauthorizedApproverError(ApprovalError):
    pass


class InvalidApprovalStateError(ApprovalError):
    pass


class ApprovalRole(Enum):
    FINANCE_MANAGER = "finance_manager"
    OPERATIONS_HEAD = "operations_head"
    CFO = "cfo"
    AUTO = "auto"


class ApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    AUTO_APPROVED = "auto_approved"
    CANCELLED = "cancelled"


class InvoiceType(Enum):
    STANDARD = "standard"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"
    PROFORMA = "proforma"


@dataclass
class ApprovalStep:
    step_number: int
    role: ApprovalRole
    status: ApprovalStatus = ApprovalStatus.PENDING
    approver_id: Optional[str] = None
    approved_at: Optional[datetime] = None
    notes: str = ""


@dataclass
class ApprovalRequest:
    request_id: str
    invoice_id: str
    submitted_by: str
    submitted_at: datetime
    approval_chain: list
    current_step: int = 0
    status: ApprovalStatus = ApprovalStatus.PENDING


@dataclass
class ApprovalResult:
    invoice_id: str
    approver_id: str
    step_number: int
    status: ApprovalStatus
    approved_at: datetime
    is_fully_approved: bool
    next_step: Optional[ApprovalStep] = None


@dataclass
class RejectionResult:
    invoice_id: str
    rejector_id: str
    step_number: int
    reason: str
    rejected_at: datetime
    status: ApprovalStatus = ApprovalStatus.REJECTED


AMOUNT_THRESHOLDS = {
    "auto_approve_max": Decimal("1000000"),
    "finance_manager_max": Decimal("5000000"),
    "operations_head_max": Decimal("10000000"),
    "cfo_required_above": Decimal("10000000"),
    "credit_note_cfo_threshold": Decimal("500000"),
    "first_invoice_always_cfo": True,
}


class ApprovalEngine:

    def __init__(self):
        self.thresholds = AMOUNT_THRESHOLDS

    def get_approval_chain(self, invoice: Any) -> list:
        amount = Decimal(str(getattr(invoice, 'total_amount', getattr(invoice, 'amount', 0))))
        invoice_type = getattr(invoice, 'invoice_type', InvoiceType.STANDARD)
        if isinstance(invoice_type, str):
            invoice_type = InvoiceType(invoice_type) if invoice_type in [e.value for e in InvoiceType] else InvoiceType.STANDARD
        client = getattr(invoice, 'client', None)
        is_first_invoice = getattr(invoice, 'is_first_invoice', False)
        if not is_first_invoice and client:
            is_first_invoice = getattr(client, 'invoice_count', 1) <= 1

        chain = []

        if invoice_type == InvoiceType.CREDIT_NOTE and amount > self.thresholds["credit_note_cfo_threshold"]:
            chain.append(ApprovalStep(step_number=1, role=ApprovalRole.FINANCE_MANAGER))
            chain.append(ApprovalStep(step_number=2, role=ApprovalRole.CFO))
            return chain

        if is_first_invoice and self.thresholds["first_invoice_always_cfo"]:
            chain.append(ApprovalStep(step_number=1, role=ApprovalRole.FINANCE_MANAGER))
            chain.append(ApprovalStep(step_number=2, role=ApprovalRole.CFO))
            return chain

        if amount < self.thresholds["auto_approve_max"]:
            chain.append(ApprovalStep(step_number=1, role=ApprovalRole.AUTO, status=ApprovalStatus.AUTO_APPROVED))
            return chain

        if amount <= self.thresholds["finance_manager_max"]:
            chain.append(ApprovalStep(step_number=1, role=ApprovalRole.FINANCE_MANAGER))
            return chain

        if amount <= self.thresholds["operations_head_max"]:
            chain.append(ApprovalStep(step_number=1, role=ApprovalRole.FINANCE_MANAGER))
            chain.append(ApprovalStep(step_number=2, role=ApprovalRole.OPERATIONS_HEAD))
            return chain

        chain.append(ApprovalStep(step_number=1, role=ApprovalRole.FINANCE_MANAGER))
        chain.append(ApprovalStep(step_number=2, role=ApprovalRole.OPERATIONS_HEAD))
        chain.append(ApprovalStep(step_number=3, role=ApprovalRole.CFO))
        return chain

    def submit_for_approval(self, invoice: Any, submitted_by: str) -> ApprovalRequest:
        if not invoice:
            raise ApprovalError("Invoice is required")

        invoice_id = str(getattr(invoice, 'id', getattr(invoice, 'invoice_id', '')))
        if not invoice_id:
            raise ApprovalError("Invoice must have an ID")

        chain = self.get_approval_chain(invoice)
        request_id = str(uuid.uuid4())

        request = ApprovalRequest(
            request_id=request_id,
            invoice_id=invoice_id,
            submitted_by=submitted_by,
            submitted_at=datetime.utcnow(),
            approval_chain=chain,
            current_step=0,
            status=ApprovalStatus.PENDING
        )

        if chain and chain[0].status == ApprovalStatus.AUTO_APPROVED:
            request.status = ApprovalStatus.AUTO_APPROVED
            request.current_step = len(chain)

        return request

    def approve(self, invoice: Any, approver: Any) -> ApprovalResult:
        invoice_id = str(getattr(invoice, 'id', getattr(invoice, 'invoice_id', '')))
        approver_id = str(getattr(approver, 'id', getattr(approver, 'user_id', str(approver))))
        approver_role = getattr(approver, 'role', None)
        if isinstance(approver_role, str):
            try:
                approver_role = ApprovalRole(approver_role)
            except ValueError:
                approver_role = None

        chain = self.get_approval_chain(invoice)
        current_step = self._get_current_pending_step(chain, invoice)

        if current_step is None:
            raise InvalidApprovalStateError(f"No pending approval steps for invoice {invoice_id}")

        if approver_role and approver_role != current_step.role:
            raise UnauthorizedApproverError(
                f"Approver with role {approver_role.value} is not authorized for step requiring {current_step.role.value}"
            )

        if not approver_role:
            if not self._is_approver_authorized(approver, current_step.role):
                raise UnauthorizedApproverError(
                    f"Approver {approver_id} is not authorized for {current_step.role.value} approval"
                )

        current_step.status = ApprovalStatus.APPROVED
        current_step.approver_id = approver_id
        current_step.approved_at = datetime.utcnow()

        next_step = self._get_next_step(chain, current_step.step_number)
        is_fully_approved = next_step is None

        return ApprovalResult(
            invoice_id=invoice_id,
            approver_id=approver_id,
            step_number=current_step.step_number,
            status=ApprovalStatus.APPROVED,
            approved_at=current_step.approved_at,
            is_fully_approved=is_fully_approved,
            next_step=next_step
        )

    def reject(self, invoice: Any, approver: Any, reason: str) -> RejectionResult:
        if not reason or not reason.strip():
            raise ApprovalError("Rejection reason is required")

        invoice_id = str(getattr(invoice, 'id', getattr(invoice, 'invoice_id', '')))
        approver_id = str(getattr(approver, 'id', getattr(approver, 'user_id', str(approver))))

        chain = self.get_approval_chain(invoice)
        current_step = self._get_current_pending_step(chain, invoice)

        if current_step is None:
            raise InvalidApprovalStateError(f"No pending approval steps for invoice {invoice_id}")

        return RejectionResult(
            invoice_id=invoice_id,
            rejector_id=approver_id,
            step_number=current_step.step_number,
            reason=reason.strip(),
            rejected_at=datetime.utcnow(),
            status=ApprovalStatus.REJECTED
        )

    def get_pending_approvals(self, user: Any) -> list:
        user_role = getattr(user, 'role', None)
        if isinstance(user_role, str):
            try:
                user_role = ApprovalRole(user_role)
            except ValueError:
                return []

        if user_role is None:
            return []

        pending_invoices = getattr(user, 'pending_invoices', [])
        result = []

        for invoice in pending_invoices:
            chain = self.get_approval_chain(invoice)
            current_step = self._get_current_pending_step(chain, invoice)
            if current_step and current_step.role == user_role:
                result.append(invoice)

        return result

    def _get_current_pending_step(self, chain: list, invoice: Any) -> Optional[ApprovalStep]:
        approved_count = getattr(invoice, 'approved_steps_count', 0)
        for step in chain:
            if step.step_number > approved_count and step.status == ApprovalStatus.PENDING:
                return step
        return None

    def _get_next_step(self, chain: list, current_step_number: int) -> Optional[ApprovalStep]:
        for step in chain:
            if step.step_number > current_step_number and step.status == ApprovalStatus.PENDING:
                return step
        return None

    def _is_approver_authorized(self, approver: Any, required_role: ApprovalRole) -> bool:
        approver_roles = getattr(approver, 'roles', [])
        if isinstance(approver_roles, str):
            approver_roles = [approver_roles]

        role_hierarchy = {
            ApprovalRole.CFO: [ApprovalRole.CFO],
            ApprovalRole.OPERATIONS_HEAD: [ApprovalRole.OPERATIONS_HEAD, ApprovalRole.CFO],
            ApprovalRole.FINANCE_MANAGER: [ApprovalRole.FINANCE_MANAGER, ApprovalRole.OPERATIONS_HEAD, ApprovalRole.CFO],
        }

        authorized_roles = role_hierarchy.get(required_role, [required_role])

        for role in approver_roles:
            if isinstance(role, str):
                try:
                    role = ApprovalRole(role)
                except ValueError:
                    continue
            if role in authorized_roles:
                return True

        return False
