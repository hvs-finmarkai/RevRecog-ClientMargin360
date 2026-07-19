from decimal import Decimal
from unittest import TestCase

from apps.invoices.approval_engine import (
    ApprovalEngine,
    ApprovalRole,
    ApprovalStatus,
    UnauthorizedApproverError,
)


class SimpleObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class ApprovalChainTests(TestCase):
    def setUp(self):
        self.engine = ApprovalEngine()

    def test_auto_approve_small_amount(self):
        invoice = SimpleObj(
            id='inv-001',
            total_amount=Decimal('500000'),
            invoice_type='standard',
            is_first_invoice=False,
            client=SimpleObj(invoice_count=5),
        )
        chain = self.engine.get_approval_chain(invoice)
        self.assertEqual(len(chain), 1)
        self.assertEqual(chain[0].role, ApprovalRole.AUTO)
        self.assertEqual(chain[0].status, ApprovalStatus.AUTO_APPROVED)

    def test_finance_manager_approval_required(self):
        invoice = SimpleObj(
            id='inv-002',
            total_amount=Decimal('2000000'),
            invoice_type='standard',
            is_first_invoice=False,
            client=SimpleObj(invoice_count=5),
        )
        chain = self.engine.get_approval_chain(invoice)
        self.assertEqual(len(chain), 1)
        self.assertEqual(chain[0].role, ApprovalRole.FINANCE_MANAGER)

    def test_multi_level_approval(self):
        invoice = SimpleObj(
            id='inv-003',
            total_amount=Decimal('15000000'),
            invoice_type='standard',
            is_first_invoice=False,
            client=SimpleObj(invoice_count=10),
        )
        chain = self.engine.get_approval_chain(invoice)
        self.assertEqual(len(chain), 3)
        self.assertEqual(chain[0].role, ApprovalRole.FINANCE_MANAGER)
        self.assertEqual(chain[1].role, ApprovalRole.OPERATIONS_HEAD)
        self.assertEqual(chain[2].role, ApprovalRole.CFO)

    def test_first_invoice_cfo_required(self):
        invoice = SimpleObj(
            id='inv-004',
            total_amount=Decimal('2000000'),
            invoice_type='standard',
            is_first_invoice=True,
            client=SimpleObj(invoice_count=0),
        )
        chain = self.engine.get_approval_chain(invoice)
        self.assertTrue(any(step.role == ApprovalRole.CFO for step in chain))


class ApprovalActionTests(TestCase):
    def setUp(self):
        self.engine = ApprovalEngine()

    def test_approve_authorized(self):
        invoice = SimpleObj(
            id='inv-005',
            total_amount=Decimal('2000000'),
            invoice_type='standard',
            is_first_invoice=False,
            client=SimpleObj(invoice_count=5),
            approved_steps_count=0,
        )
        approver = SimpleObj(
            id='user-fm-1',
            role='finance_manager',
            roles=['finance_manager'],
        )
        result = self.engine.approve(invoice, approver)
        self.assertEqual(result.status, ApprovalStatus.APPROVED)
        self.assertEqual(result.approver_id, 'user-fm-1')

    def test_approve_unauthorized(self):
        invoice = SimpleObj(
            id='inv-006',
            total_amount=Decimal('5000000'),
            invoice_type='standard',
            is_first_invoice=False,
            client=SimpleObj(invoice_count=5),
            approved_steps_count=0,
        )
        approver = SimpleObj(
            id='user-ae-1',
            role='accounts_exec',
            roles=['accounts_exec'],
        )
        with self.assertRaises(UnauthorizedApproverError):
            self.engine.approve(invoice, approver)
