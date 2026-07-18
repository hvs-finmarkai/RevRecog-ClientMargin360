# Database Schema Design
## RevRecog AI + ClientMargin360
### Finmark.ai | Denave India Pvt. Ltd.

| Field | Value |
|-------|-------|
| **Document Version** | 2.0.0 |
| **Date** | July 2026 |
| **Database** | PostgreSQL 15.x |
| **Total Tables** | 87 |
| **Multi-Tenant** | Row-Level Security (org_id) |

---

## Table of Contents

1. [Organizations & Auth](#1-organizations--auth)
2. [Contracts](#2-contracts)
3. [Clients](#3-clients)
4. [Billing](#4-billing)
5. [Billables](#5-billables)
6. [Invoices](#6-invoices)
7. [Revenue Recognition](#7-revenue-recognition)
8. [Leakage](#8-leakage)
9. [Profitability](#9-profitability)
10. [Collections](#10-collections)
11. [AI](#11-ai)
12. [Integrations](#12-integrations)
13. [Notifications](#13-notifications)
14. [Reports](#14-reports)
15. [Settings](#15-settings)

---

## Common Conventions

All tables include:
- `id` — UUID primary key (gen_random_uuid())
- `created_at` — TIMESTAMPTZ NOT NULL DEFAULT NOW()
- `updated_at` — TIMESTAMPTZ NOT NULL DEFAULT NOW()
- `created_by` — UUID REFERENCES auth.users(id)
- `is_deleted` — BOOLEAN NOT NULL DEFAULT FALSE (soft delete)
- `org_id` — UUID NOT NULL REFERENCES auth.organizations(id) (tenant isolation)

Row-Level Security (RLS) is enabled on all tables with policy filtering on `org_id`.

---

## 1. Organizations & Auth

### 1.1 organizations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | Organization unique identifier |
| name | VARCHAR(255) | NOT NULL | Organization name |
| slug | VARCHAR(100) | UNIQUE, NOT NULL | URL-friendly slug |
| domain | VARCHAR(255) | | Company domain (for SSO) |
| logo_url | TEXT | | Organization logo |
| plan_tier | VARCHAR(50) | NOT NULL DEFAULT 'starter' | Subscription tier |
| subscription_status | VARCHAR(20) | NOT NULL DEFAULT 'active' | active/suspended/cancelled |
| subscription_start | DATE | | Subscription start date |
| subscription_end | DATE | | Subscription end date |
| max_users | INTEGER | NOT NULL DEFAULT 20 | Max users allowed |
| max_contracts | INTEGER | NOT NULL DEFAULT 50 | Max contracts allowed |
| settings_json | JSONB | DEFAULT '{}' | Organization-level settings |
| address_line1 | VARCHAR(255) | | |
| address_line2 | VARCHAR(255) | | |
| city | VARCHAR(100) | | |
| state | VARCHAR(100) | | |
| country | VARCHAR(100) | DEFAULT 'India' | |
| pincode | VARCHAR(20) | | |
| gstin | VARCHAR(20) | | GST Identification Number |
| pan | VARCHAR(20) | | PAN number |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_organizations_slug` (UNIQUE), `idx_organizations_domain`, `idx_organizations_status`

---

### 1.2 users

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | User unique identifier |
| org_id | UUID | FK → organizations(id), NOT NULL | Tenant reference |
| email | VARCHAR(255) | NOT NULL | User email (unique per org) |
| password_hash | VARCHAR(255) | NOT NULL | bcrypt hashed password |
| first_name | VARCHAR(100) | NOT NULL | |
| last_name | VARCHAR(100) | NOT NULL | |
| phone | VARCHAR(20) | | |
| avatar_url | TEXT | | Profile picture |
| status | VARCHAR(20) | NOT NULL DEFAULT 'active' | active/inactive/suspended |
| email_verified | BOOLEAN | NOT NULL DEFAULT FALSE | |
| mfa_enabled | BOOLEAN | NOT NULL DEFAULT FALSE | |
| mfa_secret | VARCHAR(255) | | TOTP secret (encrypted) |
| last_login_at | TIMESTAMPTZ | | |
| last_login_ip | INET | | |
| failed_login_count | INTEGER | DEFAULT 0 | |
| locked_until | TIMESTAMPTZ | | Account lockout time |
| password_changed_at | TIMESTAMPTZ | | |
| preferences_json | JSONB | DEFAULT '{}' | User preferences |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_users_org_email` (UNIQUE on org_id, email), `idx_users_org_id`, `idx_users_status`

---

### 1.3 roles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| name | VARCHAR(100) | NOT NULL | Role name |
| slug | VARCHAR(100) | NOT NULL | Role slug (super_admin, cfo, etc.) |
| description | TEXT | | |
| is_system | BOOLEAN | DEFAULT FALSE | System-defined (non-deletable) |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_roles_org_slug` (UNIQUE on org_id, slug)

---

### 1.4 permissions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| resource | VARCHAR(100) | NOT NULL | Resource (contracts, invoices, etc.) |
| action | VARCHAR(50) | NOT NULL | Action (create, read, update, delete, approve) |
| description | TEXT | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_permissions_resource_action` (UNIQUE)

---

### 1.5 user_roles

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| user_id | UUID | FK → users(id), NOT NULL | |
| role_id | UUID | FK → roles(id), NOT NULL | |
| assigned_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| assigned_by | UUID | FK → users(id) | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_user_roles_user_role` (UNIQUE on user_id, role_id), `idx_user_roles_org`

---

### 1.6 audit_logs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| user_id | UUID | FK → users(id) | Actor (null for system) |
| action | VARCHAR(50) | NOT NULL | Action performed |
| resource_type | VARCHAR(100) | NOT NULL | Table/entity affected |
| resource_id | UUID | | ID of affected record |
| changes_json | JSONB | | Before/after values |
| ip_address | INET | | Request IP |
| user_agent | TEXT | | Browser/client info |
| request_id | UUID | | Correlation ID |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_audit_org_created` (org_id, created_at DESC), `idx_audit_resource` (resource_type, resource_id), `idx_audit_user`

---

### 1.7 sessions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| user_id | UUID | FK → users(id), NOT NULL | |
| refresh_token_hash | VARCHAR(255) | NOT NULL | Hashed refresh token |
| ip_address | INET | | |
| user_agent | TEXT | | |
| device_info | JSONB | | |
| expires_at | TIMESTAMPTZ | NOT NULL | |
| revoked_at | TIMESTAMPTZ | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_sessions_user` (user_id), `idx_sessions_token` (refresh_token_hash), `idx_sessions_expires` (expires_at)

---


## 2. Contracts

### 2.1 contracts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| contract_number | VARCHAR(50) | NOT NULL | Unique contract reference |
| title | VARCHAR(255) | NOT NULL | Contract title |
| description | TEXT | | |
| billing_model | VARCHAR(50) | NOT NULL | T&M/Fixed Milestone/Monthly Retainer/Performance-Based/Hybrid |
| status | VARCHAR(30) | NOT NULL DEFAULT 'draft' | draft/active/expired/terminated/under_review |
| total_value | NUMERIC(15,2) | NOT NULL | Total contract value |
| currency | VARCHAR(3) | DEFAULT 'INR' | |
| start_date | DATE | NOT NULL | |
| end_date | DATE | NOT NULL | |
| payment_terms_days | INTEGER | DEFAULT 30 | |
| auto_renewal | BOOLEAN | DEFAULT FALSE | |
| renewal_terms | TEXT | | |
| notice_period_days | INTEGER | DEFAULT 90 | |
| signed_date | DATE | | |
| signed_by | VARCHAR(255) | | |
| document_url | TEXT | | S3 URL for contract document |
| ai_confidence_score | NUMERIC(5,4) | | AI extraction confidence |
| ai_flags | JSONB | DEFAULT '[]' | AI-identified risks |
| metadata_json | JSONB | DEFAULT '{}' | Additional metadata |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_contracts_org_client` (org_id, client_id), `idx_contracts_number` (UNIQUE on org_id, contract_number), `idx_contracts_status`, `idx_contracts_dates` (start_date, end_date), `idx_contracts_billing_model`

---

### 2.2 contract_versions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| version_number | INTEGER | NOT NULL | Sequential version |
| changes_summary | TEXT | | Description of changes |
| changes_json | JSONB | NOT NULL | Detailed field-level changes |
| effective_date | DATE | | |
| document_url | TEXT | | Version-specific document |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_contract_versions_contract` (contract_id, version_number DESC)

---

### 2.3 contract_terms

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| term_type | VARCHAR(50) | NOT NULL | payment/escalation/penalty/sla/termination |
| term_key | VARCHAR(100) | NOT NULL | Machine-readable key |
| term_value | TEXT | NOT NULL | Term value/description |
| numeric_value | NUMERIC(15,2) | | Numeric representation |
| effective_from | DATE | | |
| effective_to | DATE | | |
| ai_extracted | BOOLEAN | DEFAULT FALSE | Extracted by AI |
| confidence_score | NUMERIC(5,4) | | AI confidence |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_contract_terms_contract` (contract_id), `idx_contract_terms_type` (term_type)

---

### 2.4 performance_obligations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| obligation_number | VARCHAR(20) | NOT NULL | PO-1, PO-2, etc. |
| description | TEXT | NOT NULL | Service/deliverable description |
| standalone_selling_price | NUMERIC(15,2) | NOT NULL | |
| allocated_price | NUMERIC(15,2) | NOT NULL | Transaction price allocation |
| satisfaction_type | VARCHAR(20) | NOT NULL | over_time/point_in_time |
| progress_measure | VARCHAR(50) | | input/output/time_based |
| completion_percentage | NUMERIC(5,2) | DEFAULT 0 | |
| status | VARCHAR(20) | DEFAULT 'active' | active/satisfied/cancelled |
| satisfied_date | DATE | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_perf_obligations_contract` (contract_id), `idx_perf_obligations_status`

---

### 2.5 contract_documents

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| document_type | VARCHAR(50) | NOT NULL | original/amendment/addendum/sow/nda |
| file_name | VARCHAR(255) | NOT NULL | |
| file_size | BIGINT | | Size in bytes |
| mime_type | VARCHAR(100) | | |
| s3_key | TEXT | NOT NULL | S3 object key |
| s3_bucket | VARCHAR(100) | NOT NULL | |
| ocr_status | VARCHAR(20) | DEFAULT 'pending' | pending/processing/completed/failed |
| ocr_text | TEXT | | Extracted text |
| upload_date | TIMESTAMPTZ | DEFAULT NOW() | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_contract_docs_contract` (contract_id), `idx_contract_docs_type` (document_type)

---

### 2.6 contract_amendments

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| amendment_number | INTEGER | NOT NULL | |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | | |
| amendment_type | VARCHAR(50) | NOT NULL | scope_change/pricing/extension/termination |
| effective_date | DATE | NOT NULL | |
| impact_analysis | JSONB | | Revenue/margin impact |
| old_value | NUMERIC(15,2) | | Previous contract value |
| new_value | NUMERIC(15,2) | | Updated contract value |
| status | VARCHAR(20) | DEFAULT 'pending' | pending/approved/rejected |
| approved_by | UUID | FK → users(id) | |
| approved_at | TIMESTAMPTZ | | |
| document_url | TEXT | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_amendments_contract` (contract_id), `idx_amendments_status`

---

## 3. Clients

### 3.1 clients

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| name | VARCHAR(255) | NOT NULL | Client company name |
| code | VARCHAR(50) | | Internal client code |
| industry_sector | VARCHAR(100) | | Telecom/BFSI/Technology/etc. |
| segment_id | UUID | FK → client_segments(id) | |
| status | VARCHAR(20) | DEFAULT 'active' | active/inactive/prospect/churned |
| website | VARCHAR(255) | | |
| gstin | VARCHAR(20) | | Client GST number |
| pan | VARCHAR(20) | | Client PAN |
| credit_limit | NUMERIC(15,2) | | |
| payment_terms_days | INTEGER | DEFAULT 30 | |
| health_score | NUMERIC(5,2) | | Composite health score (0-100) |
| lifetime_value | NUMERIC(15,2) | | Total revenue from client |
| notes | TEXT | | |
| metadata_json | JSONB | DEFAULT '{}' | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_clients_org` (org_id), `idx_clients_code` (UNIQUE on org_id, code), `idx_clients_sector`, `idx_clients_status`

---

### 3.2 client_contacts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| first_name | VARCHAR(100) | NOT NULL | |
| last_name | VARCHAR(100) | | |
| email | VARCHAR(255) | | |
| phone | VARCHAR(20) | | |
| designation | VARCHAR(100) | | |
| department | VARCHAR(100) | | |
| is_primary | BOOLEAN | DEFAULT FALSE | Primary billing contact |
| is_billing_contact | BOOLEAN | DEFAULT FALSE | Receives invoices |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_client_contacts_client` (client_id), `idx_client_contacts_primary` (client_id, is_primary)

---

### 3.3 client_addresses

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| address_type | VARCHAR(30) | NOT NULL | billing/shipping/registered |
| address_line1 | VARCHAR(255) | NOT NULL | |
| address_line2 | VARCHAR(255) | | |
| city | VARCHAR(100) | NOT NULL | |
| state | VARCHAR(100) | NOT NULL | |
| country | VARCHAR(100) | DEFAULT 'India' | |
| pincode | VARCHAR(20) | NOT NULL | |
| state_code | VARCHAR(5) | | GST state code |
| is_default | BOOLEAN | DEFAULT FALSE | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_client_addresses_client` (client_id)

---

### 3.4 client_preferences

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL, UNIQUE | |
| invoice_frequency | VARCHAR(20) | DEFAULT 'monthly' | weekly/biweekly/monthly/quarterly |
| invoice_format | VARCHAR(20) | DEFAULT 'pdf' | pdf/excel/both |
| invoice_delivery | VARCHAR(20) | DEFAULT 'email' | email/portal/both |
| po_required | BOOLEAN | DEFAULT FALSE | Purchase order required |
| auto_payment | BOOLEAN | DEFAULT FALSE | |
| preferred_currency | VARCHAR(3) | DEFAULT 'INR' | |
| custom_fields | JSONB | DEFAULT '{}' | Client-specific fields |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_client_prefs_client` (UNIQUE on client_id)

---

### 3.5 client_segments

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| name | VARCHAR(100) | NOT NULL | Segment name (Enterprise, Mid-Market, etc.) |
| description | TEXT | | |
| criteria_json | JSONB | | Segmentation criteria |
| color | VARCHAR(7) | | Display color (#hex) |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_client_segments_org` (org_id)

---


## 4. Billing

### 4.1 billing_models

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| name | VARCHAR(100) | NOT NULL | Model name |
| code | VARCHAR(50) | NOT NULL | tm/fixed_milestone/retainer/performance/hybrid |
| description | TEXT | | |
| recognition_pattern | VARCHAR(30) | NOT NULL | over_time/point_in_time/mixed |
| measurement_method | VARCHAR(50) | | input/output/time_based |
| timing_rule | TEXT | | When to recognize |
| variable_consideration | TEXT | | How to handle variable amounts |
| journal_template | JSONB | | Default journal entries |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_billing_models_org_code` (UNIQUE on org_id, code)

---

### 4.2 billing_rules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| billing_model_id | UUID | FK → billing_models(id) | |
| rule_name | VARCHAR(100) | NOT NULL | |
| rule_type | VARCHAR(50) | NOT NULL | time_based/milestone/usage/hybrid |
| trigger_condition | JSONB | NOT NULL | Conditions to trigger billing |
| amount_calculation | JSONB | NOT NULL | How to calculate amount |
| frequency | VARCHAR(20) | | monthly/quarterly/on_completion |
| is_active | BOOLEAN | DEFAULT TRUE | |
| priority | INTEGER | DEFAULT 0 | Rule priority (higher = first) |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_billing_rules_contract` (contract_id), `idx_billing_rules_active` (is_active)

---

### 4.3 billing_periods

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| period_start | DATE | NOT NULL | |
| period_end | DATE | NOT NULL | |
| status | VARCHAR(20) | DEFAULT 'open' | open/closed/invoiced |
| billable_amount | NUMERIC(15,2) | DEFAULT 0 | |
| invoiced_amount | NUMERIC(15,2) | DEFAULT 0 | |
| variance | NUMERIC(15,2) | DEFAULT 0 | |
| closed_at | TIMESTAMPTZ | | |
| closed_by | UUID | FK → users(id) | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_billing_periods_contract` (contract_id), `idx_billing_periods_dates` (period_start, period_end), `idx_billing_periods_status`

---

### 4.4 billing_schedules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| schedule_date | DATE | NOT NULL | Expected billing date |
| amount | NUMERIC(15,2) | NOT NULL | Scheduled amount |
| description | VARCHAR(255) | | |
| status | VARCHAR(20) | DEFAULT 'scheduled' | scheduled/triggered/invoiced/skipped |
| invoice_id | UUID | FK → invoices(id) | Linked invoice (after generation) |
| triggered_at | TIMESTAMPTZ | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_billing_schedules_contract` (contract_id), `idx_billing_schedules_date` (schedule_date), `idx_billing_schedules_status`

---

### 4.5 rate_cards

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| name | VARCHAR(100) | NOT NULL | Rate card name |
| effective_from | DATE | NOT NULL | |
| effective_to | DATE | | |
| currency | VARCHAR(3) | DEFAULT 'INR' | |
| status | VARCHAR(20) | DEFAULT 'active' | active/expired/superseded |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_rate_cards_contract` (contract_id), `idx_rate_cards_effective` (effective_from, effective_to)

---

### 4.6 rate_card_items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| rate_card_id | UUID | FK → rate_cards(id), NOT NULL | |
| resource_level | VARCHAR(100) | NOT NULL | senior_consultant/consultant/analyst/field_agent |
| description | VARCHAR(255) | | |
| unit | VARCHAR(20) | NOT NULL | hour/day/unit/month |
| rate | NUMERIC(10,2) | NOT NULL | Rate per unit |
| min_quantity | NUMERIC(10,2) | | Minimum billable |
| max_quantity | NUMERIC(10,2) | | Maximum billable |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_rate_card_items_card` (rate_card_id)

---

### 4.7 escalation_rules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| escalation_type | VARCHAR(50) | NOT NULL | annual_increment/cpi_linked/performance/custom |
| percentage | NUMERIC(5,2) | | Escalation percentage |
| fixed_amount | NUMERIC(15,2) | | Fixed escalation amount |
| frequency | VARCHAR(20) | NOT NULL | annual/biannual/quarterly |
| effective_date | DATE | NOT NULL | |
| next_escalation_date | DATE | | |
| last_applied_date | DATE | | |
| auto_apply | BOOLEAN | DEFAULT TRUE | |
| notification_days | INTEGER | DEFAULT 30 | Days before to notify |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_escalation_rules_contract` (contract_id), `idx_escalation_next_date` (next_escalation_date)

---

## 5. Billables

### 5.1 timesheets

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| employee_id | UUID | NOT NULL | Employee reference |
| client_id | UUID | FK → clients(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| period_start | DATE | NOT NULL | Week/period start |
| period_end | DATE | NOT NULL | |
| total_hours | NUMERIC(6,2) | NOT NULL DEFAULT 0 | |
| billable_hours | NUMERIC(6,2) | NOT NULL DEFAULT 0 | |
| non_billable_hours | NUMERIC(6,2) | DEFAULT 0 | |
| status | VARCHAR(20) | DEFAULT 'draft' | draft/submitted/approved/rejected |
| submitted_at | TIMESTAMPTZ | | |
| approved_by | UUID | FK → users(id) | |
| approved_at | TIMESTAMPTZ | | |
| source_system | VARCHAR(50) | | Origin system |
| source_id | VARCHAR(100) | | ID in origin system |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_timesheets_employee` (employee_id), `idx_timesheets_client` (client_id), `idx_timesheets_period` (period_start, period_end), `idx_timesheets_status`

---

### 5.2 timesheet_entries

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| timesheet_id | UUID | FK → timesheets(id), NOT NULL | |
| entry_date | DATE | NOT NULL | |
| hours | NUMERIC(4,2) | NOT NULL | |
| description | TEXT | | Activity description |
| activity_type | VARCHAR(50) | | meeting/development/travel/admin |
| is_billable | BOOLEAN | DEFAULT TRUE | |
| is_billed | BOOLEAN | DEFAULT FALSE | |
| billing_rate | NUMERIC(10,2) | | Applied rate |
| amount | NUMERIC(12,2) | | Calculated amount |
| invoice_id | UUID | FK → invoices(id) | Linked invoice |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_timesheet_entries_sheet` (timesheet_id), `idx_timesheet_entries_date` (entry_date), `idx_timesheet_entries_unbilled` (is_billable, is_billed)

---

### 5.3 milestones

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| milestone_number | INTEGER | NOT NULL | |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | | |
| amount | NUMERIC(15,2) | NOT NULL | Milestone value |
| due_date | DATE | | |
| completion_date | DATE | | |
| completion_percentage | NUMERIC(5,2) | DEFAULT 0 | |
| status | VARCHAR(20) | DEFAULT 'pending' | pending/in_progress/completed/accepted/invoiced |
| accepted_by | VARCHAR(255) | | Client acceptance |
| accepted_at | TIMESTAMPTZ | | |
| invoice_id | UUID | FK → invoices(id) | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_milestones_contract` (contract_id), `idx_milestones_status`, `idx_milestones_due_date`

---

### 5.4 milestone_deliverables

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| milestone_id | UUID | FK → milestones(id), NOT NULL | |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | | |
| deliverable_type | VARCHAR(50) | | report/software/data/service |
| status | VARCHAR(20) | DEFAULT 'pending' | pending/in_progress/completed |
| completed_at | TIMESTAMPTZ | | |
| evidence_url | TEXT | | Proof of delivery |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_milestone_deliverables_milestone` (milestone_id)

---

### 5.5 call_records

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id) | |
| agent_id | UUID | | Agent/employee reference |
| call_date | DATE | NOT NULL | |
| call_time | TIME | | |
| duration_seconds | INTEGER | NOT NULL | |
| call_type | VARCHAR(30) | | inbound/outbound |
| disposition | VARCHAR(50) | | connected/no_answer/voicemail/etc. |
| is_billable | BOOLEAN | DEFAULT TRUE | |
| is_billed | BOOLEAN | DEFAULT FALSE | |
| amount | NUMERIC(10,2) | | Billable amount |
| source_system | VARCHAR(50) | | Avaya/Genesys/etc. |
| source_id | VARCHAR(100) | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_call_records_client` (client_id), `idx_call_records_date` (call_date), `idx_call_records_unbilled` (is_billable, is_billed)

---

### 5.6 project_deliverables

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | | |
| quantity | NUMERIC(10,2) | NOT NULL DEFAULT 1 | |
| unit | VARCHAR(30) | | leads/units/reports/hours |
| unit_rate | NUMERIC(10,2) | | |
| total_amount | NUMERIC(15,2) | | |
| delivery_date | DATE | | |
| status | VARCHAR(20) | DEFAULT 'pending' | pending/delivered/accepted/invoiced |
| is_billed | BOOLEAN | DEFAULT FALSE | |
| invoice_id | UUID | FK → invoices(id) | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_project_deliverables_client` (client_id), `idx_project_deliverables_contract` (contract_id)

---

### 5.7 expenses

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id) | |
| employee_id | UUID | | |
| expense_date | DATE | NOT NULL | |
| category | VARCHAR(50) | NOT NULL | travel/meals/software/materials/other |
| description | TEXT | | |
| amount | NUMERIC(12,2) | NOT NULL | |
| currency | VARCHAR(3) | DEFAULT 'INR' | |
| is_reimbursable | BOOLEAN | DEFAULT TRUE | |
| is_billable | BOOLEAN | DEFAULT FALSE | Billable to client |
| is_billed | BOOLEAN | DEFAULT FALSE | |
| receipt_url | TEXT | | |
| status | VARCHAR(20) | DEFAULT 'pending' | pending/approved/rejected/billed |
| approved_by | UUID | FK → users(id) | |
| invoice_id | UUID | FK → invoices(id) | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_expenses_client` (client_id), `idx_expenses_date` (expense_date), `idx_expenses_status`

---


## 6. Invoices

### 6.1 invoices

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| invoice_number | VARCHAR(50) | NOT NULL | Sequential invoice number |
| invoice_date | DATE | NOT NULL | |
| due_date | DATE | NOT NULL | |
| billing_period_start | DATE | | |
| billing_period_end | DATE | | |
| subtotal | NUMERIC(15,2) | NOT NULL | Before tax |
| tax_amount | NUMERIC(15,2) | DEFAULT 0 | Total tax |
| cgst_amount | NUMERIC(15,2) | DEFAULT 0 | |
| sgst_amount | NUMERIC(15,2) | DEFAULT 0 | |
| igst_amount | NUMERIC(15,2) | DEFAULT 0 | |
| tds_amount | NUMERIC(15,2) | DEFAULT 0 | TDS deducted |
| total_amount | NUMERIC(15,2) | NOT NULL | Final amount |
| currency | VARCHAR(3) | DEFAULT 'INR' | |
| exchange_rate | NUMERIC(10,4) | DEFAULT 1 | |
| status | VARCHAR(20) | DEFAULT 'draft' | draft/pending_approval/approved/dispatched/paid/partially_paid/overdue/cancelled |
| payment_status | VARCHAR(20) | DEFAULT 'unpaid' | unpaid/partial/paid |
| paid_amount | NUMERIC(15,2) | DEFAULT 0 | |
| balance_amount | NUMERIC(15,2) | | |
| place_of_supply | VARCHAR(100) | | For GST determination |
| irn | VARCHAR(100) | | E-invoice reference number |
| irn_date | TIMESTAMPTZ | | |
| pdf_url | TEXT | | Generated PDF S3 URL |
| notes | TEXT | | |
| internal_notes | TEXT | | |
| template_id | UUID | FK → invoice_templates(id) | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_invoices_org_number` (UNIQUE on org_id, invoice_number), `idx_invoices_client` (client_id), `idx_invoices_contract` (contract_id), `idx_invoices_status`, `idx_invoices_due_date`, `idx_invoices_payment_status`

---

### 6.2 invoice_line_items

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| invoice_id | UUID | FK → invoices(id), NOT NULL | |
| line_number | INTEGER | NOT NULL | |
| description | TEXT | NOT NULL | |
| hsn_sac_code | VARCHAR(20) | | HSN/SAC code |
| quantity | NUMERIC(10,2) | NOT NULL DEFAULT 1 | |
| unit | VARCHAR(20) | | hours/days/units/months |
| unit_price | NUMERIC(12,2) | NOT NULL | |
| discount_percent | NUMERIC(5,2) | DEFAULT 0 | |
| discount_amount | NUMERIC(12,2) | DEFAULT 0 | |
| taxable_amount | NUMERIC(15,2) | NOT NULL | |
| gst_rate | NUMERIC(5,2) | DEFAULT 18 | |
| cgst_amount | NUMERIC(12,2) | DEFAULT 0 | |
| sgst_amount | NUMERIC(12,2) | DEFAULT 0 | |
| igst_amount | NUMERIC(12,2) | DEFAULT 0 | |
| total_amount | NUMERIC(15,2) | NOT NULL | |
| reference_type | VARCHAR(50) | | timesheet/milestone/deliverable/expense |
| reference_id | UUID | | ID of source record |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_line_items_invoice` (invoice_id), `idx_line_items_reference` (reference_type, reference_id)

---

### 6.3 invoice_templates

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| description | TEXT | | |
| template_html | TEXT | NOT NULL | HTML template |
| header_logo_url | TEXT | | |
| footer_text | TEXT | | |
| is_default | BOOLEAN | DEFAULT FALSE | |
| variables | JSONB | | Available template variables |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_invoice_templates_org` (org_id)

---

### 6.4 credit_notes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| credit_note_number | VARCHAR(50) | NOT NULL | |
| invoice_id | UUID | FK → invoices(id), NOT NULL | Original invoice |
| client_id | UUID | FK → clients(id), NOT NULL | |
| issue_date | DATE | NOT NULL | |
| amount | NUMERIC(15,2) | NOT NULL | |
| reason | TEXT | NOT NULL | |
| status | VARCHAR(20) | DEFAULT 'issued' | issued/applied/cancelled |
| applied_to_invoice_id | UUID | FK → invoices(id) | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_credit_notes_invoice` (invoice_id), `idx_credit_notes_client` (client_id)

---

### 6.5 debit_notes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| debit_note_number | VARCHAR(50) | NOT NULL | |
| invoice_id | UUID | FK → invoices(id) | Related invoice |
| client_id | UUID | FK → clients(id), NOT NULL | |
| issue_date | DATE | NOT NULL | |
| amount | NUMERIC(15,2) | NOT NULL | |
| reason | TEXT | NOT NULL | |
| status | VARCHAR(20) | DEFAULT 'issued' | issued/paid/cancelled |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_debit_notes_client` (client_id)

---

### 6.6 invoice_approvals

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| invoice_id | UUID | FK → invoices(id), NOT NULL | |
| approver_id | UUID | FK → users(id), NOT NULL | |
| approval_level | INTEGER | NOT NULL | 1, 2, 3 (sequential) |
| status | VARCHAR(20) | NOT NULL | pending/approved/rejected |
| comments | TEXT | | |
| decided_at | TIMESTAMPTZ | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_invoice_approvals_invoice` (invoice_id), `idx_invoice_approvals_approver` (approver_id, status)

---

### 6.7 invoice_dispatch

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| invoice_id | UUID | FK → invoices(id), NOT NULL | |
| dispatch_method | VARCHAR(20) | NOT NULL | email/portal/courier |
| recipient_email | VARCHAR(255) | | |
| recipient_name | VARCHAR(255) | | |
| dispatched_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| delivery_status | VARCHAR(20) | DEFAULT 'sent' | sent/delivered/bounced/opened |
| tracking_id | VARCHAR(100) | | Email message ID or courier tracking |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_invoice_dispatch_invoice` (invoice_id)

---

## 7. Revenue Recognition

### 7.1 revenue_schedules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| obligation_id | UUID | FK → performance_obligations(id) | |
| period_start | DATE | NOT NULL | |
| period_end | DATE | NOT NULL | |
| scheduled_amount | NUMERIC(15,2) | NOT NULL | |
| recognized_amount | NUMERIC(15,2) | DEFAULT 0 | |
| deferred_amount | NUMERIC(15,2) | DEFAULT 0 | |
| status | VARCHAR(20) | DEFAULT 'scheduled' | scheduled/partially_recognized/recognized/adjusted |
| recognition_date | DATE | | |
| recognition_method | VARCHAR(50) | | straight_line/output/input/point_in_time |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_rev_schedules_contract` (contract_id), `idx_rev_schedules_period` (period_start, period_end), `idx_rev_schedules_status`

---

### 7.2 revenue_entries

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| schedule_id | UUID | FK → revenue_schedules(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| entry_date | DATE | NOT NULL | |
| entry_type | VARCHAR(30) | NOT NULL | recognition/deferral/adjustment/reversal |
| debit_account | VARCHAR(100) | NOT NULL | |
| credit_account | VARCHAR(100) | NOT NULL | |
| amount | NUMERIC(15,2) | NOT NULL | |
| description | TEXT | | |
| reference_type | VARCHAR(50) | | invoice/milestone/period |
| reference_id | UUID | | |
| period_month | INTEGER | | Fiscal month (1-12) |
| period_year | INTEGER | | Fiscal year |
| is_posted | BOOLEAN | DEFAULT FALSE | Posted to GL |
| posted_at | TIMESTAMPTZ | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_rev_entries_schedule` (schedule_id), `idx_rev_entries_date` (entry_date), `idx_rev_entries_period` (period_year, period_month), `idx_rev_entries_posted`

---

### 7.3 deferred_revenue

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| invoice_id | UUID | FK → invoices(id) | Source invoice |
| original_amount | NUMERIC(15,2) | NOT NULL | Amount originally deferred |
| remaining_amount | NUMERIC(15,2) | NOT NULL | Current balance |
| release_start_date | DATE | NOT NULL | |
| release_end_date | DATE | NOT NULL | |
| release_method | VARCHAR(30) | NOT NULL | straight_line/milestone/usage |
| monthly_release | NUMERIC(15,2) | | For straight-line |
| status | VARCHAR(20) | DEFAULT 'active' | active/fully_released/cancelled |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_deferred_revenue_contract` (contract_id), `idx_deferred_revenue_status`

---

### 7.4 recognized_revenue

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| period_month | INTEGER | NOT NULL | 1-12 |
| period_year | INTEGER | NOT NULL | |
| recognized_amount | NUMERIC(15,2) | NOT NULL | |
| cumulative_recognized | NUMERIC(15,2) | NOT NULL | Total to date |
| total_contract_value | NUMERIC(15,2) | NOT NULL | |
| percentage_complete | NUMERIC(5,2) | | |
| recognition_basis | VARCHAR(50) | | Method used |
| is_finalized | BOOLEAN | DEFAULT FALSE | Period closed |
| finalized_at | TIMESTAMPTZ | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_recognized_rev_period` (org_id, period_year, period_month), `idx_recognized_rev_contract` (contract_id)

---

### 7.5 recognition_rules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| billing_model | VARCHAR(50) | NOT NULL | |
| rule_name | VARCHAR(100) | NOT NULL | |
| recognition_pattern | VARCHAR(30) | NOT NULL | over_time/point_in_time |
| measurement_method | VARCHAR(50) | NOT NULL | input/output/time_based |
| timing_description | TEXT | | |
| debit_account | VARCHAR(100) | NOT NULL | |
| credit_account | VARCHAR(100) | NOT NULL | |
| variable_consideration_method | VARCHAR(50) | | expected_value/most_likely |
| constraint_applicable | BOOLEAN | DEFAULT FALSE | |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_recognition_rules_model` (org_id, billing_model)

---

### 7.6 asc606_compliance

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id), NOT NULL | |
| step_1_contract_identified | BOOLEAN | DEFAULT FALSE | Contract with customer identified |
| step_1_notes | TEXT | | |
| step_2_obligations_identified | BOOLEAN | DEFAULT FALSE | Performance obligations identified |
| step_2_count | INTEGER | | Number of obligations |
| step_3_price_determined | BOOLEAN | DEFAULT FALSE | Transaction price determined |
| step_3_amount | NUMERIC(15,2) | | |
| step_4_price_allocated | BOOLEAN | DEFAULT FALSE | Price allocated to obligations |
| step_4_allocation_json | JSONB | | Allocation details |
| step_5_recognition_applied | BOOLEAN | DEFAULT FALSE | Revenue recognized |
| step_5_method | VARCHAR(50) | | |
| overall_status | VARCHAR(20) | DEFAULT 'incomplete' | incomplete/compliant/non_compliant/review |
| last_review_date | DATE | | |
| reviewed_by | UUID | FK → users(id) | |
| notes | TEXT | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_asc606_contract` (UNIQUE on contract_id), `idx_asc606_status` (overall_status)

---


## 8. Leakage

### 8.1 leakage_detections

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id) | |
| detection_date | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| leakage_type | VARCHAR(50) | NOT NULL | unbilled_hours/missed_milestone/rate_variance/scope_creep/escalation_missed |
| category_id | UUID | FK → leakage_categories(id) | |
| severity | VARCHAR(10) | NOT NULL | HIGH/MEDIUM/LOW |
| amount | NUMERIC(15,2) | NOT NULL | Estimated leakage amount |
| annualized_amount | NUMERIC(15,2) | | Projected annual impact |
| description | TEXT | NOT NULL | |
| root_cause | TEXT | | AI-identified root cause |
| recommendation | TEXT | | Recovery recommendation |
| status | VARCHAR(20) | DEFAULT 'open' | open/investigating/resolved/dismissed |
| resolution_id | UUID | FK → leakage_resolutions(id) | |
| scan_id | UUID | | Batch scan reference |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_leakage_detections_client` (client_id), `idx_leakage_detections_date` (detection_date), `idx_leakage_detections_status`, `idx_leakage_detections_severity`, `idx_leakage_detections_type`

---

### 8.2 leakage_rules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| rule_name | VARCHAR(100) | NOT NULL | |
| rule_type | VARCHAR(50) | NOT NULL | unbilled_hours/rate_check/milestone_check/escalation_check |
| description | TEXT | | |
| condition_json | JSONB | NOT NULL | Rule conditions |
| threshold_value | NUMERIC(15,2) | | Amount threshold |
| threshold_percentage | NUMERIC(5,2) | | Percentage threshold |
| severity_default | VARCHAR(10) | DEFAULT 'MEDIUM' | |
| is_active | BOOLEAN | DEFAULT TRUE | |
| scan_frequency | VARCHAR(20) | DEFAULT 'daily' | hourly/daily/weekly |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_leakage_rules_org` (org_id, is_active)

---

### 8.3 leakage_alerts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| detection_id | UUID | FK → leakage_detections(id), NOT NULL | |
| alert_type | VARCHAR(30) | NOT NULL | email/in_app/sms |
| recipient_id | UUID | FK → users(id), NOT NULL | |
| sent_at | TIMESTAMPTZ | | |
| read_at | TIMESTAMPTZ | | |
| acknowledged_at | TIMESTAMPTZ | | |
| escalation_level | INTEGER | DEFAULT 1 | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_leakage_alerts_detection` (detection_id), `idx_leakage_alerts_recipient` (recipient_id)

---

### 8.4 leakage_resolutions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| detection_id | UUID | FK → leakage_detections(id), NOT NULL | |
| resolution_type | VARCHAR(30) | NOT NULL | recovered/written_off/dismissed/in_progress |
| recovered_amount | NUMERIC(15,2) | DEFAULT 0 | |
| resolution_notes | TEXT | | |
| resolved_by | UUID | FK → users(id) | |
| resolved_at | TIMESTAMPTZ | | |
| invoice_id | UUID | FK → invoices(id) | Recovery invoice if applicable |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_leakage_resolutions_detection` (detection_id)

---

### 8.5 leakage_categories

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| code | VARCHAR(50) | NOT NULL | |
| description | TEXT | | |
| parent_id | UUID | FK → leakage_categories(id) | Hierarchical categories |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_leakage_categories_org` (org_id)

---

## 9. Profitability

### 9.1 cost_allocations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id) | |
| period_month | INTEGER | NOT NULL | |
| period_year | INTEGER | NOT NULL | |
| cost_type | VARCHAR(50) | NOT NULL | direct_labor/direct_material/travel/technology/other_direct |
| category | VARCHAR(100) | | Cost category |
| description | TEXT | | |
| amount | NUMERIC(15,2) | NOT NULL | |
| allocation_method | VARCHAR(30) | | direct/headcount/revenue_proportional |
| source | VARCHAR(50) | | erp/hrms/manual |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_cost_allocations_client_period` (client_id, period_year, period_month), `idx_cost_allocations_type`

---

### 9.2 overhead_allocations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| period_month | INTEGER | NOT NULL | |
| period_year | INTEGER | NOT NULL | |
| overhead_type | VARCHAR(50) | NOT NULL | rent/utilities/admin/management/infrastructure |
| amount | NUMERIC(15,2) | NOT NULL | |
| allocation_basis | VARCHAR(50) | NOT NULL | headcount/revenue/equal/custom |
| allocation_percentage | NUMERIC(5,2) | | % of total overhead |
| total_overhead_pool | NUMERIC(15,2) | | Total pool being distributed |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_overhead_client_period` (client_id, period_year, period_month)

---

### 9.3 margin_calculations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id) | |
| period_month | INTEGER | NOT NULL | |
| period_year | INTEGER | NOT NULL | |
| revenue | NUMERIC(15,2) | NOT NULL | |
| direct_costs | NUMERIC(15,2) | NOT NULL | |
| indirect_costs | NUMERIC(15,2) | NOT NULL | |
| overhead_allocated | NUMERIC(15,2) | NOT NULL | |
| total_costs | NUMERIC(15,2) | NOT NULL | |
| gross_margin | NUMERIC(15,2) | NOT NULL | Revenue - Direct Costs |
| gross_margin_percent | NUMERIC(5,2) | NOT NULL | |
| net_margin | NUMERIC(15,2) | NOT NULL | Revenue - Total Costs |
| net_margin_percent | NUMERIC(5,2) | NOT NULL | |
| margin_threshold | NUMERIC(5,2) | DEFAULT 12 | |
| is_below_threshold | BOOLEAN | | |
| trend_direction | VARCHAR(10) | | up/down/stable |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_margin_calc_client_period` (client_id, period_year, period_month), `idx_margin_calc_below_threshold` (is_below_threshold)

---

### 9.4 profitability_snapshots

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| snapshot_date | DATE | NOT NULL | |
| snapshot_type | VARCHAR(20) | NOT NULL | weekly/monthly/quarterly |
| total_clients | INTEGER | | |
| total_revenue | NUMERIC(15,2) | | |
| total_costs | NUMERIC(15,2) | | |
| avg_margin_percent | NUMERIC(5,2) | | |
| clients_above_threshold | INTEGER | | |
| clients_below_threshold | INTEGER | | |
| top_quartile_margin | NUMERIC(5,2) | | |
| bottom_quartile_margin | NUMERIC(5,2) | | |
| data_json | JSONB | | Full snapshot data |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_profitability_snapshots_date` (org_id, snapshot_date DESC)

---

### 9.5 benchmark_data

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| benchmark_type | VARCHAR(50) | NOT NULL | industry/billing_model/segment/internal |
| category | VARCHAR(100) | NOT NULL | Category being benchmarked |
| metric_name | VARCHAR(50) | NOT NULL | margin/dso/utilization/etc. |
| metric_value | NUMERIC(10,2) | NOT NULL | |
| percentile_25 | NUMERIC(10,2) | | |
| percentile_50 | NUMERIC(10,2) | | |
| percentile_75 | NUMERIC(10,2) | | |
| data_source | VARCHAR(100) | | |
| effective_date | DATE | NOT NULL | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_benchmark_type_category` (benchmark_type, category)

---

## 10. Collections

### 10.1 receivables

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| invoice_id | UUID | FK → invoices(id), NOT NULL | |
| original_amount | NUMERIC(15,2) | NOT NULL | |
| outstanding_amount | NUMERIC(15,2) | NOT NULL | |
| due_date | DATE | NOT NULL | |
| days_overdue | INTEGER | DEFAULT 0 | |
| aging_bucket | VARCHAR(20) | | current/30/60/90/90_plus |
| status | VARCHAR(20) | DEFAULT 'outstanding' | outstanding/partially_paid/paid/written_off |
| last_reminder_date | DATE | | |
| reminder_count | INTEGER | DEFAULT 0 | |
| escalation_level | INTEGER | DEFAULT 0 | |
| assigned_to | UUID | FK → users(id) | Collection assignee |
| notes | TEXT | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_receivables_client` (client_id), `idx_receivables_due_date` (due_date), `idx_receivables_status`, `idx_receivables_aging` (aging_bucket), `idx_receivables_overdue` (days_overdue)

---

### 10.2 payment_receipts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| invoice_id | UUID | FK → invoices(id) | Matched invoice |
| receipt_number | VARCHAR(50) | NOT NULL | |
| receipt_date | DATE | NOT NULL | |
| amount | NUMERIC(15,2) | NOT NULL | |
| payment_method | VARCHAR(30) | | bank_transfer/cheque/upi/card |
| bank_reference | VARCHAR(100) | | Bank transaction reference |
| bank_name | VARCHAR(100) | | |
| tds_deducted | NUMERIC(12,2) | DEFAULT 0 | |
| tds_certificate_number | VARCHAR(50) | | |
| status | VARCHAR(20) | DEFAULT 'received' | received/matched/unmatched/reversed |
| matched_at | TIMESTAMPTZ | | |
| matched_by | UUID | FK → users(id) | |
| notes | TEXT | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_payment_receipts_client` (client_id), `idx_payment_receipts_invoice` (invoice_id), `idx_payment_receipts_date` (receipt_date)

---

### 10.3 collection_schedules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| receivable_id | UUID | FK → receivables(id), NOT NULL | |
| scheduled_action | VARCHAR(50) | NOT NULL | reminder/call/email/escalate |
| scheduled_date | DATE | NOT NULL | |
| assigned_to | UUID | FK → users(id) | |
| status | VARCHAR(20) | DEFAULT 'pending' | pending/completed/skipped |
| completed_at | TIMESTAMPTZ | | |
| outcome | TEXT | | Action outcome |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_collection_schedules_date` (scheduled_date), `idx_collection_schedules_client` (client_id)

---

### 10.4 aging_buckets

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| snapshot_date | DATE | NOT NULL | |
| client_id | UUID | FK → clients(id) | NULL for org-level |
| bucket_current | NUMERIC(15,2) | DEFAULT 0 | 0-30 days |
| bucket_30 | NUMERIC(15,2) | DEFAULT 0 | 31-60 days |
| bucket_60 | NUMERIC(15,2) | DEFAULT 0 | 61-90 days |
| bucket_90 | NUMERIC(15,2) | DEFAULT 0 | 91-120 days |
| bucket_120_plus | NUMERIC(15,2) | DEFAULT 0 | 120+ days |
| total_outstanding | NUMERIC(15,2) | DEFAULT 0 | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_aging_buckets_date` (org_id, snapshot_date DESC), `idx_aging_buckets_client` (client_id)

---

### 10.5 dunning_rules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| rule_name | VARCHAR(100) | NOT NULL | |
| days_overdue_trigger | INTEGER | NOT NULL | Days after due date |
| action_type | VARCHAR(30) | NOT NULL | email/sms/call/escalate |
| template_id | UUID | FK → notification_templates(id) | |
| escalate_to_role | VARCHAR(50) | | Role to escalate to |
| is_active | BOOLEAN | DEFAULT TRUE | |
| priority | INTEGER | DEFAULT 0 | |
| max_reminders | INTEGER | DEFAULT 3 | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_dunning_rules_org` (org_id, is_active)

---

### 10.6 cash_forecasts

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| forecast_date | DATE | NOT NULL | Date being forecast |
| forecast_generated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| expected_inflow | NUMERIC(15,2) | NOT NULL | |
| confidence_level | NUMERIC(5,2) | | Prediction confidence |
| client_id | UUID | FK → clients(id) | NULL for org-level |
| basis | VARCHAR(50) | | historical/scheduled/predicted |
| actual_inflow | NUMERIC(15,2) | | Actual (filled after date passes) |
| variance | NUMERIC(15,2) | | Forecast vs actual |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_cash_forecasts_date` (org_id, forecast_date)

---


## 11. AI

### 11.1 ai_recommendations

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| client_id | UUID | FK → clients(id), NOT NULL | |
| contract_id | UUID | FK → contracts(id) | |
| recommendation_type | VARCHAR(50) | NOT NULL | reprice/restructure/exit/upsell/escalate |
| title | VARCHAR(255) | NOT NULL | |
| description | TEXT | NOT NULL | |
| reasoning | TEXT | | AI explanation |
| impact_amount | NUMERIC(15,2) | | Estimated financial impact |
| confidence_score | NUMERIC(5,4) | NOT NULL | 0.0000 to 1.0000 |
| priority | VARCHAR(10) | DEFAULT 'MEDIUM' | HIGH/MEDIUM/LOW |
| status | VARCHAR(20) | DEFAULT 'pending' | pending/accepted/rejected/implemented |
| accepted_by | UUID | FK → users(id) | |
| accepted_at | TIMESTAMPTZ | | |
| rejection_reason | TEXT | | |
| model_version_id | UUID | FK → model_versions(id) | |
| input_data_json | JSONB | | Input features used |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_ai_recs_client` (client_id), `idx_ai_recs_status` (status), `idx_ai_recs_type` (recommendation_type), `idx_ai_recs_priority` (priority)

---

### 11.2 ai_models

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id) | NULL for system models |
| name | VARCHAR(100) | NOT NULL | |
| model_type | VARCHAR(50) | NOT NULL | classification/regression/nlp/anomaly |
| purpose | VARCHAR(100) | NOT NULL | leakage_detection/margin_forecast/contract_parse |
| framework | VARCHAR(50) | | sklearn/pytorch/openai |
| current_version_id | UUID | FK → model_versions(id) | |
| is_active | BOOLEAN | DEFAULT TRUE | |
| accuracy_metric | VARCHAR(30) | | f1/rmse/accuracy |
| current_accuracy | NUMERIC(5,4) | | |
| last_trained_at | TIMESTAMPTZ | | |
| training_frequency | VARCHAR(20) | | daily/weekly/monthly/on_demand |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_ai_models_purpose` (purpose), `idx_ai_models_active` (is_active)

---

### 11.3 ai_predictions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| model_id | UUID | FK → ai_models(id), NOT NULL | |
| model_version_id | UUID | FK → model_versions(id) | |
| prediction_type | VARCHAR(50) | NOT NULL | margin_forecast/payment_prediction/churn_risk |
| subject_type | VARCHAR(50) | | client/contract/invoice |
| subject_id | UUID | | |
| input_features | JSONB | NOT NULL | |
| prediction_value | NUMERIC(15,4) | | Numeric prediction |
| prediction_label | VARCHAR(100) | | Classification label |
| prediction_json | JSONB | | Complex prediction output |
| confidence | NUMERIC(5,4) | NOT NULL | |
| actual_value | NUMERIC(15,4) | | Filled when actual known |
| actual_label | VARCHAR(100) | | |
| is_correct | BOOLEAN | | Prediction accuracy |
| prediction_date | DATE | NOT NULL | |
| target_date | DATE | | Date prediction is for |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_ai_predictions_model` (model_id), `idx_ai_predictions_subject` (subject_type, subject_id), `idx_ai_predictions_date` (prediction_date)

---

### 11.4 prompt_logs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| user_id | UUID | FK → users(id) | |
| model_name | VARCHAR(50) | NOT NULL | gpt-4/gpt-3.5/custom |
| prompt_text | TEXT | NOT NULL | Input prompt |
| response_text | TEXT | | Model response |
| purpose | VARCHAR(100) | | contract_extraction/recommendation/analysis |
| tokens_input | INTEGER | | |
| tokens_output | INTEGER | | |
| cost_usd | NUMERIC(8,4) | | API cost |
| latency_ms | INTEGER | | Response time |
| status | VARCHAR(20) | DEFAULT 'success' | success/error/timeout |
| error_message | TEXT | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_prompt_logs_org_date` (org_id, created_at DESC), `idx_prompt_logs_purpose` (purpose)

---

### 11.5 model_versions

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id) | |
| model_id | UUID | FK → ai_models(id), NOT NULL | |
| version_number | VARCHAR(20) | NOT NULL | Semver (1.0.0) |
| s3_artifact_url | TEXT | | Model artifact location |
| training_data_summary | JSONB | | Training data stats |
| hyperparameters | JSONB | | Model hyperparameters |
| metrics | JSONB | | Evaluation metrics |
| accuracy | NUMERIC(5,4) | | |
| trained_at | TIMESTAMPTZ | | |
| promoted_at | TIMESTAMPTZ | | When made current |
| status | VARCHAR(20) | DEFAULT 'training' | training/validated/promoted/deprecated |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_model_versions_model` (model_id, version_number)

---


## 12. Integrations

### 12.1 integration_configs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| integration_type | VARCHAR(50) | NOT NULL | tally/sap/salesforce/hrms/banking |
| name | VARCHAR(100) | NOT NULL | |
| description | TEXT | | |
| config_json | JSONB | NOT NULL | Connection configuration (encrypted) |
| auth_type | VARCHAR(30) | | api_key/oauth2/basic/certificate |
| credentials_secret_arn | TEXT | | AWS Secrets Manager ARN |
| base_url | TEXT | | Endpoint URL |
| sync_direction | VARCHAR(20) | DEFAULT 'bidirectional' | inbound/outbound/bidirectional |
| sync_frequency | VARCHAR(20) | DEFAULT 'hourly' | realtime/hourly/daily/manual |
| is_active | BOOLEAN | DEFAULT TRUE | |
| last_sync_at | TIMESTAMPTZ | | |
| last_sync_status | VARCHAR(20) | | success/error/partial |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_integration_configs_org` (org_id), `idx_integration_configs_type` (integration_type)

---

### 12.2 sync_logs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| integration_id | UUID | FK → integration_configs(id), NOT NULL | |
| sync_type | VARCHAR(30) | NOT NULL | full/incremental/manual |
| direction | VARCHAR(20) | NOT NULL | inbound/outbound |
| started_at | TIMESTAMPTZ | NOT NULL | |
| completed_at | TIMESTAMPTZ | | |
| status | VARCHAR(20) | NOT NULL | running/success/error/partial |
| records_processed | INTEGER | DEFAULT 0 | |
| records_created | INTEGER | DEFAULT 0 | |
| records_updated | INTEGER | DEFAULT 0 | |
| records_failed | INTEGER | DEFAULT 0 | |
| error_details | JSONB | | Error information |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_sync_logs_integration` (integration_id, started_at DESC), `idx_sync_logs_status` (status)

---

### 12.3 webhook_configs

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| url | TEXT | NOT NULL | Webhook endpoint URL |
| secret | VARCHAR(255) | | Signing secret |
| events | JSONB | NOT NULL | List of events to send |
| headers | JSONB | DEFAULT '{}' | Custom headers |
| is_active | BOOLEAN | DEFAULT TRUE | |
| retry_count | INTEGER | DEFAULT 3 | |
| timeout_seconds | INTEGER | DEFAULT 30 | |
| last_triggered_at | TIMESTAMPTZ | | |
| last_status_code | INTEGER | | |
| failure_count | INTEGER | DEFAULT 0 | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_webhook_configs_org` (org_id, is_active)

---

### 12.4 api_keys

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| user_id | UUID | FK → users(id), NOT NULL | Key owner |
| name | VARCHAR(100) | NOT NULL | Key description |
| key_prefix | VARCHAR(10) | NOT NULL | First 8 chars (for display) |
| key_hash | VARCHAR(255) | NOT NULL | SHA-256 hash of full key |
| scopes | JSONB | DEFAULT '["read"]' | Allowed scopes |
| rate_limit | INTEGER | DEFAULT 1000 | Requests per minute |
| expires_at | TIMESTAMPTZ | | |
| last_used_at | TIMESTAMPTZ | | |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_api_keys_hash` (key_hash), `idx_api_keys_org` (org_id)

---

## 13. Notifications

### 13.1 notifications

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| user_id | UUID | FK → users(id), NOT NULL | Recipient |
| type | VARCHAR(50) | NOT NULL | alert/info/warning/action_required |
| channel | VARCHAR(20) | NOT NULL | in_app/email/sms |
| title | VARCHAR(255) | NOT NULL | |
| body | TEXT | NOT NULL | |
| action_url | TEXT | | Link to relevant page |
| source_type | VARCHAR(50) | | leakage/invoice/margin/collection |
| source_id | UUID | | |
| is_read | BOOLEAN | DEFAULT FALSE | |
| read_at | TIMESTAMPTZ | | |
| sent_at | TIMESTAMPTZ | | |
| delivery_status | VARCHAR(20) | DEFAULT 'pending' | pending/sent/delivered/failed |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_notifications_user` (user_id, is_read, created_at DESC), `idx_notifications_type` (type), `idx_notifications_source` (source_type, source_id)

---

### 13.2 notification_templates

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id) | NULL for system templates |
| name | VARCHAR(100) | NOT NULL | |
| slug | VARCHAR(100) | NOT NULL | Template identifier |
| channel | VARCHAR(20) | NOT NULL | email/sms/in_app |
| subject | VARCHAR(255) | | Email subject line |
| body_template | TEXT | NOT NULL | Template with variables |
| variables | JSONB | | Available variables |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_notification_templates_slug` (slug, channel)

---

### 13.3 notification_preferences

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| user_id | UUID | FK → users(id), NOT NULL | |
| event_type | VARCHAR(50) | NOT NULL | leakage_alert/invoice_approved/margin_breach/etc. |
| channel_email | BOOLEAN | DEFAULT TRUE | |
| channel_sms | BOOLEAN | DEFAULT FALSE | |
| channel_in_app | BOOLEAN | DEFAULT TRUE | |
| frequency | VARCHAR(20) | DEFAULT 'immediate' | immediate/hourly_digest/daily_digest |
| is_enabled | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_notification_prefs_user` (user_id), `idx_notification_prefs_event` (event_type)

---

### 13.4 alert_rules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| description | TEXT | | |
| metric | VARCHAR(100) | NOT NULL | Metric to monitor |
| condition | VARCHAR(20) | NOT NULL | gt/lt/eq/gte/lte/change |
| threshold_value | NUMERIC(15,2) | NOT NULL | |
| severity | VARCHAR(10) | DEFAULT 'MEDIUM' | HIGH/MEDIUM/LOW |
| recipients | JSONB | NOT NULL | User IDs or role names |
| channels | JSONB | DEFAULT '["in_app","email"]' | |
| cooldown_minutes | INTEGER | DEFAULT 60 | Min time between alerts |
| is_active | BOOLEAN | DEFAULT TRUE | |
| last_triggered_at | TIMESTAMPTZ | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_alert_rules_org` (org_id, is_active), `idx_alert_rules_metric` (metric)

---


## 14. Reports

### 14.1 report_templates

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id) | NULL for system templates |
| name | VARCHAR(100) | NOT NULL | |
| description | TEXT | | |
| report_type | VARCHAR(50) | NOT NULL | revenue/profitability/leakage/collections/compliance |
| query_config | JSONB | NOT NULL | Data query configuration |
| layout_config | JSONB | | Visual layout settings |
| parameters | JSONB | | User-configurable parameters |
| default_format | VARCHAR(10) | DEFAULT 'pdf' | pdf/excel/csv |
| is_system | BOOLEAN | DEFAULT FALSE | |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_report_templates_org` (org_id), `idx_report_templates_type` (report_type)

---

### 14.2 report_schedules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| template_id | UUID | FK → report_templates(id), NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| frequency | VARCHAR(20) | NOT NULL | daily/weekly/monthly/quarterly |
| day_of_week | INTEGER | | 0-6 for weekly |
| day_of_month | INTEGER | | 1-31 for monthly |
| time_of_day | TIME | DEFAULT '08:00:00' | |
| timezone | VARCHAR(50) | DEFAULT 'Asia/Kolkata' | |
| recipients | JSONB | NOT NULL | Email addresses |
| parameters | JSONB | | Report parameters |
| format | VARCHAR(10) | DEFAULT 'pdf' | |
| is_active | BOOLEAN | DEFAULT TRUE | |
| last_run_at | TIMESTAMPTZ | | |
| next_run_at | TIMESTAMPTZ | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_report_schedules_next_run` (next_run_at), `idx_report_schedules_org` (org_id)

---

### 14.3 report_exports

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| template_id | UUID | FK → report_templates(id) | |
| schedule_id | UUID | FK → report_schedules(id) | NULL for ad-hoc |
| report_name | VARCHAR(255) | NOT NULL | |
| format | VARCHAR(10) | NOT NULL | pdf/excel/csv |
| parameters_used | JSONB | | Parameters for this run |
| file_url | TEXT | | S3 URL of generated file |
| file_size | BIGINT | | Size in bytes |
| status | VARCHAR(20) | DEFAULT 'generating' | generating/ready/failed/expired |
| generated_at | TIMESTAMPTZ | | |
| expires_at | TIMESTAMPTZ | | Auto-delete time |
| download_count | INTEGER | DEFAULT 0 | |
| error_message | TEXT | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_report_exports_org` (org_id, created_at DESC), `idx_report_exports_status` (status)

---

### 14.4 dashboards

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| description | TEXT | | |
| slug | VARCHAR(100) | NOT NULL | |
| layout_config | JSONB | NOT NULL | Grid layout |
| is_default | BOOLEAN | DEFAULT FALSE | |
| visibility | VARCHAR(20) | DEFAULT 'org' | private/org/public |
| owner_id | UUID | FK → users(id) | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_dashboards_org` (org_id), `idx_dashboards_slug` (org_id, slug)

---

### 14.5 dashboard_widgets

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| dashboard_id | UUID | FK → dashboards(id), NOT NULL | |
| widget_type | VARCHAR(50) | NOT NULL | chart/table/metric/list |
| title | VARCHAR(100) | NOT NULL | |
| data_source | VARCHAR(100) | NOT NULL | API endpoint or query |
| config_json | JSONB | NOT NULL | Widget configuration |
| position_x | INTEGER | NOT NULL | Grid X position |
| position_y | INTEGER | NOT NULL | Grid Y position |
| width | INTEGER | NOT NULL | Grid width |
| height | INTEGER | NOT NULL | Grid height |
| refresh_interval | INTEGER | DEFAULT 300 | Seconds |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_dashboard_widgets_dashboard` (dashboard_id)

---

## 15. Settings

### 15.1 system_settings

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| key | VARCHAR(100) | UNIQUE, NOT NULL | Setting key |
| value | TEXT | NOT NULL | Setting value |
| value_type | VARCHAR(20) | DEFAULT 'string' | string/integer/boolean/json |
| category | VARCHAR(50) | | Setting category |
| description | TEXT | | |
| is_sensitive | BOOLEAN | DEFAULT FALSE | Mask in UI |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_system_settings_key` (UNIQUE), `idx_system_settings_category` (category)

---

### 15.2 tenant_settings

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| key | VARCHAR(100) | NOT NULL | Setting key |
| value | TEXT | NOT NULL | |
| value_type | VARCHAR(20) | DEFAULT 'string' | |
| category | VARCHAR(50) | | |
| description | TEXT | | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_tenant_settings_org_key` (UNIQUE on org_id, key)

---

### 15.3 feature_flags

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id) | NULL for global |
| flag_key | VARCHAR(100) | NOT NULL | |
| is_enabled | BOOLEAN | DEFAULT FALSE | |
| description | TEXT | | |
| rollout_percentage | INTEGER | DEFAULT 100 | 0-100 for gradual rollout |
| conditions_json | JSONB | | Targeting conditions |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_feature_flags_key` (flag_key, org_id)

---

### 15.4 currencies

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| code | VARCHAR(3) | UNIQUE, NOT NULL | ISO 4217 code |
| name | VARCHAR(100) | NOT NULL | |
| symbol | VARCHAR(5) | NOT NULL | |
| decimal_places | INTEGER | DEFAULT 2 | |
| exchange_rate_to_inr | NUMERIC(12,6) | | Current rate |
| rate_updated_at | TIMESTAMPTZ | | |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_currencies_code` (UNIQUE)

---

### 15.5 tax_rules

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| org_id | UUID | FK → organizations(id), NOT NULL | |
| name | VARCHAR(100) | NOT NULL | |
| tax_type | VARCHAR(30) | NOT NULL | gst/tds/withholding |
| rate | NUMERIC(5,2) | NOT NULL | Tax rate percentage |
| conditions | JSONB | | Applicability conditions |
| effective_from | DATE | NOT NULL | |
| effective_to | DATE | | |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | FK → users(id) | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_tax_rules_org_type` (org_id, tax_type)

---

### 15.6 gst_codes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| code | VARCHAR(10) | NOT NULL | GST state code |
| state_name | VARCHAR(100) | NOT NULL | |
| state_code_numeric | VARCHAR(5) | | |
| is_union_territory | BOOLEAN | DEFAULT FALSE | |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_gst_codes_code` (UNIQUE on code)

---

### 15.7 hsn_codes

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PK, DEFAULT gen_random_uuid() | |
| code | VARCHAR(10) | NOT NULL | HSN/SAC code |
| description | TEXT | NOT NULL | |
| gst_rate | NUMERIC(5,2) | NOT NULL | Applicable GST rate |
| code_type | VARCHAR(5) | NOT NULL | hsn/sac |
| chapter | VARCHAR(10) | | Chapter heading |
| is_active | BOOLEAN | DEFAULT TRUE | |
| created_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| updated_at | TIMESTAMPTZ | NOT NULL DEFAULT NOW() | |
| created_by | UUID | | |
| is_deleted | BOOLEAN | NOT NULL DEFAULT FALSE | |

**Indexes:** `idx_hsn_codes_code` (UNIQUE on code), `idx_hsn_codes_type` (code_type)

---

## Table Count Summary

| Domain | Tables | Count |
|--------|--------|-------|
| Organizations & Auth | organizations, users, roles, permissions, user_roles, audit_logs, sessions | 7 |
| Contracts | contracts, contract_versions, contract_terms, performance_obligations, contract_documents, contract_amendments | 6 |
| Clients | clients, client_contacts, client_addresses, client_preferences, client_segments | 5 |
| Billing | billing_models, billing_rules, billing_periods, billing_schedules, rate_cards, rate_card_items, escalation_rules | 7 |
| Billables | timesheets, timesheet_entries, milestones, milestone_deliverables, call_records, project_deliverables, expenses | 7 |
| Invoices | invoices, invoice_line_items, invoice_templates, credit_notes, debit_notes, invoice_approvals, invoice_dispatch | 7 |
| Revenue Recognition | revenue_schedules, revenue_entries, deferred_revenue, recognized_revenue, recognition_rules, asc606_compliance | 6 |
| Leakage | leakage_detections, leakage_rules, leakage_alerts, leakage_resolutions, leakage_categories | 5 |
| Profitability | cost_allocations, overhead_allocations, margin_calculations, profitability_snapshots, benchmark_data | 5 |
| Collections | receivables, payment_receipts, collection_schedules, aging_buckets, dunning_rules, cash_forecasts | 6 |
| AI | ai_recommendations, ai_models, ai_predictions, prompt_logs, model_versions | 5 |
| Integrations | integration_configs, sync_logs, webhook_configs, api_keys | 4 |
| Notifications | notifications, notification_templates, notification_preferences, alert_rules | 4 |
| Reports | report_templates, report_schedules, report_exports, dashboards, dashboard_widgets | 5 |
| Settings | system_settings, tenant_settings, feature_flags, currencies, tax_rules, gst_codes, hsn_codes | 7 |
| **TOTAL** | | **87** |

---

*Document End — RevRecog AI + ClientMargin360 Database Schema v2.0.0*
