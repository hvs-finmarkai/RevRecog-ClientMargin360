import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from typing import Optional

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures


@dataclass
class ForecastPoint:
    period: str
    predicted_revenue: float
    lower_bound: float
    upper_bound: float
    confidence: float

    def to_dict(self):
        return asdict(self)


@dataclass
class CashFlowPrediction:
    period: str
    expected_inflow: float
    expected_timing_days: int
    probability_on_time: float

    def to_dict(self):
        return asdict(self)


@dataclass
class ForecastResult:
    client_id: str
    forecast_generated_at: str
    three_month_forecast: list
    six_month_forecast: list
    twelve_month_forecast: list
    total_forecast_3m: float
    total_forecast_6m: float
    total_forecast_12m: float
    cash_flow_predictions: list
    model_accuracy: float
    confidence_level: str
    assumptions: list
    risk_factors: list

    def to_dict(self):
        return {
            "client_id": self.client_id,
            "forecast_generated_at": self.forecast_generated_at,
            "three_month_forecast": [f.to_dict() for f in self.three_month_forecast],
            "six_month_forecast": [f.to_dict() for f in self.six_month_forecast],
            "twelve_month_forecast": [f.to_dict() for f in self.twelve_month_forecast],
            "total_forecast_3m": self.total_forecast_3m,
            "total_forecast_6m": self.total_forecast_6m,
            "total_forecast_12m": self.total_forecast_12m,
            "cash_flow_predictions": [c.to_dict() for c in self.cash_flow_predictions],
            "model_accuracy": self.model_accuracy,
            "confidence_level": self.confidence_level,
            "assumptions": self.assumptions,
            "risk_factors": self.risk_factors,
        }


class RevenueForecastService:
    def __init__(self, confidence_interval: float = 0.90):
        self.confidence_interval = confidence_interval
        self.linear_model = LinearRegression()
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

    def forecast(self, client_data: dict) -> ForecastResult:
        revenue_history = client_data.get("revenue_history", [])
        if len(revenue_history) < 6:
            return self._insufficient_data_result(client_data)

        features, targets = self._prepare_features(revenue_history, client_data)
        model_accuracy = self._train_models(features, targets)

        three_month = self._generate_forecast(client_data, features, targets, 3)
        six_month = self._generate_forecast(client_data, features, targets, 6)
        twelve_month = self._generate_forecast(client_data, features, targets, 12)

        cash_flow = self._predict_cash_flow(client_data, three_month + six_month[3:] + twelve_month[6:])

        confidence_level = self._determine_confidence_level(model_accuracy, len(revenue_history))

        return ForecastResult(
            client_id=client_data.get("client_id", ""),
            forecast_generated_at=datetime.now().isoformat(),
            three_month_forecast=three_month,
            six_month_forecast=six_month,
            twelve_month_forecast=twelve_month,
            total_forecast_3m=round(sum(f.predicted_revenue for f in three_month), 2),
            total_forecast_6m=round(sum(f.predicted_revenue for f in six_month), 2),
            total_forecast_12m=round(sum(f.predicted_revenue for f in twelve_month), 2),
            cash_flow_predictions=cash_flow,
            model_accuracy=round(model_accuracy, 3),
            confidence_level=confidence_level,
            assumptions=self._generate_assumptions(client_data),
            risk_factors=self._identify_risk_factors(client_data),
        )

    def _prepare_features(self, revenue_history: list, client_data: dict) -> tuple:
        n = len(revenue_history)
        features = []
        targets = []

        for i in range(n):
            month_index = i
            month_of_year = (i % 12) + 1
            quarter = ((month_of_year - 1) // 3) + 1

            lag_1 = revenue_history[i - 1] if i > 0 else revenue_history[0]
            lag_3 = revenue_history[i - 3] if i > 2 else revenue_history[0]
            rolling_avg_3 = np.mean(revenue_history[max(0, i - 2):i + 1])
            rolling_avg_6 = np.mean(revenue_history[max(0, i - 5):i + 1])

            growth_rate = (revenue_history[i] - lag_1) / max(lag_1, 1) if i > 0 else 0

            seasonality_sin = np.sin(2 * np.pi * month_of_year / 12)
            seasonality_cos = np.cos(2 * np.pi * month_of_year / 12)

            health_score = client_data.get("health_score", 50) / 100
            pipeline_value = client_data.get("pipeline_value", 0)

            features.append([
                month_index,
                month_of_year,
                quarter,
                lag_1,
                lag_3,
                rolling_avg_3,
                rolling_avg_6,
                growth_rate,
                seasonality_sin,
                seasonality_cos,
                health_score,
                pipeline_value,
            ])
            targets.append(revenue_history[i])

        return np.array(features), np.array(targets)

    def _train_models(self, features: np.ndarray, targets: np.ndarray) -> float:
        if len(features) < 4:
            return 0.0

        split_idx = max(2, int(len(features) * 0.8))
        train_x, test_x = features[:split_idx], features[split_idx:]
        train_y, test_y = targets[:split_idx], targets[split_idx:]

        self.linear_model.fit(train_x, train_y)
        self.rf_model.fit(train_x, train_y)

        if len(test_x) > 0:
            linear_pred = self.linear_model.predict(test_x)
            rf_pred = self.rf_model.predict(test_x)
            ensemble_pred = (linear_pred + rf_pred) / 2

            mape = np.mean(np.abs((test_y - ensemble_pred) / np.maximum(test_y, 1))) * 100
            accuracy = max(0, 100 - mape) / 100
        else:
            accuracy = 0.5

        self.linear_model.fit(features, targets)
        self.rf_model.fit(features, targets)

        return accuracy

    def _generate_forecast(self, client_data: dict, features: np.ndarray, targets: np.ndarray, months: int) -> list:
        forecast_points = []
        last_idx = len(targets) - 1
        revenue_history = list(targets)

        residuals = targets - (self.linear_model.predict(features) + self.rf_model.predict(features)) / 2
        residual_std = np.std(residuals) if len(residuals) > 1 else np.std(targets) * 0.1

        z_score = 1.645 if self.confidence_interval == 0.90 else 1.96

        for i in range(months):
            future_idx = last_idx + 1 + i
            month_of_year = ((future_idx) % 12) + 1
            quarter = ((month_of_year - 1) // 3) + 1

            recent_history = revenue_history[-(min(6, len(revenue_history))):]
            lag_1 = revenue_history[-1]
            lag_3 = revenue_history[-3] if len(revenue_history) >= 3 else revenue_history[0]
            rolling_avg_3 = np.mean(revenue_history[-3:])
            rolling_avg_6 = np.mean(revenue_history[-6:]) if len(revenue_history) >= 6 else np.mean(revenue_history)

            growth_rate = (revenue_history[-1] - revenue_history[-2]) / max(revenue_history[-2], 1) if len(revenue_history) >= 2 else 0

            seasonality_sin = np.sin(2 * np.pi * month_of_year / 12)
            seasonality_cos = np.cos(2 * np.pi * month_of_year / 12)

            health_score = client_data.get("health_score", 50) / 100
            pipeline_value = client_data.get("pipeline_value", 0)

            future_features = np.array([[
                future_idx,
                month_of_year,
                quarter,
                lag_1,
                lag_3,
                rolling_avg_3,
                rolling_avg_6,
                growth_rate,
                seasonality_sin,
                seasonality_cos,
                health_score,
                pipeline_value,
            ]])

            linear_pred = self.linear_model.predict(future_features)[0]
            rf_pred = self.rf_model.predict(future_features)[0]
            ensemble_pred = (linear_pred + rf_pred) / 2

            uncertainty_growth = 1 + (i * 0.1)
            interval_width = z_score * residual_std * uncertainty_growth

            predicted = max(0, ensemble_pred)
            lower = max(0, predicted - interval_width)
            upper = predicted + interval_width

            confidence = max(0.3, 1.0 - (i * 0.05))

            base_date = datetime.now()
            forecast_date = base_date + timedelta(days=30 * (i + 1))
            period_label = forecast_date.strftime("%Y-%m")

            forecast_points.append(ForecastPoint(
                period=period_label,
                predicted_revenue=round(predicted, 2),
                lower_bound=round(lower, 2),
                upper_bound=round(upper, 2),
                confidence=round(confidence, 3),
            ))

            revenue_history.append(predicted)

        return forecast_points

    def _predict_cash_flow(self, client_data: dict, forecast_points: list) -> list:
        payment_terms_days = client_data.get("payment_terms_days", 30)
        historical_delay = client_data.get("avg_payment_delay_days", 0)
        expected_timing = payment_terms_days + historical_delay

        payment_reliability = client_data.get("payment_reliability_score", 80) / 100

        predictions = []
        for point in forecast_points[:6]:
            predictions.append(CashFlowPrediction(
                period=point.period,
                expected_inflow=round(point.predicted_revenue, 2),
                expected_timing_days=expected_timing,
                probability_on_time=round(payment_reliability, 2),
            ))
        return predictions

    def _determine_confidence_level(self, accuracy: float, data_points: int) -> str:
        if accuracy > 0.85 and data_points >= 24:
            return "HIGH"
        elif accuracy > 0.70 and data_points >= 12:
            return "MEDIUM"
        return "LOW"

    def _generate_assumptions(self, client_data: dict) -> list:
        assumptions = [
            "Historical revenue patterns continue with similar trajectory",
            "No major contract changes or cancellations in forecast period",
            "Market conditions remain comparable to recent history",
        ]

        if client_data.get("pipeline_value", 0) > 0:
            assumptions.append("Pipeline opportunities convert at historical win rates")

        if client_data.get("contract_renewal_pending", False):
            assumptions.append("Contract renewal proceeds on similar or improved terms")

        return assumptions

    def _identify_risk_factors(self, client_data: dict) -> list:
        risks = []

        margin = client_data.get("current_margin", 25)
        if margin < 15:
            risks.append("Low margin may trigger contract renegotiation or scope reduction")

        contract_months_remaining = client_data.get("contract_expiry_months", 12)
        if contract_months_remaining < 6:
            risks.append("Contract expiring within forecast window")

        health_score = client_data.get("health_score", 50)
        if health_score < 40:
            risks.append("Poor client health score indicates engagement instability")

        revenue_volatility = client_data.get("revenue_volatility", 0)
        if revenue_volatility > 0.3:
            risks.append("High revenue volatility reduces forecast reliability")

        return risks

    def _insufficient_data_result(self, client_data: dict) -> ForecastResult:
        return ForecastResult(
            client_id=client_data.get("client_id", ""),
            forecast_generated_at=datetime.now().isoformat(),
            three_month_forecast=[],
            six_month_forecast=[],
            twelve_month_forecast=[],
            total_forecast_3m=0,
            total_forecast_6m=0,
            total_forecast_12m=0,
            cash_flow_predictions=[],
            model_accuracy=0.0,
            confidence_level="INSUFFICIENT_DATA",
            assumptions=["Insufficient historical data for reliable forecasting"],
            risk_factors=["Less than 6 months of revenue history available"],
        )
