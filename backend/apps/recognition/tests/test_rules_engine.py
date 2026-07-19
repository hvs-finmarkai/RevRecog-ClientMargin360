from decimal import Decimal
from unittest import TestCase

from apps.recognition.rules_engine import (
    ASC606Engine,
    BillingRuleEngine,
    PerformanceObligation,
    RevenueTimingType,
    RecognitionStatus,
)


class SimpleObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class Step1ContractIdentificationTests(TestCase):
    def setUp(self):
        self.engine = ASC606Engine()

    def test_step1_valid_contract(self):
        client = SimpleObj(tier='enterprise', payment_history_score=Decimal('0.95'))
        contract = SimpleObj(
            is_signed=True,
            scope_of_work='Deliver software platform',
            payment_terms='net_30',
            billing_model='fixed_price',
            total_value=Decimal('5000000'),
            client=client,
        )
        result = self.engine.step1_identify_contract(contract)
        self.assertTrue(result.is_valid_contract)
        self.assertTrue(result.approval_exists)
        self.assertTrue(result.rights_identifiable)
        self.assertTrue(result.payment_terms_identifiable)
        self.assertTrue(result.commercial_substance)
        self.assertTrue(result.collectability_probable)

    def test_step1_invalid_contract(self):
        client = SimpleObj(tier='startup', payment_history_score=Decimal('0.40'))
        contract = SimpleObj(
            is_signed=False,
            scope_of_work=None,
            payment_terms=None,
            billing_model=None,
            total_value=Decimal('0'),
            client=client,
        )
        result = self.engine.step1_identify_contract(contract)
        self.assertFalse(result.is_valid_contract)
        self.assertFalse(result.approval_exists)


class Step3TransactionPriceTests(TestCase):
    def setUp(self):
        self.engine = ASC606Engine()

    def test_step3_fixed_price(self):
        client = SimpleObj(tier='enterprise', payment_history_score=Decimal('0.95'))
        contract = SimpleObj(
            total_value=Decimal('5000000'),
            fixed_price=Decimal('5000000'),
            variable_components=[],
            payment_advance_months=0,
            client=client,
        )
        result = self.engine.step3_determine_price(contract)
        self.assertEqual(result.fixed_amount, Decimal('5000000'))
        self.assertEqual(result.total_price, Decimal('5000000'))

    def test_step3_variable_consideration(self):
        client = SimpleObj(tier='enterprise', payment_history_score=Decimal('0.95'))
        variable_comp = SimpleObj(
            type='performance_bonus',
            estimated_amount=Decimal('500000'),
            probability=Decimal('0.80'),
        )
        contract = SimpleObj(
            total_value=Decimal('5000000'),
            fixed_price=Decimal('5000000'),
            variable_components=[variable_comp],
            payment_advance_months=0,
            experience_level='moderate',
            client=client,
        )
        result = self.engine.step3_determine_price(contract)
        self.assertGreater(result.variable_amount, Decimal('0'))
        self.assertGreater(result.total_price, Decimal('5000000'))


class Step5RevenueRecognitionTests(TestCase):
    def setUp(self):
        self.engine = ASC606Engine()

    def test_step5_over_time_recognition(self):
        obligation = PerformanceObligation(
            obligation_id='OB-001',
            description='Software development',
            is_distinct=True,
            is_series=False,
            standalone_selling_price=Decimal('1000000'),
            timing_type=RevenueTimingType.OVER_TIME,
            progress_measure='input',
            completion_percentage=Decimal('50'),
        )
        result = self.engine.step5_recognize_revenue(obligation, '2024-06')
        self.assertEqual(result.cumulative_recognized, Decimal('500000.00'))
        self.assertEqual(result.remaining_amount, Decimal('500000.00'))
        self.assertEqual(result.status, RecognitionStatus.PARTIAL)

    def test_step5_point_in_time_not_complete(self):
        obligation = PerformanceObligation(
            obligation_id='OB-002',
            description='License delivery',
            is_distinct=True,
            is_series=False,
            standalone_selling_price=Decimal('2000000'),
            timing_type=RevenueTimingType.POINT_IN_TIME,
            completion_percentage=Decimal('50'),
        )
        result = self.engine.step5_recognize_revenue(obligation, '2024-06')
        self.assertEqual(result.amount_recognized, Decimal('0'))
        self.assertEqual(result.status, RecognitionStatus.DEFERRED)

    def test_step5_point_in_time_complete(self):
        obligation = PerformanceObligation(
            obligation_id='OB-003',
            description='License delivery',
            is_distinct=True,
            is_series=False,
            standalone_selling_price=Decimal('2000000'),
            timing_type=RevenueTimingType.POINT_IN_TIME,
            completion_percentage=Decimal('100'),
        )
        result = self.engine.step5_recognize_revenue(obligation, '2024-06')
        self.assertEqual(result.amount_recognized, Decimal('2000000'))
        self.assertEqual(result.status, RecognitionStatus.RECOGNIZED)


class TMBillingTests(TestCase):
    def setUp(self):
        self.engine = BillingRuleEngine()

    def test_tm_billing(self):
        contract = SimpleObj(
            currency='INR',
            hourly_rate=Decimal('2500'),
            monthly_cap=Decimal('0'),
            tax_rate=Decimal('0.18'),
        )
        timesheets = [
            SimpleObj(hours=Decimal('40'), rate=Decimal('2500'), resource_name='Dev A'),
            SimpleObj(hours=Decimal('35'), rate=Decimal('2500'), resource_name='Dev B'),
        ]
        result = self.engine.evaluate_tm_billing(contract, timesheets)
        expected_gross = Decimal('40') * Decimal('2500') + Decimal('35') * Decimal('2500')
        self.assertEqual(result.gross_amount, expected_gross)
        self.assertEqual(result.currency, 'INR')


class MilestoneBillingTests(TestCase):
    def setUp(self):
        self.engine = BillingRuleEngine()

    def test_milestone_billing(self):
        contract = SimpleObj(
            currency='INR',
            tax_rate=Decimal('0.18'),
        )
        milestones = [
            SimpleObj(is_completed=True, is_approved=True, amount=Decimal('500000'), description='Phase 1', completion_date='2024-03-01'),
            SimpleObj(is_completed=False, is_approved=False, amount=Decimal('500000'), description='Phase 2', completion_date='2024-06-01'),
            SimpleObj(is_completed=True, is_approved=True, amount=Decimal('300000'), description='Phase 3', completion_date='2024-04-15'),
        ]
        result = self.engine.evaluate_milestone_billing(contract, milestones)
        self.assertEqual(result.gross_amount, Decimal('800000'))
        self.assertEqual(len(result.line_items), 2)
