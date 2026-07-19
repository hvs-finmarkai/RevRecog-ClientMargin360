# System Architecture Document
## RevRecog AI + ClientMargin360
### Finmark.ai

| Field | Value |
|-------|-------|
| **Document Version** | 2.0.0 |
| **Date** | July 2026 |
| **Status** | Production-Ready |
| **Classification** | Confidential |

---

## Table of Contents

1. [High-Level Architecture](#1-high-level-architecture)
2. [Microservices Architecture](#2-microservices-architecture)
3. [API Gateway Design](#3-api-gateway-design)
4. [Authentication & Authorization](#4-authentication--authorization)
5. [Event-Driven Architecture](#5-event-driven-architecture)
6. [Queue Architecture](#6-queue-architecture)
7. [Database Architecture](#7-database-architecture)
8. [Deployment Architecture](#8-deployment-architecture)
9. [AWS Architecture](#9-aws-architecture)
10. [Security Architecture](#10-security-architecture)
11. [Monitoring & Observability](#11-monitoring--observability)

---

## 1. High-Level Architecture

### 1.1 Architecture Overview Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │  Web App     │  │  Mobile App  │  │  Admin Panel │  │  External Partners   │    │
│  │  (React.js)  │  │  (React Nat.)│  │  (React.js)  │  │  (API Consumers)     │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘    │
└─────────┼──────────────────┼──────────────────┼─────────────────────┼────────────────┘
          │                  │                  │                     │
          ▼                  ▼                  ▼                     ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           CDN + WAF LAYER (CloudFront + AWS WAF)                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY (Kong / AWS API Gateway)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────────┐  │
│  │ Rate Limit  │  │ Auth Check  │  │ Request Log │  │ Load Balancing (ALB)     │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         MICROSERVICES LAYER (ECS/EKS)                                 │
│                                                                                       │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐       │
│  │  Auth      │ │  Contract  │ │  Billing   │ │  Invoice   │ │ Recognition│       │
│  │  Service   │ │  Service   │ │  Service   │ │  Service   │ │  Service   │       │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘       │
│                                                                                       │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐       │
│  │Profitabilit│ │  Leakage   │ │  AI        │ │Notification│ │Integration │       │
│  │  Service   │ │  Service   │ │  Service   │ │  Service   │ │  Service   │       │
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────────┘       │
└─────────────────────────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                         EVENT & MESSAGING LAYER                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────────────────┐  │
│  │  RabbitMQ        │  │  Redis (Celery)  │  │  AWS SQS (Dead Letter Queues)    │  │
│  │  (Event Bus)     │  │  (Task Queue)    │  │                                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ PostgreSQL   │  │ Redis Cache  │  │Elasticsearch │  │  AWS S3              │   │
│  │ (Primary DB) │  │ (Sessions,   │  │ (Full-Text   │  │  (Documents,         │   │
│  │ Multi-AZ RDS │  │  Caching)    │  │  Search)     │  │   Invoices, Backups) │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                      MONITORING & OBSERVABILITY                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │ CloudWatch   │  │ Prometheus   │  │  Grafana     │  │  ELK Stack           │   │
│  │ (AWS Metrics)│  │ (App Metrics)│  │ (Dashboards) │  │  (Log Aggregation)   │   │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Architecture Principles

| Principle | Description |
|-----------|-------------|
| Microservices | Independently deployable services with single responsibility |
| Event-Driven | Asynchronous communication via events for loose coupling |
| API-First | All functionality exposed through well-defined REST APIs |
| Cloud-Native | Designed for AWS with auto-scaling and managed services |
| Security-First | Zero-trust architecture with encryption everywhere |
| Multi-Tenant | Single deployment serving multiple organizations |
| Domain-Driven | Services aligned with business domains |
| 12-Factor App | Following 12-factor methodology for cloud apps |

### 1.3 Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| Frontend | React.js | 18.x | Web application |
| Frontend | TypeScript | 5.x | Type safety |
| Frontend | TailwindCSS | 3.x | Styling |
| Frontend | Redux Toolkit | 2.x | State management |
| Backend | Python | 3.11+ | Microservices |
| Backend | FastAPI | 0.100+ | REST API framework |
| Backend | Celery | 5.x | Async task processing |
| Backend | SQLAlchemy | 2.x | ORM |
| Database | PostgreSQL | 15.x | Primary data store |
| Cache | Redis | 7.x | Caching, sessions, queues |
| Search | Elasticsearch | 8.x | Full-text search |
| Message Broker | RabbitMQ | 3.12+ | Event bus |
| AI/ML | scikit-learn | 1.x | ML models |
| AI/ML | OpenAI GPT-4 | Latest | NLP, contract parsing |
| AI/ML | AWS Textract | Latest | OCR processing |
| Container | Docker | 24.x | Containerization |
| Orchestration | AWS ECS/EKS | Latest | Container orchestration |
| CI/CD | GitHub Actions | Latest | Deployment pipeline |
| IaC | Terraform | 1.5+ | Infrastructure as Code |

---


## 2. Microservices Architecture

### 2.1 Service Registry

| Service | Port | Domain | Responsibilities |
|---------|------|--------|-----------------|
| Auth Service | 8001 | Identity & Access | Authentication, authorization, user management, RBAC |
| Contract Service | 8002 | Contract Lifecycle | Contract CRUD, parsing, classification, OCR, versioning |
| Billing Service | 8003 | Billing Rules | Billing models, rate cards, schedules, triggers, escalations |
| Invoice Service | 8004 | Invoicing | Invoice generation, approval, dispatch, credit/debit notes |
| Recognition Service | 8005 | Revenue Recognition | ASC 606 compliance, schedules, journal entries, deferrals |
| Profitability Service | 8006 | ClientMargin360 | Margin calculation, cost allocation, forecasts, benchmarks |
| Leakage Service | 8007 | Revenue Assurance | Detection, alerts, resolution tracking, trending |
| AI Service | 8008 | Intelligence | ML models, recommendations, predictions, NLP |
| Notification Service | 8009 | Communications | Email, SMS, in-app notifications, alerts |
| Integration Service | 8010 | External Systems | ERP sync, CRM sync, banking, webhooks |

### 2.2 Service Details

#### 2.2.1 Auth Service

```yaml
name: auth-service
language: Python 3.11
framework: FastAPI
database: PostgreSQL (shared schema: auth)
cache: Redis (sessions, tokens)
responsibilities:
  - User registration and authentication
  - JWT token issuance and refresh
  - OAuth2 provider integration (Google, Microsoft)
  - Role and permission management
  - Session management
  - Password reset flows
  - MFA (TOTP, SMS)
  - API key management
  - Audit logging for auth events
dependencies:
  - PostgreSQL
  - Redis
  - Email Service (for password reset)
scaling: 2-4 instances (CPU-bound during token validation)
```

#### 2.2.2 Contract Service

```yaml
name: contract-service
language: Python 3.11
framework: FastAPI
database: PostgreSQL (schema: contracts)
storage: AWS S3 (document storage)
dependencies:
  - AI Service (for OCR and NLP extraction)
  - Auth Service (authorization)
  - Billing Service (classification sync)
responsibilities:
  - Contract CRUD operations
  - Document upload and storage
  - AI-powered term extraction
  - Billing model classification
  - Version control and diffing
  - Amendment tracking
  - Performance obligation identification
  - Compliance validation
  - Contract search and filtering
scaling: 2-6 instances (I/O bound during OCR)
async_tasks:
  - contract.ocr_processing
  - contract.ai_extraction
  - contract.compliance_check
```

#### 2.2.3 Billing Service

```yaml
name: billing-service
language: Python 3.11
framework: FastAPI
database: PostgreSQL (schema: billing)
responsibilities:
  - Billing model configuration
  - Rate card management
  - Billing schedule creation
  - Trigger engine (milestone, period, SLA-based)
  - Escalation rule application
  - Billable activity ingestion
  - Timesheet processing
  - Activity classification (billable/non-billable)
dependencies:
  - Contract Service (contract terms)
  - Integration Service (timesheet/CRM data)
  - Invoice Service (trigger invoicing)
scaling: 3-8 instances (high throughput during billing cycles)
async_tasks:
  - billing.check_triggers
  - billing.process_timesheets
  - billing.apply_escalations
```

#### 2.2.4 Invoice Service

```yaml
name: invoice-service
language: Python 3.11
framework: FastAPI
database: PostgreSQL (schema: invoices)
storage: AWS S3 (generated PDFs)
responsibilities:
  - Invoice generation (single and bulk)
  - GST/TDS calculation
  - PDF rendering
  - Approval workflow management
  - Credit note and debit note handling
  - E-invoicing (IRP integration)
  - Invoice dispatch (email)
  - Template management
  - HSN/SAC code application
dependencies:
  - Billing Service (billable data)
  - Contract Service (contract terms)
  - Notification Service (email dispatch)
  - Integration Service (e-invoicing)
scaling: 2-10 instances (burst during month-end)
async_tasks:
  - invoice.generate_pdf
  - invoice.bulk_generate
  - invoice.dispatch_email
  - invoice.e_invoice_registration
```

#### 2.2.5 Recognition Service

```yaml
name: recognition-service
language: Python 3.11
framework: FastAPI
database: PostgreSQL (schema: revenue)
responsibilities:
  - ASC 606 five-step implementation
  - Ind AS 115 compliance
  - Revenue schedule generation
  - Journal entry creation
  - Deferred revenue management
  - Variable consideration constraints
  - Period close processing
  - Contract modification handling
  - Disclosure report generation
dependencies:
  - Contract Service (performance obligations)
  - Billing Service (billing periods)
  - Invoice Service (invoice data)
scaling: 2-4 instances (compute-heavy during period close)
async_tasks:
  - recognition.period_close
  - recognition.generate_schedules
  - recognition.compliance_report
```

#### 2.2.6 Profitability Service

```yaml
name: profitability-service
language: Python 3.11
framework: FastAPI
database: PostgreSQL (schema: profitability)
responsibilities:
  - Real-time margin calculation
  - Cost allocation (direct + indirect)
  - Overhead distribution
  - Client benchmarking
  - Profitability ranking
  - Trend analysis
  - Health score computation
  - What-if scenario modeling
dependencies:
  - Billing Service (revenue data)
  - Integration Service (cost data from HRMS/ERP)
  - AI Service (forecasts, recommendations)
scaling: 2-4 instances
async_tasks:
  - profitability.recalculate_all
  - profitability.generate_forecast
  - profitability.snapshot
```

#### 2.2.7 Leakage Service

```yaml
name: leakage-service
language: Python 3.11
framework: FastAPI
database: PostgreSQL (schema: leakage)
responsibilities:
  - Continuous leakage scanning
  - Unbilled hours detection
  - Missed milestone detection
  - Rate card variance detection
  - Scope creep identification
  - Escalation monitoring
  - Alert generation and management
  - Resolution workflow
  - Leakage trending and reporting
dependencies:
  - Billing Service (billable activities)
  - Contract Service (contracted terms)
  - AI Service (anomaly detection)
  - Notification Service (alerts)
scaling: 2-4 instances
async_tasks:
  - leakage.full_scan
  - leakage.client_scan
  - leakage.monthly_report
```

#### 2.2.8 AI Service

```yaml
name: ai-service
language: Python 3.11
framework: FastAPI
database: PostgreSQL (schema: ai)
gpu: Optional (for model inference)
responsibilities:
  - Contract NLP parsing (GPT-4 integration)
  - OCR processing (AWS Textract)
  - Anomaly detection
  - Margin forecasting (6-month)
  - Recommendation generation
  - Collection prediction
  - Leakage prediction
  - Model management and versioning
  - Confidence scoring
dependencies:
  - AWS Textract (OCR)
  - OpenAI API (NLP)
  - All other services (data for predictions)
scaling: 2-6 instances (GPU instances for ML inference)
async_tasks:
  - ai.contract_parse
  - ai.generate_recommendations
  - ai.train_model
  - ai.anomaly_scan
```

#### 2.2.9 Notification Service

```yaml
name: notification-service
language: Python 3.11
framework: FastAPI
database: PostgreSQL (schema: notifications)
responsibilities:
  - Email notifications (SES/SendGrid)
  - In-app notifications (WebSocket)
  - SMS notifications (SNS)
  - Alert management
  - Notification preferences
  - Template management
  - Delivery tracking
  - Digest/summary notifications
dependencies:
  - AWS SES (email)
  - AWS SNS (SMS)
  - Redis (WebSocket pub/sub)
scaling: 2-4 instances
async_tasks:
  - notification.send_email
  - notification.send_sms
  - notification.send_digest
```

#### 2.2.10 Integration Service

```yaml
name: integration-service
language: Python 3.11
framework: FastAPI
database: PostgreSQL (schema: integrations)
responsibilities:
  - Tally Prime sync (ledgers, vouchers)
  - SAP sync (cost centers, GL)
  - Salesforce CRM sync (opportunities, activities)
  - HRMS sync (employee costs, timesheets)
  - Banking integration (payment receipts)
  - GST portal integration (e-invoicing)
  - Webhook management (inbound/outbound)
  - Data transformation and mapping
  - Sync scheduling and retry logic
dependencies:
  - External systems (Tally, SAP, Salesforce, etc.)
  - All internal services (data sync)
scaling: 2-6 instances (I/O bound)
async_tasks:
  - integration.sync_tally
  - integration.sync_sap
  - integration.sync_crm
  - integration.process_webhook
```

### 2.3 Inter-Service Communication

```
┌─────────────────────────────────────────────────────────────────┐
│                  COMMUNICATION PATTERNS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  SYNCHRONOUS (REST/gRPC):                                        │
│  ├── Auth validation (every request)                             │
│  ├── Contract lookup (billing needs contract terms)              │
│  ├── Rate card lookup (invoice needs rates)                      │
│  └── User profile (notification needs contact info)              │
│                                                                   │
│  ASYNCHRONOUS (RabbitMQ Events):                                 │
│  ├── contract.created → Billing, Recognition                     │
│  ├── contract.amended → Recognition, Profitability               │
│  ├── invoice.generated → Recognition, Notification               │
│  ├── payment.received → Recognition, Profitability               │
│  ├── leakage.detected → Notification, Profitability              │
│  ├── margin.alert → Notification, AI                             │
│  ├── billing.trigger_fired → Invoice                             │
│  └── ai.recommendation_ready → Notification                      │
│                                                                   │
│  ASYNC TASKS (Celery + Redis):                                   │
│  ├── PDF generation                                              │
│  ├── Bulk invoice processing                                     │
│  ├── OCR processing                                              │
│  ├── AI model inference                                          │
│  ├── Report generation                                           │
│  ├── Scheduled scans                                             │
│  └── Data sync jobs                                              │
└─────────────────────────────────────────────────────────────────┘
```

---


## 3. API Gateway Design

### 3.1 Gateway Configuration (Kong / AWS API Gateway)

```yaml
gateway:
  type: Kong Enterprise / AWS API Gateway
  deployment: ECS container (Kong) or managed (AWS)
  
  features:
    rate_limiting:
      default: 1000 requests/minute/tenant
      burst: 2000 requests/minute
      strategy: sliding_window
      
    authentication:
      primary: JWT Bearer Token
      fallback: API Key (for integrations)
      
    cors:
      allowed_origins: ["https://*.finmark.ai"]
      allowed_methods: ["GET", "POST", "PUT", "PATCH", "DELETE"]
      max_age: 86400
      
    request_transformation:
      - Add tenant_id from JWT
      - Add request_id (UUID)
      - Add timestamp
      
    response_transformation:
      - Remove internal headers
      - Add rate limit headers
      - Compress (gzip/brotli)
      
    plugins:
      - rate-limiting
      - jwt-auth
      - cors
      - request-transformer
      - response-transformer
      - ip-restriction
      - bot-detection
      - prometheus
      - request-size-limiting (50MB max)
```

### 3.2 Route Configuration

| Route Pattern | Service | Auth | Rate Limit |
|---------------|---------|------|------------|
| `/api/auth/*` | Auth Service | Public (login/register) | 20/min |
| `/api/contracts/*` | Contract Service | JWT Required | 1000/min |
| `/api/billing/*` | Billing Service | JWT Required | 1000/min |
| `/api/invoices/*` | Invoice Service | JWT Required | 500/min |
| `/api/revenue/*` | Recognition Service | JWT Required | 500/min |
| `/api/profitability/*` | Profitability Service | JWT Required | 1000/min |
| `/api/leakage/*` | Leakage Service | JWT Required | 500/min |
| `/api/ai/*` | AI Service | JWT Required | 200/min |
| `/api/notifications/*` | Notification Service | JWT Required | 500/min |
| `/api/integrations/*` | Integration Service | JWT + API Key | 500/min |
| `/api/reports/*` | Report Aggregator | JWT Required | 200/min |
| `/api/dashboard/*` | Dashboard Aggregator | JWT Required | 1000/min |
| `/api/settings/*` | Config Service | JWT + Admin | 200/min |
| `/health` | All Services | None | Unlimited |

### 3.3 Load Balancing Strategy

```
                    ┌─────────────────────┐
                    │   AWS ALB (L7)      │
                    │   Health Checks     │
                    │   SSL Termination   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                 ▼
       ┌────────────┐  ┌────────────┐  ┌────────────┐
       │ Target     │  │ Target     │  │ Target     │
       │ Group A    │  │ Group B    │  │ Group C    │
       │ (Auth)     │  │ (Business) │  │ (AI/Heavy) │
       └────────────┘  └────────────┘  └────────────┘
       
Strategy: Least Outstanding Requests
Health Check: /health every 30s
Deregistration Delay: 60s
Stickiness: Disabled (stateless services)
```

---

## 4. Authentication & Authorization

### 4.1 Authentication Flow

```
┌──────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Client  │────>│  API Gateway │────>│ Auth Service │────>│  PostgreSQL  │
│  (React) │     │  (Kong)      │     │  (FastAPI)   │     │  (Users DB)  │
└──────────┘     └──────────────┘     └──────────────┘     └──────────────┘
     │                  │                     │                     │
     │  1. POST /login  │                     │                     │
     │─────────────────>│  2. Forward         │                     │
     │                  │────────────────────>│  3. Validate creds  │
     │                  │                     │────────────────────>│
     │                  │                     │<────────────────────│
     │                  │                     │  4. Generate JWT    │
     │                  │  5. Return tokens   │                     │
     │<─────────────────│<────────────────────│                     │
     │                  │                     │  6. Store session   │
     │  {access_token,  │                     │──────> Redis        │
     │   refresh_token} │                     │                     │
     │                  │                     │                     │
     │  7. API Request  │                     │                     │
     │  + Bearer Token  │                     │                     │
     │─────────────────>│  8. Validate JWT    │                     │
     │                  │────────────────────>│                     │
     │                  │<────────────────────│  9. OK + claims     │
     │                  │  10. Forward to svc │                     │
     │                  │───────────────────────────────> Service   │
     │<─────────────────│<─────────────────────────────── Response  │
```

### 4.2 JWT Token Structure

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "key-2026-07"
  },
  "payload": {
    "sub": "usr_a1b2c3d4",
    "org_id": "org_x1y2z3",
    "email": "user@finmark.ai",
    "name": "Priya Verma",
    "roles": ["finance_manager"],
    "permissions": ["invoice.create", "invoice.approve", "contract.read"],
    "iat": 1721324400,
    "exp": 1721328000,
    "iss": "https://auth.finmark.ai",
    "aud": "https://api.finmark.ai"
  }
}
```

**Token Lifetimes:**
| Token Type | Lifetime | Storage |
|------------|----------|---------|
| Access Token | 1 hour | Memory (client) |
| Refresh Token | 7 days | HttpOnly cookie + Redis |
| API Key | 1 year (revocable) | Database |

### 4.3 Role-Based Access Control (RBAC)

| Role | Description | Key Permissions |
|------|-------------|-----------------|
| `super_admin` | System administrator | All permissions, tenant management |
| `org_admin` | Organization admin | All org permissions, user management |
| `cfo` | Chief Financial Officer | Full read, approvals, write-offs, settings |
| `finance_manager` | Finance Manager | Invoice approve (<50L), recognition, reports |
| `accountant` | Senior Accountant | Invoice create/edit, payment recording |
| `operations_head` | VP Operations | Billable tracking, milestone management |
| `client_partner` | Account Manager | Client data (assigned only), recommendations |
| `auditor` | External Auditor | Read-only access to all financial data |
| `viewer` | Read-only User | Dashboard and report viewing only |

### 4.4 Permission Matrix

| Resource | Create | Read | Update | Delete | Approve |
|----------|--------|------|--------|--------|---------|
| Contracts | FM, OA | All | FM, OA | OA | CFO |
| Invoices | AC, FM | All | AC, FM | FM | FM, CFO |
| Revenue Entries | FM | All | FM | — | CFO |
| Leakage Alerts | System | All | FM, AC | — | — |
| Client Data | OA, CP | All | OA, CP | OA | — |
| Settings | OA | OA, CFO | OA | OA | — |
| Users | OA | OA | OA | OA | — |
| Reports | All | All | FM, OA | FM | — |

*Legend: OA=Org Admin, CFO=CFO, FM=Finance Manager, AC=Accountant, CP=Client Partner*

---

## 5. Event-Driven Architecture

### 5.1 Event Bus (RabbitMQ)

```yaml
rabbitmq:
  cluster: 3-node cluster (HA)
  vhost: /revrecog
  
  exchanges:
    - name: revrecog.events
      type: topic
      durable: true
      
    - name: revrecog.commands
      type: direct
      durable: true
      
    - name: revrecog.dlx
      type: fanout
      durable: true
      description: Dead Letter Exchange

  queues:
    contract_events:
      binding: revrecog.events / contract.*
      consumers: [billing-service, recognition-service, leakage-service]
      
    invoice_events:
      binding: revrecog.events / invoice.*
      consumers: [recognition-service, notification-service, profitability-service]
      
    payment_events:
      binding: revrecog.events / payment.*
      consumers: [recognition-service, profitability-service, notification-service]
      
    leakage_events:
      binding: revrecog.events / leakage.*
      consumers: [notification-service, profitability-service]
      
    margin_events:
      binding: revrecog.events / margin.*
      consumers: [notification-service, ai-service]
      
    integration_events:
      binding: revrecog.events / integration.*
      consumers: [billing-service, profitability-service]
```

### 5.2 Event Catalog

| Event Name | Producer | Consumers | Payload |
|------------|----------|-----------|---------|
| `contract.created` | Contract Service | Billing, Recognition | contract_id, org_id, billing_model |
| `contract.amended` | Contract Service | Recognition, Profitability | contract_id, changes, effective_date |
| `contract.expiring` | Contract Service | Notification | contract_id, expiry_date, days_remaining |
| `billing.trigger_fired` | Billing Service | Invoice Service | client_id, trigger_type, amount |
| `billing.escalation_applied` | Billing Service | Notification, Contract | client_id, new_rate, effective_date |
| `invoice.generated` | Invoice Service | Recognition, Notification | invoice_id, amount, client_id |
| `invoice.approved` | Invoice Service | Notification, Dispatch | invoice_id, approver_id |
| `invoice.dispatched` | Invoice Service | Notification | invoice_id, dispatch_method |
| `payment.received` | Integration Service | Recognition, Profitability | payment_id, invoice_id, amount |
| `payment.overdue` | Collections | Notification, Escalation | invoice_id, days_overdue, amount |
| `leakage.detected` | Leakage Service | Notification, Profitability | alert_id, type, amount, severity |
| `leakage.resolved` | Leakage Service | Profitability | alert_id, resolution, recovered_amount |
| `margin.below_threshold` | Profitability | Notification, AI | client_id, margin, threshold |
| `margin.eroding` | Profitability | Notification, AI | client_id, trend, months |
| `ai.recommendation_ready` | AI Service | Notification | recommendation_id, client_id, type |
| `recognition.period_closed` | Recognition | Notification, Reporting | period, total_recognized |
| `integration.sync_completed` | Integration | All relevant | source, records_synced, errors |
| `user.login` | Auth Service | Audit | user_id, ip, timestamp |

### 5.3 Event Schema (CloudEvents Format)

```json
{
  "specversion": "1.0",
  "id": "evt_a1b2c3d4e5f6",
  "source": "urn:finmark:service:invoice",
  "type": "invoice.generated",
  "time": "2026-07-18T17:00:00Z",
  "datacontenttype": "application/json",
  "subject": "inv_123456",
  "data": {
    "invoice_id": "inv_123456",
    "org_id": "org_x1y2z3",
    "client_id": "cli_789",
    "amount": 1500000,
    "currency": "INR",
    "billing_period": "2026-07",
    "generated_by": "system"
  }
}
```

---

## 6. Queue Architecture

### 6.1 Celery Task Queues (Redis Backend)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CELERY TASK ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  HIGH PRIORITY QUEUE (celery_high):                              │
│  ├── Invoice approval notifications                              │
│  ├── Leakage alerts (HIGH severity)                              │
│  ├── Payment received processing                                 │
│  ├── Margin breach alerts                                        │
│  └── Workers: 4 dedicated                                        │
│                                                                   │
│  DEFAULT QUEUE (celery_default):                                 │
│  ├── Invoice PDF generation                                      │
│  ├── Revenue recognition processing                              │
│  ├── Report generation                                           │
│  ├── Email notifications                                         │
│  ├── Data sync operations                                        │
│  └── Workers: 8 auto-scaled                                      │
│                                                                   │
│  BULK QUEUE (celery_bulk):                                       │
│  ├── Bulk invoice generation (month-end)                         │
│  ├── Full leakage scan                                           │
│  ├── Portfolio profitability recalculation                       │
│  ├── Scheduled report generation                                 │
│  └── Workers: 4-16 (auto-scale on queue depth)                   │
│                                                                   │
│  AI QUEUE (celery_ai):                                           │
│  ├── Contract OCR processing                                     │
│  ├── NLP term extraction                                         │
│  ├── AI recommendation generation                                │
│  ├── Anomaly detection scans                                     │
│  ├── Forecast model inference                                    │
│  └── Workers: 2-8 (GPU-enabled instances)                        │
│                                                                   │
│  SCHEDULED QUEUE (celery_beat):                                  │
│  ├── Daily: Leakage scan, margin alerts, aging update            │
│  ├── Weekly: Profitability snapshot, trend analysis              │
│  ├── Monthly: Period close, compliance report                    │
│  ├── Hourly: Billing trigger check, payment sync                 │
│  └── Workers: 2 dedicated                                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 Queue Configuration

```python
# celery_config.py
from celery import Celery
from celery.schedules import crontab

app = Celery('revrecog')

app.conf.update(
    broker_url='redis://redis-cluster:6379/0',
    result_backend='redis://redis-cluster:6379/1',
    
    task_queues={
        'celery_high': {'exchange': 'high', 'routing_key': 'high'},
        'celery_default': {'exchange': 'default', 'routing_key': 'default'},
        'celery_bulk': {'exchange': 'bulk', 'routing_key': 'bulk'},
        'celery_ai': {'exchange': 'ai', 'routing_key': 'ai'},
        'celery_beat': {'exchange': 'beat', 'routing_key': 'beat'},
    },
    
    task_routes={
        'invoice.generate_pdf': {'queue': 'celery_default'},
        'invoice.bulk_generate': {'queue': 'celery_bulk'},
        'invoice.approve_notify': {'queue': 'celery_high'},
        'leakage.full_scan': {'queue': 'celery_bulk'},
        'leakage.alert_high': {'queue': 'celery_high'},
        'ai.contract_ocr': {'queue': 'celery_ai'},
        'ai.generate_recommendation': {'queue': 'celery_ai'},
        'recognition.period_close': {'queue': 'celery_bulk'},
        'notification.send_email': {'queue': 'celery_default'},
        'integration.sync_*': {'queue': 'celery_default'},
    },
    
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Kolkata',
    enable_utc=True,
    
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,       # 10 minutes hard limit
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    
    beat_schedule={
        'hourly-billing-triggers': {
            'task': 'billing.check_all_triggers',
            'schedule': crontab(minute=0),
        },
        'daily-leakage-scan': {
            'task': 'leakage.full_scan',
            'schedule': crontab(hour=6, minute=0),
        },
        'daily-margin-alerts': {
            'task': 'profitability.check_margins',
            'schedule': crontab(hour=7, minute=0),
        },
        'daily-aging-update': {
            'task': 'collections.update_aging',
            'schedule': crontab(hour=1, minute=0),
        },
        'weekly-profitability-snapshot': {
            'task': 'profitability.take_snapshot',
            'schedule': crontab(hour=2, minute=0, day_of_week=1),
        },
        'monthly-period-close-reminder': {
            'task': 'recognition.period_close_reminder',
            'schedule': crontab(hour=9, minute=0, day_of_month=28),
        },
    }
)
```

### 6.3 Dead Letter Queue (DLQ) Strategy

| Queue | Max Retries | Retry Delay | DLQ Action |
|-------|-------------|-------------|------------|
| celery_high | 5 | Exponential (1s, 5s, 30s, 2m, 10m) | Alert on-call + manual review |
| celery_default | 3 | Exponential (30s, 5m, 30m) | Log + retry next cycle |
| celery_bulk | 2 | Fixed (5m) | Log + admin notification |
| celery_ai | 3 | Exponential (1m, 5m, 15m) | Fallback to rule-based |
| celery_beat | 1 | None | Log + next schedule |

---


## 7. Database Architecture

### 7.1 Database Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  PostgreSQL 15 (AWS RDS Multi-AZ)                        │    │
│  │  ├── Primary: db.r6g.2xlarge (8 vCPU, 64 GB RAM)       │    │
│  │  ├── Read Replica 1: db.r6g.xlarge (reporting)          │    │
│  │  ├── Read Replica 2: db.r6g.xlarge (analytics)          │    │
│  │  ├── Storage: 500 GB gp3 (auto-scaling to 2TB)         │    │
│  │  ├── Encryption: AES-256 (aws/rds KMS key)             │    │
│  │  └── Backup: Daily snapshots, 35-day retention          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Redis 7 (AWS ElastiCache Cluster)                       │    │
│  │  ├── Primary: cache.r6g.xlarge (3-node cluster)         │    │
│  │  ├── Purpose: Sessions, caching, Celery broker          │    │
│  │  ├── Eviction: allkeys-lru                              │    │
│  │  ├── Persistence: AOF (appendonly)                      │    │
│  │  └── TTL Defaults: Session=30m, Cache=5m, Token=1h     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Elasticsearch 8 (AWS OpenSearch)                        │    │
│  │  ├── Cluster: 3 data nodes (r6g.large)                  │    │
│  │  ├── Purpose: Full-text search, log aggregation         │    │
│  │  ├── Indices: contracts, invoices, audit_logs           │    │
│  │  └── Retention: 90 days for logs, permanent for search  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  AWS S3                                                   │    │
│  │  ├── Bucket: finmark-documents (contracts, invoices)    │    │
│  │  ├── Bucket: finmark-backups (DB backups, exports)      │    │
│  │  ├── Bucket: finmark-assets (static assets)             │    │
│  │  ├── Lifecycle: IA after 90d, Glacier after 365d        │    │
│  │  ├── Encryption: SSE-S3 + bucket policy                 │    │
│  │  └── Versioning: Enabled for documents bucket           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Schema Isolation (Multi-Tenant)

```sql
-- Schema per logical domain, tenant isolation via org_id column
-- Row-Level Security (RLS) for tenant isolation

CREATE SCHEMA auth;      -- organizations, users, roles, permissions
CREATE SCHEMA contracts; -- contracts, versions, terms, obligations
CREATE SCHEMA billing;   -- models, rules, schedules, rate_cards
CREATE SCHEMA invoices;  -- invoices, line_items, approvals
CREATE SCHEMA revenue;   -- schedules, entries, deferred, recognized
CREATE SCHEMA leakage;   -- detections, rules, alerts, resolutions
CREATE SCHEMA profitability; -- costs, margins, snapshots, benchmarks
CREATE SCHEMA collections;   -- receivables, payments, aging, dunning
CREATE SCHEMA ai;        -- recommendations, models, predictions
CREATE SCHEMA integrations;  -- configs, sync_logs, webhooks
CREATE SCHEMA notifications; -- notifications, templates, preferences
CREATE SCHEMA reports;   -- templates, schedules, exports, dashboards
CREATE SCHEMA settings;  -- system_settings, feature_flags, tax

-- Row-Level Security Example
ALTER TABLE contracts.contracts ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON contracts.contracts
  USING (org_id = current_setting('app.current_org_id')::UUID);
```

### 7.3 Connection Pooling

```yaml
pgbouncer:
  deployment: Sidecar container per service
  pool_mode: transaction
  max_client_connections: 1000
  default_pool_size: 20
  min_pool_size: 5
  reserve_pool_size: 5
  reserve_pool_timeout: 3
  server_idle_timeout: 600
  query_timeout: 30
```

---

## 8. Deployment Architecture

### 8.1 Container Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  DOCKER CONTAINER LAYOUT                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Service Container (per microservice):                           │
│  ┌───────────────────────────────────────────────┐              │
│  │  Base Image: python:3.11-slim-bookworm         │              │
│  │  ├── App code (FastAPI)                        │              │
│  │  ├── Dependencies (pip, requirements.txt)      │              │
│  │  ├── Health check endpoint                     │              │
│  │  ├── Non-root user (appuser:1000)              │              │
│  │  └── Resource limits defined                   │              │
│  └───────────────────────────────────────────────┘              │
│                                                                   │
│  Worker Container (Celery):                                      │
│  ┌───────────────────────────────────────────────┐              │
│  │  Base Image: python:3.11-slim-bookworm         │              │
│  │  ├── Celery worker process                     │              │
│  │  ├── Queue-specific concurrency settings       │              │
│  │  ├── Health check (celery inspect ping)        │              │
│  │  └── Auto-scaling based on queue depth         │              │
│  └───────────────────────────────────────────────┘              │
│                                                                   │
│  Frontend Container:                                             │
│  ┌───────────────────────────────────────────────┐              │
│  │  Base Image: node:20-alpine (build)            │              │
│  │  Runtime: nginx:alpine                         │              │
│  │  ├── React build artifacts                     │              │
│  │  ├── Nginx config (SPA routing)                │              │
│  │  └── Served via CloudFront                     │              │
│  └───────────────────────────────────────────────┘              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 8.2 ECS Task Definitions

| Service | vCPU | Memory | Min Tasks | Max Tasks | Scaling Metric |
|---------|------|--------|-----------|-----------|---------------|
| Auth Service | 0.5 | 1 GB | 2 | 4 | CPU > 70% |
| Contract Service | 1.0 | 2 GB | 2 | 6 | CPU > 70% |
| Billing Service | 1.0 | 2 GB | 3 | 8 | Queue depth |
| Invoice Service | 1.0 | 2 GB | 2 | 10 | Queue depth |
| Recognition Service | 1.0 | 2 GB | 2 | 4 | CPU > 70% |
| Profitability Service | 0.5 | 1 GB | 2 | 4 | CPU > 70% |
| Leakage Service | 0.5 | 1 GB | 2 | 4 | CPU > 70% |
| AI Service | 2.0 | 4 GB | 2 | 8 | Queue depth + CPU |
| Notification Service | 0.25 | 512 MB | 2 | 4 | Queue depth |
| Integration Service | 0.5 | 1 GB | 2 | 6 | Queue depth |
| Celery Workers (default) | 1.0 | 2 GB | 4 | 16 | Queue depth |
| Celery Workers (AI) | 2.0 | 4 GB | 2 | 8 | Queue depth |
| Celery Beat | 0.25 | 512 MB | 1 | 1 | — |

### 8.3 CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
pipeline:
  stages:
    - lint_and_test:
        - ruff (Python linting)
        - pytest (unit tests, >80% coverage)
        - mypy (type checking)
        - eslint + jest (frontend)
        
    - build:
        - Docker build (multi-stage)
        - Push to ECR
        - Tag with git SHA + semver
        
    - deploy_staging:
        - ECS update (staging cluster)
        - Run integration tests
        - Run E2E tests (Playwright)
        - Performance baseline check
        
    - deploy_production:
        - Blue/green deployment
        - Canary release (10% → 50% → 100%)
        - Automated rollback on error rate >1%
        - Post-deploy smoke tests
        
    - post_deploy:
        - Update Grafana annotations
        - Notify Slack
        - Update changelog
```

---

## 9. AWS Architecture

### 9.1 AWS Infrastructure Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  AWS Region: ap-south-1 (Mumbai)                                             │
│                                                                               │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  VPC: 10.0.0.0/16                                                     │  │
│  │                                                                         │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  PUBLIC SUBNETS (10.0.1.0/24, 10.0.2.0/24, 10.0.3.0/24)       │  │  │
│  │  │  ├── NAT Gateways (x3, one per AZ)                             │  │  │
│  │  │  ├── Application Load Balancer (ALB)                            │  │  │
│  │  │  └── Bastion Host (for emergency access)                        │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                         │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  PRIVATE SUBNETS - APP (10.0.10.0/24, 10.0.11.0/24, 10.0.12.0)│  │  │
│  │  │  ├── ECS Fargate Tasks (all microservices)                      │  │  │
│  │  │  ├── Celery Workers                                             │  │  │
│  │  │  └── Internal ALB (service-to-service)                          │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                         │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │  PRIVATE SUBNETS - DATA (10.0.20.0/24, 10.0.21.0/24, 10.0.22.0)│  │  │
│  │  │  ├── RDS PostgreSQL (Multi-AZ)                                  │  │  │
│  │  │  ├── ElastiCache Redis (Cluster)                                │  │  │
│  │  │  ├── OpenSearch (Elasticsearch)                                 │  │  │
│  │  │  └── RabbitMQ (Amazon MQ)                                       │  │  │
│  │  └─────────────────────────────────────────────────────────────────┘  │  │
│  │                                                                         │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  GLOBAL SERVICES                                                     │    │
│  │  ├── CloudFront (CDN for frontend + API acceleration)               │    │
│  │  ├── Route 53 (DNS: api.finmark.ai, app.finmark.ai)                │    │
│  │  ├── ACM (SSL certificates)                                         │    │
│  │  ├── WAF (Web Application Firewall)                                 │    │
│  │  ├── S3 (Documents, backups, static assets)                         │    │
│  │  ├── SQS (Dead letter queues, async decoupling)                     │    │
│  │  ├── SES (Transactional email)                                      │    │
│  │  ├── SNS (SMS notifications, alerts)                                │    │
│  │  ├── Lambda (Scheduled tasks, event processing)                     │    │
│  │  ├── Textract (OCR for contracts)                                   │    │
│  │  ├── KMS (Encryption key management)                                │    │
│  │  ├── Secrets Manager (API keys, credentials)                        │    │
│  │  ├── ECR (Container registry)                                       │    │
│  │  └── CloudWatch (Logs, metrics, alarms)                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 9.2 AWS Service Configuration

| Service | Configuration | Monthly Cost (Est.) |
|---------|---------------|-------------------|
| ECS Fargate | 30-60 tasks, mixed vCPU/memory | Rs. 3-5L |
| RDS PostgreSQL | db.r6g.2xlarge Multi-AZ + 2 replicas | Rs. 2-3L |
| ElastiCache Redis | cache.r6g.xlarge 3-node cluster | Rs. 80K-1L |
| OpenSearch | 3x r6g.large data nodes | Rs. 1-1.5L |
| Amazon MQ (RabbitMQ) | mq.m5.large 3-node | Rs. 60-80K |
| S3 | ~1TB with lifecycle | Rs. 20-30K |
| CloudFront | 500GB transfer/month | Rs. 30-40K |
| ALB | 2 ALBs (public + internal) | Rs. 15-20K |
| NAT Gateway | 3 (one per AZ) | Rs. 30-40K |
| Textract | ~1000 pages/month | Rs. 10-15K |
| SES | ~50K emails/month | Rs. 5-8K |
| CloudWatch | Logs, metrics, alarms | Rs. 20-30K |
| WAF | Standard rules + custom | Rs. 15-20K |
| Secrets Manager | ~50 secrets | Rs. 5K |
| **Total Infrastructure** | | **Rs. 8-12L/month** |

### 9.3 AWS Lambda Functions

| Function | Trigger | Purpose |
|----------|---------|---------|
| `contract-ocr-trigger` | S3 PUT (contracts bucket) | Trigger OCR on new contract upload |
| `invoice-pdf-watermark` | S3 PUT (invoices bucket) | Add watermark to draft invoices |
| `scheduled-aging-update` | CloudWatch Events (daily) | Update aging buckets |
| `webhook-processor` | API Gateway (webhook endpoint) | Process inbound webhooks |
| `backup-validator` | S3 PUT (backups bucket) | Validate DB backup integrity |
| `metric-aggregator` | CloudWatch Events (5-min) | Aggregate custom business metrics |
| `alert-escalation` | SNS Topic | Escalate unacknowledged alerts |

---


## 10. Security Architecture

### 10.1 Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  LAYER 1: PERIMETER                                              │
│  ├── AWS WAF (SQL injection, XSS, rate limiting)                │
│  ├── CloudFront (DDoS protection, geo-restriction)              │
│  ├── Shield Standard (L3/L4 DDoS)                               │
│  └── IP Whitelisting (optional per tenant)                       │
│                                                                   │
│  LAYER 2: NETWORK                                                │
│  ├── VPC isolation (private subnets for app + data)             │
│  ├── Security Groups (least privilege)                           │
│  ├── NACLs (subnet-level filtering)                             │
│  ├── VPC Flow Logs (traffic monitoring)                          │
│  └── PrivateLink (AWS service endpoints)                         │
│                                                                   │
│  LAYER 3: APPLICATION                                            │
│  ├── JWT + OAuth2 authentication                                 │
│  ├── RBAC authorization (every endpoint)                         │
│  ├── Input validation (Pydantic models)                          │
│  ├── SQL injection prevention (parameterized queries)            │
│  ├── XSS prevention (content security policy)                    │
│  ├── CSRF protection (SameSite cookies)                          │
│  ├── Rate limiting (per user, per tenant)                        │
│  └── Request size limits (50MB max)                              │
│                                                                   │
│  LAYER 4: DATA                                                   │
│  ├── Encryption at rest (AES-256, KMS managed)                  │
│  ├── Encryption in transit (TLS 1.3)                             │
│  ├── Row-Level Security (tenant isolation)                       │
│  ├── Column-level encryption (PII fields)                        │
│  ├── Data masking (in non-prod environments)                     │
│  ├── Backup encryption                                           │
│  └── Key rotation (annual, automated)                            │
│                                                                   │
│  LAYER 5: MONITORING & RESPONSE                                  │
│  ├── Real-time threat detection (GuardDuty)                     │
│  ├── Configuration compliance (AWS Config)                       │
│  ├── Audit logging (CloudTrail + app audit)                     │
│  ├── Vulnerability scanning (Inspector)                          │
│  ├── Incident response playbooks                                 │
│  └── Security Information & Event Management (SIEM)              │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 WAF Rules

| Rule | Action | Description |
|------|--------|-------------|
| AWS Managed - Common | Block | OWASP Top 10 protections |
| AWS Managed - SQL Injection | Block | SQLi pattern detection |
| AWS Managed - XSS | Block | Cross-site scripting |
| Rate Limit - IP | Block (>2000/5min) | DDoS prevention |
| Rate Limit - Auth | Block (>20/min) | Brute force prevention |
| Geo Restriction | Allow IN, US, GB, SG | Geographic filtering |
| Bot Control | Challenge | Bot detection and mitigation |
| Custom - API Abuse | Block | Custom patterns for API abuse |

### 10.3 PII Handling

| Data Type | Storage | Access | Masking |
|-----------|---------|--------|---------|
| User email | Encrypted column | Auth + self | Partial mask in logs |
| Phone number | Encrypted column | Auth + self | Full mask |
| Bank details | Encrypted column | Finance role only | Full mask |
| PAN/Aadhaar | Encrypted (separate key) | Compliance only | Full mask |
| Client names | Plain text | All authenticated | No mask |
| Invoice amounts | Plain text | Role-based | No mask |
| Passwords | bcrypt hash (12 rounds) | Never readable | N/A |
| API keys | SHA-256 hash | Never readable | Prefix only shown |

### 10.4 Compliance Controls

| Standard | Controls Implemented |
|----------|---------------------|
| SOC 2 Type II | Access controls, encryption, monitoring, incident response, change management |
| OWASP Top 10 | WAF, input validation, parameterized queries, CSP, secure headers |
| ISO 27001 | Information security policies, risk assessment, access management |
| GDPR (applicable parts) | Data minimization, right to erasure, consent management |
| PCI DSS (Level 3) | Card data encryption, access logging, vulnerability management |

### 10.5 Security Headers

```nginx
# Nginx/ALB response headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-Frame-Options "DENY" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' fonts.googleapis.com; font-src 'self' fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.finmark.ai" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
```

---

## 11. Monitoring & Observability

### 11.1 Monitoring Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                 OBSERVABILITY ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  METRICS:                                                        │
│  ├── Prometheus (application metrics)                            │
│  │   ├── Request rate, latency, errors (RED)                    │
│  │   ├── Queue depth, processing time                           │
│  │   ├── DB connections, query time                             │
│  │   └── Custom business metrics                                │
│  ├── CloudWatch (infrastructure metrics)                         │
│  │   ├── CPU, memory, disk, network                             │
│  │   ├── ECS task health                                        │
│  │   ├── RDS performance insights                               │
│  │   └── ALB request counts, latency                            │
│  └── StatsD (custom counters/timers)                             │
│                                                                   │
│  LOGS:                                                           │
│  ├── CloudWatch Logs (centralized)                               │
│  │   ├── Application logs (structured JSON)                     │
│  │   ├── Access logs (ALB)                                      │
│  │   ├── VPC Flow Logs                                          │
│  │   └── CloudTrail (API audit)                                 │
│  └── ELK Stack (optional, for search/analysis)                   │
│      ├── Filebeat → Logstash → Elasticsearch                    │
│      └── Kibana dashboards                                       │
│                                                                   │
│  VISUALIZATION:                                                  │
│  ├── Grafana (primary dashboards)                                │
│  │   ├── Service health dashboard                               │
│  │   ├── Business metrics dashboard                             │
│  │   ├── Infrastructure dashboard                               │
│  │   └── Alert overview                                         │
│  └── CloudWatch Dashboards (AWS-native)                          │
│                                                                   │
│  ALERTING:                                                       │
│  ├── Grafana Alerts → PagerDuty/Slack                           │
│  ├── CloudWatch Alarms → SNS → Slack/Email                     │
│  └── Custom alert rules (business-critical)                      │
│                                                                   │
│  TRACING:                                                        │
│  ├── AWS X-Ray (distributed tracing)                             │
│  │   ├── Request trace across services                          │
│  │   ├── Latency analysis                                       │
│  │   └── Error root cause                                       │
│  └── OpenTelemetry (instrumentation)                             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 11.2 Key Dashboards

| Dashboard | Metrics | Audience |
|-----------|---------|----------|
| Service Health | Uptime, error rate, latency per service | DevOps |
| Business Metrics | Invoices generated, leakage detected, revenue recognized | Product/Finance |
| Infrastructure | CPU, memory, disk, network, RDS performance | DevOps |
| Queue Monitoring | Queue depth, processing time, DLQ count | DevOps |
| Security | Failed logins, WAF blocks, suspicious activity | Security |
| AI Performance | Model accuracy, prediction latency, queue times | Data Team |
| Cost Optimization | AWS spend by service, cost anomalies | Finance/DevOps |

### 11.3 Alert Rules

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| Service Down | Health check fails 3x consecutive | P1-Critical | PagerDuty + Slack |
| High Error Rate | >5% 5xx in 5 minutes | P1-Critical | PagerDuty + Slack |
| High Latency | p99 >5s for 10 minutes | P2-High | Slack + Email |
| Queue Backup | Depth >1000 for 15 minutes | P2-High | Slack + Auto-scale |
| DB Connections | >80% pool utilized | P2-High | Slack + Email |
| Disk Space | >85% utilized | P3-Medium | Email |
| Certificate Expiry | <30 days to expiry | P3-Medium | Email |
| DLQ Messages | Any message in DLQ | P2-High | Slack + Email |
| Cost Anomaly | >20% increase day-over-day | P3-Medium | Email |
| Security: Brute Force | >50 failed logins from IP | P1-Critical | Auto-block + Slack |
| Business: Leakage Spike | >Rs.10L detected in single scan | P2-High | CFO Alert |

### 11.4 Log Format (Structured JSON)

```json
{
  "timestamp": "2026-07-18T17:14:33.639Z",
  "level": "INFO",
  "service": "invoice-service",
  "trace_id": "abc123def456",
  "span_id": "span_789",
  "request_id": "req_a1b2c3",
  "org_id": "org_x1y2z3",
  "user_id": "usr_456",
  "method": "POST",
  "path": "/api/invoices/generate",
  "status_code": 201,
  "duration_ms": 1250,
  "message": "Invoice generated successfully",
  "metadata": {
    "invoice_id": "inv_789",
    "client_id": "cli_123",
    "amount": 1500000
  }
}
```

### 11.5 SLA Monitoring

| SLA | Target | Measurement | Dashboard |
|-----|--------|-------------|-----------|
| Availability | 99.9% | Synthetic monitoring (5-min intervals) | Service Health |
| API Latency (p95) | <500ms | Prometheus histogram | Service Health |
| Invoice Generation | <30s | Custom timer metric | Business Metrics |
| Data Freshness | <5 min | Lag measurement | Business Metrics |
| Incident Response | <15 min (P1) | PagerDuty metrics | Security |

---

*Document End — RevRecog AI + ClientMargin360 System Architecture v2.0.0*
