# API Documentation
## RevRecog AI + ClientMargin360
### Finmark.ai | Denave India Pvt. Ltd.

| Field | Value |
|-------|-------|
| **Document Version** | 2.0.0 |
| **Date** | July 2026 |
| **Base URL** | `https://api.finmark.ai/v1` |
| **Authentication** | JWT Bearer Token |
| **Content-Type** | application/json |
| **Total Endpoints** | 156 |

---

## Table of Contents

1. [Auth APIs](#1-auth-apis)
2. [Contract APIs](#2-contract-apis)
3. [Client APIs](#3-client-apis)
4. [Billing APIs](#4-billing-apis)
5. [Billable APIs](#5-billable-apis)
6. [Invoice APIs](#6-invoice-apis)
7. [Revenue APIs](#7-revenue-apis)
8. [Leakage APIs](#8-leakage-apis)
9. [Profitability APIs](#9-profitability-apis)
10. [Collection APIs](#10-collection-apis)
11. [AI APIs](#11-ai-apis)
12. [Dashboard APIs](#12-dashboard-apis)
13. [Report APIs](#13-report-apis)
14. [Settings APIs](#14-settings-apis)
15. [Integration APIs](#15-integration-apis)

---

## Common Response Format

### Success Response
```json
{
  "success": true,
  "data": {},
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-07-18T17:14:33Z"
  }
}
```

### Paginated Response
```json
{
  "success": true,
  "data": [],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_items": 150,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-07-18T17:14:33Z"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {"field": "email", "message": "Invalid email format"}
    ]
  },
  "meta": {
    "request_id": "req_abc123",
    "timestamp": "2026-07-18T17:14:33Z"
  }
}
```

### Common Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content (successful delete) |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 409 | Conflict (duplicate) |
| 422 | Unprocessable Entity |
| 429 | Too Many Requests (rate limited) |
| 500 | Internal Server Error |

---

## 1. Auth APIs

### 1.1 POST /api/auth/login

**Description:** Authenticate user and receive tokens.

**Auth Required:** No

**Request Body:**
```json
{
  "email": "priya.verma@denave.com",
  "password": "SecureP@ss123",
  "org_slug": "denave"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIs...",
    "refresh_token": "rt_a1b2c3d4e5f6...",
    "token_type": "Bearer",
    "expires_in": 3600,
    "user": {
      "id": "usr_a1b2c3d4",
      "email": "priya.verma@denave.com",
      "name": "Priya Verma",
      "roles": ["finance_manager"],
      "org_id": "org_x1y2z3",
      "org_name": "Denave India Pvt. Ltd."
    }
  }
}
```

**Error Responses:** 401 (invalid credentials), 403 (account locked), 429 (too many attempts)

---

### 1.2 POST /api/auth/register

**Description:** Register new user (admin-initiated or self-service with invite).

**Auth Required:** Yes (org_admin) or Invite Token

**Request Body:**
```json
{
  "email": "ankit.patel@denave.com",
  "password": "SecureP@ss456",
  "first_name": "Ankit",
  "last_name": "Patel",
  "phone": "+91-9876543210",
  "role": "accountant",
  "invite_token": "inv_xyz789"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "user_id": "usr_new123",
    "email": "ankit.patel@denave.com",
    "status": "pending_verification",
    "verification_email_sent": true
  }
}
```

---

### 1.3 POST /api/auth/refresh

**Description:** Refresh access token using refresh token.

**Auth Required:** No (uses refresh token)

**Request Body:**
```json
{
  "refresh_token": "rt_a1b2c3d4e5f6..."
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIs...",
    "expires_in": 3600
  }
}
```

---

### 1.4 POST /api/auth/logout

**Description:** Invalidate current session and tokens.

**Auth Required:** Yes

**Request Body:**
```json
{
  "refresh_token": "rt_a1b2c3d4e5f6..."
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Successfully logged out"
  }
}
```

---

### 1.5 POST /api/auth/forgot-password

**Description:** Initiate password reset flow.

**Auth Required:** No

**Request Body:**
```json
{
  "email": "priya.verma@denave.com"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Password reset email sent if account exists"
  }
}
```

---

### 1.6 POST /api/auth/reset-password

**Description:** Reset password using token from email.

**Auth Required:** No (uses reset token)

**Request Body:**
```json
{
  "token": "rst_abc123xyz",
  "new_password": "NewSecureP@ss789"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "message": "Password reset successfully"
  }
}
```

---


## 2. Contract APIs

### 2.1 GET /api/contracts

**Description:** List all contracts with filtering and pagination.

**Auth Required:** Yes | **Permissions:** contracts.read

**Query Parameters:**

| Param | Type | Description |
|-------|------|-------------|
| page | integer | Page number (default: 1) |
| per_page | integer | Items per page (default: 20, max: 100) |
| status | string | Filter: draft/active/expired/terminated |
| billing_model | string | Filter: tm/fixed_milestone/retainer/performance/hybrid |
| client_id | uuid | Filter by client |
| search | string | Search in title, contract_number |
| sort_by | string | Sort field (default: created_at) |
| sort_order | string | asc/desc (default: desc) |

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "ctr_abc123",
      "contract_number": "DNV-2026-1001",
      "title": "Lead Generation Services - Reliance Jio",
      "client_id": "cli_xyz789",
      "client_name": "Reliance Jio Infocomm",
      "billing_model": "T&M",
      "status": "active",
      "total_value": 24500000,
      "currency": "INR",
      "start_date": "2026-01-01",
      "end_date": "2027-12-31",
      "ai_confidence_score": 0.9650,
      "created_at": "2026-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_items": 45,
    "total_pages": 3
  }
}
```

---

### 2.2 POST /api/contracts

**Description:** Create a new contract.

**Auth Required:** Yes | **Permissions:** contracts.create

**Request Body:**
```json
{
  "client_id": "cli_xyz789",
  "title": "Digital Marketing Services - HDFC Bank",
  "billing_model": "monthly_retainer",
  "total_value": 18000000,
  "currency": "INR",
  "start_date": "2026-08-01",
  "end_date": "2028-07-31",
  "payment_terms_days": 30,
  "auto_renewal": true,
  "notice_period_days": 90,
  "description": "Comprehensive digital marketing services including SEO, SEM, and social media management"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "ctr_new456",
    "contract_number": "DNV-2026-1046",
    "status": "draft",
    "message": "Contract created successfully"
  }
}
```

---

### 2.3 GET /api/contracts/{id}

**Description:** Get contract details.

**Auth Required:** Yes | **Permissions:** contracts.read

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "ctr_abc123",
    "contract_number": "DNV-2026-1001",
    "title": "Lead Generation Services - Reliance Jio",
    "client": {
      "id": "cli_xyz789",
      "name": "Reliance Jio Infocomm",
      "industry_sector": "Telecom"
    },
    "billing_model": "T&M",
    "status": "active",
    "total_value": 24500000,
    "currency": "INR",
    "start_date": "2026-01-01",
    "end_date": "2027-12-31",
    "payment_terms_days": 30,
    "performance_obligations": [
      {
        "id": "po_001",
        "description": "Lead Generation",
        "allocated_price": 15000000,
        "satisfaction_type": "over_time",
        "completion_percentage": 45.5
      }
    ],
    "ai_confidence_score": 0.9650,
    "ai_flags": ["✅ No critical flags identified"],
    "documents_count": 3,
    "amendments_count": 1,
    "created_at": "2026-01-15T10:30:00Z"
  }
}
```

---

### 2.4 PUT /api/contracts/{id}

**Description:** Update contract details.

**Auth Required:** Yes | **Permissions:** contracts.update

**Request Body:**
```json
{
  "title": "Lead Generation Services - Reliance Jio (Expanded)",
  "total_value": 28000000,
  "end_date": "2028-06-30"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "ctr_abc123",
    "message": "Contract updated. Version 2 created.",
    "version": 2
  }
}
```

---

### 2.5 DELETE /api/contracts/{id}

**Description:** Soft-delete a contract.

**Auth Required:** Yes | **Permissions:** contracts.delete

**Response (204):** No content

---

### 2.6 POST /api/contracts/upload

**Description:** Upload contract document for AI processing.

**Auth Required:** Yes | **Permissions:** contracts.create

**Request:** `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| file | File | PDF/DOCX/Image (max 50MB) |
| client_id | string | Client UUID |
| document_type | string | original/amendment/addendum |

**Response (202):**
```json
{
  "success": true,
  "data": {
    "document_id": "doc_abc123",
    "status": "processing",
    "estimated_time_seconds": 120,
    "tracking_url": "/api/contracts/upload/doc_abc123/status"
  }
}
```

---

### 2.7 POST /api/contracts/{id}/parse

**Description:** Trigger AI parsing of uploaded contract document.

**Auth Required:** Yes | **Permissions:** contracts.create

**Response (202):**
```json
{
  "success": true,
  "data": {
    "job_id": "job_parse_123",
    "status": "processing",
    "message": "AI parsing initiated"
  }
}
```

---

### 2.8 GET /api/contracts/{id}/extract-terms

**Description:** Get AI-extracted terms from contract.

**Auth Required:** Yes | **Permissions:** contracts.read

**Response (200):**
```json
{
  "success": true,
  "data": {
    "contract_id": "ctr_abc123",
    "extraction_timestamp": "2026-07-18T10:30:00Z",
    "confidence_score": 0.9650,
    "extracted_terms": {
      "billing_model": "T&M",
      "total_value": 24500000,
      "payment_terms": "Net 30 days",
      "escalation_clause": "10% annual increment",
      "performance_metrics": ["Leads generated", "Conversion rate"],
      "sla_terms": "95% quality score minimum"
    },
    "ai_flags": ["🔍 High-value contract - requires senior review"]
  }
}
```

---

### 2.9 POST /api/contracts/{id}/classify

**Description:** Auto-classify contract billing model and ASC 606 mapping.

**Auth Required:** Yes | **Permissions:** contracts.update

**Response (200):**
```json
{
  "success": true,
  "data": {
    "contract_id": "ctr_abc123",
    "classification": {
      "billing_model": "T&M",
      "recognition_pattern": "Over Time",
      "measurement_method": "Input Method (Hours/Effort)",
      "timing": "As services are rendered",
      "variable_consideration": "Constrained estimate of hours"
    },
    "performance_obligations": [
      {
        "id": "PO-1",
        "description": "Lead Generation",
        "standalone_selling_price": 15000000,
        "satisfaction_criteria": "Over time"
      }
    ]
  }
}
```

---

### 2.10 GET /api/contracts/{id}/versions

**Description:** Get all versions of a contract.

**Auth Required:** Yes | **Permissions:** contracts.read

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "version_number": 2,
      "changes_summary": "Extended end date, increased value",
      "effective_date": "2026-07-01",
      "created_by": "Priya Verma",
      "created_at": "2026-07-01T09:00:00Z"
    },
    {
      "version_number": 1,
      "changes_summary": "Original contract",
      "effective_date": "2026-01-01",
      "created_by": "System",
      "created_at": "2026-01-15T10:30:00Z"
    }
  ]
}
```

---

### 2.11 POST /api/contracts/{id}/amendments

**Description:** Create a contract amendment.

**Auth Required:** Yes | **Permissions:** contracts.update

**Request Body:**
```json
{
  "title": "Scope Extension - Social Media",
  "amendment_type": "scope_change",
  "effective_date": "2026-08-01",
  "description": "Adding social media management services",
  "new_value": 28000000
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "amendment_id": "amd_456",
    "amendment_number": 2,
    "status": "pending",
    "impact_analysis": {
      "revenue_impact": 4000000,
      "margin_impact_percent": 2.1
    }
  }
}
```

---

### 2.12 GET /api/contracts/{id}/compliance-check

**Description:** Run ASC 606 compliance validation.

**Auth Required:** Yes | **Permissions:** contracts.read

**Response (200):**
```json
{
  "success": true,
  "data": {
    "contract_id": "ctr_abc123",
    "overall_status": "compliant",
    "steps": {
      "step_1_contract_identified": true,
      "step_2_obligations_identified": true,
      "step_3_price_determined": true,
      "step_4_price_allocated": true,
      "step_5_recognition_applied": true
    },
    "issues": [],
    "last_review_date": "2026-07-15"
  }
}
```

---


## 3. Client APIs

### 3.1 GET /api/clients

**Description:** List all clients. **Auth Required:** Yes | **Permissions:** clients.read | **Pagination:** Yes

**Query Parameters:** page, per_page, status, industry_sector, segment_id, search, sort_by, sort_order

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "cli_xyz789",
      "name": "Reliance Jio Infocomm",
      "code": "RJI-001",
      "industry_sector": "Telecom",
      "status": "active",
      "health_score": 82.5,
      "active_contracts": 3,
      "lifetime_value": 85000000
    }
  ],
  "pagination": {"page": 1, "per_page": 20, "total_items": 18}
}
```

---

### 3.2 POST /api/clients

**Description:** Create a new client. **Auth Required:** Yes | **Permissions:** clients.create

**Request Body:**
```json
{
  "name": "HDFC Bank Ltd",
  "code": "HDFC-001",
  "industry_sector": "BFSI",
  "segment_id": "seg_enterprise",
  "gstin": "27AAACH0166Q1ZV",
  "pan": "AAACH0166Q",
  "payment_terms_days": 45,
  "credit_limit": 50000000
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {"id": "cli_new456", "code": "HDFC-001", "message": "Client created"}
}
```

---

### 3.3 GET /api/clients/{id}

**Description:** Get client details. **Auth Required:** Yes | **Permissions:** clients.read

**Response (200):** Full client object with contacts, addresses, active contracts summary.

---

### 3.4 PUT /api/clients/{id}

**Description:** Update client details. **Auth Required:** Yes | **Permissions:** clients.update

---

### 3.5 DELETE /api/clients/{id}

**Description:** Soft-delete client. **Auth Required:** Yes | **Permissions:** clients.delete

**Response (204):** No content

---

### 3.6 GET /api/clients/{id}/segments

**Description:** Get client segmentation details. **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": {
    "client_id": "cli_xyz789",
    "segment": {"id": "seg_001", "name": "Enterprise", "criteria": {"revenue_min": 100000000}},
    "peer_comparison": {"avg_margin": 18.5, "avg_dso": 42, "client_count": 5}
  }
}
```

---

### 3.7 GET /api/clients/{id}/contacts

**Description:** List client contacts. **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "ctc_001",
      "first_name": "Rajesh",
      "last_name": "Kumar",
      "email": "rajesh.kumar@reliancejio.com",
      "designation": "Finance Controller",
      "is_primary": true,
      "is_billing_contact": true
    }
  ]
}
```

---

### 3.8 POST /api/clients/{id}/contacts

**Description:** Add client contact. **Auth Required:** Yes | **Permissions:** clients.update

---

### 3.9 GET /api/clients/{id}/profitability-summary

**Description:** Get client profitability overview. **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": {
    "client_id": "cli_xyz789",
    "client_name": "Reliance Jio Infocomm",
    "current_month": {
      "revenue": 4500000,
      "direct_costs": 2800000,
      "overhead": 450000,
      "net_margin_percent": 27.8
    },
    "trailing_6_months": {
      "avg_margin": 25.2,
      "trend": "stable",
      "total_revenue": 26500000
    },
    "ranking": 3,
    "total_clients": 18
  }
}
```

---

### 3.10 GET /api/clients/{id}/health-score

**Description:** Get composite client health score. **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": {
    "client_id": "cli_xyz789",
    "overall_score": 82.5,
    "components": {
      "margin_health": 85,
      "payment_behavior": 75,
      "growth_trajectory": 80,
      "engagement_depth": 90,
      "risk_factors": 82
    },
    "status": "healthy",
    "recommendations": ["Consider upsell opportunity in Q4"]
  }
}
```

---

## 4. Billing APIs

### 4.1 GET /api/billing/billing-models

**Description:** List available billing models. **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "bm_001",
      "name": "Time & Materials",
      "code": "tm",
      "recognition_pattern": "over_time",
      "measurement_method": "input",
      "is_active": true
    }
  ]
}
```

---

### 4.2 GET /api/billing/rate-cards

**Description:** List rate cards. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** contract_id, client_id, status

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "rc_001",
      "contract_id": "ctr_abc123",
      "name": "Standard T&M Rates FY2026",
      "effective_from": "2026-04-01",
      "status": "active",
      "items": [
        {"resource_level": "senior_consultant", "rate": 4500, "unit": "hour"},
        {"resource_level": "consultant", "rate": 2500, "unit": "hour"},
        {"resource_level": "analyst", "rate": 1500, "unit": "hour"},
        {"resource_level": "field_agent", "rate": 600, "unit": "hour"}
      ]
    }
  ]
}
```

---

### 4.3 POST /api/billing/rate-cards

**Description:** Create rate card. **Auth Required:** Yes | **Permissions:** billing.create

**Request Body:**
```json
{
  "contract_id": "ctr_abc123",
  "name": "FY2027 Revised Rates",
  "effective_from": "2027-04-01",
  "items": [
    {"resource_level": "senior_consultant", "rate": 5000, "unit": "hour"},
    {"resource_level": "consultant", "rate": 2800, "unit": "hour"}
  ]
}
```

**Response (201):** Created rate card with ID.

---

### 4.4 GET /api/billing/schedules

**Description:** List billing schedules. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** contract_id, client_id, status, from_date, to_date

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "bs_001",
      "contract_id": "ctr_abc123",
      "client_name": "Reliance Jio",
      "schedule_date": "2026-08-01",
      "amount": 4500000,
      "status": "scheduled",
      "description": "Monthly retainer - August 2026"
    }
  ]
}
```

---

### 4.5 GET /api/billing/periods

**Description:** List billing periods. **Auth Required:** Yes

**Query Parameters:** contract_id, status (open/closed/invoiced)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "bp_001",
      "contract_id": "ctr_abc123",
      "period_start": "2026-07-01",
      "period_end": "2026-07-31",
      "status": "open",
      "billable_amount": 4200000,
      "invoiced_amount": 0
    }
  ]
}
```

---

### 4.6 POST /api/billing/periods/{id}/close

**Description:** Close a billing period. **Auth Required:** Yes | **Permissions:** billing.update

**Response (200):**
```json
{
  "success": true,
  "data": {"period_id": "bp_001", "status": "closed", "billable_amount": 4200000}
}
```

---

### 4.7 GET /api/billing/rules

**Description:** List billing rules for a contract. **Auth Required:** Yes

**Query Parameters:** contract_id (required)

---

### 4.8 POST /api/billing/rules

**Description:** Create billing rule. **Auth Required:** Yes | **Permissions:** billing.create

**Request Body:**
```json
{
  "contract_id": "ctr_abc123",
  "rule_name": "Monthly Timesheet Trigger",
  "rule_type": "time_based",
  "trigger_condition": {"type": "period_end", "day_of_month": 25},
  "amount_calculation": {"method": "timesheet_hours", "rate_card_id": "rc_001"},
  "frequency": "monthly"
}
```

---

### 4.9 GET /api/billing/escalations

**Description:** List upcoming escalations. **Auth Required:** Yes

**Query Parameters:** contract_id, upcoming_days (default: 90)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "esc_001",
      "contract_id": "ctr_abc123",
      "client_name": "Reliance Jio",
      "escalation_type": "annual_increment",
      "percentage": 10,
      "next_escalation_date": "2027-01-01",
      "days_until": 167,
      "auto_apply": true
    }
  ]
}
```

---

### 4.10 POST /api/billing/escalations/{id}/apply

**Description:** Manually apply an escalation. **Auth Required:** Yes | **Permissions:** billing.update

**Response (200):**
```json
{
  "success": true,
  "data": {
    "escalation_id": "esc_001",
    "applied": true,
    "old_rates": {"senior_consultant": 4500},
    "new_rates": {"senior_consultant": 4950},
    "effective_date": "2027-01-01"
  }
}
```

---


## 5. Billable APIs

### 5.1 GET /api/billables/timesheets

**Description:** List timesheets. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** client_id, contract_id, employee_id, status, period_start, period_end

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "ts_001",
      "employee_id": "emp_123",
      "employee_name": "Rahul Sharma",
      "client_name": "Reliance Jio",
      "period": "2026-07-01 to 2026-07-07",
      "total_hours": 42,
      "billable_hours": 38,
      "status": "submitted"
    }
  ]
}
```

---

### 5.2 POST /api/billables/timesheets

**Description:** Submit a timesheet. **Auth Required:** Yes

**Request Body:**
```json
{
  "employee_id": "emp_123",
  "client_id": "cli_xyz789",
  "contract_id": "ctr_abc123",
  "period_start": "2026-07-14",
  "period_end": "2026-07-20",
  "entries": [
    {"entry_date": "2026-07-14", "hours": 8, "description": "Lead qualification", "is_billable": true},
    {"entry_date": "2026-07-15", "hours": 7.5, "description": "Client meeting", "is_billable": true},
    {"entry_date": "2026-07-16", "hours": 8, "description": "Campaign execution", "is_billable": true}
  ]
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {"id": "ts_new001", "status": "draft", "total_hours": 23.5, "billable_hours": 23.5}
}
```

---

### 5.3 POST /api/billables/timesheets/{id}/approve

**Description:** Approve a timesheet. **Auth Required:** Yes | **Permissions:** billables.approve

**Response (200):**
```json
{
  "success": true,
  "data": {"id": "ts_001", "status": "approved", "approved_by": "Priya Verma"}
}
```

---

### 5.4 GET /api/billables/milestones

**Description:** List milestones. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** contract_id, client_id, status

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "ms_001",
      "contract_id": "ctr_abc123",
      "title": "Phase 1 - Pilot Launch",
      "amount": 5000000,
      "due_date": "2026-08-15",
      "completion_percentage": 75,
      "status": "in_progress"
    }
  ]
}
```

---

### 5.5 PUT /api/billables/milestones/{id}

**Description:** Update milestone status/progress. **Auth Required:** Yes | **Permissions:** billables.update

**Request Body:**
```json
{
  "completion_percentage": 100,
  "status": "completed",
  "completion_date": "2026-08-10"
}
```

---

### 5.6 GET /api/billables/call-records

**Description:** List call records. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** client_id, date_from, date_to, is_billed, agent_id

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "cr_001",
      "client_name": "HDFC Bank",
      "agent_id": "emp_456",
      "call_date": "2026-07-18",
      "duration_seconds": 480,
      "disposition": "connected",
      "is_billable": true,
      "is_billed": false,
      "amount": 120
    }
  ]
}
```

---

### 5.7 GET /api/billables/deliverables

**Description:** List project deliverables. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** client_id, contract_id, status, is_billed

---

### 5.8 POST /api/billables/deliverables

**Description:** Record a project deliverable. **Auth Required:** Yes

**Request Body:**
```json
{
  "client_id": "cli_xyz789",
  "contract_id": "ctr_abc123",
  "title": "Monthly Campaign Report - July 2026",
  "quantity": 1,
  "unit": "reports",
  "unit_rate": 50000,
  "delivery_date": "2026-07-31"
}
```

---

### 5.9 GET /api/billables/expenses

**Description:** List expenses. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** client_id, status, is_billable, date_from, date_to

---

### 5.10 POST /api/billables/sync

**Description:** Trigger sync from external systems (timesheets, CRM, calls). **Auth Required:** Yes | **Permissions:** billables.sync

**Request Body:**
```json
{
  "source_systems": ["timesheet_pro", "salesforce_crm", "avaya_cms"],
  "sync_type": "incremental",
  "date_from": "2026-07-01"
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "sync_job_id": "sync_abc123",
    "status": "processing",
    "systems_queued": 3
  }
}
```

---

## 6. Invoice APIs

### 6.1 GET /api/invoices

**Description:** List invoices. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** client_id, contract_id, status, payment_status, date_from, date_to, search

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "inv_001",
      "invoice_number": "INV-202607-10001",
      "client_name": "Reliance Jio Infocomm",
      "invoice_date": "2026-07-01",
      "due_date": "2026-07-31",
      "subtotal": 4500000,
      "tax_amount": 810000,
      "total_amount": 5310000,
      "status": "dispatched",
      "payment_status": "unpaid",
      "balance_amount": 5310000
    }
  ]
}
```

---

### 6.2 POST /api/invoices/generate

**Description:** Generate invoice for a client/contract. **Auth Required:** Yes | **Permissions:** invoices.create

**Request Body:**
```json
{
  "client_id": "cli_xyz789",
  "contract_id": "ctr_abc123",
  "billing_period_start": "2026-07-01",
  "billing_period_end": "2026-07-31",
  "line_items": [
    {
      "description": "Senior Consultant - 160 hours",
      "quantity": 160,
      "unit": "hours",
      "unit_price": 4500,
      "hsn_sac_code": "998311"
    },
    {
      "description": "Consultant - 320 hours",
      "quantity": 320,
      "unit": "hours",
      "unit_price": 2500,
      "hsn_sac_code": "998311"
    }
  ],
  "notes": "Services for July 2026",
  "template_id": "tmpl_001"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": "inv_new001",
    "invoice_number": "INV-202607-10045",
    "subtotal": 1520000,
    "cgst_amount": 136800,
    "sgst_amount": 136800,
    "total_amount": 1793600,
    "status": "draft",
    "pdf_url": null
  }
}
```

---

### 6.3 POST /api/invoices/{id}/approve

**Description:** Approve an invoice. **Auth Required:** Yes | **Permissions:** invoices.approve

**Request Body:**
```json
{
  "comments": "Approved - all line items verified"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "invoice_id": "inv_001",
    "status": "approved",
    "approved_by": "Priya Verma",
    "pdf_url": "https://s3.ap-south-1.amazonaws.com/finmark-docs/invoices/inv_001.pdf"
  }
}
```

---

### 6.4 POST /api/invoices/{id}/dispatch

**Description:** Dispatch invoice to client. **Auth Required:** Yes | **Permissions:** invoices.update

**Request Body:**
```json
{
  "method": "email",
  "recipients": ["finance@reliancejio.com", "rajesh.kumar@reliancejio.com"],
  "cc": ["priya.verma@denave.com"],
  "message": "Please find attached invoice for services rendered in July 2026."
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "dispatch_id": "dsp_001",
    "status": "sent",
    "dispatched_at": "2026-07-18T10:00:00Z"
  }
}
```

---

### 6.5 POST /api/invoices/{id}/credit-note

**Description:** Issue credit note against invoice. **Auth Required:** Yes | **Permissions:** invoices.create

**Request Body:**
```json
{
  "amount": 150000,
  "reason": "Discount for early payment"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "credit_note_id": "cn_001",
    "credit_note_number": "CN-202607-001",
    "amount": 150000,
    "status": "issued"
  }
}
```

---

### 6.6 GET /api/invoices/templates

**Description:** List invoice templates. **Auth Required:** Yes

---

### 6.7 POST /api/invoices/bulk-generate

**Description:** Bulk generate invoices for billing cycle. **Auth Required:** Yes | **Permissions:** invoices.create

**Request Body:**
```json
{
  "billing_period_end": "2026-07-31",
  "client_ids": ["cli_001", "cli_002", "cli_003"],
  "auto_approve": false,
  "send_notification": true
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_abc123",
    "total_invoices": 12,
    "status": "processing",
    "estimated_completion": "2026-07-18T10:10:00Z"
  }
}
```

---


## 7. Revenue APIs

### 7.1 POST /api/revenue/recognize

**Description:** Recognize revenue for a period. **Auth Required:** Yes | **Permissions:** revenue.create

**Request Body:**
```json
{
  "contract_id": "ctr_abc123",
  "period_month": 7,
  "period_year": 2026,
  "amount": 4500000,
  "recognition_basis": "input_method",
  "reference_type": "invoice",
  "reference_id": "inv_001"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "entry_id": "re_001",
    "journal_entry": {
      "debit": {"account": "Accounts Receivable", "amount": 4500000},
      "credit": {"account": "Service Revenue - T&M", "amount": 4500000}
    },
    "cumulative_recognized": 31500000,
    "percentage_complete": 45.5
  }
}
```

---

### 7.2 POST /api/revenue/defer

**Description:** Defer revenue to future periods. **Auth Required:** Yes | **Permissions:** revenue.create

**Request Body:**
```json
{
  "contract_id": "ctr_abc123",
  "invoice_id": "inv_001",
  "amount": 1200000,
  "release_method": "straight_line",
  "release_start_date": "2026-08-01",
  "release_end_date": "2026-12-31",
  "reason": "Advance billing for future services"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "deferred_id": "df_001",
    "monthly_release": 240000,
    "release_schedule": [
      {"month": "2026-08", "amount": 240000},
      {"month": "2026-09", "amount": 240000},
      {"month": "2026-10", "amount": 240000},
      {"month": "2026-11", "amount": 240000},
      {"month": "2026-12", "amount": 240000}
    ]
  }
}
```

---

### 7.3 GET /api/revenue/schedule

**Description:** Get revenue recognition schedule. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** contract_id, client_id, period_from, period_to, status

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "rs_001",
      "contract_id": "ctr_abc123",
      "client_name": "Reliance Jio",
      "period": "2026-07",
      "scheduled_amount": 4500000,
      "recognized_amount": 4500000,
      "deferred_amount": 0,
      "status": "recognized"
    }
  ]
}
```

---

### 7.4 GET /api/revenue/compliance

**Description:** Get ASC 606/Ind AS 115 compliance status. **Auth Required:** Yes

**Query Parameters:** status (compliant/non_compliant/review)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_contracts": 45,
      "compliant": 40,
      "under_review": 3,
      "non_compliant": 2
    },
    "non_compliant_contracts": [
      {"contract_id": "ctr_008", "client": "Tata Motors", "issue": "Step 4 allocation pending"}
    ]
  }
}
```

---

### 7.5 POST /api/revenue/adjustments

**Description:** Create revenue adjustment entry. **Auth Required:** Yes | **Permissions:** revenue.update

**Request Body:**
```json
{
  "contract_id": "ctr_abc123",
  "adjustment_type": "reversal",
  "amount": -500000,
  "period_month": 6,
  "period_year": 2026,
  "reason": "Milestone completion reversed - client rejected deliverable"
}
```

---

### 7.6 GET /api/revenue/reports

**Description:** Get revenue recognition reports. **Auth Required:** Yes

**Query Parameters:** report_type (monthly_summary/contract_detail/compliance_disclosure), period

**Response (200):**
```json
{
  "success": true,
  "data": {
    "report_type": "monthly_summary",
    "period": "2026-07",
    "total_recognized": 98000000,
    "total_deferred": 12000000,
    "total_unbilled": 8000000,
    "by_billing_model": {
      "T&M": 25800000,
      "Milestone": 20600000,
      "Retainer": 30900000,
      "Performance": 15500000,
      "Hybrid": 5200000
    }
  }
}
```

---

### 7.7 POST /api/revenue/period-close

**Description:** Close a revenue recognition period. **Auth Required:** Yes | **Permissions:** revenue.approve

**Request Body:**
```json
{
  "period_month": 7,
  "period_year": 2026
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "period": "2026-07",
    "status": "closed",
    "total_recognized": 98000000,
    "contracts_processed": 45,
    "journal_entries_created": 92
  }
}
```

---

## 8. Leakage APIs

### 8.1 POST /api/leakage/detect

**Description:** Trigger leakage detection scan. **Auth Required:** Yes | **Permissions:** leakage.create

**Request Body:**
```json
{
  "scan_type": "full",
  "client_ids": null,
  "categories": ["unbilled_hours", "missed_milestone", "rate_variance", "scope_creep"]
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "scan_id": "scan_abc123",
    "status": "processing",
    "clients_to_scan": 18,
    "estimated_time_seconds": 300
  }
}
```

---

### 8.2 GET /api/leakage/alerts

**Description:** List leakage alerts. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** severity (HIGH/MEDIUM/LOW), status (open/investigating/resolved), client_id, type, date_from

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "la_001",
      "client_name": "Reliance Jio",
      "leakage_type": "unbilled_hours",
      "severity": "HIGH",
      "amount": 240000,
      "description": "160 hours worked but not billed - timesheet not linked",
      "root_cause": "Timesheet not linked to billing system",
      "recommendation": "Immediate billing - include in next invoice cycle",
      "status": "open",
      "detected_at": "2026-07-18T06:00:00Z"
    }
  ]
}
```

---

### 8.3 POST /api/leakage/alerts/{id}/resolve

**Description:** Resolve a leakage alert. **Auth Required:** Yes | **Permissions:** leakage.update

**Request Body:**
```json
{
  "resolution_type": "recovered",
  "recovered_amount": 220000,
  "notes": "Added to next billing cycle. 20K written off as goodwill.",
  "invoice_id": "inv_045"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "alert_id": "la_001",
    "status": "resolved",
    "recovered_amount": 220000,
    "recovery_rate": 91.7
  }
}
```

---

### 8.4 GET /api/leakage/rules

**Description:** List leakage detection rules. **Auth Required:** Yes

---

### 8.5 POST /api/leakage/rules

**Description:** Create leakage detection rule. **Auth Required:** Yes | **Permissions:** leakage.create

**Request Body:**
```json
{
  "rule_name": "Escalation Not Applied",
  "rule_type": "escalation_check",
  "condition_json": {"check": "annual_escalation", "grace_days": 30},
  "threshold_percentage": 5,
  "severity_default": "HIGH",
  "scan_frequency": "weekly"
}
```

---

### 8.6 GET /api/leakage/dashboard

**Description:** Get leakage dashboard summary. **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_leakage_detected": 8500000,
    "annualized_leakage": 102000000,
    "recovery_potential": 86700000,
    "total_alerts": 42,
    "by_severity": {"HIGH": 8, "MEDIUM": 22, "LOW": 12},
    "by_type": {
      "unbilled_hours": 3200000,
      "missed_milestone": 2800000,
      "rate_variance": 1500000,
      "scope_creep": 700000,
      "escalation_missed": 300000
    },
    "leakage_rate_percent": 2.8,
    "target_rate_percent": 0.5
  }
}
```

---

### 8.7 GET /api/leakage/trends

**Description:** Get leakage trends over time. **Auth Required:** Yes

**Query Parameters:** months (default: 12), client_id

**Response (200):**
```json
{
  "success": true,
  "data": {
    "trend_data": [
      {"month": "2026-01", "amount": 12000000, "rate_percent": 4.1},
      {"month": "2026-02", "amount": 10500000, "rate_percent": 3.6},
      {"month": "2026-07", "amount": 8500000, "rate_percent": 2.8}
    ],
    "improvement_percent": 31.7,
    "on_track_for_target": true
  }
}
```

---


## 9. Profitability APIs

### 9.1 POST /api/profitability/calculate

**Description:** Trigger profitability calculation for a client/period. **Auth Required:** Yes | **Permissions:** profitability.create

**Request Body:**
```json
{
  "client_id": "cli_xyz789",
  "period_month": 7,
  "period_year": 2026,
  "include_overhead": true
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "client_id": "cli_xyz789",
    "client_name": "Reliance Jio",
    "period": "2026-07",
    "revenue": 4500000,
    "direct_costs": 2800000,
    "indirect_costs": 350000,
    "overhead_allocated": 450000,
    "total_costs": 3600000,
    "gross_margin": 1700000,
    "gross_margin_percent": 37.8,
    "net_margin": 900000,
    "net_margin_percent": 20.0,
    "is_above_threshold": true,
    "threshold": 12.0
  }
}
```

---

### 9.2 GET /api/profitability/margins

**Description:** Get margin data for all clients. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** period_month, period_year, sort_by (margin_percent), below_threshold_only

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "client_id": "cli_xyz789",
      "client_name": "Reliance Jio",
      "billing_model": "T&M",
      "revenue": 4500000,
      "net_margin_percent": 20.0,
      "trend": "stable",
      "ranking": 3
    }
  ]
}
```

---

### 9.3 GET /api/profitability/benchmarks

**Description:** Get benchmark comparison data. **Auth Required:** Yes

**Query Parameters:** benchmark_type (industry/billing_model/segment)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "avg_net_margin": 16.2,
    "top_quartile_margin": 24.5,
    "bottom_quartile_margin": 8.3,
    "clients_above_threshold": 13,
    "clients_below_threshold": 5,
    "highest_margin_client": {"name": "Apollo Hospitals", "margin": 32.1},
    "lowest_margin_client": {"name": "Tata Motors", "margin": 5.8},
    "by_billing_model": {
      "T&M": {"avg_margin": 18.5, "count": 5},
      "Retainer": {"avg_margin": 22.1, "count": 6},
      "Milestone": {"avg_margin": 14.2, "count": 4},
      "Performance": {"avg_margin": 11.5, "count": 2},
      "Hybrid": {"avg_margin": 15.8, "count": 1}
    }
  }
}
```

---

### 9.4 GET /api/profitability/trends

**Description:** Get profitability trends over time. **Auth Required:** Yes

**Query Parameters:** client_id, months (default: 6)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "client_id": "cli_xyz789",
    "client_name": "Reliance Jio",
    "trend_data": [
      {"month": "2026-02", "margin_percent": 22.1},
      {"month": "2026-03", "margin_percent": 21.5},
      {"month": "2026-04", "margin_percent": 20.8},
      {"month": "2026-05", "margin_percent": 20.3},
      {"month": "2026-06", "margin_percent": 20.1},
      {"month": "2026-07", "margin_percent": 20.0}
    ],
    "trend_direction": "slightly_declining",
    "decline_rate_per_month": -0.4
  }
}
```

---

### 9.5 GET /api/profitability/forecasts

**Description:** Get 6-month margin forecast. **Auth Required:** Yes

**Query Parameters:** client_id

**Response (200):**
```json
{
  "success": true,
  "data": {
    "client_id": "cli_xyz789",
    "forecast": [
      {"month": "2026-08", "predicted_margin": 19.6, "confidence": 0.92},
      {"month": "2026-09", "predicted_margin": 19.2, "confidence": 0.88},
      {"month": "2026-10", "predicted_margin": 18.8, "confidence": 0.84},
      {"month": "2026-11", "predicted_margin": 18.4, "confidence": 0.79},
      {"month": "2026-12", "predicted_margin": 18.0, "confidence": 0.74},
      {"month": "2027-01", "predicted_margin": 17.6, "confidence": 0.68}
    ],
    "risk_level": "MEDIUM",
    "action_needed": false
  }
}
```

---

### 9.6 GET /api/profitability/recommendations

**Description:** Get AI-generated profitability recommendations. **Auth Required:** Yes

**Query Parameters:** client_id, priority (HIGH/MEDIUM/LOW)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "rec_001",
      "client_name": "Tata Motors",
      "type": "restructure",
      "title": "Restructure delivery model to reduce costs",
      "description": "Current margin at 5.8%. Recommend shifting 40% field team to tele-calling model.",
      "impact_amount": 1200000,
      "confidence": 0.87,
      "priority": "HIGH",
      "status": "pending"
    }
  ]
}
```

---

## 10. Collection APIs

### 10.1 GET /api/collections/receivables

**Description:** List outstanding receivables. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** client_id, aging_bucket, status, min_amount, sort_by (days_overdue/amount)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "rcv_001",
      "client_name": "Tata Motors",
      "invoice_number": "INV-202606-10032",
      "original_amount": 5310000,
      "outstanding_amount": 5310000,
      "due_date": "2026-06-30",
      "days_overdue": 18,
      "aging_bucket": "30",
      "escalation_level": 1,
      "last_reminder": "2026-07-10"
    }
  ],
  "summary": {
    "total_outstanding": 45000000,
    "total_overdue": 18000000,
    "avg_dso": 52
  }
}
```

---

### 10.2 GET /api/collections/aging

**Description:** Get aging analysis. **Auth Required:** Yes

**Query Parameters:** as_of_date, client_id

**Response (200):**
```json
{
  "success": true,
  "data": {
    "as_of_date": "2026-07-18",
    "summary": {
      "current": 27000000,
      "bucket_30": 12000000,
      "bucket_60": 4500000,
      "bucket_90": 1200000,
      "bucket_120_plus": 300000,
      "total": 45000000
    },
    "by_client": [
      {
        "client_name": "Tata Motors",
        "current": 0,
        "bucket_30": 5310000,
        "bucket_60": 2100000,
        "total": 7410000
      }
    ]
  }
}
```

---

### 10.3 POST /api/collections/dunning/{receivable_id}

**Description:** Trigger dunning action for a receivable. **Auth Required:** Yes | **Permissions:** collections.update

**Request Body:**
```json
{
  "action_type": "email",
  "template_id": "tmpl_reminder_1",
  "escalate": false
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "action": "email_sent",
    "recipient": "finance@tatamotors.com",
    "reminder_count": 2,
    "next_escalation_date": "2026-08-01"
  }
}
```

---

### 10.4 POST /api/collections/payments

**Description:** Record a payment receipt. **Auth Required:** Yes | **Permissions:** collections.create

**Request Body:**
```json
{
  "client_id": "cli_tata",
  "invoice_id": "inv_032",
  "amount": 5000000,
  "receipt_date": "2026-07-18",
  "payment_method": "bank_transfer",
  "bank_reference": "NEFT/2026071800123456",
  "tds_deducted": 500000
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "receipt_id": "pmt_001",
    "receipt_number": "RCT-202607-001",
    "matched_invoice": "INV-202606-10032",
    "remaining_balance": 310000,
    "payment_status": "partially_paid"
  }
}
```

---

### 10.5 POST /api/collections/reconcile

**Description:** Auto-reconcile payments with invoices. **Auth Required:** Yes | **Permissions:** collections.update

**Request Body:**
```json
{
  "date_from": "2026-07-01",
  "date_to": "2026-07-18",
  "auto_match": true
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_payments": 15,
    "auto_matched": 12,
    "manual_review_needed": 3,
    "total_amount_matched": 38500000
  }
}
```

---

### 10.6 GET /api/collections/forecast

**Description:** Get cash collection forecast. **Auth Required:** Yes

**Query Parameters:** days_ahead (default: 30), client_id

**Response (200):**
```json
{
  "success": true,
  "data": {
    "forecast_period": "2026-07-18 to 2026-08-17",
    "expected_inflows": [
      {"week": "Jul 18-24", "amount": 12000000, "confidence": 0.90},
      {"week": "Jul 25-31", "amount": 8500000, "confidence": 0.85},
      {"week": "Aug 01-07", "amount": 15000000, "confidence": 0.78},
      {"week": "Aug 08-14", "amount": 6000000, "confidence": 0.72}
    ],
    "total_expected": 41500000,
    "avg_confidence": 0.81
  }
}
```

---


## 11. AI APIs

### 11.1 GET /api/ai/recommendations

**Description:** List AI recommendations. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** client_id, type, priority, status

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "rec_001",
      "client_name": "Tata Motors",
      "recommendation_type": "restructure",
      "title": "Restructure delivery model",
      "description": "Shift 40% field operations to tele-calling to improve margin from 5.8% to 14.2%",
      "impact_amount": 1200000,
      "confidence_score": 0.87,
      "priority": "HIGH",
      "status": "pending",
      "reasoning": "Based on 6-month trend analysis showing consistent margin erosion with high field costs",
      "created_at": "2026-07-18T06:00:00Z"
    }
  ]
}
```

---

### 11.2 POST /api/ai/recommendations/{id}/accept

**Description:** Accept an AI recommendation. **Auth Required:** Yes | **Permissions:** ai.update

**Request Body:**
```json
{
  "implementation_notes": "Will implement in phases starting August"
}
```

---

### 11.3 POST /api/ai/recommendations/{id}/reject

**Description:** Reject an AI recommendation. **Auth Required:** Yes | **Permissions:** ai.update

**Request Body:**
```json
{
  "rejection_reason": "Client relationship too strategic to restructure"
}
```

---

### 11.4 GET /api/ai/predictions

**Description:** List AI predictions. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** prediction_type, subject_type, client_id

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "pred_001",
      "prediction_type": "payment_prediction",
      "client_name": "HDFC Bank",
      "invoice_id": "inv_055",
      "prediction_value": 0.92,
      "prediction_label": "will_pay_on_time",
      "confidence": 0.88,
      "target_date": "2026-08-15"
    }
  ]
}
```

---

### 11.5 POST /api/ai/contract-parse

**Description:** Parse contract using AI/NLP. **Auth Required:** Yes | **Permissions:** ai.create

**Request Body:**
```json
{
  "document_id": "doc_abc123",
  "extraction_fields": ["billing_model", "payment_terms", "milestones", "sla", "escalation"],
  "model": "gpt-4"
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "job_id": "ai_job_001",
    "status": "processing",
    "estimated_seconds": 45
  }
}
```

---

### 11.6 POST /api/ai/anomaly-detect

**Description:** Run anomaly detection on billing/revenue data. **Auth Required:** Yes | **Permissions:** ai.create

**Request Body:**
```json
{
  "scope": "all_clients",
  "data_types": ["billing_amounts", "activity_volumes", "payment_patterns"],
  "lookback_days": 90
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "anomalies_found": 5,
    "anomalies": [
      {
        "client": "Flipkart Internet",
        "type": "billing_amount_spike",
        "expected_range": [3000000, 4500000],
        "actual_value": 7200000,
        "severity": "HIGH",
        "explanation": "Billing amount 60% above historical average"
      }
    ]
  }
}
```

---

### 11.7 POST /api/ai/forecast

**Description:** Generate forecast for specified metric. **Auth Required:** Yes | **Permissions:** ai.create

**Request Body:**
```json
{
  "metric": "revenue",
  "client_id": "cli_xyz789",
  "forecast_months": 6,
  "include_confidence_intervals": true
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "metric": "revenue",
    "client_name": "Reliance Jio",
    "forecast": [
      {"month": "2026-08", "value": 4600000, "lower_bound": 4200000, "upper_bound": 5000000},
      {"month": "2026-09", "value": 4700000, "lower_bound": 4200000, "upper_bound": 5200000},
      {"month": "2026-10", "value": 4750000, "lower_bound": 4100000, "upper_bound": 5400000}
    ],
    "model_used": "prophet_v2",
    "r_squared": 0.91
  }
}
```

---

## 12. Dashboard APIs

### 12.1 GET /api/dashboard/overview

**Description:** Get executive dashboard overview. **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": {
    "active_clients": 18,
    "total_contract_value": 450000000,
    "monthly_revenue": 42000000,
    "leakage_detected_monthly": 8500000,
    "annualized_leakage": 102000000,
    "recovery_potential": 86700000,
    "outstanding_receivables": 45000000,
    "overdue_amount": 18000000,
    "avg_collection_days": 52,
    "avg_margin_percent": 16.2,
    "clients_above_threshold": 13,
    "clients_below_threshold": 5,
    "invoices_pending_approval": 4,
    "alerts_unresolved": 8
  }
}
```

---

### 12.2 GET /api/dashboard/revenue-trend

**Description:** Get revenue trend data for charts. **Auth Required:** Yes

**Query Parameters:** months (default: 12), granularity (monthly/weekly)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "trend": [
      {"period": "2026-01", "recognized": 92000000, "deferred": 8000000, "unbilled": 5000000},
      {"period": "2026-02", "recognized": 95000000, "deferred": 7000000, "unbilled": 4500000},
      {"period": "2026-07", "recognized": 98000000, "deferred": 12000000, "unbilled": 8000000}
    ],
    "growth_rate": 6.5,
    "total_ytd": 680000000
  }
}
```

---

### 12.3 GET /api/dashboard/margin-summary

**Description:** Get margin summary for dashboard. **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": {
    "portfolio_margin": 16.2,
    "top_5_clients": [
      {"name": "Apollo Hospitals", "margin": 32.1},
      {"name": "Reliance Jio", "margin": 20.0},
      {"name": "HDFC Bank", "margin": 19.5}
    ],
    "bottom_5_clients": [
      {"name": "Tata Motors", "margin": 5.8},
      {"name": "Mahindra Tech", "margin": 8.2}
    ],
    "margin_distribution": {
      "above_25": 4,
      "15_to_25": 6,
      "12_to_15": 3,
      "below_12": 5
    }
  }
}
```

---

### 12.4 GET /api/dashboard/leakage-summary

**Description:** Get leakage summary for dashboard. **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": {
    "current_month_leakage": 8500000,
    "leakage_rate": 2.8,
    "target_rate": 0.5,
    "by_category": {
      "unbilled_hours": 3200000,
      "missed_milestones": 2800000,
      "rate_variance": 1500000,
      "scope_creep": 700000,
      "escalation_missed": 300000
    },
    "alerts_open": 42,
    "alerts_high": 8,
    "recovery_this_month": 5200000,
    "recovery_rate_percent": 61.2
  }
}
```

---

### 12.5 GET /api/dashboard/collections

**Description:** Get collections dashboard data. **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": {
    "total_outstanding": 45000000,
    "total_overdue": 18000000,
    "dso_current": 52,
    "dso_target": 40,
    "aging_summary": {
      "current": 27000000,
      "30_days": 12000000,
      "60_days": 4500000,
      "90_days": 1200000,
      "120_plus": 300000
    },
    "collection_this_month": 38500000,
    "collection_target": 42000000,
    "achievement_percent": 91.7
  }
}
```

---


## 13. Report APIs

### 13.1 POST /api/reports/generate

**Description:** Generate a report on-demand. **Auth Required:** Yes | **Permissions:** reports.create

**Request Body:**
```json
{
  "template_id": "tmpl_revenue_monthly",
  "parameters": {
    "period_month": 7,
    "period_year": 2026,
    "client_ids": null,
    "include_details": true
  },
  "format": "pdf"
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "export_id": "exp_001",
    "status": "generating",
    "estimated_seconds": 30
  }
}
```

---

### 13.2 GET /api/reports/generate/{export_id}

**Description:** Check report generation status and get download URL. **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": {
    "export_id": "exp_001",
    "status": "ready",
    "download_url": "https://s3.ap-south-1.amazonaws.com/finmark-reports/exp_001.pdf",
    "expires_at": "2026-07-19T10:00:00Z",
    "file_size": 2450000
  }
}
```

---

### 13.3 POST /api/reports/schedule

**Description:** Schedule recurring report generation. **Auth Required:** Yes | **Permissions:** reports.create

**Request Body:**
```json
{
  "template_id": "tmpl_leakage_monthly",
  "name": "Monthly Leakage Report - CFO",
  "frequency": "monthly",
  "day_of_month": 2,
  "time_of_day": "08:00",
  "format": "pdf",
  "recipients": ["cfo@denave.com", "finance.head@denave.com"]
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "schedule_id": "sch_001",
    "next_run_at": "2026-08-02T08:00:00+05:30"
  }
}
```

---

### 13.4 GET /api/reports/export

**Description:** List recent report exports. **Auth Required:** Yes | **Pagination:** Yes

**Query Parameters:** status, format, date_from

---

### 13.5 GET /api/reports/templates

**Description:** List available report templates. **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "tmpl_revenue_monthly",
      "name": "Monthly Revenue Recognition Report",
      "report_type": "revenue",
      "description": "Detailed revenue recognition by contract with ASC 606 compliance status",
      "parameters": ["period_month", "period_year", "client_ids"],
      "formats": ["pdf", "excel"]
    },
    {
      "id": "tmpl_leakage_monthly",
      "name": "Monthly Leakage Detection Report",
      "report_type": "leakage",
      "description": "Comprehensive leakage analysis with recovery recommendations"
    },
    {
      "id": "tmpl_profitability_quarterly",
      "name": "Quarterly Client Profitability Report",
      "report_type": "profitability",
      "description": "Client-wise profitability with benchmarks and AI recommendations"
    }
  ]
}
```

---

## 14. Settings APIs

### 14.1 GET /api/settings/organization

**Description:** Get organization settings. **Auth Required:** Yes | **Permissions:** settings.read

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": "org_x1y2z3",
    "name": "Denave India Pvt. Ltd.",
    "plan_tier": "enterprise",
    "gstin": "07AAACN0164C1ZW",
    "financial_year_start": 4,
    "default_currency": "INR",
    "margin_threshold": 12.0,
    "invoice_prefix": "INV",
    "invoice_auto_numbering": true,
    "approval_thresholds": {
      "level_1": 1000000,
      "level_2": 5000000,
      "level_3": 10000000
    }
  }
}
```

---

### 14.2 PUT /api/settings/organization

**Description:** Update organization settings. **Auth Required:** Yes | **Permissions:** settings.update

---

### 14.3 GET /api/settings/users

**Description:** List organization users. **Auth Required:** Yes | **Permissions:** users.read | **Pagination:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "usr_001",
      "email": "priya.verma@denave.com",
      "name": "Priya Verma",
      "roles": ["finance_manager"],
      "status": "active",
      "last_login": "2026-07-18T09:30:00Z"
    }
  ]
}
```

---

### 14.4 POST /api/settings/users

**Description:** Create/invite a user. **Auth Required:** Yes | **Permissions:** users.create

**Request Body:**
```json
{
  "email": "new.user@denave.com",
  "first_name": "New",
  "last_name": "User",
  "role": "accountant",
  "send_invite": true
}
```

---

### 14.5 GET /api/settings/roles

**Description:** List roles and permissions. **Auth Required:** Yes | **Permissions:** roles.read

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "role_001",
      "name": "Finance Manager",
      "slug": "finance_manager",
      "permissions": ["contracts.read", "invoices.create", "invoices.approve", "revenue.create"],
      "user_count": 3
    }
  ]
}
```

---

### 14.6 POST /api/settings/roles

**Description:** Create custom role. **Auth Required:** Yes | **Permissions:** roles.create

---

### 14.7 GET /api/settings/integrations

**Description:** List integration configurations. **Auth Required:** Yes | **Permissions:** integrations.read

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "int_001",
      "integration_type": "tally",
      "name": "Tally Prime Integration",
      "status": "active",
      "last_sync": "2026-07-18T06:00:00Z",
      "last_sync_status": "success",
      "records_synced": 45
    }
  ]
}
```

---

### 14.8 POST /api/settings/integrations

**Description:** Configure new integration. **Auth Required:** Yes | **Permissions:** integrations.create

---

### 14.9 GET /api/settings/notifications

**Description:** Get notification preferences. **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": {
    "preferences": [
      {"event": "leakage_alert_high", "email": true, "sms": true, "in_app": true},
      {"event": "invoice_approved", "email": true, "sms": false, "in_app": true},
      {"event": "margin_breach", "email": true, "sms": false, "in_app": true},
      {"event": "payment_received", "email": false, "sms": false, "in_app": true}
    ]
  }
}
```

---

### 14.10 PUT /api/settings/notifications

**Description:** Update notification preferences. **Auth Required:** Yes

---

### 14.11 GET /api/settings/tax

**Description:** Get tax configuration (GST rates, HSN codes, TDS). **Auth Required:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": {
    "gst_rates": [
      {"rate": 18, "description": "Standard services", "hsn_codes": ["998311", "998312"]},
      {"rate": 12, "description": "IT services (specific)", "hsn_codes": ["998313"]}
    ],
    "tds_rate": 10,
    "states": [
      {"code": "07", "name": "Delhi", "is_ut": true},
      {"code": "27", "name": "Maharashtra", "is_ut": false}
    ]
  }
}
```

---

### 14.12 PUT /api/settings/tax

**Description:** Update tax configuration. **Auth Required:** Yes | **Permissions:** settings.update

---

## 15. Integration APIs

### 15.1 POST /api/integrations/tally/sync

**Description:** Trigger Tally Prime synchronization. **Auth Required:** Yes | **Permissions:** integrations.sync

**Request Body:**
```json
{
  "sync_type": "incremental",
  "entities": ["ledgers", "vouchers", "cost_centers"],
  "date_from": "2026-07-01"
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "sync_id": "sync_tally_001",
    "status": "processing",
    "entities_queued": 3
  }
}
```

---

### 15.2 POST /api/integrations/sap/sync

**Description:** Trigger SAP synchronization. **Auth Required:** Yes | **Permissions:** integrations.sync

**Request Body:**
```json
{
  "sync_type": "full",
  "modules": ["FI", "CO", "SD"],
  "company_code": "1000"
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "sync_id": "sync_sap_001",
    "status": "processing"
  }
}
```

---

### 15.3 POST /api/integrations/crm/sync

**Description:** Trigger CRM (Salesforce) synchronization. **Auth Required:** Yes | **Permissions:** integrations.sync

**Request Body:**
```json
{
  "sync_type": "incremental",
  "objects": ["opportunities", "activities", "contacts"],
  "last_modified_after": "2026-07-17T00:00:00Z"
}
```

**Response (202):**
```json
{
  "success": true,
  "data": {
    "sync_id": "sync_crm_001",
    "status": "processing",
    "objects_queued": 3
  }
}
```

---

### 15.4 POST /api/integrations/webhook

**Description:** Receive inbound webhook from external systems. **Auth Required:** API Key + HMAC signature

**Headers:**
```
X-Webhook-Signature: sha256=abc123...
X-Webhook-Source: tally_prime
Content-Type: application/json
```

**Request Body:**
```json
{
  "event": "payment_received",
  "timestamp": "2026-07-18T14:30:00Z",
  "payload": {
    "voucher_number": "RCV-2026-0789",
    "amount": 5310000,
    "party_name": "Reliance Jio Infocomm",
    "bank_date": "2026-07-18"
  }
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "webhook_id": "wh_received_001",
    "status": "accepted",
    "processing_queue": "payment_events"
  }
}
```

---

### 15.5 GET /api/integrations/webhook/logs

**Description:** List webhook delivery logs. **Auth Required:** Yes | **Pagination:** Yes

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": "wh_log_001",
      "webhook_name": "Tally Payment Sync",
      "event": "payment_received",
      "status": "delivered",
      "status_code": 200,
      "timestamp": "2026-07-18T14:30:00Z",
      "response_time_ms": 245
    }
  ]
}
```

---

## Endpoint Summary

| Category | Endpoints | Methods |
|----------|-----------|---------|
| Auth | 6 | POST |
| Contracts | 12 | GET, POST, PUT, DELETE |
| Clients | 10 | GET, POST, PUT, DELETE |
| Billing | 10 | GET, POST, PUT |
| Billables | 10 | GET, POST, PUT |
| Invoices | 7 | GET, POST |
| Revenue | 7 | GET, POST |
| Leakage | 7 | GET, POST |
| Profitability | 6 | GET, POST |
| Collections | 6 | GET, POST |
| AI | 7 | GET, POST |
| Dashboard | 5 | GET |
| Reports | 5 | GET, POST |
| Settings | 12 | GET, POST, PUT |
| Integrations | 5 | GET, POST |
| **TOTAL** | **115 documented (156 with sub-resources)** | |

> **Note:** Additional CRUD sub-endpoints (PUT/DELETE for individual resources, nested resource operations) bring the total to 156+ endpoints. Standard patterns (GET list, GET by ID, POST create, PUT update, DELETE soft-delete) apply to all resource endpoints.

---

## Rate Limiting

| Tier | Requests/Minute | Burst |
|------|----------------|-------|
| Starter | 100 | 200 |
| Professional | 500 | 1000 |
| Enterprise | 1000 | 2000 |

Rate limit headers included in every response:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 998
X-RateLimit-Reset: 1721324460
```

---

## Versioning

API versioning is done via URL path: `/api/v1/`, `/api/v2/`

Breaking changes will increment the major version. Non-breaking additions (new fields, new endpoints) will be added to the current version.

Deprecation notice: Minimum 6 months before version sunset.

---

*Document End — RevRecog AI + ClientMargin360 API Documentation v2.0.0*
