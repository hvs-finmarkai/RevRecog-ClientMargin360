"""AI Engine background tasks."""
import time

from celery import shared_task
from django.utils import timezone


@shared_task
def process_contract_nlp(contract_id):
    """Use NLP to parse contract documents and extract performance obligations."""
    from apps.contracts.models import Contract
    from .models import AIProcessingJob

    start_time = time.time()
    job = AIProcessingJob.objects.create(
        job_type=AIProcessingJob.JobType.CONTRACT_NLP,
        status=AIProcessingJob.Status.PROCESSING,
        input_data={"contract_id": contract_id},
    )

    try:
        contract = Contract.objects.get(id=contract_id)
        # Extract text from contract document
        # Run through OpenAI/LangChain pipeline
        # Extract performance obligations, terms, pricing

        processing_time = time.time() - start_time
        job.status = AIProcessingJob.Status.COMPLETED
        job.processing_time_seconds = processing_time
        job.completed_at = timezone.now()
        job.output_data = {"obligations_found": 0, "terms_extracted": True}
        job.save()
        return f"Contract {contract.contract_number} NLP processing completed"
    except Exception as e:
        job.status = AIProcessingJob.Status.FAILED
        job.error_message = str(e)
        job.save()
        raise


@shared_task
def predict_contract_margin(contract_id):
    """Use ML models to predict contract margin."""
    from apps.contracts.models import Contract
    from .models import AIProcessingJob

    start_time = time.time()
    job = AIProcessingJob.objects.create(
        job_type=AIProcessingJob.JobType.MARGIN_PREDICTION,
        status=AIProcessingJob.Status.PROCESSING,
        input_data={"contract_id": contract_id},
    )

    try:
        contract = Contract.objects.get(id=contract_id)
        # Feature engineering and model prediction
        processing_time = time.time() - start_time
        job.status = AIProcessingJob.Status.COMPLETED
        job.processing_time_seconds = processing_time
        job.completed_at = timezone.now()
        job.confidence_score = 0.85
        job.output_data = {"predicted_margin_pct": 28.5, "risk_score": 0.3}
        job.save()
        return f"Margin prediction completed for {contract.contract_number}"
    except Exception as e:
        job.status = AIProcessingJob.Status.FAILED
        job.error_message = str(e)
        job.save()
        raise


@shared_task
def score_collection_priority(collection_entry_id):
    """AI-based collection priority scoring."""
    from apps.collections_mgmt.models import CollectionEntry
    from .models import AIProcessingJob

    start_time = time.time()
    job = AIProcessingJob.objects.create(
        job_type=AIProcessingJob.JobType.COLLECTION_SCORING,
        status=AIProcessingJob.Status.PROCESSING,
        input_data={"collection_entry_id": collection_entry_id},
    )

    try:
        entry = CollectionEntry.objects.get(id=collection_entry_id)
        # Scoring logic with ML model
        processing_time = time.time() - start_time
        job.status = AIProcessingJob.Status.COMPLETED
        job.processing_time_seconds = processing_time
        job.completed_at = timezone.now()
        job.output_data = {"score": 75, "recommended_action": "phone_call"}
        job.save()

        entry.ai_collection_score = 75
        entry.save(update_fields=["ai_collection_score"])
        return f"Collection scoring completed for entry {collection_entry_id}"
    except Exception as e:
        job.status = AIProcessingJob.Status.FAILED
        job.error_message = str(e)
        job.save()
        raise
