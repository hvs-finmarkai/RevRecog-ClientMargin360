import numpy as np
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class LeakageType(str, Enum):
    UNBILLED_HOURS = "unbilled_hours"
    MISSED_MILESTONES = "missed_milestones"
    RATE_ESCALATION_NOT_APPLIED = "rate_escalation_not_applied"
    EXPENSES_NOT_BILLED = "expenses_not_billed"
    SCOPE_CREEP = "scope_creep"
    UNDERCHARGING = "undercharging"


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class LeakageInstance:
    leakage_type: str
    description: str
    severity: str
    confidence: float
    estimated_amount: float
    client_id: str
    contract_id: str
    detected_at: str = ""
    evidence: dict = field(default_factory=dict)
    recommendation: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class LeakageReport:
    client_id: str
    total_leakage_amount: float
    leakage_count: int
    leakages: list
    analysis_period_start: str
    analysis_period_end: str
    risk_score: float
    trend: str

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "total_leakage_amount": self.total_leakage_amount,
            "leakage_count": self.leakage_count,
            "leakages": [l.to_dict() for l in self.leakages],
            "analysis_period_start": self.analysis_period_start,
            "analysis_period_end": self.analysis_period_end,
            "risk_score": self.risk_score,
            "trend": self.trend,
        }


class LeakageDetectorService:
    def __init__(self, anomaly_contamination: float = 0.1):
        self.anomaly_contamination = anomaly_contamination
        self.isolation_forest = IsolationForest(
            contamination=anomaly_contamination,
            random_state=42,
            n_estimators=100,
        )
        self.scaler = StandardScaler()

    def detect_leakage(self, client_data: dict) -> LeakageReport:
        leakages = []
        leakages.extend(self._detect_unbilled_hours(client_data))
        leakages.extend(self._detect_missed_milestones(client_data))
        leakages.extend(self._detect_rate_escalation_gaps(client_data))
        leakages.extend(self._detect_unbilled_expenses(client_data))
        leakages.extend(self._detect_scope_creep(client_data))
        leakages.extend(self._detect_undercharging(client_data))

        anomaly_leakages = self._detect_anomalies(client_data)
        leakages.extend(anomaly_leakages)

        total_amount = sum(l.estimated_amount for l in leakages)
        risk_score = self._calculate_risk_score(leakages, client_data)
        trend = self._analyze_trend(client_data)

        return LeakageReport(
            client_id=client_data.get("client_id", ""),
            total_leakage_amount=round(total_amount, 2),
            leakage_count=len(leakages),
            leakages=leakages,
            analysis_period_start=client_data.get("period_start", ""),
            analysis_period_end=client_data.get("period_end", ""),
            risk_score=round(risk_score, 2),
            trend=trend,
        )

    def batch_detect(self, clients_data: list) -> list:
        reports = []
        for client_data in clients_data:
            report = self.detect_leakage(client_data)
            reports.append(report)
        reports.sort(key=lambda r: r.total_leakage_amount, reverse=True)
        return reports

    def _detect_unbilled_hours(self, client_data: dict) -> list:
        leakages = []
        timesheets = client_data.get("timesheets", [])
        invoices = client_data.get("invoices", [])
        billed_hours = sum(inv.get("hours_billed", 0) for inv in invoices)
        logged_hours = sum(ts.get("hours", 0) for ts in timesheets)
        unbilled_hours = logged_hours - billed_hours

        if unbilled_hours > 0:
            hourly_rate = client_data.get("contracted_rate", 0)
            estimated_amount = unbilled_hours * hourly_rate
            severity = self._severity_from_amount(estimated_amount, client_data.get("contract_value", 1))

            leakages.append(LeakageInstance(
                leakage_type=LeakageType.UNBILLED_HOURS,
                description=f"{unbilled_hours:.1f} hours logged but not billed",
                severity=severity,
                confidence=0.85,
                estimated_amount=round(estimated_amount, 2),
                client_id=client_data.get("client_id", ""),
                contract_id=client_data.get("contract_id", ""),
                detected_at=datetime.now().isoformat(),
                evidence={
                    "logged_hours": logged_hours,
                    "billed_hours": billed_hours,
                    "unbilled_hours": unbilled_hours,
                    "hourly_rate": hourly_rate,
                },
                recommendation="Review timesheet entries and generate supplementary invoice for unbilled hours",
            ))
        return leakages

    def _detect_missed_milestones(self, client_data: dict) -> list:
        leakages = []
        milestones = client_data.get("milestones", [])

        for milestone in milestones:
            if milestone.get("status") == "completed" and not milestone.get("invoiced"):
                estimated_amount = milestone.get("value", 0)
                leakages.append(LeakageInstance(
                    leakage_type=LeakageType.MISSED_MILESTONES,
                    description=f"Milestone '{milestone.get('name', '')}' completed but not invoiced",
                    severity=self._severity_from_amount(estimated_amount, client_data.get("contract_value", 1)),
                    confidence=0.90,
                    estimated_amount=estimated_amount,
                    client_id=client_data.get("client_id", ""),
                    contract_id=client_data.get("contract_id", ""),
                    detected_at=datetime.now().isoformat(),
                    evidence={
                        "milestone_name": milestone.get("name"),
                        "completion_date": milestone.get("completion_date"),
                        "milestone_value": estimated_amount,
                    },
                    recommendation=f"Invoice milestone '{milestone.get('name', '')}' immediately",
                ))
        return leakages

    def _detect_rate_escalation_gaps(self, client_data: dict) -> list:
        leakages = []
        escalation_clauses = client_data.get("escalation_clauses", [])
        current_rates = client_data.get("current_billing_rates", {})
        contract_start = client_data.get("contract_start_date")

        if not contract_start or not escalation_clauses:
            return leakages

        for clause in escalation_clauses:
            escalation_pct = clause.get("percentage", 0)
            frequency_months = clause.get("frequency_months", 12)
            applicable_from = clause.get("applicable_from")

            if applicable_from:
                try:
                    from_date = datetime.fromisoformat(applicable_from)
                    if from_date <= datetime.now():
                        expected_rate = clause.get("base_rate", 0) * (1 + escalation_pct / 100)
                        actual_rate = current_rates.get(clause.get("rate_type", "standard"), 0)

                        if actual_rate < expected_rate:
                            monthly_hours = client_data.get("avg_monthly_hours", 160)
                            rate_gap = expected_rate - actual_rate
                            months_missed = max(1, (datetime.now() - from_date).days // 30)
                            estimated_amount = rate_gap * monthly_hours * months_missed

                            leakages.append(LeakageInstance(
                                leakage_type=LeakageType.RATE_ESCALATION_NOT_APPLIED,
                                description=f"Rate escalation of {escalation_pct}% not applied since {applicable_from}",
                                severity=self._severity_from_amount(estimated_amount, client_data.get("contract_value", 1)),
                                confidence=0.80,
                                estimated_amount=round(estimated_amount, 2),
                                client_id=client_data.get("client_id", ""),
                                contract_id=client_data.get("contract_id", ""),
                                detected_at=datetime.now().isoformat(),
                                evidence={
                                    "expected_rate": expected_rate,
                                    "actual_rate": actual_rate,
                                    "escalation_percentage": escalation_pct,
                                    "months_missed": months_missed,
                                },
                                recommendation="Apply contractual rate escalation and issue back-billing invoice",
                            ))
                except (ValueError, TypeError):
                    pass
        return leakages

    def _detect_unbilled_expenses(self, client_data: dict) -> list:
        leakages = []
        expenses = client_data.get("expenses", [])
        billed_expense_ids = set(client_data.get("billed_expense_ids", []))

        unbilled_expenses = [e for e in expenses if e.get("id") not in billed_expense_ids and e.get("billable", True)]
        total_unbilled = sum(e.get("amount", 0) for e in unbilled_expenses)

        if total_unbilled > 0:
            leakages.append(LeakageInstance(
                leakage_type=LeakageType.EXPENSES_NOT_BILLED,
                description=f"{len(unbilled_expenses)} billable expenses totaling {total_unbilled:.2f} not invoiced",
                severity=self._severity_from_amount(total_unbilled, client_data.get("contract_value", 1)),
                confidence=0.88,
                estimated_amount=round(total_unbilled, 2),
                client_id=client_data.get("client_id", ""),
                contract_id=client_data.get("contract_id", ""),
                detected_at=datetime.now().isoformat(),
                evidence={
                    "unbilled_expense_count": len(unbilled_expenses),
                    "total_unbilled_amount": total_unbilled,
                    "expense_categories": list(set(e.get("category", "other") for e in unbilled_expenses)),
                },
                recommendation="Submit expense reimbursement invoice for all billable expenses",
            ))
        return leakages

    def _detect_scope_creep(self, client_data: dict) -> list:
        leakages = []
        contracted_scope = client_data.get("contracted_scope_hours", 0)
        actual_hours = client_data.get("actual_hours_delivered", 0)

        if contracted_scope > 0:
            scope_overrun_pct = ((actual_hours - contracted_scope) / contracted_scope) * 100

            if scope_overrun_pct > 10:
                excess_hours = actual_hours - contracted_scope
                hourly_rate = client_data.get("contracted_rate", 0)
                estimated_amount = excess_hours * hourly_rate

                severity = Severity.LOW
                if scope_overrun_pct > 50:
                    severity = Severity.CRITICAL
                elif scope_overrun_pct > 30:
                    severity = Severity.HIGH
                elif scope_overrun_pct > 20:
                    severity = Severity.MEDIUM

                leakages.append(LeakageInstance(
                    leakage_type=LeakageType.SCOPE_CREEP,
                    description=f"Scope overrun of {scope_overrun_pct:.1f}% ({excess_hours:.0f} hours over contract)",
                    severity=severity.value,
                    confidence=0.75,
                    estimated_amount=round(estimated_amount, 2),
                    client_id=client_data.get("client_id", ""),
                    contract_id=client_data.get("contract_id", ""),
                    detected_at=datetime.now().isoformat(),
                    evidence={
                        "contracted_hours": contracted_scope,
                        "actual_hours": actual_hours,
                        "overrun_percentage": round(scope_overrun_pct, 1),
                        "excess_hours": excess_hours,
                    },
                    recommendation="Initiate change request process and negotiate scope adjustment or additional billing",
                ))
        return leakages

    def _detect_undercharging(self, client_data: dict) -> list:
        leakages = []
        invoices = client_data.get("invoices", [])
        contracted_rate = client_data.get("contracted_rate", 0)

        for invoice in invoices:
            hours = invoice.get("hours_billed", 0)
            amount = invoice.get("amount", 0)
            if hours > 0:
                effective_rate = amount / hours
                if effective_rate < contracted_rate * 0.95:
                    gap = (contracted_rate - effective_rate) * hours
                    leakages.append(LeakageInstance(
                        leakage_type=LeakageType.UNDERCHARGING,
                        description=f"Invoice {invoice.get('id', '')} billed at {effective_rate:.2f}/hr vs contracted {contracted_rate:.2f}/hr",
                        severity=self._severity_from_amount(gap, client_data.get("contract_value", 1)),
                        confidence=0.82,
                        estimated_amount=round(gap, 2),
                        client_id=client_data.get("client_id", ""),
                        contract_id=client_data.get("contract_id", ""),
                        detected_at=datetime.now().isoformat(),
                        evidence={
                            "invoice_id": invoice.get("id"),
                            "effective_rate": round(effective_rate, 2),
                            "contracted_rate": contracted_rate,
                            "hours": hours,
                        },
                        recommendation="Verify rate applied and issue correction or credit note adjustment",
                    ))
        return leakages

    def _detect_anomalies(self, client_data: dict) -> list:
        leakages = []
        billing_history = client_data.get("billing_history", [])

        if len(billing_history) < 10:
            return leakages

        features = np.array([[
            entry.get("amount", 0),
            entry.get("hours", 0),
            entry.get("expense_amount", 0),
            entry.get("effective_rate", 0),
        ] for entry in billing_history])

        if features.shape[0] < 5:
            return leakages

        scaled_features = self.scaler.fit_transform(features)
        predictions = self.isolation_forest.fit_predict(scaled_features)

        for idx, prediction in enumerate(predictions):
            if prediction == -1:
                entry = billing_history[idx]
                avg_amount = np.mean(features[:, 0])
                deviation = abs(entry.get("amount", 0) - avg_amount)

                leakages.append(LeakageInstance(
                    leakage_type="anomaly_detected",
                    description=f"Anomalous billing pattern in period {entry.get('period', 'unknown')}",
                    severity=Severity.MEDIUM.value,
                    confidence=0.65,
                    estimated_amount=round(deviation, 2),
                    client_id=client_data.get("client_id", ""),
                    contract_id=client_data.get("contract_id", ""),
                    detected_at=datetime.now().isoformat(),
                    evidence={
                        "period": entry.get("period"),
                        "amount": entry.get("amount"),
                        "average_amount": round(avg_amount, 2),
                        "deviation": round(deviation, 2),
                    },
                    recommendation="Review billing entry for potential errors or missed revenue",
                ))
        return leakages

    def _calculate_risk_score(self, leakages: list, client_data: dict) -> float:
        if not leakages:
            return 0.0

        severity_weights = {
            Severity.LOW.value: 1,
            Severity.MEDIUM.value: 2,
            Severity.HIGH.value: 4,
            Severity.CRITICAL.value: 8,
        }

        weighted_sum = sum(
            severity_weights.get(l.severity, 1) * l.confidence
            for l in leakages
        )

        contract_value = client_data.get("contract_value", 1)
        leakage_ratio = sum(l.estimated_amount for l in leakages) / max(contract_value, 1)

        base_score = min(100, (weighted_sum * 5) + (leakage_ratio * 200))
        return min(100.0, base_score)

    def _analyze_trend(self, client_data: dict) -> str:
        historical_leakages = client_data.get("historical_leakage_amounts", [])
        if len(historical_leakages) < 3:
            return "insufficient_data"

        recent = np.mean(historical_leakages[-3:])
        older = np.mean(historical_leakages[:-3]) if len(historical_leakages) > 3 else recent

        if recent > older * 1.2:
            return "worsening"
        elif recent < older * 0.8:
            return "improving"
        return "stable"

    def _severity_from_amount(self, amount: float, contract_value: float) -> str:
        if contract_value <= 0:
            contract_value = 1
        ratio = amount / contract_value

        if ratio > 0.10:
            return Severity.CRITICAL.value
        elif ratio > 0.05:
            return Severity.HIGH.value
        elif ratio > 0.02:
            return Severity.MEDIUM.value
        return Severity.LOW.value
