CONTRACT_EXTRACTION_PROMPT = """You are a contract analysis specialist. Extract structured information from the following contract text.

Contract Text:
{contract_text}

Extract the following fields in JSON format:
- contract_number: The unique identifier or reference number
- client_name: The client or counterparty name
- billing_model: Type of billing (T&M, Fixed Price, Milestone, Retainer, Hybrid)
- start_date: Contract start date (ISO format)
- end_date: Contract end date (ISO format)
- total_value: Total contract value in numeric format
- currency: Currency code
- payment_terms: Payment terms (Net 30, Net 60, etc.)
- escalation_clauses: Any rate escalation or price adjustment clauses
- milestones: List of deliverable milestones with dates and amounts
- renewal_terms: Auto-renewal or renewal conditions
- termination_clause: Early termination conditions and penalties

Respond ONLY with valid JSON. Include a confidence score (0.0-1.0) for each field."""


LEAKAGE_ANALYSIS_PROMPT = """You are a revenue leakage analyst for a professional services company. Analyze the following billing and operational data to identify potential revenue leakage.

Client: {client_name}
Contract Type: {billing_model}
Contract Value: {contract_value}
Period: {analysis_period}

Billing Data:
{billing_data}

Timesheet Data:
{timesheet_data}

Expense Data:
{expense_data}

Identify any of the following leakage types:
1. Unbilled hours - work performed but not invoiced
2. Missed milestones - deliverables completed but not billed
3. Rate escalation not applied - contractual rate increases missed
4. Expenses not billed - reimbursable expenses not charged
5. Scope creep - work beyond SOW not captured
6. Undercharging - rates below contracted amounts

For each leakage found, provide:
- type: leakage category
- description: specific details
- severity: LOW, MEDIUM, HIGH, CRITICAL
- estimated_amount: monetary impact
- evidence: supporting data points
- recommendation: corrective action

Respond ONLY with valid JSON."""


RECOMMENDATION_PROMPT = """You are a strategic advisor for a professional services firm. Based on the following client data, provide actionable recommendations.

Client: {client_name}
Current Margin: {current_margin}%
Margin Trend: {margin_trend}
Revenue (Annual): {annual_revenue}
Contract Tenure: {tenure_months} months
Billing Model: {billing_model}
Industry Sector: {sector}
Team Size: {team_size}
Client Health Score: {health_score}/100

Historical Performance:
{performance_history}

Benchmark Data:
{benchmark_data}

Provide recommendations from the following types:
- REPRICE: Adjust pricing or billing rates
- EXPAND: Grow scope or cross-sell services
- RESTRUCTURE: Change billing model or engagement structure
- EXIT: Planned disengagement for unprofitable clients
- OPTIMIZE: Improve delivery efficiency

For each recommendation:
- type: recommendation category
- title: brief description
- rationale: why this is recommended
- expected_impact: estimated margin improvement in percentage points
- implementation_steps: ordered list of actions
- risk_level: LOW, MEDIUM, HIGH
- priority: 1-5 (1 = highest)
- timeline: implementation timeframe

Respond ONLY with valid JSON."""


REVENUE_FORECAST_PROMPT = """You are a financial forecasting specialist. Analyze the following revenue data and provide forward-looking projections.

Client: {client_name}
Historical Revenue (Monthly):
{revenue_history}

Contract Pipeline:
{pipeline_data}

Seasonality Patterns:
{seasonality}

Market Conditions:
{market_context}

Provide:
1. Revenue forecast for next 3, 6, and 12 months
2. Confidence intervals (low, mid, high scenarios)
3. Key assumptions
4. Risk factors that could impact the forecast
5. Cash flow timing predictions based on payment terms

Respond ONLY with valid JSON containing monthly projections with confidence bands."""


INVOICE_VALIDATION_PROMPT = """You are an invoice validation specialist. Review the following invoice against the contract terms and delivery records.

Invoice Details:
{invoice_data}

Contract Terms:
{contract_terms}

Delivery Records:
{delivery_records}

Timesheet Summary:
{timesheet_summary}

Validate:
1. Rate accuracy - do billed rates match contract rates?
2. Hours accuracy - do billed hours align with timesheets?
3. Milestone completion - are billed milestones actually delivered?
4. Expense compliance - are expenses within policy limits?
5. Tax calculation - are taxes correctly computed?
6. Payment terms - are payment terms correctly stated?

For each validation check:
- check_name: what was validated
- status: PASS, FAIL, WARNING
- expected_value: what it should be
- actual_value: what was found
- variance: difference amount
- recommendation: action if failed

Respond ONLY with valid JSON."""


CLIENT_HEALTH_PROMPT = """You are a client relationship analyst. Assess the overall health of the following client engagement.

Client: {client_name}
Engagement Duration: {tenure}
Current Contracts: {active_contracts}

Financial Metrics:
{financial_metrics}

Operational Metrics:
{operational_metrics}

Relationship Indicators:
{relationship_data}

Score the client on these dimensions (0-100):
1. Financial Health: profitability, payment behavior, revenue stability
2. Operational Health: delivery quality, resource utilization, SLA compliance
3. Relationship Health: stakeholder satisfaction, communication frequency, escalations
4. Growth Potential: expansion opportunities, cross-sell potential, strategic alignment
5. Risk Level: concentration risk, dependency, contract stability

Provide:
- overall_health_score: weighted composite (0-100)
- dimension_scores: individual scores with justification
- trend: IMPROVING, STABLE, DECLINING
- alerts: any immediate concerns
- opportunities: growth or improvement areas

Respond ONLY with valid JSON."""


MARGIN_INSIGHT_PROMPT = """You are a profitability analyst for a professional services company. Analyze the following margin data and provide actionable insights.

Client: {client_name}
Billing Model: {billing_model}
Sector: {sector}

Margin History:
{margin_history}

Cost Breakdown:
{cost_breakdown}

Benchmark Comparison:
{benchmarks}

Resource Allocation:
{resource_data}

Provide:
1. Margin drivers - what is positively/negatively impacting margins
2. Cost optimization opportunities - where costs can be reduced
3. Pricing opportunities - where pricing can be improved
4. Structural insights - billing model effectiveness
5. Trend analysis - where margins are heading
6. Scenario modeling - impact of specific changes

For each insight:
- category: driver, optimization, pricing, structural, trend
- finding: specific observation
- impact: quantified margin impact in basis points
- actionability: IMMEDIATE, SHORT_TERM, LONG_TERM
- confidence: HIGH, MEDIUM, LOW

Respond ONLY with valid JSON."""
