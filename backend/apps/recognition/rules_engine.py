from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum
from typing import Any, Optional
from datetime import date, datetime


class RevenueTimingType(Enum):
    OVER_TIME = "over_time"
    POINT_IN_TIME = "point_in_time"


class AllocationMethod(Enum):
    STANDALONE_SELLING_PRICE = "standalone_selling_price"
    RESIDUAL = "residual"
    ADJUSTED_MARKET = "adjusted_market"


class ModificationType(Enum):
    PROSPECTIVE = "prospective"
    CUMULATIVE_CATCH_UP = "cumulative_catch_up"
    SEPARATE_CONTRACT = "separate_contract"


class VariableConsiderationMethod(Enum):
    EXPECTED_VALUE = "expected_value"
    MOST_LIKELY_AMOUNT = "most_likely_amount"


class BillingModelType(Enum):
    TIME_AND_MATERIAL = "time_and_material"
    MILESTONE = "milestone"
    RETAINER = "retainer"
    PERFORMANCE = "performance"
    HYBRID = "hybrid"


class RecognitionStatus(Enum):
    RECOGNIZED = "recognized"
    DEFERRED = "deferred"
    PARTIAL = "partial"
    NOT_RECOGNIZED = "not_recognized"


class ConstraintLevel(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


@dataclass
class ContractIdentification:
    is_valid_contract: bool
    approval_exists: bool
    rights_identifiable: bool
    payment_terms_identifiable: bool
    commercial_substance: bool
    collectability_probable: bool
    reasons: list = field(default_factory=list)


@dataclass
class PerformanceObligation:
    obligation_id: str
    description: str
    is_distinct: bool
    is_series: bool
    standalone_selling_price: Decimal
    timing_type: RevenueTimingType
    progress_measure: str = ""
    completion_percentage: Decimal = Decimal("0")


@dataclass
class TransactionPrice:
    fixed_amount: Decimal
    variable_amount: Decimal
    constraint_applied: bool
    constraint_level: ConstraintLevel
    total_price: Decimal
    financing_component: Decimal = Decimal("0")
    non_cash_consideration: Decimal = Decimal("0")
    payable_to_customer: Decimal = Decimal("0")
    estimation_method: VariableConsiderationMethod = VariableConsiderationMethod.EXPECTED_VALUE


@dataclass
class AllocationResult:
    obligation_id: str
    allocated_amount: Decimal
    allocation_percentage: Decimal
    method_used: AllocationMethod


@dataclass
class RecognitionResult:
    obligation_id: str
    period: str
    amount_recognized: Decimal
    cumulative_recognized: Decimal
    remaining_amount: Decimal
    status: RecognitionStatus
    timing_type: RevenueTimingType


@dataclass
class BillingAmount:
    gross_amount: Decimal
    tax_amount: Decimal
    net_amount: Decimal
    currency: str
    billing_model: BillingModelType
    line_items: list = field(default_factory=list)
    adjustments: list = field(default_factory=list)


BUSINESS_RULES = {
    "timing_rules": [
        {"id": "TR001", "name": "output_method_services", "condition": "service_delivery_continuous", "timing": "over_time", "measure": "output"},
        {"id": "TR002", "name": "input_method_construction", "condition": "asset_no_alternative_use", "timing": "over_time", "measure": "input"},
        {"id": "TR003", "name": "point_in_time_license", "condition": "right_to_use_license", "timing": "point_in_time", "measure": "transfer"},
        {"id": "TR004", "name": "over_time_right_to_access", "condition": "right_to_access_license", "timing": "over_time", "measure": "time"},
        {"id": "TR005", "name": "customer_controls_wip", "condition": "customer_controls_asset", "timing": "over_time", "measure": "input"},
        {"id": "TR006", "name": "no_alternative_use_payment_right", "condition": "enforceable_payment_right", "timing": "over_time", "measure": "input"},
        {"id": "TR007", "name": "milestone_completion", "condition": "deliverable_at_point", "timing": "point_in_time", "measure": "milestone"},
        {"id": "TR008", "name": "subscription_service", "condition": "stand_ready_obligation", "timing": "over_time", "measure": "time"},
    ],
    "variable_consideration_rules": [
        {"id": "VC001", "name": "performance_bonus", "method": "most_likely_amount", "threshold": Decimal("0.75")},
        {"id": "VC002", "name": "volume_discount", "method": "expected_value", "threshold": Decimal("0.50")},
        {"id": "VC003", "name": "penalty_clause", "method": "most_likely_amount", "threshold": Decimal("0.80")},
        {"id": "VC004", "name": "success_fee", "method": "most_likely_amount", "threshold": Decimal("0.60")},
        {"id": "VC005", "name": "royalty_based", "method": "expected_value", "threshold": Decimal("0.50")},
        {"id": "VC006", "name": "tiered_pricing", "method": "expected_value", "threshold": Decimal("0.65")},
        {"id": "VC007", "name": "refund_liability", "method": "expected_value", "threshold": Decimal("0.70")},
        {"id": "VC008", "name": "price_concession", "method": "most_likely_amount", "threshold": Decimal("0.85")},
    ],
    "constraint_rules": [
        {"id": "CR001", "name": "high_susceptibility_external", "level": "high", "reversal_risk": Decimal("0.80")},
        {"id": "CR002", "name": "long_resolution_period", "level": "high", "reversal_risk": Decimal("0.75")},
        {"id": "CR003", "name": "limited_experience", "level": "medium", "reversal_risk": Decimal("0.60")},
        {"id": "CR004", "name": "broad_price_range", "level": "medium", "reversal_risk": Decimal("0.55")},
        {"id": "CR005", "name": "large_variable_outcomes", "level": "high", "reversal_risk": Decimal("0.70")},
        {"id": "CR006", "name": "established_history", "level": "low", "reversal_risk": Decimal("0.20")},
        {"id": "CR007", "name": "short_resolution_known", "level": "none", "reversal_risk": Decimal("0.10")},
    ],
    "allocation_rules": [
        {"id": "AR001", "name": "observable_price_exists", "method": "standalone_selling_price", "priority": 1},
        {"id": "AR002", "name": "similar_goods_market", "method": "adjusted_market", "priority": 2},
        {"id": "AR003", "name": "highly_variable_price", "method": "residual", "priority": 3},
        {"id": "AR004", "name": "bundled_discount_all", "method": "standalone_selling_price", "priority": 1},
        {"id": "AR005", "name": "bundled_discount_specific", "method": "residual", "priority": 2},
        {"id": "AR006", "name": "renewal_option_material_right", "method": "standalone_selling_price", "priority": 1},
    ],
    "modification_rules": [
        {"id": "MR001", "name": "distinct_additional_goods", "type": "separate_contract", "condition": "price_reflects_standalone"},
        {"id": "MR002", "name": "distinct_not_priced_standalone", "type": "prospective", "condition": "remaining_distinct"},
        {"id": "MR003", "name": "not_distinct_from_original", "type": "cumulative_catch_up", "condition": "single_obligation_partially_satisfied"},
        {"id": "MR004", "name": "scope_change_only", "type": "prospective", "condition": "additional_scope_distinct"},
        {"id": "MR005", "name": "price_reduction_existing", "type": "cumulative_catch_up", "condition": "existing_obligation_modified"},
        {"id": "MR006", "name": "termination_existing_new_contract", "type": "separate_contract", "condition": "full_termination_new_arrangement"},
    ],
    "financing_rules": [
        {"id": "FR001", "name": "significant_advance_payment", "threshold_months": 12, "adjustment_required": True},
        {"id": "FR002", "name": "payment_extended_beyond_delivery", "threshold_months": 12, "adjustment_required": True},
        {"id": "FR003", "name": "short_term_exception", "threshold_months": 12, "adjustment_required": False},
        {"id": "FR004", "name": "variable_timing_customer", "threshold_months": 0, "adjustment_required": False},
        {"id": "FR005", "name": "retainer_advance", "threshold_months": 3, "adjustment_required": False},
        {"id": "FR006", "name": "substantial_advance_over_year", "threshold_months": 12, "adjustment_required": True},
    ],
    "collectability_rules": [
        {"id": "CL001", "name": "new_client_no_history", "probability_threshold": Decimal("0.70"), "requires_review": True},
        {"id": "CL002", "name": "established_client_good_history", "probability_threshold": Decimal("0.90"), "requires_review": False},
        {"id": "CL003", "name": "client_financial_difficulty", "probability_threshold": Decimal("0.50"), "requires_review": True},
        {"id": "CL004", "name": "government_client", "probability_threshold": Decimal("0.95"), "requires_review": False},
        {"id": "CL005", "name": "startup_client", "probability_threshold": Decimal("0.60"), "requires_review": True},
        {"id": "CL006", "name": "multinational_client", "probability_threshold": Decimal("0.85"), "requires_review": False},
    ],
    "distinct_obligation_rules": [
        {"id": "DO001", "name": "capable_of_being_distinct", "criteria": "customer_can_benefit_standalone"},
        {"id": "DO002", "name": "separately_identifiable", "criteria": "not_highly_interrelated"},
        {"id": "DO003", "name": "integration_service", "criteria": "significant_integration", "is_distinct": False},
        {"id": "DO004", "name": "customization_service", "criteria": "significant_customization", "is_distinct": False},
        {"id": "DO005", "name": "series_guidance", "criteria": "same_pattern_of_transfer", "is_series": True},
        {"id": "DO006", "name": "warranty_service_type", "criteria": "beyond_assurance_warranty", "is_distinct": True},
        {"id": "DO007", "name": "training_standalone", "criteria": "available_from_others", "is_distinct": True},
    ],
}



class ASC606EngineError(Exception):
    pass


class ContractValidationError(ASC606EngineError):
    pass


class ObligationError(ASC606EngineError):
    pass


class PriceAllocationError(ASC606EngineError):
    pass


class ASC606Engine:

    def __init__(self):
        self.rules = BUSINESS_RULES

    def step1_identify_contract(self, contract: Any) -> ContractIdentification:
        approval_exists = bool(getattr(contract, 'is_signed', False) or getattr(contract, 'approval_date', None))
        rights_identifiable = bool(getattr(contract, 'scope_of_work', None) or getattr(contract, 'obligations', []))
        payment_terms_identifiable = bool(getattr(contract, 'payment_terms', None) or getattr(contract, 'billing_model', None))
        commercial_substance = bool(getattr(contract, 'total_value', Decimal("0")) > Decimal("0"))

        collectability_probable = self._assess_collectability(contract)

        is_valid = all([
            approval_exists,
            rights_identifiable,
            payment_terms_identifiable,
            commercial_substance,
            collectability_probable
        ])

        reasons = []
        if not approval_exists:
            reasons.append("Contract approval/signature not found")
        if not rights_identifiable:
            reasons.append("Rights and obligations not clearly identifiable")
        if not payment_terms_identifiable:
            reasons.append("Payment terms not identifiable")
        if not commercial_substance:
            reasons.append("Contract lacks commercial substance")
        if not collectability_probable:
            reasons.append("Collectability is not probable")

        return ContractIdentification(
            is_valid_contract=is_valid,
            approval_exists=approval_exists,
            rights_identifiable=rights_identifiable,
            payment_terms_identifiable=payment_terms_identifiable,
            commercial_substance=commercial_substance,
            collectability_probable=collectability_probable,
            reasons=reasons
        )

    def _assess_collectability(self, contract: Any) -> bool:
        client = getattr(contract, 'client', None)
        if client is None:
            return False

        client_tier = getattr(client, 'tier', 'standard')
        payment_history = getattr(client, 'payment_history_score', Decimal("0.75"))

        for rule in self.rules["collectability_rules"]:
            if client_tier == 'government' and rule["id"] == "CL004":
                return payment_history >= rule["probability_threshold"]
            if client_tier == 'enterprise' and rule["id"] == "CL002":
                return payment_history >= rule["probability_threshold"]
            if client_tier == 'startup' and rule["id"] == "CL005":
                return payment_history >= rule["probability_threshold"]

        return payment_history >= Decimal("0.70")

    def step2_identify_obligations(self, contract: Any) -> list:
        obligations_data = getattr(contract, 'obligations', [])
        if not obligations_data:
            obligations_data = getattr(contract, 'deliverables', [])

        if not obligations_data:
            raise ObligationError("No performance obligations found in contract")

        result = []
        for idx, ob in enumerate(obligations_data):
            obligation_id = getattr(ob, 'id', f"OB-{idx+1:03d}")
            description = getattr(ob, 'description', f"Obligation {idx+1}")
            ssp = Decimal(str(getattr(ob, 'standalone_selling_price', getattr(ob, 'value', 0))))

            is_distinct = self._evaluate_distinct(ob)
            is_series = self._evaluate_series(ob)
            timing_type = self._determine_timing(ob, contract)
            progress = getattr(ob, 'progress_measure', 'input')
            completion = Decimal(str(getattr(ob, 'completion_percentage', 0)))

            result.append(PerformanceObligation(
                obligation_id=str(obligation_id),
                description=description,
                is_distinct=is_distinct,
                is_series=is_series,
                standalone_selling_price=ssp,
                timing_type=timing_type,
                progress_measure=progress,
                completion_percentage=completion
            ))

        return result

    def _evaluate_distinct(self, obligation: Any) -> bool:
        ob_type = getattr(obligation, 'type', '').lower()
        for rule in self.rules["distinct_obligation_rules"]:
            if "is_distinct" in rule:
                if rule.get("criteria") == "significant_integration" and ob_type == "integration":
                    return False
                if rule.get("criteria") == "significant_customization" and ob_type == "customization":
                    return False
                if rule.get("criteria") == "available_from_others" and ob_type == "training":
                    return True
        return True

    def _evaluate_series(self, obligation: Any) -> bool:
        ob_type = getattr(obligation, 'type', '').lower()
        return ob_type in ('recurring', 'subscription', 'retainer', 'managed_service')

    def _determine_timing(self, obligation: Any, contract: Any) -> RevenueTimingType:
        billing_model = getattr(contract, 'billing_model', '').lower()
        ob_type = getattr(obligation, 'type', '').lower()

        if billing_model in ('time_and_material', 'retainer', 'subscription'):
            return RevenueTimingType.OVER_TIME
        if ob_type in ('license_right_to_use', 'product_delivery'):
            return RevenueTimingType.POINT_IN_TIME
        if ob_type in ('service', 'managed_service', 'consulting'):
            return RevenueTimingType.OVER_TIME
        if getattr(obligation, 'customer_controls_wip', False):
            return RevenueTimingType.OVER_TIME
        if getattr(obligation, 'no_alternative_use', False) and getattr(obligation, 'enforceable_payment_right', False):
            return RevenueTimingType.OVER_TIME

        return RevenueTimingType.POINT_IN_TIME

    def step3_determine_price(self, contract: Any) -> TransactionPrice:
        fixed_amount = Decimal(str(getattr(contract, 'fixed_price', getattr(contract, 'total_value', 0))))
        variable_components = getattr(contract, 'variable_components', [])

        variable_amount = Decimal("0")
        estimation_method = VariableConsiderationMethod.EXPECTED_VALUE
        constraint_applied = False
        constraint_level = ConstraintLevel.NONE

        for component in variable_components:
            comp_type = getattr(component, 'type', '')
            comp_amount = Decimal(str(getattr(component, 'estimated_amount', 0)))
            probability = Decimal(str(getattr(component, 'probability', Decimal("0.5"))))

            rule = self._find_variable_rule(comp_type)
            if rule:
                estimation_method = VariableConsiderationMethod(rule["method"])
                if estimation_method == VariableConsiderationMethod.MOST_LIKELY_AMOUNT:
                    if probability >= rule["threshold"]:
                        variable_amount += comp_amount
                else:
                    variable_amount += comp_amount * probability

        if variable_amount > Decimal("0"):
            constraint_level, constraint_applied = self._assess_constraint(contract, variable_amount)
            if constraint_applied:
                constraint_factor = self._get_constraint_factor(constraint_level)
                variable_amount = variable_amount * constraint_factor

        financing_component = self._calculate_financing_component(contract)

        total_price = fixed_amount + variable_amount - financing_component

        return TransactionPrice(
            fixed_amount=fixed_amount,
            variable_amount=variable_amount,
            constraint_applied=constraint_applied,
            constraint_level=constraint_level,
            total_price=total_price,
            financing_component=financing_component,
            estimation_method=estimation_method
        )

    def _find_variable_rule(self, comp_type: str) -> Optional[dict]:
        for rule in self.rules["variable_consideration_rules"]:
            if rule["name"] == comp_type or comp_type.lower() in rule["name"]:
                return rule
        return self.rules["variable_consideration_rules"][0]

    def _assess_constraint(self, contract: Any, variable_amount: Decimal) -> tuple:
        experience_level = getattr(contract, 'experience_level', 'moderate')
        variable_ratio = variable_amount / max(Decimal(str(getattr(contract, 'total_value', 1))), Decimal("1"))

        if variable_ratio > Decimal("0.5") or experience_level == 'limited':
            return ConstraintLevel.HIGH, True
        if variable_ratio > Decimal("0.3"):
            return ConstraintLevel.MEDIUM, True
        if variable_ratio > Decimal("0.1"):
            return ConstraintLevel.LOW, True
        return ConstraintLevel.NONE, False

    def _get_constraint_factor(self, level: ConstraintLevel) -> Decimal:
        factors = {
            ConstraintLevel.HIGH: Decimal("0.50"),
            ConstraintLevel.MEDIUM: Decimal("0.75"),
            ConstraintLevel.LOW: Decimal("0.90"),
            ConstraintLevel.NONE: Decimal("1.00"),
        }
        return factors[level]

    def _calculate_financing_component(self, contract: Any) -> Decimal:
        payment_timing_months = getattr(contract, 'payment_advance_months', 0)

        for rule in self.rules["financing_rules"]:
            if payment_timing_months >= rule["threshold_months"] and rule["adjustment_required"]:
                discount_rate = Decimal(str(getattr(contract, 'discount_rate', Decimal("0.08"))))
                total_value = Decimal(str(getattr(contract, 'total_value', 0)))
                years = Decimal(str(payment_timing_months)) / Decimal("12")
                return (total_value * discount_rate * years).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return Decimal("0")

    def step4_allocate_price(self, contract: Any, obligations: list) -> list:
        transaction_price = self.step3_determine_price(contract)
        total_ssp = sum(ob.standalone_selling_price for ob in obligations)

        if total_ssp == Decimal("0"):
            raise PriceAllocationError("Total standalone selling price is zero, cannot allocate")

        results = []
        allocated_total = Decimal("0")

        for idx, ob in enumerate(obligations):
            method = self._determine_allocation_method(ob)

            if method == AllocationMethod.STANDALONE_SELLING_PRICE:
                ratio = ob.standalone_selling_price / total_ssp
                allocated = (transaction_price.total_price * ratio).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            elif method == AllocationMethod.RESIDUAL:
                other_ssp = sum(o.standalone_selling_price for o in obligations if o.obligation_id != ob.obligation_id)
                allocated = (transaction_price.total_price - other_ssp).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            else:
                ratio = ob.standalone_selling_price / total_ssp
                market_adjustment = Decimal(str(getattr(ob, 'market_adjustment_factor', Decimal("1.0"))))
                allocated = (transaction_price.total_price * ratio * market_adjustment).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            if idx == len(obligations) - 1:
                allocated = transaction_price.total_price - allocated_total

            allocated_total += allocated
            percentage = (allocated / transaction_price.total_price * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            results.append(AllocationResult(
                obligation_id=ob.obligation_id,
                allocated_amount=allocated,
                allocation_percentage=percentage,
                method_used=method
            ))

        return results

    def _determine_allocation_method(self, obligation: Any) -> AllocationMethod:
        if getattr(obligation, 'observable_price', None):
            return AllocationMethod.STANDALONE_SELLING_PRICE
        if getattr(obligation, 'highly_variable', False):
            return AllocationMethod.RESIDUAL
        return AllocationMethod.STANDALONE_SELLING_PRICE

    def step5_recognize_revenue(self, obligation: PerformanceObligation, period: str) -> RecognitionResult:
        if obligation.timing_type == RevenueTimingType.OVER_TIME:
            return self._recognize_over_time(obligation, period)
        return self._recognize_point_in_time(obligation, period)

    def _recognize_over_time(self, obligation: PerformanceObligation, period: str) -> RecognitionResult:
        completion = obligation.completion_percentage / Decimal("100") if obligation.completion_percentage > Decimal("1") else obligation.completion_percentage
        ssp = obligation.standalone_selling_price

        cumulative = (ssp * completion).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        prior_recognized = Decimal(str(getattr(obligation, 'prior_recognized', Decimal("0"))))
        current_period = cumulative - prior_recognized
        remaining = ssp - cumulative

        if completion >= Decimal("1"):
            status = RecognitionStatus.RECOGNIZED
        elif completion > Decimal("0"):
            status = RecognitionStatus.PARTIAL
        else:
            status = RecognitionStatus.NOT_RECOGNIZED

        return RecognitionResult(
            obligation_id=obligation.obligation_id,
            period=period,
            amount_recognized=current_period,
            cumulative_recognized=cumulative,
            remaining_amount=remaining,
            status=status,
            timing_type=RevenueTimingType.OVER_TIME
        )

    def _recognize_point_in_time(self, obligation: PerformanceObligation, period: str) -> RecognitionResult:
        is_transferred = obligation.completion_percentage >= Decimal("100") or getattr(obligation, 'is_delivered', False)

        if is_transferred:
            return RecognitionResult(
                obligation_id=obligation.obligation_id,
                period=period,
                amount_recognized=obligation.standalone_selling_price,
                cumulative_recognized=obligation.standalone_selling_price,
                remaining_amount=Decimal("0"),
                status=RecognitionStatus.RECOGNIZED,
                timing_type=RevenueTimingType.POINT_IN_TIME
            )

        return RecognitionResult(
            obligation_id=obligation.obligation_id,
            period=period,
            amount_recognized=Decimal("0"),
            cumulative_recognized=Decimal("0"),
            remaining_amount=obligation.standalone_selling_price,
            status=RecognitionStatus.DEFERRED,
            timing_type=RevenueTimingType.POINT_IN_TIME
        )



class BillingRuleEngineError(Exception):
    pass


class BillingRuleEngine:

    def evaluate_tm_billing(self, contract: Any, timesheets: list) -> BillingAmount:
        if not timesheets:
            raise BillingRuleEngineError("No timesheets provided for T&M billing")

        currency = getattr(contract, 'currency', 'INR')
        line_items = []
        gross_total = Decimal("0")

        for ts in timesheets:
            hours = Decimal(str(getattr(ts, 'hours', 0)))
            rate = Decimal(str(getattr(ts, 'rate', getattr(contract, 'hourly_rate', 0))))
            resource_name = getattr(ts, 'resource_name', 'Unknown')
            amount = (hours * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            gross_total += amount
            line_items.append({
                "resource": resource_name,
                "hours": str(hours),
                "rate": str(rate),
                "amount": str(amount)
            })

        cap = Decimal(str(getattr(contract, 'monthly_cap', 0)))
        adjustments = []
        if cap > Decimal("0") and gross_total > cap:
            adjustments.append({"type": "cap_adjustment", "amount": str(cap - gross_total)})
            gross_total = cap

        tax_rate = Decimal(str(getattr(contract, 'tax_rate', Decimal("0.18"))))
        tax_amount = (gross_total * tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return BillingAmount(
            gross_amount=gross_total,
            tax_amount=tax_amount,
            net_amount=gross_total + tax_amount,
            currency=currency,
            billing_model=BillingModelType.TIME_AND_MATERIAL,
            line_items=line_items,
            adjustments=adjustments
        )

    def evaluate_milestone_billing(self, contract: Any, milestones: list) -> BillingAmount:
        if not milestones:
            raise BillingRuleEngineError("No milestones provided for milestone billing")

        currency = getattr(contract, 'currency', 'INR')
        line_items = []
        gross_total = Decimal("0")

        for ms in milestones:
            if not getattr(ms, 'is_completed', False) and not getattr(ms, 'is_approved', False):
                continue

            amount = Decimal(str(getattr(ms, 'amount', 0)))
            description = getattr(ms, 'description', 'Milestone')
            gross_total += amount
            line_items.append({
                "milestone": description,
                "amount": str(amount),
                "completion_date": str(getattr(ms, 'completion_date', ''))
            })

        tax_rate = Decimal(str(getattr(contract, 'tax_rate', Decimal("0.18"))))
        tax_amount = (gross_total * tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return BillingAmount(
            gross_amount=gross_total,
            tax_amount=tax_amount,
            net_amount=gross_total + tax_amount,
            currency=currency,
            billing_model=BillingModelType.MILESTONE,
            line_items=line_items
        )

    def evaluate_retainer_billing(self, contract: Any, period: Any) -> BillingAmount:
        currency = getattr(contract, 'currency', 'INR')
        monthly_retainer = Decimal(str(getattr(contract, 'monthly_retainer', 0)))

        if monthly_retainer <= Decimal("0"):
            raise BillingRuleEngineError("Monthly retainer amount not defined in contract")

        period_str = str(getattr(period, 'name', getattr(period, 'month', str(period))))
        escalation_rate = Decimal(str(getattr(contract, 'annual_escalation_rate', Decimal("0"))))
        contract_start = getattr(contract, 'start_date', None)
        period_date = getattr(period, 'start_date', None)

        amount = monthly_retainer
        if escalation_rate > Decimal("0") and contract_start and period_date:
            years_elapsed = Decimal(str((period_date - contract_start).days)) / Decimal("365")
            if years_elapsed >= Decimal("1"):
                escalation_factor = (Decimal("1") + escalation_rate) ** int(years_elapsed)
                amount = (monthly_retainer * escalation_factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        line_items = [{"period": period_str, "retainer_amount": str(amount)}]

        tax_rate = Decimal(str(getattr(contract, 'tax_rate', Decimal("0.18"))))
        tax_amount = (amount * tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return BillingAmount(
            gross_amount=amount,
            tax_amount=tax_amount,
            net_amount=amount + tax_amount,
            currency=currency,
            billing_model=BillingModelType.RETAINER,
            line_items=line_items
        )

    def evaluate_performance_billing(self, contract: Any, metrics: Any) -> BillingAmount:
        currency = getattr(contract, 'currency', 'INR')
        base_fee = Decimal(str(getattr(contract, 'base_fee', Decimal("0"))))
        performance_rate = Decimal(str(getattr(contract, 'performance_rate', Decimal("0"))))

        achieved_value = Decimal(str(getattr(metrics, 'achieved_value', 0)))
        target_value = Decimal(str(getattr(metrics, 'target_value', 1)))

        achievement_ratio = achieved_value / max(target_value, Decimal("1"))

        performance_fee = Decimal("0")
        if achievement_ratio >= Decimal("1"):
            performance_fee = (achieved_value * performance_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            overachievement_multiplier = Decimal(str(getattr(contract, 'overachievement_multiplier', Decimal("1.0"))))
            if achievement_ratio > Decimal("1.2") and overachievement_multiplier > Decimal("1"):
                excess = achieved_value - target_value
                bonus = (excess * performance_rate * overachievement_multiplier).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                performance_fee += bonus
        elif achievement_ratio >= Decimal("0.8"):
            pro_rata_factor = (achievement_ratio - Decimal("0.8")) / Decimal("0.2")
            performance_fee = (achieved_value * performance_rate * pro_rata_factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        gross_total = base_fee + performance_fee

        cap = Decimal(str(getattr(contract, 'performance_cap', 0)))
        adjustments = []
        if cap > Decimal("0") and gross_total > cap:
            adjustments.append({"type": "performance_cap", "amount": str(cap - gross_total)})
            gross_total = cap

        line_items = [
            {"type": "base_fee", "amount": str(base_fee)},
            {"type": "performance_fee", "amount": str(performance_fee)},
            {"type": "achievement_ratio", "value": str(achievement_ratio)}
        ]

        tax_rate = Decimal(str(getattr(contract, 'tax_rate', Decimal("0.18"))))
        tax_amount = (gross_total * tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return BillingAmount(
            gross_amount=gross_total,
            tax_amount=tax_amount,
            net_amount=gross_total + tax_amount,
            currency=currency,
            billing_model=BillingModelType.PERFORMANCE,
            line_items=line_items,
            adjustments=adjustments
        )

    def evaluate_hybrid_billing(self, contract: Any, data: Any) -> BillingAmount:
        currency = getattr(contract, 'currency', 'INR')
        components = getattr(contract, 'billing_components', [])

        if not components:
            raise BillingRuleEngineError("No billing components defined for hybrid billing")

        total_gross = Decimal("0")
        all_line_items = []
        all_adjustments = []

        for component in components:
            comp_type = getattr(component, 'type', '').lower()
            comp_data = getattr(data, comp_type, None) if hasattr(data, comp_type) else data

            if comp_type == 'time_and_material':
                timesheets = getattr(comp_data, 'timesheets', []) if comp_data else []
                if timesheets:
                    result = self.evaluate_tm_billing(contract, timesheets)
                    total_gross += result.gross_amount
                    all_line_items.extend(result.line_items)
                    all_adjustments.extend(result.adjustments)

            elif comp_type == 'milestone':
                milestones = getattr(comp_data, 'milestones', []) if comp_data else []
                if milestones:
                    result = self.evaluate_milestone_billing(contract, milestones)
                    total_gross += result.gross_amount
                    all_line_items.extend(result.line_items)

            elif comp_type == 'retainer':
                period = getattr(comp_data, 'period', comp_data) if comp_data else None
                if period:
                    result = self.evaluate_retainer_billing(contract, period)
                    total_gross += result.gross_amount
                    all_line_items.extend(result.line_items)

            elif comp_type == 'performance':
                metrics = getattr(comp_data, 'metrics', comp_data) if comp_data else None
                if metrics:
                    result = self.evaluate_performance_billing(contract, metrics)
                    total_gross += result.gross_amount
                    all_line_items.extend(result.line_items)
                    all_adjustments.extend(result.adjustments)

        tax_rate = Decimal(str(getattr(contract, 'tax_rate', Decimal("0.18"))))
        tax_amount = (total_gross * tax_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return BillingAmount(
            gross_amount=total_gross,
            tax_amount=tax_amount,
            net_amount=total_gross + tax_amount,
            currency=currency,
            billing_model=BillingModelType.HYBRID,
            line_items=all_line_items,
            adjustments=all_adjustments
        )
