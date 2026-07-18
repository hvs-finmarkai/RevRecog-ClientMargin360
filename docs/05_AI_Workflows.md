# AI Workflows Documentation

## RevRecog AI + ClientMargin360 — AI Engine Specifications

---

## 1. Contract Parser AI

### Workflow Pipeline

```
PDF Upload → OCR (Tesseract) → Raw Text → spaCy NLP → Entity Extraction → Validation → Confidence Score → Review Queue → Database
```

### Stage Details

| Stage | Technology | Input | Output |
|-------|-----------|-------|--------|
| Document Intake | Django File Upload | PDF/DOCX/Image | Stored file + metadata |
| OCR Processing | Tesseract 5.x | Image/PDF pages | Raw text blocks |
| Text Preprocessing | Python (regex, ftfy) | Raw text | Cleaned, normalized text |
| NLP Processing | spaCy (en_core_web_lg) | Cleaned text | Doc object with entities |
| Entity Extraction | Custom spaCy pipeline | Doc object | Structured entities |
| Validation | Rule engine | Extracted entities | Validated entities + flags |
| Confidence Scoring | Weighted algorithm | Validation results | Score 0.0–1.0 |
| Review Queue | Django + Celery | Low-confidence items | Human review assignments |
| Database Storage | PostgreSQL | Validated entities | Contract records |

### Entity Extraction Targets

- Client name and legal entity
- Contract start date and end date
- Total contract value (TCV)
- Payment terms (Net 30, Net 60, milestone-based)
- Performance obligations (deliverables)
- Variable consideration clauses
- Renewal terms and termination clauses
- SLA metrics and penalties
- Billing frequency and escalation rates

### Model Specifications

| Component | Model | Version | License |
|-----------|-------|---------|---------|
| OCR Engine | Tesseract | 5.3.x | Apache 2.0 |
| NLP Pipeline | spaCy | 3.7.x | MIT |
| Language Model | en_core_web_lg | 3.7.x | MIT |
| Custom NER | spaCy trained model | Custom | Proprietary |
| Date Parser | dateutil | 2.8.x | Apache 2.0 |
| Currency Parser | Custom regex + babel | - | BSD |

### Prompt Templates

#### Entity Extraction Template

```
Given the following contract text, extract structured information:

TEXT: {document_text}

Extract the following fields:
- client_name: Legal name of the client
- contract_value: Total contract value with currency
- start_date: Contract effective date (ISO format)
- end_date: Contract expiration date (ISO format)
- payment_terms: Payment terms description
- performance_obligations: List of deliverables
- billing_frequency: How often invoices are generated
- renewal_type: Auto-renewal, manual, or fixed-term

Confidence: Rate each field extraction 0.0–1.0
```

#### Validation Template

```
Validate the following extracted contract data against business rules:

EXTRACTED DATA: {entities_json}

Rules:
1. end_date must be after start_date
2. contract_value must be positive
3. payment_terms must match known patterns
4. All required fields must be present

Return validation status and issues found.
```

### Fallback Strategy

1. **OCR Failure**: Retry with different preprocessing (deskew, binarization, contrast adjustment)
2. **Low Confidence (<0.6)**: Route to manual review queue with highlighted problem areas
3. **NLP Model Unavailable**: Fall back to regex-based extraction for critical fields
4. **Partial Extraction**: Store partial results, flag missing fields, notify reviewer

---

## 2. Leakage Detection AI

### Workflow Pipeline

```
Data Collection → Feature Engineering → IsolationForest → Rule Engine → Scoring → Alert Generation → Dashboard
```

### Stage Details

| Stage | Technology | Input | Output |
|-------|-----------|-------|--------|
| Data Collection | Django ORM + Pandas | Multiple DB tables | Unified DataFrame |
| Feature Engineering | Pandas + NumPy | Raw data | Engineered features |
| Anomaly Detection | scikit-learn IsolationForest | Feature matrix | Anomaly scores |
| Rule Engine | Custom Python | Business rules + data | Rule violations |
| Composite Scoring | Weighted algorithm | Anomaly + rule scores | Leakage score 0–100 |
| Alert Generation | Celery tasks | High scores | Alert records |
| Dashboard | React + Chart.js | Alert records | Visual dashboard |

### Feature Engineering

| Feature | Description | Source Tables |
|---------|-------------|---------------|
| billing_ratio | Billed hours / worked hours | Timesheets, Invoices |
| rate_deviation | Actual rate vs contracted rate | Contracts, Invoices |
| milestone_delay | Days past due on milestones | Milestones, Contracts |
| unbilled_hours | Hours logged but not invoiced | Timesheets, Invoices |
| escalation_gap | Expected vs actual rate increases | Contracts, Invoices |
| scope_creep_index | Additional work without billing | Timesheets, SOW |
| collection_efficiency | Collected / Invoiced ratio | Invoices, Payments |
| margin_erosion_rate | Margin change over time | Profitability snapshots |

### Model Specifications

| Component | Model | Parameters | License |
|-----------|-------|-----------|---------|
| Anomaly Detector | IsolationForest | n_estimators=200, contamination=0.05 | BSD (scikit-learn) |
| Feature Scaler | StandardScaler | - | BSD (scikit-learn) |
| Rule Engine | Custom Python | Configurable thresholds | Proprietary |
| Scoring | Weighted ensemble | anomaly_weight=0.4, rule_weight=0.6 | Proprietary |

### Detection Rules

```python
LEAKAGE_RULES = {
    "unbilled_hours": {
        "threshold": 8,
        "severity": "high",
        "description": "Hours worked but not billed exceeding threshold"
    },
    "rate_below_contract": {
        "threshold": 0.95,
        "severity": "critical",
        "description": "Billing rate below 95% of contracted rate"
    },
    "missed_escalation": {
        "threshold": 30,
        "severity": "medium",
        "description": "Rate escalation not applied within 30 days of due date"
    },
    "scope_creep": {
        "threshold": 1.15,
        "severity": "high",
        "description": "Delivered scope exceeds contracted scope by 15%"
    },
    "late_invoicing": {
        "threshold": 7,
        "severity": "medium",
        "description": "Invoice generated more than 7 days after period end"
    }
}
```

### Fallback Strategy

1. **Insufficient Data**: Use rule-based detection only (skip ML model)
2. **Model Training Failure**: Fall back to previous model version
3. **Feature Computation Error**: Use available features subset, flag reduced confidence
4. **High False Positive Rate**: Auto-adjust contamination parameter, increase threshold

---

## 3. Recommendation Engine

### Workflow Pipeline

```
Client Data → Health Score → Decision Tree → Impact Estimation → Priority → Recommendation
```

### Stage Details

| Stage | Technology | Input | Output |
|-------|-----------|-------|--------|
| Client Data Aggregation | Django ORM + Pandas | Multiple sources | Client profile DataFrame |
| Health Score Calculation | Weighted algorithm | Client metrics | Score 0–100 |
| Decision Tree | scikit-learn DecisionTreeClassifier | Health score + features | Action category |
| Impact Estimation | Linear model | Action + client data | Revenue impact estimate |
| Priority Assignment | Scoring algorithm | Impact + urgency + effort | Priority rank |
| Recommendation Output | Template engine | All above | Actionable recommendation |

### Health Score Components

| Metric | Weight | Calculation |
|--------|--------|-------------|
| Revenue Growth | 0.20 | YoY revenue change percentage |
| Margin Health | 0.25 | Current margin vs target margin |
| Collection Speed | 0.15 | Average DSO vs terms |
| Contract Utilization | 0.15 | Actual vs contracted capacity |
| Relationship Tenure | 0.10 | Months of active engagement |
| Leakage Score | 0.15 | Inverse of leakage detection score |

### Recommendation Categories

| Category | Trigger Conditions | Potential Actions |
|----------|-------------------|-------------------|
| **Reprice** | Margin < target, market rates increased | Rate card adjustment, contract amendment |
| **Expand** | High utilization, strong health score | Upsell services, increase headcount |
| **Restructure** | Mixed signals, operational inefficiency | SOW revision, team composition change |
| **Exit** | Sustained negative margin, high leakage | Graceful transition plan, contract non-renewal |

### Model Specifications

| Component | Model | Parameters | License |
|-----------|-------|-----------|---------|
| Decision Tree | DecisionTreeClassifier | max_depth=6, min_samples_leaf=10 | BSD (scikit-learn) |
| Impact Model | LinearRegression | - | BSD (scikit-learn) |
| Priority Scorer | Custom weighted algorithm | configurable weights | Proprietary |

### Prompt Templates

#### Recommendation Summary Template

```
Client: {client_name}
Health Score: {health_score}/100
Recommendation: {action_category}

Analysis:
- Revenue Trend: {revenue_trend}
- Margin Status: {margin_status}
- Key Risk: {primary_risk}
- Opportunity: {primary_opportunity}

Recommended Action: {specific_action}
Estimated Impact: {revenue_impact} over {time_horizon}
Priority: {priority_level}
Next Steps: {action_items}
```

### Fallback Strategy

1. **Insufficient History**: Use industry benchmarks instead of client-specific trends
2. **Model Prediction Failure**: Default to rule-based recommendation matrix
3. **Missing Data Points**: Calculate partial health score, flag confidence reduction
4. **Conflicting Signals**: Present multiple options ranked by confidence

---

## 4. Revenue Forecaster

### Workflow Pipeline

```
Historical Data → Feature Engineering → Linear Regression + Random Forest → Ensemble → Confidence Intervals → Projections
```

### Stage Details

| Stage | Technology | Input | Output |
|-------|-----------|-------|--------|
| Data Collection | Django ORM + Pandas | Revenue history (24+ months) | Time series DataFrame |
| Feature Engineering | Pandas + NumPy | Raw time series | Engineered feature matrix |
| Linear Regression | scikit-learn | Feature matrix | Linear predictions |
| Random Forest | scikit-learn | Feature matrix | RF predictions |
| Ensemble | Weighted average | Both predictions | Combined forecast |
| Confidence Intervals | Statistical computation | Ensemble + residuals | Upper/lower bounds |
| Projection Output | Pandas | Ensemble + CI | 12-month forecast |

### Feature Engineering

| Feature | Type | Description |
|---------|------|-------------|
| month_of_year | Cyclical | Seasonality encoding (sin/cos) |
| quarter | Categorical | Q1–Q4 indicator |
| trend | Numeric | Linear time trend |
| lag_1, lag_3, lag_6 | Numeric | Lagged revenue values |
| rolling_mean_3 | Numeric | 3-month rolling average |
| rolling_std_3 | Numeric | 3-month rolling std deviation |
| active_contracts | Numeric | Count of active contracts |
| pipeline_value | Numeric | Weighted pipeline revenue |
| yoy_growth | Numeric | Year-over-year growth rate |
| client_concentration | Numeric | HHI index of client revenue |

### Model Specifications

| Component | Model | Parameters | License |
|-----------|-------|-----------|---------|
| Linear Model | LinearRegression | normalize=False | BSD (scikit-learn) |
| Random Forest | RandomForestRegressor | n_estimators=100, max_depth=10 | BSD (scikit-learn) |
| Ensemble Weights | Optimized | linear=0.3, rf=0.7 (default) | Proprietary |
| Confidence | Statistical | 80% and 95% intervals | - |

### Ensemble Strategy

```
forecast = (weight_linear * linear_prediction) + (weight_rf * rf_prediction)

Default weights: linear=0.3, rf=0.7
Weights optimized via cross-validation on rolling 6-month windows

Confidence Intervals:
- 80% CI: forecast ± 1.28 * residual_std
- 95% CI: forecast ± 1.96 * residual_std
```

### Fallback Strategy

1. **Insufficient History (<12 months)**: Use linear regression only with wider confidence intervals
2. **Model Training Failure**: Fall back to simple moving average projection
3. **Data Quality Issues**: Exclude outliers (>3 sigma), interpolate missing months
4. **High Prediction Error (MAPE >20%)**: Flag forecast as low-confidence, recommend manual review

---

## 5. Embedding Service

### Workflow Pipeline

```
Document → Chunking → sentence-transformers → ChromaDB → Similarity Search
```

### Stage Details

| Stage | Technology | Input | Output |
|-------|-----------|-------|--------|
| Document Intake | Django | PDF/DOCX/Text | Raw document content |
| Text Extraction | PyPDF2 + python-docx | Document file | Plain text |
| Chunking | LangChain TextSplitter | Plain text | Text chunks (512 tokens) |
| Embedding | sentence-transformers | Text chunks | 384-dim vectors |
| Storage | ChromaDB | Vectors + metadata | Persistent collection |
| Similarity Search | ChromaDB | Query vector | Top-k similar chunks |

### Model Specifications

| Component | Model | Dimensions | License |
|-----------|-------|-----------|---------|
| Embedding Model | all-MiniLM-L6-v2 | 384 | Apache 2.0 |
| Vector Store | ChromaDB | - | Apache 2.0 |
| Text Splitter | RecursiveCharacterTextSplitter | chunk_size=512, overlap=50 | MIT (LangChain) |
| Tokenizer | sentence-transformers | max_seq_length=256 | Apache 2.0 |

### Chunking Strategy

```
Parameters:
- chunk_size: 512 characters
- chunk_overlap: 50 characters
- separators: ["\n\n", "\n", ". ", " "]
- length_function: len

Metadata per chunk:
- document_id: UUID reference
- chunk_index: Position in document
- source_page: Page number (if PDF)
- document_type: contract/invoice/report
- organization_id: Tenant identifier
- created_at: Timestamp
```

### Search Configuration

```
Similarity Metric: Cosine similarity
Top-k Results: 5 (configurable)
Score Threshold: 0.7 minimum relevance
Filters: organization_id (mandatory), document_type (optional)
```

### Prompt Templates

#### Semantic Search Query Template

```
Find documents related to the following query within organization {org_id}:

Query: {user_query}
Document Types: {filter_types}
Date Range: {date_from} to {date_to}

Return top {k} most relevant document chunks with similarity scores.
```

#### Document Summarization Template

```
Summarize the following document chunks for a finance professional:

CHUNKS:
{retrieved_chunks}

Provide:
1. Key financial terms and values
2. Important dates and deadlines
3. Obligations and deliverables
4. Risk factors identified
```

### Fallback Strategy

1. **Embedding Model Unavailable**: Queue documents for later processing, serve from cache
2. **ChromaDB Connection Failure**: Fall back to PostgreSQL full-text search (pg_trgm)
3. **Low Relevance Results**: Expand search with query reformulation, reduce threshold
4. **Large Document (>100 pages)**: Process in batches, prioritize first/last pages + ToC

---

## Global Caching Strategy

### Cache Layers

| Layer | Technology | TTL | Use Case |
|-------|-----------|-----|----------|
| L1 - Request | Django per-request cache | Request lifecycle | Repeated DB queries |
| L2 - Application | Redis | 5–60 minutes | API responses, computed metrics |
| L3 - Model | Redis | 24 hours | ML model predictions |
| L4 - Embedding | ChromaDB (persistent) | Until document update | Vector embeddings |
| L5 - Report | Redis + S3 | 1 hour – 7 days | Generated reports |

### Cache Keys Convention

```
Pattern: {service}:{org_id}:{entity}:{identifier}:{version}

Examples:
- forecast:org_123:revenue:monthly:v2
- leakage:org_123:score:client_456:latest
- embedding:org_123:doc:doc_789:chunk_3
- health:org_123:client:client_456:current
- recommendation:org_123:client:client_456:latest
```

### Cache Invalidation Rules

| Trigger | Invalidated Keys | Strategy |
|---------|-----------------|----------|
| New invoice created | billing_ratio, leakage scores | Event-driven |
| Contract updated | contract parser results, embeddings | Event-driven |
| Timesheet submitted | unbilled_hours, utilization | Event-driven |
| Payment received | collection metrics, aging buckets | Event-driven |
| Model retrained | All model prediction caches | Bulk invalidation |
| Daily schedule | Stale forecasts, health scores | TTL expiry |

### Performance Targets

| Operation | Target Latency | Cache Hit Rate |
|-----------|---------------|----------------|
| Dashboard load | < 500ms | > 90% |
| Leakage score | < 2s (fresh), < 100ms (cached) | > 80% |
| Contract parsing | < 30s (async) | N/A |
| Similarity search | < 200ms | > 85% |
| Revenue forecast | < 5s (fresh), < 200ms (cached) | > 75% |
| Health score | < 1s (fresh), < 50ms (cached) | > 85% |
