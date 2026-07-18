import re
import json
from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

import spacy
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image

from ..prompts.templates import CONTRACT_EXTRACTION_PROMPT


@dataclass
class ExtractedField:
    value: object
    confidence: float
    source: str = "nlp"


@dataclass
class ContractExtractionResult:
    contract_number: ExtractedField = None
    client_name: ExtractedField = None
    billing_model: ExtractedField = None
    start_date: ExtractedField = None
    end_date: ExtractedField = None
    total_value: ExtractedField = None
    payment_terms: ExtractedField = None
    escalation_clauses: ExtractedField = None
    milestones: ExtractedField = None
    raw_text: str = ""
    overall_confidence: float = 0.0
    validation_errors: list = field(default_factory=list)

    def to_dict(self):
        result = {}
        for field_name in [
            "contract_number", "client_name", "billing_model", "start_date",
            "end_date", "total_value", "payment_terms", "escalation_clauses", "milestones"
        ]:
            field_val = getattr(self, field_name)
            if field_val:
                result[field_name] = asdict(field_val)
        result["overall_confidence"] = self.overall_confidence
        result["validation_errors"] = self.validation_errors
        return result


class LLMClient:
    def __init__(self, provider: str = "ollama", base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.provider = provider
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str) -> str:
        if self.provider == "ollama":
            import requests
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False}
            )
            response.raise_for_status()
            return response.json().get("response", "")
        raise ValueError(f"Unsupported LLM provider: {self.provider}")


class ContractParserService:
    BILLING_MODELS = ["time_and_materials", "fixed_price", "milestone", "retainer", "hybrid", "outcome_based"]
    PAYMENT_TERMS_PATTERNS = [
        r"net\s*(\d+)",
        r"payment\s+within\s+(\d+)\s+days",
        r"(\d+)\s+days?\s+from\s+invoice",
    ]
    AMOUNT_PATTERN = r"(?:USD|INR|EUR|GBP|\$|₹|€|£)\s*[\d,]+(?:\.\d{2})?|[\d,]+(?:\.\d{2})?\s*(?:USD|INR|EUR|GBP)"
    CONTRACT_NUMBER_PATTERNS = [
        r"contract\s*(?:no|number|#|id)[:\s]*([A-Z0-9\-/]+)",
        r"agreement\s*(?:no|number|#|id)[:\s]*([A-Z0-9\-/]+)",
        r"ref(?:erence)?[:\s]*([A-Z0-9\-/]+)",
    ]

    def __init__(self, spacy_model: str = "en_core_web_sm", llm_config: Optional[dict] = None):
        self.nlp = spacy.load(spacy_model)
        self.llm_client = None
        if llm_config:
            self.llm_client = LLMClient(**llm_config)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        images = convert_from_path(pdf_path)
        extracted_pages = []
        for image in images:
            page_text = pytesseract.image_to_string(image)
            extracted_pages.append(page_text)
        return "\n\n".join(extracted_pages)

    def extract_text_from_pdf_bytes(self, pdf_bytes: bytes) -> str:
        images = convert_from_bytes(pdf_bytes)
        extracted_pages = []
        for image in images:
            page_text = pytesseract.image_to_string(image)
            extracted_pages.append(page_text)
        return "\n\n".join(extracted_pages)

    def extract_text_from_image(self, image_path: str) -> str:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image)

    def parse_contract(self, source: str, source_type: str = "pdf") -> ContractExtractionResult:
        if source_type == "pdf":
            raw_text = self.extract_text_from_pdf(source)
        elif source_type == "pdf_bytes":
            raw_text = self.extract_text_from_pdf_bytes(source)
        elif source_type == "image":
            raw_text = self.extract_text_from_image(source)
        elif source_type == "text":
            raw_text = source
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

        result = self._extract_with_nlp(raw_text)

        if self.llm_client:
            llm_result = self._extract_with_llm(raw_text)
            result = self._merge_results(result, llm_result)

        result.raw_text = raw_text
        result.overall_confidence = self._calculate_overall_confidence(result)
        result.validation_errors = self._validate_extraction(result)
        return result

    def _extract_with_nlp(self, text: str) -> ContractExtractionResult:
        doc = self.nlp(text)
        result = ContractExtractionResult()
        result.contract_number = self._extract_contract_number(text)
        result.client_name = self._extract_client_name(doc, text)
        result.billing_model = self._extract_billing_model(text)
        result.start_date = self._extract_dates(doc, text, "start")
        result.end_date = self._extract_dates(doc, text, "end")
        result.total_value = self._extract_total_value(text)
        result.payment_terms = self._extract_payment_terms(text)
        result.escalation_clauses = self._extract_escalation_clauses(text)
        result.milestones = self._extract_milestones(text)
        return result

    def _extract_contract_number(self, text: str) -> ExtractedField:
        for pattern in self.CONTRACT_NUMBER_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return ExtractedField(value=match.group(1).strip(), confidence=0.85, source="regex")
        return ExtractedField(value=None, confidence=0.0, source="regex")

    def _extract_client_name(self, doc, text: str) -> ExtractedField:
        org_entities = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
        party_patterns = [
            r"(?:between|party|client|customer)[:\s]+([A-Z][A-Za-z\s&.,]+(?:Ltd|LLC|Inc|Corp|Pvt|Private|Limited)?)",
            r"(?:M/s|Messrs)[.\s]+([A-Z][A-Za-z\s&.,]+)",
        ]
        for pattern in party_patterns:
            match = re.search(pattern, text)
            if match:
                return ExtractedField(value=match.group(1).strip(), confidence=0.80, source="regex")
        if org_entities:
            return ExtractedField(value=org_entities[0], confidence=0.65, source="nlp")
        return ExtractedField(value=None, confidence=0.0, source="nlp")

    def _extract_billing_model(self, text: str) -> ExtractedField:
        text_lower = text.lower()
        billing_indicators = {
            "time_and_materials": ["time and material", "t&m", "hourly rate", "per hour"],
            "fixed_price": ["fixed price", "fixed fee", "lump sum", "fixed cost"],
            "milestone": ["milestone", "deliverable-based", "phase-based"],
            "retainer": ["retainer", "monthly fee", "recurring fee", "subscription"],
            "hybrid": ["hybrid", "mixed model", "combination"],
            "outcome_based": ["outcome-based", "performance-based", "success fee"],
        }
        detected_models = {}
        for model, keywords in billing_indicators.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected_models[model] = detected_models.get(model, 0) + 1
        if detected_models:
            best_model = max(detected_models, key=detected_models.get)
            confidence = min(0.9, 0.6 + (detected_models[best_model] * 0.1))
            return ExtractedField(value=best_model, confidence=confidence, source="regex")
        return ExtractedField(value=None, confidence=0.0, source="regex")

    def _extract_dates(self, doc, text: str, date_type: str) -> ExtractedField:
        date_entities = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
        if date_type == "start":
            patterns = [
                r"(?:start|commencement|effective)\s*(?:date)?[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(?:start|commencement|effective)\s*(?:date)?[:\s]*(\w+\s+\d{1,2},?\s+\d{4})",
            ]
        else:
            patterns = [
                r"(?:end|expiry|termination|completion)\s*(?:date)?[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                r"(?:end|expiry|termination|completion)\s*(?:date)?[:\s]*(\w+\s+\d{1,2},?\s+\d{4})",
            ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return ExtractedField(value=match.group(1).strip(), confidence=0.80, source="regex")
        if date_entities:
            idx = 0 if date_type == "start" else min(1, len(date_entities) - 1)
            return ExtractedField(value=date_entities[idx], confidence=0.50, source="nlp")
        return ExtractedField(value=None, confidence=0.0, source="nlp")

    def _extract_total_value(self, text: str) -> ExtractedField:
        value_patterns = [
            r"(?:total|contract)\s*(?:value|amount|price|consideration)[:\s]*(" + self.AMOUNT_PATTERN + r")",
            r"(?:aggregate|overall)\s*(?:value|fee|cost)[:\s]*(" + self.AMOUNT_PATTERN + r")",
        ]
        for pattern in value_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return ExtractedField(value=match.group(1).strip(), confidence=0.80, source="regex")
        all_amounts = re.findall(self.AMOUNT_PATTERN, text)
        if all_amounts:
            largest = max(all_amounts, key=lambda x: float(re.sub(r"[^\d.]", "", x) or "0"))
            return ExtractedField(value=largest, confidence=0.45, source="regex")
        return ExtractedField(value=None, confidence=0.0, source="regex")

    def _extract_payment_terms(self, text: str) -> ExtractedField:
        for pattern in self.PAYMENT_TERMS_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                days = match.group(1)
                return ExtractedField(value=f"Net {days}", confidence=0.85, source="regex")
        return ExtractedField(value=None, confidence=0.0, source="regex")

    def _extract_escalation_clauses(self, text: str) -> ExtractedField:
        escalation_patterns = [
            r"(?:escalation|increase|adjustment)[^.]*(?:\d+(?:\.\d+)?%)[^.]*\.",
            r"(?:annual|yearly|periodic)\s*(?:rate|price|fee)\s*(?:increase|adjustment)[^.]*\.",
        ]
        clauses = []
        for pattern in escalation_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            clauses.extend(matches)
        if clauses:
            return ExtractedField(value=clauses, confidence=0.70, source="regex")
        return ExtractedField(value=[], confidence=0.3, source="regex")

    def _extract_milestones(self, text: str) -> ExtractedField:
        milestone_patterns = [
            r"(?:milestone|phase|deliverable)\s*(\d+)[:\s]*([^,\n]+)",
            r"(?:stage|sprint)\s*(\d+)[:\s]*([^,\n]+)",
        ]
        milestones = []
        for pattern in milestone_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                milestones.append({
                    "number": match.group(1),
                    "description": match.group(2).strip(),
                })
        confidence = 0.75 if milestones else 0.0
        return ExtractedField(value=milestones, confidence=confidence, source="regex")

    def _extract_with_llm(self, text: str) -> ContractExtractionResult:
        prompt = CONTRACT_EXTRACTION_PROMPT.format(contract_text=text[:4000])
        response = self.llm_client.generate(prompt)
        try:
            parsed = json.loads(response)
        except json.JSONDecodeError:
            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                parsed = json.loads(json_match.group())
            else:
                return ContractExtractionResult()
        result = ContractExtractionResult()
        field_mapping = {
            "contract_number": "contract_number",
            "client_name": "client_name",
            "billing_model": "billing_model",
            "start_date": "start_date",
            "end_date": "end_date",
            "total_value": "total_value",
            "payment_terms": "payment_terms",
            "escalation_clauses": "escalation_clauses",
            "milestones": "milestones",
        }
        for json_key, field_name in field_mapping.items():
            if json_key in parsed:
                confidence = parsed.get(f"{json_key}_confidence", 0.7)
                setattr(result, field_name, ExtractedField(
                    value=parsed[json_key], confidence=confidence, source="llm"
                ))
        return result

    def _merge_results(self, nlp_result: ContractExtractionResult, llm_result: ContractExtractionResult) -> ContractExtractionResult:
        merged = ContractExtractionResult()
        fields = [
            "contract_number", "client_name", "billing_model", "start_date",
            "end_date", "total_value", "payment_terms", "escalation_clauses", "milestones"
        ]
        for field_name in fields:
            nlp_field = getattr(nlp_result, field_name)
            llm_field = getattr(llm_result, field_name)
            if nlp_field and llm_field and nlp_field.value and llm_field.value:
                if nlp_field.value == llm_field.value:
                    merged_field = ExtractedField(
                        value=nlp_field.value,
                        confidence=min(1.0, (nlp_field.confidence + llm_field.confidence) / 2 + 0.1),
                        source="consensus"
                    )
                elif nlp_field.confidence >= llm_field.confidence:
                    merged_field = nlp_field
                else:
                    merged_field = llm_field
            elif nlp_field and nlp_field.value:
                merged_field = nlp_field
            elif llm_field and llm_field.value:
                merged_field = llm_field
            else:
                merged_field = ExtractedField(value=None, confidence=0.0, source="none")
            setattr(merged, field_name, merged_field)
        return merged

    def _calculate_overall_confidence(self, result: ContractExtractionResult) -> float:
        fields = ["contract_number", "client_name", "billing_model", "start_date", "end_date", "total_value", "payment_terms"]
        weights = [0.15, 0.20, 0.15, 0.10, 0.10, 0.15, 0.15]
        total_weight = 0.0
        weighted_confidence = 0.0
        for field_name, weight in zip(fields, weights):
            field_val = getattr(result, field_name)
            if field_val:
                weighted_confidence += field_val.confidence * weight
                total_weight += weight
        if total_weight == 0:
            return 0.0
        return round(weighted_confidence / total_weight, 3)

    def _validate_extraction(self, result: ContractExtractionResult) -> list:
        errors = []
        if result.start_date and result.end_date and result.start_date.value and result.end_date.value:
            try:
                start = self._parse_date(result.start_date.value)
                end = self._parse_date(result.end_date.value)
                if start and end and start >= end:
                    errors.append("End date is before or equal to start date")
            except (ValueError, TypeError):
                pass
        if result.billing_model and result.billing_model.value:
            if result.billing_model.value not in self.BILLING_MODELS:
                errors.append(f"Unknown billing model: {result.billing_model.value}")
        if result.total_value and result.total_value.value:
            try:
                numeric_value = float(re.sub(r"[^\d.]", "", str(result.total_value.value)))
                if numeric_value <= 0:
                    errors.append("Contract value must be positive")
            except (ValueError, TypeError):
                errors.append("Could not parse contract value as numeric")
        required_fields = ["client_name", "billing_model", "total_value"]
        for field_name in required_fields:
            field_val = getattr(result, field_name)
            if not field_val or not field_val.value:
                errors.append(f"Required field missing: {field_name}")
        return errors

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        formats = ["%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d", "%d-%m-%Y", "%B %d, %Y", "%b %d, %Y"]
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        return None
