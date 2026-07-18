import numpy as np
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum


class CostAllocationMethod(str, Enum):
    ACTIVITY_BASED = "activity_based"
    REVENUE_PROPORTIONAL = "revenue_proportional"
    HEADCOUNT_BASED = "headcount_based"


class MarginTrend(str, Enum):
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"


@dataclass
class MarginBreakdown:
    gross_revenue: float
    direct_costs: float
    allocated_overhead: float
    gross_margin: float
    gross_margin_pct: float
    net_margin: float
    net_margin_pct: float
    contribution_margin: float
    contribution_margin_pct: float

    def to_dict(self):
        return asdict(self)


@dataclass
class BenchmarkComparison:
    metric: str
    client_value: float
    benchmark_value: float
    percentile_rank: int
    deviation_pct: float
    assessment: str

    def to_dict(self):
        return asdict(self)


@dataclass
class ScenarioResult:
    scenario_name: str
    description: str
    inputs_changed: dict
    resulting_margin: float
    margin_change: float
    revenue_impact: float
    feasibility: str

    def to_dict(self):
        return asdict(self)


@dataclass
class ProfitabilityReport:
    client_id: str
    analysis_period: str
    margin_breakdown: MarginBreakdown
    cost_allocation: dict
    benchmarks: list
    trend: str
    trend_data: list
    scenarios: list
    insights: list
    generated_at: str

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "analysis_period": self.analysis_period,
            "margin_breakdown": self.margin_breakdown.to_dict(),
            "cost_allocation": self.cost_allocation,
            "benchmarks": [b.to_dict() for b in self.benchmarks],
            "trend": self.trend,
            "trend_data": self.trend_data,
            "scenarios": [s.to_dict() for s in self.scenarios],
            "insights": self.insights,
            "generated_at": self.generated_at,
        }


class ProfitabilityAnalyzer:
    SECTOR_BENCHMARKS = {
        "technology": {"gross_margin": 35.0, "net_margin": 22.0, "utilization": 0.82},
        "bfsi": {"gross_margin": 30.0, "net_margin": 18.0, "utilization": 0.80},
        "healthcare": {"gross_margin": 28.0, "net_margin": 16.0, "utilization": 0.78},
        "manufacturing": {"gross_margin": 25.0, "net_margin": 14.0, "utilization": 0.75},
        "retail": {"gross_margin": 27.0, "net_margin": 15.0, "utilization": 0.77},
        "telecom": {"gross_margin": 32.0, "net_margin": 20.0, "utilization": 0.80},
        "default": {"gross_margin": 28.0, "net_margin": 16.0, "utilization": 0.78},
    }

    BILLING_MODEL_BENCHMARKS = {
        "time_and_materials": {"target_margin": 30.0, "cost_ratio": 0.65},
        "fixed_price": {"target_margin": 35.0, "cost_ratio": 0.60},
        "milestone": {"target_margin": 32.0, "cost_ratio": 0.62},
        "retainer": {"target_margin": 28.0, "cost_ratio": 0.68},
        "hybrid": {"target_margin": 30.0, "cost_ratio": 0.65},
    }

    TEAM_SIZE_BENCHMARKS = {
        "small": {"max_size": 5, "overhead_pct": 12.0, "target_margin": 32.0},
        "medium": {"max_size": 15, "overhead_pct": 15.0, "target_margin": 28.0},
        "large": {"max_size": 50, "overhead_pct": 18.0, "target_margin": 25.0},
        "enterprise": {"max_size": 999, "overhead_pct": 22.0, "target_margin": 22.0},
    }

    def __init__(self, default_allocation_method: str = CostAllocationMethod.ACTIVITY_BASED):
        self.default_allocation_method = default_allocation_method

    def analyze(self, client_data: dict) -> ProfitabilityReport:
        margin_breakdown = self._calculate_margins(client_data)
        cost_allocation = self._allocate_costs(client_data)
        benchmarks = self._perform_benchmark_analysis(client_data, margin_breakdown)
        trend, trend_data = self._detect_trend(client_data)
        scenarios = self._run_scenarios(client_data, margin_breakdown)
        insights = self._generate_insights(client_data, margin_breakdown, benchmarks, trend)

        return ProfitabilityReport(
            client_id=client_data.get("client_id", ""),
            analysis_period=client_data.get("analysis_period", ""),
            margin_breakdown=margin_breakdown,
            cost_allocation=cost_allocation,
            benchmarks=benchmarks,
            trend=trend,
            trend_data=trend_data,
            scenarios=scenarios,
            insights=insights,
            generated_at=datetime.now().isoformat(),
        )

    def _calculate_margins(self, client_data: dict) -> MarginBreakdown:
        gross_revenue = client_data.get("gross_revenue", 0)
        direct_labor_cost = client_data.get("direct_labor_cost", 0)
        direct_expenses = client_data.get("direct_expenses", 0)
        subcontractor_costs = client_data.get("subcontractor_costs", 0)
        direct_costs = direct_labor_cost + direct_expenses + subcontractor_costs

        overhead_allocation = self._calculate_overhead_allocation(client_data)

        gross_margin = gross_revenue - direct_costs
        gross_margin_pct = (gross_margin / gross_revenue * 100) if gross_revenue > 0 else 0

        net_margin = gross_margin - overhead_allocation
        net_margin_pct = (net_margin / gross_revenue * 100) if gross_revenue > 0 else 0

        variable_costs = direct_labor_cost + direct_expenses
        contribution_margin = gross_revenue - variable_costs
        contribution_margin_pct = (contribution_margin / gross_revenue * 100) if gross_revenue > 0 else 0

        return MarginBreakdown(
            gross_revenue=round(gross_revenue, 2),
            direct_costs=round(direct_costs, 2),
            allocated_overhead=round(overhead_allocation, 2),
            gross_margin=round(gross_margin, 2),
            gross_margin_pct=round(gross_margin_pct, 2),
            net_margin=round(net_margin, 2),
            net_margin_pct=round(net_margin_pct, 2),
            contribution_margin=round(contribution_margin, 2),
            contribution_margin_pct=round(contribution_margin_pct, 2),
        )

    def _calculate_overhead_allocation(self, client_data: dict) -> float:
        total_overhead = client_data.get("total_company_overhead", 0)
        method = client_data.get("allocation_method", self.default_allocation_method)

        if method == CostAllocationMethod.ACTIVITY_BASED:
            return self._activity_based_allocation(client_data, total_overhead)
        elif method == CostAllocationMethod.REVENUE_PROPORTIONAL:
            return self._revenue_proportional_allocation(client_data, total_overhead)
        elif method == CostAllocationMethod.HEADCOUNT_BASED:
            return self._headcount_based_allocation(client_data, total_overhead)
        return self._activity_based_allocation(client_data, total_overhead)

    def _activity_based_allocation(self, client_data: dict, total_overhead: float) -> float:
        activity_drivers = {
            "management_time_pct": 0.30,
            "support_tickets_pct": 0.20,
            "infrastructure_usage_pct": 0.25,
            "recruitment_effort_pct": 0.15,
            "admin_effort_pct": 0.10,
        }

        weighted_share = 0.0
        for driver, weight in activity_drivers.items():
            driver_value = client_data.get(driver, client_data.get("revenue_share_pct", 10)) / 100
            weighted_share += driver_value * weight

        return total_overhead * weighted_share

    def _revenue_proportional_allocation(self, client_data: dict, total_overhead: float) -> float:
        revenue_share = client_data.get("revenue_share_pct", 10) / 100
        return total_overhead * revenue_share

    def _headcount_based_allocation(self, client_data: dict, total_overhead: float) -> float:
        client_headcount = client_data.get("team_size", 1)
        total_headcount = client_data.get("total_company_headcount", 100)
        headcount_share = client_headcount / max(total_headcount, 1)
        return total_overhead * headcount_share

    def _allocate_costs(self, client_data: dict) -> dict:
        total_overhead = client_data.get("total_company_overhead", 0)
        return {
            CostAllocationMethod.ACTIVITY_BASED: round(self._activity_based_allocation(client_data, total_overhead), 2),
            CostAllocationMethod.REVENUE_PROPORTIONAL: round(self._revenue_proportional_allocation(client_data, total_overhead), 2),
            CostAllocationMethod.HEADCOUNT_BASED: round(self._headcount_based_allocation(client_data, total_overhead), 2),
        }

    def _perform_benchmark_analysis(self, client_data: dict, margins: MarginBreakdown) -> list:
        benchmarks = []
        sector = client_data.get("sector", "default")
        sector_bench = self.SECTOR_BENCHMARKS.get(sector, self.SECTOR_BENCHMARKS["default"])

        benchmarks.append(self._create_benchmark(
            "Gross Margin (Sector)",
            margins.gross_margin_pct,
            sector_bench["gross_margin"]
        ))
        benchmarks.append(self._create_benchmark(
            "Net Margin (Sector)",
            margins.net_margin_pct,
            sector_bench["net_margin"]
        ))

        billing_model = client_data.get("billing_model", "time_and_materials")
        model_bench = self.BILLING_MODEL_BENCHMARKS.get(billing_model, self.BILLING_MODEL_BENCHMARKS["time_and_materials"])
        benchmarks.append(self._create_benchmark(
            "Margin vs Billing Model Target",
            margins.net_margin_pct,
            model_bench["target_margin"]
        ))

        team_size = client_data.get("team_size", 5)
        team_bench = self._get_team_size_benchmark(team_size)
        benchmarks.append(self._create_benchmark(
            "Margin vs Team Size Benchmark",
            margins.net_margin_pct,
            team_bench["target_margin"]
        ))

        utilization = client_data.get("resource_utilization", 0.75) * 100
        benchmarks.append(self._create_benchmark(
            "Resource Utilization",
            utilization,
            sector_bench["utilization"] * 100
        ))

        return benchmarks

    def _create_benchmark(self, metric: str, client_value: float, benchmark_value: float) -> BenchmarkComparison:
        deviation = ((client_value - benchmark_value) / max(benchmark_value, 1)) * 100

        if deviation > 10:
            assessment = "above_benchmark"
        elif deviation > -5:
            assessment = "at_benchmark"
        else:
            assessment = "below_benchmark"

        percentile = min(99, max(1, int(50 + deviation)))

        return BenchmarkComparison(
            metric=metric,
            client_value=round(client_value, 2),
            benchmark_value=round(benchmark_value, 2),
            percentile_rank=percentile,
            deviation_pct=round(deviation, 2),
            assessment=assessment,
        )

    def _get_team_size_benchmark(self, team_size: int) -> dict:
        for category, specs in self.TEAM_SIZE_BENCHMARKS.items():
            if team_size <= specs["max_size"]:
                return specs
        return self.TEAM_SIZE_BENCHMARKS["enterprise"]

    def _detect_trend(self, client_data: dict) -> tuple:
        margin_history = client_data.get("margin_history", [])

        if len(margin_history) < 3:
            return MarginTrend.STABLE.value, margin_history

        recent_window = margin_history[-3:]
        older_window = margin_history[:-3] if len(margin_history) > 3 else margin_history[:3]

        recent_avg = np.mean(recent_window)
        older_avg = np.mean(older_window)

        if len(margin_history) >= 4:
            x = np.arange(len(margin_history)).reshape(-1, 1)
            y = np.array(margin_history)
            slope = np.polyfit(x.flatten(), y, 1)[0]
        else:
            slope = recent_avg - older_avg

        if slope > 0.5 and recent_avg > older_avg:
            trend = MarginTrend.IMPROVING.value
        elif slope < -0.5 and recent_avg < older_avg:
            trend = MarginTrend.DECLINING.value
        else:
            trend = MarginTrend.STABLE.value

        return trend, margin_history

    def _run_scenarios(self, client_data: dict, current_margins: MarginBreakdown) -> list:
        scenarios = []

        scenarios.append(self._scenario_rate_increase(client_data, current_margins))
        scenarios.append(self._scenario_utilization_improvement(client_data, current_margins))
        scenarios.append(self._scenario_team_optimization(client_data, current_margins))
        scenarios.append(self._scenario_overhead_reduction(client_data, current_margins))

        return scenarios

    def _scenario_rate_increase(self, client_data: dict, margins: MarginBreakdown) -> ScenarioResult:
        rate_increase_pct = 10
        new_revenue = margins.gross_revenue * (1 + rate_increase_pct / 100)
        new_net_margin = new_revenue - margins.direct_costs - margins.allocated_overhead
        new_margin_pct = (new_net_margin / new_revenue * 100) if new_revenue > 0 else 0
        margin_change = new_margin_pct - margins.net_margin_pct

        return ScenarioResult(
            scenario_name="Rate Increase 10%",
            description="Increase billing rates by 10% while maintaining current cost structure",
            inputs_changed={"billing_rate": "+10%"},
            resulting_margin=round(new_margin_pct, 2),
            margin_change=round(margin_change, 2),
            revenue_impact=round(new_revenue - margins.gross_revenue, 2),
            feasibility="medium",
        )

    def _scenario_utilization_improvement(self, client_data: dict, margins: MarginBreakdown) -> ScenarioResult:
        current_utilization = client_data.get("resource_utilization", 0.75)
        target_utilization = min(0.90, current_utilization + 0.10)
        utilization_gain = (target_utilization - current_utilization) / current_utilization

        additional_revenue = margins.gross_revenue * utilization_gain
        new_revenue = margins.gross_revenue + additional_revenue
        additional_variable_cost = additional_revenue * 0.3

        new_net_margin = new_revenue - margins.direct_costs - additional_variable_cost - margins.allocated_overhead
        new_margin_pct = (new_net_margin / new_revenue * 100) if new_revenue > 0 else 0
        margin_change = new_margin_pct - margins.net_margin_pct

        return ScenarioResult(
            scenario_name="Utilization Improvement",
            description=f"Improve utilization from {current_utilization*100:.0f}% to {target_utilization*100:.0f}%",
            inputs_changed={"utilization": f"{current_utilization*100:.0f}% -> {target_utilization*100:.0f}%"},
            resulting_margin=round(new_margin_pct, 2),
            margin_change=round(margin_change, 2),
            revenue_impact=round(additional_revenue, 2),
            feasibility="high",
        )

    def _scenario_team_optimization(self, client_data: dict, margins: MarginBreakdown) -> ScenarioResult:
        team_size = client_data.get("team_size", 10)
        avg_cost_per_head = margins.direct_costs / max(team_size, 1)
        reduction = max(1, int(team_size * 0.1))
        cost_savings = reduction * avg_cost_per_head

        new_direct_costs = margins.direct_costs - cost_savings
        new_net_margin = margins.gross_revenue - new_direct_costs - margins.allocated_overhead
        new_margin_pct = (new_net_margin / margins.gross_revenue * 100) if margins.gross_revenue > 0 else 0
        margin_change = new_margin_pct - margins.net_margin_pct

        return ScenarioResult(
            scenario_name="Team Right-Sizing",
            description=f"Reduce team by {reduction} FTE through efficiency improvements",
            inputs_changed={"team_size": f"{team_size} -> {team_size - reduction}"},
            resulting_margin=round(new_margin_pct, 2),
            margin_change=round(margin_change, 2),
            revenue_impact=0,
            feasibility="medium",
        )

    def _scenario_overhead_reduction(self, client_data: dict, margins: MarginBreakdown) -> ScenarioResult:
        overhead_reduction_pct = 15
        new_overhead = margins.allocated_overhead * (1 - overhead_reduction_pct / 100)
        new_net_margin = margins.gross_revenue - margins.direct_costs - new_overhead
        new_margin_pct = (new_net_margin / margins.gross_revenue * 100) if margins.gross_revenue > 0 else 0
        margin_change = new_margin_pct - margins.net_margin_pct

        return ScenarioResult(
            scenario_name="Overhead Optimization",
            description="Reduce allocated overhead by 15% through shared services efficiency",
            inputs_changed={"overhead": "-15%"},
            resulting_margin=round(new_margin_pct, 2),
            margin_change=round(margin_change, 2),
            revenue_impact=0,
            feasibility="high",
        )

    def _generate_insights(self, client_data: dict, margins: MarginBreakdown, benchmarks: list, trend: str) -> list:
        insights = []

        below_benchmark = [b for b in benchmarks if b.assessment == "below_benchmark"]
        for benchmark in below_benchmark:
            insights.append({
                "category": "gap_analysis",
                "finding": f"{benchmark.metric} is {abs(benchmark.deviation_pct):.1f}% below benchmark",
                "impact_bps": int(abs(benchmark.deviation_pct) * 10),
                "actionability": "SHORT_TERM",
                "confidence": "HIGH",
            })

        if trend == MarginTrend.DECLINING.value:
            insights.append({
                "category": "trend",
                "finding": "Margins showing declining trend over recent periods",
                "impact_bps": 200,
                "actionability": "IMMEDIATE",
                "confidence": "HIGH",
            })

        cost_ratio = margins.direct_costs / max(margins.gross_revenue, 1)
        billing_model = client_data.get("billing_model", "time_and_materials")
        target_ratio = self.BILLING_MODEL_BENCHMARKS.get(billing_model, {}).get("cost_ratio", 0.65)

        if cost_ratio > target_ratio + 0.05:
            insights.append({
                "category": "cost_optimization",
                "finding": f"Direct cost ratio ({cost_ratio*100:.1f}%) exceeds target ({target_ratio*100:.1f}%)",
                "impact_bps": int((cost_ratio - target_ratio) * 10000),
                "actionability": "SHORT_TERM",
                "confidence": "MEDIUM",
            })

        if margins.allocated_overhead / max(margins.gross_revenue, 1) > 0.20:
            insights.append({
                "category": "overhead",
                "finding": "Overhead allocation exceeds 20% of revenue",
                "impact_bps": int((margins.allocated_overhead / max(margins.gross_revenue, 1) - 0.20) * 10000),
                "actionability": "LONG_TERM",
                "confidence": "MEDIUM",
            })

        return insights
