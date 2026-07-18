"""Analytics background tasks."""
from celery import shared_task
from django.utils import timezone
from django.db.models import Sum, Count, Avg


@shared_task
def compute_dashboard_metrics():
    """Compute and cache dashboard metrics."""
    from .models import MetricSnapshot
    from apps.contracts.models import Contract
    from apps.invoices.models import Invoice
    from apps.recognition.models import RevenueRecognitionEvent

    period = timezone.now().strftime("%Y-%m")

    # Total Revenue Recognized
    total_recognized = RevenueRecognitionEvent.objects.filter(
        status="recognized", period=period
    ).aggregate(total=Sum("amount"))["total"] or 0

    MetricSnapshot.objects.update_or_create(
        metric_name="total_revenue_recognized", period=period,
        defaults={"metric_value": float(total_recognized), "computed_at": timezone.now()}
    )

    # Active Contracts
    active_contracts = Contract.objects.filter(status="active").count()
    MetricSnapshot.objects.update_or_create(
        metric_name="active_contracts", period=period,
        defaults={"metric_value": active_contracts, "computed_at": timezone.now()}
    )

    # Outstanding Collections
    outstanding = Invoice.objects.filter(
        status__in=["sent", "partially_paid", "overdue"]
    ).aggregate(total=Sum("total_amount"))["total"] or 0

    MetricSnapshot.objects.update_or_create(
        metric_name="total_outstanding", period=period,
        defaults={"metric_value": float(outstanding), "computed_at": timezone.now()}
    )

    return f"Computed dashboard metrics for {period}"


@shared_task
def compute_trend_data():
    """Compute trend data for charts over the last 12 months."""
    from .models import MetricSnapshot
    from apps.recognition.models import RevenueRecognitionEvent
    from django.db.models.functions import TruncMonth

    # Monthly revenue trend
    twelve_months_ago = timezone.now() - timezone.timedelta(days=365)
    monthly_revenue = (
        RevenueRecognitionEvent.objects.filter(
            status="recognized", recognition_date__gte=twelve_months_ago
        )
        .annotate(month=TruncMonth("recognition_date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    for entry in monthly_revenue:
        period = entry["month"].strftime("%Y-%m")
        MetricSnapshot.objects.update_or_create(
            metric_name="monthly_revenue_trend", period=period,
            defaults={"metric_value": float(entry["total"]), "computed_at": timezone.now()}
        )

    return "Computed trend data"
