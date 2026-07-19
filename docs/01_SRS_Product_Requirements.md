# Software Requirements Specification (SRS)
## RevRecog AI + ClientMargin360
### Finmark.ai

| Field | Value |
|-------|-------|
| **Document Version** | 2.0.0 |
| **Date** | July 2026 |
| **Status** | Production-Ready |
| **Classification** | Confidential |
| **Product** | RevRecog AI + ClientMargin360 |
| **Platform** | Finmark.ai PnL AutoTrack Suite |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Objectives & KPIs](#2-business-objectives--kpis)
3. [User Personas](#3-user-personas)
4. [Functional Requirements](#4-functional-requirements)
5. [Non-Functional Requirements](#5-non-functional-requirements)
6. [Acceptance Criteria](#6-acceptance-criteria)
7. [Revenue Model](#7-revenue-model)
8. [Assumptions & Dependencies](#8-assumptions--dependencies)
9. [Glossary](#9-glossary)

---

## 1. Executive Summary

### 1.1 Purpose

RevRecog AI + ClientMargin360 is an AI-powered enterprise platform that automates revenue recognition (ASC 606 / Ind AS 115 compliant), eliminates billing leakage, and provides real-time client profitability analytics for professional services organizations. Built specifically for Finmark.ai as the anchor customer, the platform addresses chronic revenue leakage of 3-5% annually (Rs. 9-15 Cr) through intelligent automation of the entire billing-to-recognition lifecycle.

### 1.2 Scope

The platform encompasses an 8-step automated workflow:

1. **Contract Ingestion** — AI-powered extraction of billing terms from contracts
2. **Billing Classification** — Auto-classify contracts and map ASC 606 revenue recognition rules
3. **Billable Activity Tracking** — Real-time tracking across timesheets, CRM, call systems
4. **Billing Trigger Engine** — Auto-trigger invoicing based on milestones, periods, and SLAs
5. **Invoice Generation** — Automated GST-compliant invoice creation with approval workflows
6. **Revenue Recognition** — ASC 606/Ind AS 115 compliant recognition with journal entries
7. **Payment Reconciliation** — Match payments, flag overdue, manage collections
8. **Leakage Detection** — AI-powered continuous scanning for revenue leakage

Plus the **ClientMargin360** layer providing:
- Real-time client profitability dashboards
- Trend tracking and eroding margin alerts
- AI recommendations (reprice/restructure/exit)
- 6-month profitability forecasts
- Client benchmarking and comparison

### 1.3 Saving Potential

| Category | Annual Savings |
|----------|---------------|
| Operational Automation | Rs. 3-6 Cr/year |
| Leakage Recovery | Rs. 9-15 Cr/year |
| **Total Impact** | **Rs. 12-21 Cr/year** |

### 1.4 Target Users

Professional services companies with 50+ active client engagements, multiple billing models (T&M, Fixed Milestone, Monthly Retainer, Performance-Based, Hybrid), and complex revenue recognition requirements.

---

## 2. Business Objectives & KPIs

### 2.1 Primary Objectives

| # | Objective | Current State | Target State | Timeline |
|---|-----------|---------------|--------------|----------|
| O1 | Reduce revenue leakage | 3-5% of annual revenue | <0.5% of annual revenue | 6 months |
| O2 | Automate invoice generation | 40% manual processing | 95% automated | 4 months |
| O3 | Real-time margin visibility | Monthly Excel reports | Live dashboards (<5 min lag) | 3 months |
| O4 | ASC 606 compliance | Partial/manual | 100% automated compliance | 4 months |
| O5 | Reduce DSO (Days Sales Outstanding) | 65-90 days | 35-45 days | 8 months |
| O6 | Eliminate unbilled work | 8% activities unbilled | <1% unbilled | 4 months |

### 2.2 Key Performance Indicators (KPIs)

#### Financial KPIs

| KPI | Metric | Target | Measurement |
|-----|--------|--------|-------------|
| Leakage Rate | % revenue lost to unbilled/missed items | <0.5% | Monthly scan |
| Collection Efficiency | % invoices collected within terms | >92% | Weekly |
| Margin Accuracy | Variance between reported vs actual margin | <2% | Monthly |
| Revenue Recognition Timeliness | Days to recognize after obligation met | <2 days | Daily |
| Invoice Accuracy | % invoices without errors | >99.5% | Per cycle |

#### Operational KPIs

| KPI | Metric | Target | Measurement |
|-----|--------|--------|-------------|
| Invoice Generation Time | Time from trigger to invoice ready | <30 minutes | Per invoice |
| Contract Processing Time | Time to ingest and classify new contract | <2 hours | Per contract |
| Alert Response Time | Time from detection to action | <4 hours | Per alert |
| System Availability | Platform uptime | 99.9% | Monthly |
| Report Generation | Time to produce financial reports | <60 seconds | On demand |

#### AI/ML KPIs

| KPI | Metric | Target | Measurement |
|-----|--------|--------|-------------|
| Contract Extraction Accuracy | % fields correctly extracted | >95% | Per contract |
| Leakage Detection Precision | % true positive alerts | >90% | Monthly |
| Forecast Accuracy | Margin forecast vs actual (6-month) | ±5% | Quarterly |
| Recommendation Acceptance | % AI recommendations acted upon | >70% | Monthly |

### 2.3 Success Criteria

- **Phase 1 (Month 1-3)**: Core billing automation live, leakage detection active
- **Phase 2 (Month 4-6)**: Full ASC 606 compliance, ClientMargin360 dashboards
- **Phase 3 (Month 7-9)**: AI recommendations, predictive forecasting
- **Phase 4 (Month 10-12)**: Multi-tenant SaaS, integration marketplace

---

## 3. User Personas

### 3.1 Chief Financial Officer (CFO)

| Attribute | Detail |
|-----------|--------|
| **Name** | Rajesh Sharma |
| **Role** | CFO, Finmark.ai |
| **Goals** | Maximize revenue realization, ensure compliance, strategic margin decisions |
| **Pain Points** | Lack of real-time visibility, manual compliance processes, surprise leakage discoveries |
| **Key Features** | Executive dashboard, margin alerts, compliance reports, forecasts |
| **Access Level** | Full read access, approval authority for write-offs |
| **Usage Frequency** | Daily (5-10 min dashboard), Weekly (deep-dive reviews) |

### 3.2 Finance Manager

| Attribute | Detail |
|-----------|--------|
| **Name** | Priya Verma |
| **Role** | Finance Manager |
| **Goals** | Accurate billing cycles, timely recognition, clean audit trails |
| **Pain Points** | Reconciling multiple data sources, month-end crunch, manual journal entries |
| **Key Features** | Invoice management, revenue schedules, reconciliation, leakage resolution |
| **Access Level** | Full module access, approval for invoices up to Rs. 50L |
| **Usage Frequency** | Multiple times daily |

### 3.3 Accounts Team Member

| Attribute | Detail |
|-----------|--------|
| **Name** | Ankit Patel |
| **Role** | Senior Accountant |
| **Goals** | Process invoices accurately, manage collections, maintain records |
| **Pain Points** | Data entry errors, chasing payments, complex GST calculations |
| **Key Features** | Invoice generation, payment tracking, GST compliance, aging reports |
| **Access Level** | Invoice creation/edit, payment recording, limited approvals |
| **Usage Frequency** | Continuous throughout workday |

### 3.4 Operations Head

| Attribute | Detail |
|-----------|--------|
| **Name** | Vikram Singh |
| **Role** | VP Operations |
| **Goals** | Ensure all delivered work is billed, optimize resource utilization |
| **Pain Points** | Unbilled work visibility, milestone tracking gaps, cross-system reconciliation |
| **Key Features** | Billable tracking, milestone management, resource-to-billing mapping |
| **Access Level** | Read access to billing data, write access to deliverable tracking |
| **Usage Frequency** | Daily reviews, weekly deep-dives |

### 3.5 Client Partner / Account Manager

| Attribute | Detail |
|-----------|--------|
| **Name** | Sneha Kapoor |
| **Role** | Client Partner |
| **Goals** | Healthy client margins, proactive issue resolution, upsell opportunities |
| **Pain Points** | Late discovery of margin erosion, no client health visibility, reactive management |
| **Key Features** | Client profitability views, health scores, AI recommendations, trend analysis |
| **Access Level** | Read access to assigned client data, flag issues |
| **Usage Frequency** | 2-3 times per week |

---


## 4. Functional Requirements

### 4.1 Contract Management (FR-CM)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-CM-001 | Contract Upload | P0 | Upload contracts in PDF, DOCX, image formats (up to 50MB) |
| FR-CM-002 | AI Contract Parsing | P0 | Extract billing terms, payment conditions, SLAs, milestones using NLP |
| FR-CM-003 | Term Extraction | P0 | Auto-identify: billing model, total value, payment terms, escalation clauses |
| FR-CM-004 | Contract Classification | P0 | Classify into: T&M, Fixed Milestone, Monthly Retainer, Performance-Based, Hybrid |
| FR-CM-005 | Version Control | P1 | Maintain full version history with diff comparison |
| FR-CM-006 | Amendment Tracking | P1 | Track amendments with impact analysis on revenue schedules |
| FR-CM-007 | Compliance Check | P0 | Validate contract against ASC 606 five-step model |
| FR-CM-008 | Performance Obligation ID | P0 | Identify distinct performance obligations per contract |
| FR-CM-009 | Document Storage | P1 | Secure encrypted storage with full-text search |
| FR-CM-010 | AI Flags & Risks | P0 | Auto-flag: missing escalation clauses, high-value contracts, complex milestones |
| FR-CM-011 | Contract Templates | P2 | Maintain library of contract templates by billing model |
| FR-CM-012 | Expiry Alerts | P1 | Auto-alert 90/60/30 days before contract expiry |
| FR-CM-013 | Bulk Import | P1 | Import existing contracts via CSV/Excel with validation |
| FR-CM-014 | OCR Processing | P0 | OCR scanned contracts with >95% extraction accuracy |
| FR-CM-015 | Confidence Scoring | P0 | Provide AI confidence score (target >92%) for extracted terms |

### 4.2 Billing Classification (FR-BC)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-BC-001 | Auto-Classification | P0 | Automatically classify billing model from contract terms |
| FR-BC-002 | ASC 606 Mapping | P0 | Map each model to recognition pattern, method, timing |
| FR-BC-003 | Recognition Pattern | P0 | Determine: Over Time vs Point in Time for each obligation |
| FR-BC-004 | Measurement Method | P0 | Assign: Input Method (hours), Output Method (milestones/units), Time-Based |
| FR-BC-005 | Variable Consideration | P0 | Handle constrained estimates for performance-based contracts |
| FR-BC-006 | Transaction Price Allocation | P0 | Allocate total price to individual performance obligations |
| FR-BC-007 | Journal Entry Templates | P1 | Auto-generate journal entry templates per billing model |
| FR-BC-008 | Multi-Model Support | P0 | Support hybrid contracts with multiple billing models |
| FR-BC-009 | Rule Configuration | P1 | Allow finance team to configure classification rules |
| FR-BC-010 | Override Capability | P1 | Manual override with audit trail and reason capture |

### 4.3 Billable Activity Tracking (FR-BT)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-BT-001 | Timesheet Integration | P0 | Ingest timesheet data from multiple systems (Timesheet Pro, etc.) |
| FR-BT-002 | CRM Activity Sync | P0 | Sync billable activities from Salesforce/CRM |
| FR-BT-003 | Call Record Capture | P1 | Capture call records from Avaya/telephony systems |
| FR-BT-004 | Field Visit Tracking | P1 | Track field visits via mobile app GPS |
| FR-BT-005 | Milestone Progress | P0 | Track milestone completion percentage |
| FR-BT-006 | Unbilled Detection | P0 | Real-time flagging of activities not linked to billing |
| FR-BT-007 | Multi-Source Reconciliation | P0 | Reconcile activities across 4+ source systems |
| FR-BT-008 | Activity Approval | P1 | Workflow for billable activity approval |
| FR-BT-009 | Rate Card Application | P0 | Apply correct rate card based on resource level and client |
| FR-BT-010 | Expense Tracking | P1 | Track reimbursable expenses linked to client engagements |
| FR-BT-011 | Utilization Dashboard | P2 | Show billable vs non-billable utilization |
| FR-BT-012 | Auto-Classification | P1 | AI-classify activities as billable/non-billable |
| FR-BT-013 | Duplicate Detection | P1 | Detect and flag duplicate activity entries |
| FR-BT-014 | Batch Import | P1 | Import activities via API or file upload |
| FR-BT-015 | Audit Trail | P0 | Complete audit trail for all activity changes |

### 4.4 Leakage Detection (FR-LD)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-LD-001 | Unbilled Hours Detection | P0 | Identify hours worked but not billed across all clients |
| FR-LD-002 | Missed Milestone Detection | P0 | Detect completed milestones without corresponding invoices |
| FR-LD-003 | Rate Card Variance | P0 | Flag instances where billed rate < contracted rate |
| FR-LD-004 | Scope Creep Detection | P0 | Identify work delivered beyond contracted scope without billing |
| FR-LD-005 | Escalation Clause Monitoring | P1 | Alert when annual escalations are not applied |
| FR-LD-006 | Continuous Scanning | P0 | Real-time continuous scanning (not just month-end) |
| FR-LD-007 | Severity Classification | P0 | Classify alerts as HIGH/MEDIUM/LOW with amount impact |
| FR-LD-008 | Root Cause Analysis | P1 | AI-identify root cause of each leakage instance |
| FR-LD-009 | Recovery Recommendations | P0 | Provide specific recovery actions with estimated amounts |
| FR-LD-010 | Leakage Trending | P1 | Show leakage trends over time by category/client |
| FR-LD-011 | Threshold Configuration | P1 | Configurable thresholds for alert generation |
| FR-LD-012 | Resolution Workflow | P0 | Track leakage from detection → investigation → resolution |
| FR-LD-013 | Monthly Leakage Report | P0 | Auto-generate monthly leakage summary for CFO |
| FR-LD-014 | Annualized Impact | P0 | Show annualized financial impact of detected leakage |
| FR-LD-015 | Recovery Rate Tracking | P1 | Track % of detected leakage successfully recovered (target: 85%) |

### 4.5 Invoice Generation (FR-IG)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-IG-001 | Auto-Generation | P0 | Generate invoices automatically from billing triggers |
| FR-IG-002 | GST Compliance | P0 | Full GST compliance with CGST/SGST/IGST calculation |
| FR-IG-003 | TDS Handling | P0 | Handle TDS deduction at source (10% default) |
| FR-IG-004 | Template Engine | P1 | Customizable invoice templates per client/model |
| FR-IG-005 | Multi-Currency | P1 | Support INR, USD, EUR, GBP with exchange rate management |
| FR-IG-006 | Approval Workflow | P0 | Configurable approval chains (amount-based routing) |
| FR-IG-007 | Bulk Generation | P0 | Generate multiple invoices in batch (month-end cycle) |
| FR-IG-008 | Credit Notes | P0 | Issue credit notes with linking to original invoice |
| FR-IG-009 | Debit Notes | P1 | Issue debit notes for additional charges |
| FR-IG-010 | PDF Generation | P0 | Generate professional PDF invoices |
| FR-IG-011 | Email Dispatch | P0 | Auto-dispatch invoices via email to client contacts |
| FR-IG-012 | E-Invoicing | P1 | Integration with GST e-invoicing portal (IRP) |
| FR-IG-013 | HSN/SAC Codes | P0 | Auto-apply correct HSN/SAC codes |
| FR-IG-014 | Line Item Detail | P0 | Detailed line items with hours, rates, descriptions |
| FR-IG-015 | Revision History | P1 | Track all invoice revisions with reasons |

### 4.6 Revenue Recognition (FR-RR)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-RR-001 | ASC 606 Five-Step Model | P0 | Implement complete ASC 606 five-step recognition framework |
| FR-RR-002 | Ind AS 115 Compliance | P0 | Parallel compliance with Indian accounting standard |
| FR-RR-003 | Over Time Recognition | P0 | Recognize revenue over time for T&M and retainer contracts |
| FR-RR-004 | Point in Time Recognition | P0 | Recognize at completion for milestone-based contracts |
| FR-RR-005 | Deferred Revenue | P0 | Manage deferred revenue with automated release schedules |
| FR-RR-006 | Unbilled Revenue | P0 | Track and manage unbilled (accrued) revenue |
| FR-RR-007 | Journal Entry Generation | P0 | Auto-generate journal entries (Dr/Cr) per recognition event |
| FR-RR-008 | Variable Consideration | P0 | Apply constraint on variable consideration (expected value/most likely) |
| FR-RR-009 | Contract Modifications | P1 | Handle contract modifications (prospective/cumulative catch-up) |
| FR-RR-010 | Revenue Schedules | P0 | Generate monthly/quarterly recognition schedules |
| FR-RR-011 | Period Close | P0 | Automated period close with recognition completeness check |
| FR-RR-012 | Audit Trail | P0 | Complete audit trail for every recognition event |
| FR-RR-013 | Disclosure Reports | P1 | Generate ASC 606 disclosure reports for auditors |
| FR-RR-014 | Constraint Application | P0 | Apply revenue constraint when uncertainty exists |
| FR-RR-015 | Multi-Period Allocation | P0 | Allocate revenue across multiple periods correctly |

### 4.7 Client Profitability — ClientMargin360 (FR-CP)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-CP-001 | Real-Time Margin Calculation | P0 | Calculate net margin per client in real-time |
| FR-CP-002 | Cost Allocation | P0 | Allocate direct + indirect costs to each client |
| FR-CP-003 | Overhead Distribution | P1 | Distribute overhead costs based on configurable rules |
| FR-CP-004 | Margin Threshold Alerts | P0 | Alert when client margin drops below 12% threshold |
| FR-CP-005 | Trend Tracking | P0 | Track margin trends over 6-12 month periods |
| FR-CP-006 | Client Benchmarking | P1 | Compare client profitability across portfolio |
| FR-CP-007 | Profitability Ranking | P0 | Rank clients by net margin with drill-down |
| FR-CP-008 | Eroding Margin Detection | P0 | Detect and alert on consistently declining margins |
| FR-CP-009 | AI Recommendations | P0 | Generate actionable recommendations (reprice/restructure/exit) |
| FR-CP-010 | 6-Month Forecast | P1 | Predict margin trajectory using ML models |
| FR-CP-011 | What-If Analysis | P2 | Scenario modeling for pricing changes |
| FR-CP-012 | Segment Analysis | P1 | Profitability by industry sector, billing model, geography |
| FR-CP-013 | Resource Cost Tracking | P0 | Track resource costs (salaries, overheads) per client |
| FR-CP-014 | Revenue per FTE | P1 | Calculate and track revenue per FTE per client |
| FR-CP-015 | Client Health Score | P0 | Composite score: margin + payment behavior + growth |

### 4.8 AI Recommendations Engine (FR-AI)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-AI-001 | Margin Improvement Recs | P0 | AI-generated recommendations for margin improvement |
| FR-AI-002 | Pricing Optimization | P1 | Suggest optimal pricing based on historical data |
| FR-AI-003 | Anomaly Detection | P0 | Detect anomalies in billing patterns, costs, activities |
| FR-AI-004 | Contract Risk Scoring | P1 | Score contracts for revenue/margin risk |
| FR-AI-005 | Collection Prediction | P1 | Predict payment probability and timing |
| FR-AI-006 | Leakage Prediction | P0 | Predict where leakage is likely to occur |
| FR-AI-007 | Client Churn Risk | P2 | Predict client churn based on engagement patterns |
| FR-AI-008 | Resource Optimization | P2 | Suggest resource allocation for margin optimization |
| FR-AI-009 | Confidence Scoring | P0 | Provide confidence level for all AI outputs |
| FR-AI-010 | Explainability | P1 | Provide reasoning for each recommendation |
| FR-AI-011 | Feedback Loop | P1 | Learn from accepted/rejected recommendations |
| FR-AI-012 | Model Versioning | P1 | Track model versions and performance metrics |

### 4.9 Collections Management (FR-CO)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-CO-001 | Aging Analysis | P0 | Real-time aging buckets (Current, 30, 60, 90, 90+ days) |
| FR-CO-002 | Auto-Reminders | P0 | Automated payment reminders at configurable intervals |
| FR-CO-003 | Escalation Workflow | P0 | Multi-level escalation (Auto → Account Manager → Finance Head → CFO → Legal) |
| FR-CO-004 | Payment Matching | P0 | Auto-match incoming payments to outstanding invoices |
| FR-CO-005 | Partial Payment | P0 | Handle partial payments with balance tracking |
| FR-CO-006 | DSO Tracking | P0 | Track Days Sales Outstanding per client and portfolio |
| FR-CO-007 | Cash Flow Forecast | P1 | Predict cash inflows based on payment patterns |
| FR-CO-008 | Dunning Management | P0 | Configurable dunning letters and schedules |
| FR-CO-009 | Write-Off Management | P1 | Manage bad debt write-offs with approval |
| FR-CO-010 | Bank Reconciliation | P1 | Reconcile bank statements with receivables |
| FR-CO-011 | Collection Analytics | P1 | Collection effectiveness metrics and trends |
| FR-CO-012 | Credit Limit Management | P2 | Set and enforce client credit limits |

### 4.10 Reporting & Analytics (FR-RP)

| ID | Requirement | Priority | Description |
|----|-------------|----------|-------------|
| FR-RP-001 | Executive Dashboard | P0 | Real-time KPI dashboard for CFO |
| FR-RP-002 | Revenue Reports | P0 | Monthly/quarterly revenue recognition reports |
| FR-RP-003 | Leakage Reports | P0 | Detailed leakage analysis with recovery tracking |
| FR-RP-004 | Profitability Reports | P0 | Client profitability by segment, model, period |
| FR-RP-005 | Collection Reports | P0 | Aging, DSO, collection efficiency reports |
| FR-RP-006 | Compliance Reports | P0 | ASC 606/Ind AS 115 compliance and disclosure reports |
| FR-RP-007 | Custom Reports | P1 | User-configurable report builder |
| FR-RP-008 | Scheduled Reports | P1 | Auto-generate and email reports on schedule |
| FR-RP-009 | Export Formats | P0 | Export to PDF, Excel, CSV |
| FR-RP-010 | Drill-Down | P0 | Drill from summary to transaction-level detail |
| FR-RP-011 | Comparative Analysis | P1 | Period-over-period, YoY comparisons |
| FR-RP-012 | Audit Reports | P0 | Complete audit trail reports for external auditors |

---


## 5. Non-Functional Requirements

### 5.1 Performance Requirements (NFR-P)

| ID | Requirement | Metric | Target |
|----|-------------|--------|--------|
| NFR-P-001 | Page Load Time | Time to interactive | <2 seconds (95th percentile) |
| NFR-P-002 | API Response Time | Server response | <500ms (95th percentile) |
| NFR-P-003 | Dashboard Refresh | Data freshness | <5 minutes lag |
| NFR-P-004 | Invoice Generation | Single invoice | <30 seconds |
| NFR-P-005 | Bulk Invoice Generation | 100 invoices | <10 minutes |
| NFR-P-006 | Report Generation | Standard reports | <60 seconds |
| NFR-P-007 | Search Response | Full-text search | <1 second |
| NFR-P-008 | AI Recommendation | Single recommendation | <5 seconds |
| NFR-P-009 | Contract OCR | Single document | <2 minutes |
| NFR-P-010 | Leakage Scan | Full portfolio scan | <5 minutes |
| NFR-P-011 | Database Queries | Complex aggregations | <3 seconds |
| NFR-P-012 | File Upload | 50MB document | <30 seconds |

### 5.2 Availability & Reliability (NFR-A)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-A-001 | System Uptime | 99.9% (8.76 hours max downtime/year) |
| NFR-A-002 | RTO (Recovery Time Objective) | <1 hour |
| NFR-A-003 | RPO (Recovery Point Objective) | <15 minutes |
| NFR-A-004 | Planned Maintenance Window | Sunday 2-4 AM IST |
| NFR-A-005 | Zero-Downtime Deployments | Blue/green deployment |
| NFR-A-006 | Auto-Failover | <30 seconds for database failover |
| NFR-A-007 | Data Backup | Daily full + hourly incremental |
| NFR-A-008 | Cross-Region DR | Active-passive in secondary region |

### 5.3 Security Requirements (NFR-S)

| ID | Requirement | Standard | Description |
|----|-------------|----------|-------------|
| NFR-S-001 | SOC 2 Type II Compliance | SOC 2 | Annual audit and certification |
| NFR-S-002 | OWASP Top 10 | OWASP | Protection against all OWASP Top 10 vulnerabilities |
| NFR-S-003 | Encryption at Rest | AES-256 | All data encrypted at rest |
| NFR-S-004 | Encryption in Transit | TLS 1.3 | All communications over TLS 1.3 |
| NFR-S-005 | Authentication | JWT + OAuth2 | Multi-factor authentication support |
| NFR-S-006 | Authorization | RBAC | Role-based access control with 5+ roles |
| NFR-S-007 | PII Protection | GDPR-aligned | Mask/encrypt all personally identifiable information |
| NFR-S-008 | Audit Logging | Complete | Every data access and modification logged |
| NFR-S-009 | Session Management | Secure | 30-min idle timeout, concurrent session limit |
| NFR-S-010 | API Security | Rate limiting | Rate limiting, input validation, CORS |
| NFR-S-011 | Vulnerability Scanning | Weekly | Automated DAST/SAST scanning |
| NFR-S-012 | Penetration Testing | Annual | Third-party penetration testing |
| NFR-S-013 | Data Retention | Configurable | 7-year default retention for financial data |
| NFR-S-014 | IP Whitelisting | Configurable | Restrict access to known IP ranges |
| NFR-S-015 | WAF Protection | AWS WAF | Web Application Firewall for all endpoints |

### 5.4 Scalability Requirements (NFR-SC)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-SC-001 | Concurrent Users | 500+ simultaneous users |
| NFR-SC-002 | Total Users | 10,000+ registered users |
| NFR-SC-003 | Tenants | 100+ organizations (multi-tenant) |
| NFR-SC-004 | Contracts | 50,000+ contracts per tenant |
| NFR-SC-005 | Invoices | 1,000,000+ invoices in system |
| NFR-SC-006 | Transactions/Second | 1,000+ TPS |
| NFR-SC-007 | Data Growth | 100GB+ per year per tenant |
| NFR-SC-008 | Horizontal Scaling | Auto-scale based on load |
| NFR-SC-009 | Database Scaling | Read replicas, connection pooling |
| NFR-SC-010 | File Storage | Unlimited via object storage |

### 5.5 Usability Requirements (NFR-U)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-U-001 | Responsive Design | Desktop, tablet, mobile |
| NFR-U-002 | Browser Support | Chrome, Firefox, Safari, Edge (latest 2 versions) |
| NFR-U-003 | Accessibility | WCAG 2.1 AA compliant |
| NFR-U-004 | Localization | English, Hindi (extensible) |
| NFR-U-005 | Onboarding | <2 hours for new user proficiency |
| NFR-U-006 | Help System | Contextual help, tooltips, documentation |
| NFR-U-007 | Error Messages | Clear, actionable error messages |
| NFR-U-008 | Keyboard Navigation | Full keyboard accessibility |

### 5.6 Integration Requirements (NFR-I)

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-I-001 | ERP Integration | Tally Prime, SAP, Oracle |
| NFR-I-002 | CRM Integration | Salesforce, HubSpot |
| NFR-I-003 | HRMS Integration | SuccessFactors, Darwinbox |
| NFR-I-004 | Banking Integration | ICICI, HDFC, SBI corporate banking |
| NFR-I-005 | GST Portal | E-invoicing (IRP), GSTR filing |
| NFR-I-006 | Email | SMTP, SendGrid, SES |
| NFR-I-007 | Storage | AWS S3, Azure Blob |
| NFR-I-008 | SSO | SAML 2.0, OpenID Connect |
| NFR-I-009 | Webhooks | Outbound webhooks for events |
| NFR-I-010 | API Rate Limits | 1000 requests/minute per tenant |

---

## 6. Acceptance Criteria

### 6.1 Contract Management Module

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| AC-CM-1 | System extracts billing model with >95% accuracy from uploaded contracts | Test with 50 sample contracts |
| AC-CM-2 | OCR processes scanned documents within 2 minutes | Performance test |
| AC-CM-3 | All 5 billing models correctly classified | Functional test with each type |
| AC-CM-4 | Contract version history maintained with full diff | User acceptance test |
| AC-CM-5 | Amendment impact analysis generated within 30 seconds | Performance test |
| AC-CM-6 | AI confidence score displayed for each extraction | UI verification |
| AC-CM-7 | Expiry alerts triggered at 90/60/30 day marks | Scheduled job verification |

### 6.2 Billing & Invoicing Module

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| AC-BI-1 | Invoices auto-generated within 30 minutes of trigger event | End-to-end test |
| AC-BI-2 | GST calculations accurate to 2 decimal places | Calculation verification |
| AC-BI-3 | Bulk generation of 100 invoices completes in <10 minutes | Load test |
| AC-BI-4 | Approval workflow routes correctly based on amount thresholds | Workflow test |
| AC-BI-5 | Credit notes automatically link to original invoice | Functional test |
| AC-BI-6 | E-invoicing integration generates valid IRN | Integration test |
| AC-BI-7 | 95% of invoices generated without manual intervention | Production metric |

### 6.3 Revenue Recognition Module

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| AC-RR-1 | All 5 ASC 606 steps automated for each contract | Compliance audit |
| AC-RR-2 | Revenue schedules generated for 12 months forward | Functional test |
| AC-RR-3 | Journal entries balance (debits = credits) for every transaction | Automated validation |
| AC-RR-4 | Deferred revenue automatically releases per schedule | Schedule test |
| AC-RR-5 | Variable consideration constraints applied correctly | Scenario testing |
| AC-RR-6 | Period close completes with 100% recognition coverage | Month-end test |
| AC-RR-7 | Audit trail captures every recognition event with timestamp/user | Audit verification |

### 6.4 Leakage Detection Module

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| AC-LD-1 | System detects >90% of planted leakage scenarios | Controlled test |
| AC-LD-2 | False positive rate <10% | Production metric over 3 months |
| AC-LD-3 | Alerts generated within 5 minutes of detection | Real-time test |
| AC-LD-4 | Annualized leakage reduced from 3-5% to <0.5% | Production metric |
| AC-LD-5 | Recovery recommendations provided for each alert | Functional test |
| AC-LD-6 | Resolution workflow tracks from detection to closure | End-to-end test |
| AC-LD-7 | Monthly leakage report auto-generated by 2nd business day | Scheduled test |

### 6.5 Client Profitability Module

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| AC-CP-1 | Margin calculated with <2% variance from manual calculation | Accuracy test |
| AC-CP-2 | Alerts triggered within 1 hour of margin dropping below 12% | Threshold test |
| AC-CP-3 | 6-month forecast accuracy within ±5% of actual | Backtest validation |
| AC-CP-4 | AI recommendations generated for all below-threshold clients | Functional test |
| AC-CP-5 | Client health score updated daily | Schedule verification |
| AC-CP-6 | Benchmarking compares across all relevant dimensions | Functional test |
| AC-CP-7 | Real-time dashboard updates within 5 minutes of data change | Freshness test |

### 6.6 Collections Module

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| AC-CO-1 | Aging buckets calculated accurately in real-time | Calculation test |
| AC-CO-2 | Auto-reminders sent per configured schedule | Schedule test |
| AC-CO-3 | Escalation triggers at correct thresholds (30/45/60/90 days) | Workflow test |
| AC-CO-4 | Payment matching accuracy >98% for standard payments | Matching test |
| AC-CO-5 | DSO reduced from 65-90 days to 35-45 days | Production metric |
| AC-CO-6 | Cash forecast accuracy within ±10% for 30-day window | Backtest |
| AC-CO-7 | All dunning activities logged with response tracking | Audit test |

---

## 7. Revenue Model

### 7.1 SaaS Subscription Pricing

| Tier | Annual Price | Included | Target Segment |
|------|-------------|----------|----------------|
| **Starter** | Rs. 45L/year | Up to 50 contracts, 20 users, Basic AI | Mid-size companies (Revenue 100-500 Cr) |
| **Professional** | Rs. 60L/year | Up to 200 contracts, 50 users, Full AI | Large companies (Revenue 500-2000 Cr) |
| **Enterprise** | Rs. 75L/year | Unlimited contracts, unlimited users, Custom AI | Enterprise (Revenue 2000+ Cr) |

### 7.2 Pricing Components

| Component | Starter | Professional | Enterprise |
|-----------|---------|--------------|------------|
| Contract Management | ✅ | ✅ | ✅ |
| Billing Automation | ✅ | ✅ | ✅ |
| Invoice Generation | ✅ | ✅ | ✅ |
| Revenue Recognition | Basic | Full ASC 606 | Full + Custom |
| Leakage Detection | ✅ | ✅ | ✅ |
| ClientMargin360 | Basic | Full | Full + Predictive |
| AI Recommendations | Limited (10/month) | Unlimited | Unlimited + Custom Models |
| Collections | Basic | Full | Full + Predictive |
| Integrations | 2 systems | 5 systems | Unlimited |
| API Access | 100 req/min | 500 req/min | 1000 req/min |
| Support | Email (48h) | Priority (4h) | Dedicated CSM |
| Custom Reports | 5 templates | 20 templates | Unlimited |
| Training | Online | On-site (2 days) | On-site (5 days) + Ongoing |

### 7.3 Additional Revenue Streams

| Stream | Pricing |
|--------|---------|
| Implementation & Setup | Rs. 5-15L one-time |
| Custom Integration Development | Rs. 2-5L per integration |
| Training & Certification | Rs. 1-2L per batch |
| Premium Support (24/7) | Rs. 5L/year add-on |
| Data Migration Services | Rs. 3-8L one-time |
| Custom AI Model Training | Rs. 5-10L per model |

### 7.4 ROI Justification

For a company with Rs. 300 Cr annual revenue:
- **Leakage recovery (3% → 0.5%)**: Rs. 7.5 Cr saved
- **Automation savings**: Rs. 3 Cr/year (reduced headcount, faster cycles)
- **DSO improvement**: Rs. 2 Cr working capital freed
- **Total benefit**: Rs. 12.5 Cr/year
- **Platform cost**: Rs. 60L/year
- **ROI**: **~20x return on investment**

---

## 8. Assumptions & Dependencies

### 8.1 Assumptions

1. Client organizations have digital contracts (or willing to digitize)
2. Existing timesheet/CRM systems have API access
3. Finance team available for UAT within 2 weeks of module delivery
4. GST e-invoicing APIs remain stable (government portal)
5. Client data quality is sufficient for AI model training (>6 months history)
6. Internet connectivity available for cloud-hosted deployment

### 8.2 Dependencies

| Dependency | Type | Risk | Mitigation |
|------------|------|------|-----------|
| AWS Infrastructure | External | Low | Multi-AZ deployment |
| GST Portal APIs | External | Medium | Offline queue, retry logic |
| Client ERP Systems | External | Medium | Adapter pattern, fallback |
| OCR Service (Textract) | External | Low | Fallback to Tesseract |
| AI/ML Models | Internal | Medium | Rule-based fallback |
| Payment Gateway | External | Low | Multiple gateway support |

---

## 9. Glossary

| Term | Definition |
|------|-----------|
| ASC 606 | Revenue from Contracts with Customers (US GAAP standard) |
| Ind AS 115 | Indian equivalent of ASC 606 |
| T&M | Time and Materials billing model |
| DSO | Days Sales Outstanding |
| Leakage | Revenue lost due to unbilled work, missed escalations, or errors |
| Performance Obligation | Promise to deliver a distinct good/service to a customer |
| Variable Consideration | Transaction price that can vary (bonuses, penalties, etc.) |
| Deferred Revenue | Revenue received but not yet earned/recognized |
| Dunning | Process of systematically communicating with customers about overdue payments |
| GST | Goods and Services Tax (India) |
| TDS | Tax Deducted at Source |
| HSN | Harmonized System of Nomenclature (product classification) |
| SAC | Services Accounting Code |
| IRN | Invoice Reference Number (e-invoicing) |
| IRP | Invoice Registration Portal |
| RBAC | Role-Based Access Control |
| FTE | Full-Time Equivalent |
| WIP | Work in Progress |

---

*Document End — RevRecog AI + ClientMargin360 SRS v2.0.0*
