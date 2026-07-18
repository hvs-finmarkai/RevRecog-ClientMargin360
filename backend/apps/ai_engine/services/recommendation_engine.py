from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional


class RecommendationType(str, Enum):
    REPRICE = "REPRICE"
    EXPAND = "EXPAND"
    RESTRUCTURE = "RESTRUCTURE"
    EXIT = "EXIT"
    OPTIMIZE = "OPTIMIZE"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class Recommendation:
    recommendation_type: str
    title: str
    rationale: str
    expected_margin_improvement: float
    implementation_steps: list
    risk_level: str
    priority: int
    timeline: str
    estimated_revenue_impact: float = 0.0
    confidence: float = 0.0

    def to_dict(self):
        return asdict(self)


@dataclass
class ClientHealthScore:
    client_id: str
    overall_score: float
    financial_health: float
    operational_health: float
    relationship_health: float
    growth_potential: float
    risk_level: float
    trend: str
    factors: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


@dataclass
class RecommendationReport:
    client_id: str
    client_name: str
    health_score: ClientHealthScore
    recommendations: list
    generated_at: str = ""

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "health_score": self.health_score.to_dict(),
            "recommendations": [r.to_dict() for r in self.recommendations],
            "generated_at": self.generated_at,
        }


class RecommendationEngine:
    MARGIN_THRESHOLDS = {
        "critical_low": 5.0,
        "low": 15.0,
        "target": 25.0,
        "high": 40.0,
    }

    BILLING_MODEL_BENCHMARKS = {
        "time_and_materials": {"target_margin": 30.0, "efficiency_factor": 0.85},
        "fixed_price": {"target_margin": 35.0, "efficiency_factor": 0.90},
        "milestone": {"target_margin": 32.0, "efficiency_factor": 0.88},
        "retainer": {"target_margin": 28.0, "efficiency_factor": 0.92},
        "hybrid": {"target_margin": 30.0, "efficiency_factor": 0.87},
        "outcome_based": {"target_margin": 40.0, "efficiency_factor": 0.80},
    }

    def __init__(self):
        self.weights = {
            "financial_health": 0.30,
            "operational_health": 0.25,
            "relationship_health": 0.20,
            "growth_potential": 0.15,
            "risk_level": 0.10,
        }

    def generate_recommendations(self, client_data: dict) -> RecommendationReport:
        from datetime import datetime

        health_score = self.calculate_health_score(client_data)
        recommendations = []

        recommendations.extend(self._evaluate_repricing(client_data, health_score))
        recommendations.extend(self._evaluate_expansion(client_data, health_score))
        recommendations.extend(self._evaluate_restructuring(client_data, health_score))
        recommendations.extend(self._evaluate_exit(client_data, health_score))
        recommendations.extend(self._evaluate_optimization(client_data, health_score))

        recommendations.sort(key=lambda r: r.priority)

        return RecommendationReport(
            client_id=client_data.get("client_id", ""),
            client_name=client_data.get("client_name", ""),
            health_score=health_score,
            recommendations=recommendations,
            generated_at=datetime.now().isoformat(),
        )

    def calculate_health_score(self, client_data: dict) -> ClientHealthScore:
        financial = self._score_financial_health(client_data)
        operational = self._score_operational_health(client_data)
        relationship = self._score_relationship_health(client_data)
        growth = self._score_growth_potential(client_data)
        risk = self._score_risk_level(client_data)

        overall = (
            financial * self.weights["financial_health"]
            + operational * self.weights["operational_health"]
            + relationship * self.weights["relationship_health"]
            + growth * self.weights["growth_potential"]
            + (100 - risk) * self.weights["risk_level"]
        )

        trend = self._determine_trend(client_data)

        return ClientHealthScore(
            client_id=client_data.get("client_id", ""),
            overall_score=round(overall, 1),
            financial_health=round(financial, 1),
            operational_health=round(operational, 1),
            relationship_health=round(relationship, 1),
            growth_potential=round(growth, 1),
            risk_level=round(risk, 1),
            trend=trend,
            factors=self._extract_key_factors(client_data),
        )

    def _score_financial_health(self, client_data: dict) -> float:
        score = 50.0
        margin = client_data.get("current_margin", 0)
        if margin >= self.MARGIN_THRESHOLDS["high"]:
            score += 30
        elif margin >= self.MARGIN_THRESHOLDS["target"]:
            score += 20
        elif margin >= self.MARGIN_THRESHOLDS["low"]:
            score += 5
        elif margin >= self.MARGIN_THRESHOLDS["critical_low"]:
            score -= 20
        else:
            score -= 40

        revenue_growth = client_data.get("revenue_growth_pct", 0)
        score += min(20, max(-20, revenue_growth * 2))

        payment_score = client_data.get("payment_reliability_score", 50)
        score += (payment_score - 50) * 0.2

        return max(0, min(100, score))

    def _score_operational_health(self, client_data: dict) -> float:
        score = 50.0
        utilization = client_data.get("resource_utilization", 0.75)
        if utilization >= 0.85:
            score += 20
        elif utilization >= 0.75:
            score += 10
        elif utilization < 0.60:
            score -= 20

        delivery_on_time_pct = client_data.get("delivery_on_time_pct", 80)
        score += (delivery_on_time_pct - 80) * 0.5

        sla_compliance = client_data.get("sla_compliance_pct", 90)
        score += (sla_compliance - 90) * 1.0

        return max(0, min(100, score))

    def _score_relationship_health(self, client_data: dict) -> float:
        score = 50.0
        nps = client_data.get("nps_score", 0)
        score += nps * 0.5

        escalation_count = client_data.get("escalation_count_last_quarter", 0)
        score -= escalation_count * 10

        communication_frequency = client_data.get("communication_score", 50)
        score += (communication_frequency - 50) * 0.3

        tenure_months = client_data.get("tenure_months", 0)
        score += min(15, tenure_months * 0.5)

        return max(0, min(100, score))

    def _score_growth_potential(self, client_data: dict) -> float:
        score = 50.0
        wallet_share = client_data.get("wallet_share_pct", 50)
        score += (100 - wallet_share) * 0.3

        cross_sell_opportunities = client_data.get("cross_sell_opportunities", 0)
        score += min(20, cross_sell_opportunities * 5)

        client_growth_rate = client_data.get("client_company_growth_pct", 0)
        score += min(15, max(-15, client_growth_rate * 1.5))

        strategic_alignment = client_data.get("strategic_alignment_score", 50)
        score += (strategic_alignment - 50) * 0.2

        return max(0, min(100, score))

    def _score_risk_level(self, client_data: dict) -> float:
        risk = 20.0
        revenue_concentration = client_data.get("revenue_concentration_pct", 5)
        if revenue_concentration > 20:
            risk += 30
        elif revenue_concentration > 10:
            risk += 15

        contract_expiry_months = client_data.get("contract_expiry_months", 12)
        if contract_expiry_months < 3:
            risk += 25
        elif contract_expiry_months < 6:
            risk += 10

        single_point_of_contact = client_data.get("single_poc_risk", False)
        if single_point_of_contact:
            risk += 15

        payment_delays = client_data.get("avg_payment_delay_days", 0)
        if payment_delays > 60:
            risk += 20
        elif payment_delays > 30:
            risk += 10

        return max(0, min(100, risk))

    def _determine_trend(self, client_data: dict) -> str:
        margin_history = client_data.get("margin_history", [])
        if len(margin_history) < 3:
            return "stable"

        recent_avg = sum(margin_history[-3:]) / 3
        older_avg = sum(margin_history[:-3]) / max(1, len(margin_history) - 3)

        if recent_avg > older_avg * 1.10:
            return "improving"
        elif recent_avg < older_avg * 0.90:
            return "declining"
        return "stable"

    def _extract_key_factors(self, client_data: dict) -> dict:
        return {
            "current_margin": client_data.get("current_margin", 0),
            "billing_model": client_data.get("billing_model", "unknown"),
            "tenure_months": client_data.get("tenure_months", 0),
            "annual_revenue": client_data.get("annual_revenue", 0),
            "team_size": client_data.get("team_size", 0),
        }

    def _evaluate_repricing(self, client_data: dict, health: ClientHealthScore) -> list:
        recommendations = []
        margin = client_data.get("current_margin", 0)
        billing_model = client_data.get("billing_model", "time_and_materials")
        benchmark = self.BILLING_MODEL_BENCHMARKS.get(billing_model, {})
        target_margin = benchmark.get("target_margin", 25)

        if margin < target_margin - 5:
            gap = target_margin - margin
            annual_revenue = client_data.get("annual_revenue", 0)
            revenue_impact = annual_revenue * (gap / 100)

            priority = 1 if margin < self.MARGIN_THRESHOLDS["critical_low"] else 2

            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.REPRICE.value,
                title=f"Increase rates to close {gap:.1f}pp margin gap",
                rationale=f"Current margin of {margin:.1f}% is {gap:.1f}pp below target of {target_margin:.1f}% for {billing_model} engagements",
                expected_margin_improvement=gap * 0.6,
                implementation_steps=[
                    "Analyze rate card vs market benchmarks",
                    "Prepare value justification documentation",
                    "Schedule pricing review with client stakeholder",
                    "Propose phased rate adjustment over 2 cycles",
                    "Monitor impact on utilization post-adjustment",
                ],
                risk_level=RiskLevel.MEDIUM.value if gap < 10 else RiskLevel.HIGH.value,
                priority=priority,
                timeline="30-60 days",
                estimated_revenue_impact=round(revenue_impact, 2),
                confidence=0.75,
            ))
        return recommendations

    def _evaluate_expansion(self, client_data: dict, health: ClientHealthScore) -> list:
        recommendations = []

        if health.growth_potential > 60 and health.relationship_health > 50:
            wallet_share = client_data.get("wallet_share_pct", 50)
            annual_revenue = client_data.get("annual_revenue", 0)
            expansion_potential = annual_revenue * ((100 - wallet_share) / 100) * 0.3

            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.EXPAND.value,
                title="Cross-sell additional service lines",
                rationale=f"Strong relationship (score: {health.relationship_health:.0f}) with growth headroom (wallet share: {wallet_share}%)",
                expected_margin_improvement=3.0,
                implementation_steps=[
                    "Map client's unmet needs and pain points",
                    "Identify complementary service offerings",
                    "Develop tailored proposal with ROI projections",
                    "Arrange executive sponsorship meeting",
                    "Pilot new service with defined success criteria",
                ],
                risk_level=RiskLevel.LOW.value,
                priority=3,
                timeline="60-90 days",
                estimated_revenue_impact=round(expansion_potential, 2),
                confidence=0.65,
            ))
        return recommendations

    def _evaluate_restructuring(self, client_data: dict, health: ClientHealthScore) -> list:
        recommendations = []
        billing_model = client_data.get("billing_model", "time_and_materials")
        margin = client_data.get("current_margin", 0)
        benchmark = self.BILLING_MODEL_BENCHMARKS.get(billing_model, {})
        target_margin = benchmark.get("target_margin", 25)

        if margin < target_margin - 10 and health.operational_health < 60:
            better_models = [
                (model, specs) for model, specs in self.BILLING_MODEL_BENCHMARKS.items()
                if specs["target_margin"] > target_margin and model != billing_model
            ]

            if better_models:
                suggested_model = better_models[0][0]
                improvement = better_models[0][1]["target_margin"] - margin

                recommendations.append(Recommendation(
                    recommendation_type=RecommendationType.RESTRUCTURE.value,
                    title=f"Transition from {billing_model} to {suggested_model}",
                    rationale=f"Current billing model underperforming by {target_margin - margin:.1f}pp; {suggested_model} offers better margin potential",
                    expected_margin_improvement=improvement * 0.5,
                    implementation_steps=[
                        "Analyze historical delivery data for new model feasibility",
                        "Build financial model comparing current vs proposed structure",
                        "Draft transition proposal with risk mitigation plan",
                        "Negotiate new contract terms with client",
                        "Implement phased transition with parallel tracking",
                    ],
                    risk_level=RiskLevel.HIGH.value,
                    priority=3,
                    timeline="90-180 days",
                    estimated_revenue_impact=0,
                    confidence=0.55,
                ))
        return recommendations

    def _evaluate_exit(self, client_data: dict, health: ClientHealthScore) -> list:
        recommendations = []
        margin = client_data.get("current_margin", 0)
        tenure_months = client_data.get("tenure_months", 0)
        margin_trend = self._determine_trend(client_data)

        should_exit = (
            margin < self.MARGIN_THRESHOLDS["critical_low"]
            and margin_trend == "declining"
            and health.overall_score < 30
            and tenure_months > 12
        )

        if should_exit:
            annual_revenue = client_data.get("annual_revenue", 0)
            annual_loss = annual_revenue * abs(margin) / 100 if margin < 0 else 0

            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.EXIT.value,
                title="Planned disengagement recommended",
                rationale=f"Persistently unprofitable (margin: {margin:.1f}%, trend: declining) with low health score ({health.overall_score:.0f}/100)",
                expected_margin_improvement=abs(margin),
                implementation_steps=[
                    "Document current obligations and contract terms",
                    "Identify natural exit points (contract renewal, milestone completion)",
                    "Develop transition plan for client continuity",
                    "Reallocate team resources to higher-value engagements",
                    "Execute graceful disengagement over agreed timeline",
                ],
                risk_level=RiskLevel.HIGH.value,
                priority=2,
                timeline="90-180 days",
                estimated_revenue_impact=-annual_revenue,
                confidence=0.70,
            ))
        return recommendations

    def _evaluate_optimization(self, client_data: dict, health: ClientHealthScore) -> list:
        recommendations = []
        utilization = client_data.get("resource_utilization", 0.75)
        margin = client_data.get("current_margin", 0)

        if utilization < 0.75 and margin < self.MARGIN_THRESHOLDS["target"]:
            improvement_potential = (0.85 - utilization) * margin * 0.5
            annual_revenue = client_data.get("annual_revenue", 0)

            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.OPTIMIZE.value,
                title=f"Improve resource utilization from {utilization*100:.0f}% to 85%",
                rationale=f"Below-target utilization ({utilization*100:.0f}%) directly impacting margins; 10pp improvement yields significant margin gain",
                expected_margin_improvement=improvement_potential,
                implementation_steps=[
                    "Audit current resource allocation and bench time",
                    "Implement capacity planning and demand forecasting",
                    "Cross-train team members for multi-project deployment",
                    "Optimize sprint planning to minimize idle time",
                    "Track utilization weekly with automated dashboards",
                ],
                risk_level=RiskLevel.LOW.value,
                priority=2,
                timeline="30-60 days",
                estimated_revenue_impact=round(annual_revenue * 0.05, 2),
                confidence=0.80,
            ))

        delivery_on_time = client_data.get("delivery_on_time_pct", 80)
        if delivery_on_time < 80:
            recommendations.append(Recommendation(
                recommendation_type=RecommendationType.OPTIMIZE.value,
                title="Improve delivery timeliness to reduce cost overruns",
                rationale=f"Only {delivery_on_time}% on-time delivery causing rework and extended timelines",
                expected_margin_improvement=2.5,
                implementation_steps=[
                    "Root cause analysis of delivery delays",
                    "Implement agile ceremonies and sprint discipline",
                    "Add early warning metrics and escalation triggers",
                    "Review and right-size team composition",
                    "Establish delivery quality gates",
                ],
                risk_level=RiskLevel.LOW.value,
                priority=3,
                timeline="30-60 days",
                estimated_revenue_impact=0,
                confidence=0.70,
            ))
        return recommendations
