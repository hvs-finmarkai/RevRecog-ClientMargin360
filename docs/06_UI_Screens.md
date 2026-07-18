# UI Screens Documentation

## RevRecog AI + ClientMargin360 — Screen Specifications

---

## 1. Login Screen

### Page Name
Login / Authentication

### Layout Description
Centered card layout with company branding at top, form fields in middle, action buttons at bottom. Background uses subtle gradient.

### Components Used
- Logo component
- Email input field
- Password input field with visibility toggle
- "Remember me" checkbox
- Primary login button
- "Forgot password" link
- SSO login buttons (Google, Microsoft)

### Data Displayed
- Application name and logo
- Error messages on failed login
- Loading spinner during authentication

### User Interactions
| Action | Behavior |
|--------|----------|
| Submit login form | POST credentials, redirect to Dashboard |
| Click "Forgot password" | Navigate to password reset flow |
| Click SSO button | Redirect to OAuth provider |
| Toggle password visibility | Show/hide password characters |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/auth/login/ | POST | Authenticate user |
| /api/v1/auth/token/refresh/ | POST | Refresh JWT token |
| /api/v1/auth/sso/{provider}/ | GET | Initiate SSO flow |

---

## 2. Dashboard / Overview

### Page Name
Dashboard Overview

### Layout Description
Top navigation bar with user menu. Left sidebar with navigation links. Main content area with grid of metric cards (top row), charts (middle row), and recent activity table (bottom).

### Components Used
- MetricCard (revenue, margin, leakage, collections)
- LineChart (revenue trend 12 months)
- BarChart (client profitability comparison)
- DonutChart (revenue by client segment)
- AlertBadge (pending alerts count)
- RecentActivityTable
- DateRangePicker (top filter)
- OrganizationSelector

### Data Displayed
- Total recognized revenue (current period)
- Average client margin percentage
- Total leakage detected (currency)
- Outstanding collections amount
- Revenue trend chart (12 months)
- Top 5 clients by revenue
- Top 5 leakage alerts
- Recent activity feed (last 10 actions)

### User Interactions
| Action | Behavior |
|--------|----------|
| Change date range | Refresh all metrics for selected period |
| Click metric card | Navigate to detailed module |
| Hover chart point | Show tooltip with exact values |
| Click alert badge | Navigate to alerts list |
| Click activity item | Navigate to related entity |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/dashboard/metrics/ | GET | Fetch summary metrics |
| /api/v1/dashboard/revenue-trend/ | GET | Revenue chart data |
| /api/v1/dashboard/top-clients/ | GET | Top clients list |
| /api/v1/dashboard/recent-activity/ | GET | Activity feed |
| /api/v1/alerts/?status=active&limit=5 | GET | Active alerts count |

---

## 3. Contracts — List View

### Page Name
Contracts List

### Layout Description
Full-width table with filter bar above. Bulk action toolbar appears on row selection. Pagination at bottom.

### Components Used
- SearchInput (contract name/client search)
- FilterDropdown (status, client, date range)
- DataTable with sortable columns
- StatusBadge (Active, Expired, Draft, Pending Review)
- BulkActionToolbar
- Pagination
- ExportButton (CSV/Excel)

### Data Displayed
| Column | Description |
|--------|-------------|
| Contract ID | Auto-generated identifier |
| Client Name | Associated client |
| Contract Value | Total contract value |
| Start Date | Effective start |
| End Date | Expiration date |
| Status | Current status badge |
| Revenue Recognized | Amount recognized to date |
| Compliance | ASC 606 compliance indicator |

### User Interactions
| Action | Behavior |
|--------|----------|
| Click row | Navigate to contract detail |
| Click "New Contract" | Open upload/create modal |
| Apply filters | Filter table results |
| Select rows + bulk action | Apply action to multiple contracts |
| Click export | Download filtered results |
| Sort column header | Sort table by column |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/contracts/ | GET | List contracts (paginated) |
| /api/v1/contracts/export/ | GET | Export filtered contracts |
| /api/v1/clients/ | GET | Client dropdown options |

---

## 4. Contracts — Detail View

### Page Name
Contract Detail

### Layout Description
Two-column layout. Left column (60%) shows contract information in tabbed sections. Right column (40%) shows AI extraction results and timeline.

### Components Used
- BreadcrumbNav
- TabGroup (Overview, Obligations, Billing, Documents, History)
- ContractInfoPanel
- AIExtractionPanel with confidence badges
- TimelineWidget (contract events)
- DocumentViewer (PDF preview)
- EditButton / ApproveButton
- ComplianceChecklist

### Data Displayed
- Full contract metadata (all extracted fields)
- AI extraction confidence scores per field
- Performance obligations list with status
- Billing schedule
- Attached documents
- Audit history / changelog
- ASC 606 compliance checklist

### User Interactions
| Action | Behavior |
|--------|----------|
| Edit field | Inline edit with save/cancel |
| Approve extraction | Mark AI extraction as verified |
| Override extraction | Manually correct AI result |
| Switch tabs | Show different contract sections |
| Download document | Download original PDF |
| Run compliance check | Trigger ASC 606 check task |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/contracts/{id}/ | GET | Contract details |
| /api/v1/contracts/{id}/ | PATCH | Update contract fields |
| /api/v1/contracts/{id}/obligations/ | GET | Performance obligations |
| /api/v1/contracts/{id}/compliance/ | GET | Compliance status |
| /api/v1/contracts/{id}/documents/ | GET | Attached documents |
| /api/v1/contracts/{id}/history/ | GET | Audit history |

---

## 5. Contracts — Upload

### Page Name
Contract Upload

### Layout Description
Modal overlay with step wizard (3 steps): Upload, Review Extraction, Confirm.

### Components Used
- StepWizard (3 steps)
- DragDropUploader
- FilePreview
- ProgressBar (OCR processing)
- ExtractionResultsForm (editable)
- ConfidenceBadge per field
- ConfirmButton / RejectButton

### Data Displayed
- Upload progress indicator
- OCR processing status
- Extracted fields with confidence scores
- Highlighted low-confidence fields
- Document preview alongside extraction

### User Interactions
| Action | Behavior |
|--------|----------|
| Drag/drop file | Upload document |
| Click browse | Open file picker |
| Wait for processing | Show progress bar during OCR |
| Edit extracted fields | Correct AI extraction |
| Confirm extraction | Save contract to database |
| Reject extraction | Send to manual review queue |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/contracts/upload/ | POST | Upload document |
| /api/v1/contracts/{id}/parse/ | POST | Trigger OCR + extraction |
| /api/v1/contracts/{id}/extraction/ | GET | Get extraction results |
| /api/v1/contracts/{id}/confirm/ | POST | Confirm and save |

---

## 6. Billing & Invoices — List View

### Page Name
Invoices List

### Layout Description
Table view with summary metric cards at top (Total Invoiced, Paid, Overdue, Draft). Filter bar below metrics. Full-width data table.

### Components Used
- MetricCard (4 summary cards)
- FilterBar (status, client, date range, amount range)
- DataTable with sortable columns
- StatusBadge (Draft, Sent, Paid, Overdue, Cancelled)
- BulkActionToolbar
- Pagination
- QuickActions dropdown per row

### Data Displayed
| Column | Description |
|--------|-------------|
| Invoice # | Unique invoice number |
| Client | Client name |
| Amount | Invoice total |
| Issue Date | Date issued |
| Due Date | Payment due date |
| Status | Current status |
| Days Outstanding | Days since issue |
| Payment Date | Date paid (if applicable) |

### User Interactions
| Action | Behavior |
|--------|----------|
| Click "Generate Invoice" | Open invoice generation modal |
| Click row | Navigate to invoice detail |
| Bulk select + "Send" | Send multiple invoices |
| Filter by status | Filter table |
| Click "Export" | Download invoice list |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/invoices/ | GET | List invoices (paginated) |
| /api/v1/invoices/summary/ | GET | Summary metrics |
| /api/v1/invoices/export/ | GET | Export data |

---

## 7. Billing & Invoices — Generate

### Page Name
Generate Invoice

### Layout Description
Multi-step form in full-page or large modal. Steps: Select Contract, Select Period, Review Line Items, Preview, Confirm.

### Components Used
- StepWizard (4 steps)
- ContractSelector (searchable dropdown)
- DateRangePicker (billing period)
- LineItemsTable (editable)
- InvoicePreview (formatted preview)
- TotalCalculation panel
- ConfirmButton

### Data Displayed
- Available contracts for invoicing
- Billable items for selected period
- Calculated totals (subtotal, tax, total)
- Invoice preview (PDF-like format)

### User Interactions
| Action | Behavior |
|--------|----------|
| Select contract | Load billable items for contract |
| Set period | Filter billable items by date |
| Edit line item | Adjust quantity/rate |
| Remove line item | Exclude from invoice |
| Preview | Show formatted invoice |
| Confirm | Generate and save invoice |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/contracts/?status=active | GET | Active contracts |
| /api/v1/billables/?contract={id}&period={range} | GET | Billable items |
| /api/v1/invoices/preview/ | POST | Preview invoice |
| /api/v1/invoices/ | POST | Create invoice |



---

## 8. Billing & Invoices — Approve

### Page Name
Invoice Approval Queue

### Layout Description
Split view with list of pending invoices on left panel and invoice detail/preview on right panel.

### Components Used
- PendingInvoiceList (left panel)
- InvoicePreviewPanel (right panel)
- ApproveButton / RejectButton
- RejectionReasonModal
- ApprovalHistoryTimeline
- NotesInput

### Data Displayed
- List of invoices pending approval
- Selected invoice full detail
- Approval workflow status
- Previous approver notes
- Invoice line items and totals

### User Interactions
| Action | Behavior |
|--------|----------|
| Select invoice from list | Show detail in right panel |
| Click Approve | Approve and move to next status |
| Click Reject | Open rejection reason modal |
| Add note | Attach note to approval |
| Bulk approve | Approve multiple selected invoices |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/invoices/?status=pending_approval | GET | Pending invoices |
| /api/v1/invoices/{id}/ | GET | Invoice detail |
| /api/v1/invoices/{id}/approve/ | POST | Approve invoice |
| /api/v1/invoices/{id}/reject/ | POST | Reject invoice |

---

## 9. Billables — Timesheets

### Page Name
Timesheet Management

### Layout Description
Calendar-style weekly view at top with daily hour entry. Summary table below showing submitted timesheets. Filter bar for team/client/project.

### Components Used
- WeeklyCalendarGrid
- HourEntryCell (per day per project)
- ProjectSelector
- TeamMemberFilter
- SubmitButton
- ApprovalStatusBadge
- WeekNavigator (prev/next week)
- SummaryTable

### Data Displayed
- Hours logged per day per project
- Weekly totals per project
- Submission status (Draft, Submitted, Approved)
- Team member timesheets (for managers)
- Billable vs non-billable breakdown

### User Interactions
| Action | Behavior |
|--------|----------|
| Click cell | Enter hours for day/project |
| Submit week | Submit timesheet for approval |
| Navigate weeks | View previous/next weeks |
| Filter by team member | Show specific person's timesheet |
| Approve timesheet | Manager approves submitted time |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/timesheets/?week={date} | GET | Get timesheet for week |
| /api/v1/timesheets/ | POST | Create/update timesheet entry |
| /api/v1/timesheets/{id}/submit/ | POST | Submit for approval |
| /api/v1/timesheets/{id}/approve/ | POST | Approve timesheet |
| /api/v1/projects/ | GET | Available projects |

---

## 10. Billables — Milestones

### Page Name
Milestone Tracking

### Layout Description
Kanban-style board with columns for milestone stages (Not Started, In Progress, Completed, Invoiced). Cards represent individual milestones.

### Components Used
- KanbanBoard (4 columns)
- MilestoneCard (draggable)
- MilestoneDetailModal
- ProgressBar (percentage complete)
- FilterBar (client, contract, due date)
- AddMilestoneButton
- TimelineView toggle

### Data Displayed
- Milestone name and description
- Associated contract and client
- Due date and completion percentage
- Milestone value (billable amount)
- Assignee
- Days until due / days overdue

### User Interactions
| Action | Behavior |
|--------|----------|
| Drag card to column | Update milestone status |
| Click card | Open milestone detail modal |
| Click "Add Milestone" | Create new milestone |
| Toggle view | Switch between Kanban and Timeline |
| Filter | Filter milestones by criteria |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/milestones/ | GET | List milestones |
| /api/v1/milestones/ | POST | Create milestone |
| /api/v1/milestones/{id}/ | PATCH | Update milestone status |
| /api/v1/milestones/{id}/ | GET | Milestone details |

---

## 11. Revenue Recognition — Schedule

### Page Name
Revenue Recognition Schedule

### Layout Description
Top section shows summary metrics (Total Recognized, Deferred, Backlog). Main content is a matrix table showing recognition schedule by month (columns) and contract (rows).

### Components Used
- MetricCard (Recognized, Deferred, Backlog)
- RecognitionMatrixTable
- MonthSelector (fiscal year navigation)
- ContractFilter
- RecognitionMethodBadge (point-in-time, over-time)
- ExportButton
- ComplianceIndicator

### Data Displayed
| Element | Description |
|---------|-------------|
| Monthly recognition amounts | Per contract per month |
| Recognition method | Over-time or point-in-time |
| Cumulative recognized | Running total |
| Remaining obligation | Unrecognized amount |
| Compliance status | ASC 606 compliance flag |
| Adjustments | Manual adjustments applied |

### User Interactions
| Action | Behavior |
|--------|----------|
| Navigate months | Scroll through fiscal year |
| Click cell | View recognition detail |
| Apply filter | Filter by contract/client |
| Export | Download schedule as Excel |
| Click compliance flag | View compliance details |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/revenue/schedule/ | GET | Recognition schedule data |
| /api/v1/revenue/summary/ | GET | Summary metrics |
| /api/v1/revenue/schedule/export/ | GET | Export schedule |
| /api/v1/revenue/{id}/detail/ | GET | Line item detail |

---

## 12. Revenue Recognition — Compliance

### Page Name
ASC 606 Compliance Dashboard

### Layout Description
Compliance overview with status cards at top, checklist table in middle, and issue resolution panel at bottom.

### Components Used
- ComplianceScoreCard (overall percentage)
- StepChecklist (5 ASC 606 steps)
- IssueTable (non-compliant items)
- ResolutionPanel
- AuditTrailTimeline
- RunComplianceCheckButton

### Data Displayed
- Overall compliance score
- Per-contract compliance status
- ASC 606 five-step model checklist per contract
- Non-compliant items with severity
- Recommended remediation steps
- Last compliance check timestamp

### User Interactions
| Action | Behavior |
|--------|----------|
| Run compliance check | Trigger compliance analysis task |
| Click issue | Expand issue details and remediation |
| Mark resolved | Update issue status |
| View audit trail | Show compliance history |
| Export report | Download compliance report |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/revenue/compliance/ | GET | Compliance overview |
| /api/v1/revenue/compliance/check/ | POST | Run compliance check |
| /api/v1/revenue/compliance/issues/ | GET | List issues |
| /api/v1/revenue/compliance/issues/{id}/resolve/ | POST | Resolve issue |

---

## 13. Client Profitability — Analysis

### Page Name
Client Profitability Analysis

### Layout Description
Top row with filter controls. Second row with 4 KPI cards. Main area split between a profitability chart (left 60%) and client ranking table (right 40%).

### Components Used
- ClientFilter / DateRangePicker
- KPICard (Avg Margin, Best Client, Worst Client, At-Risk Count)
- WaterfallChart (revenue to profit breakdown)
- ScatterPlot (revenue vs margin by client)
- ClientRankingTable
- DrillDownModal

### Data Displayed
- Revenue per client
- Direct costs per client
- Gross margin and percentage
- Overhead allocation
- Net margin
- Margin trend (vs previous period)
- Cost breakdown (labor, tools, travel, other)

### User Interactions
| Action | Behavior |
|--------|----------|
| Select client | Show detailed profitability breakdown |
| Change period | Recalculate for selected timeframe |
| Click chart point | Drill into client detail |
| Sort ranking table | Rank clients by metric |
| Export analysis | Download profitability report |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/profitability/analysis/ | GET | Profitability data |
| /api/v1/profitability/clients/ | GET | Client rankings |
| /api/v1/profitability/clients/{id}/ | GET | Client detail |
| /api/v1/profitability/export/ | GET | Export report |

---

## 14. Client Profitability — Benchmark

### Page Name
Client Benchmarking

### Layout Description
Comparison view with benchmark criteria selector at top. Main content shows radar charts and comparison tables.

### Components Used
- BenchmarkCriteriaSelector
- RadarChart (multi-client comparison)
- ComparisonTable
- IndustryBenchmarkOverlay
- ClientMultiSelect (up to 5 clients)
- PeriodSelector
- RecommendationPanel

### Data Displayed
- Client metrics vs organization average
- Client metrics vs industry benchmarks
- Peer comparison (similar-sized clients)
- Performance dimensions (revenue, margin, growth, efficiency, risk)
- AI recommendations per client

### User Interactions
| Action | Behavior |
|--------|----------|
| Select clients to compare | Update radar and comparison |
| Toggle industry benchmark | Show/hide industry overlay |
| Click recommendation | View detailed recommendation |
| Change period | Update benchmark calculations |
| Export | Download benchmark report |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/profitability/benchmark/ | GET | Benchmark data |
| /api/v1/profitability/benchmark/compare/ | POST | Multi-client comparison |
| /api/v1/profitability/benchmark/industry/ | GET | Industry benchmarks |
| /api/v1/recommendations/?client_ids={ids} | GET | Recommendations |



---

## 15. Leakage Detection — Alerts

### Page Name
Leakage Alerts

### Layout Description
Summary bar at top showing total leakage amount and alert counts by severity. Main content is alert list with expandable rows. Right sidebar shows leakage trend chart.

### Components Used
- LeakageSummaryBar (total amount, critical/high/medium counts)
- AlertListTable (expandable rows)
- SeverityBadge (Critical, High, Medium, Low)
- LeakageTrendChart (line chart)
- FilterBar (severity, client, type, date)
- AlertDetailExpander
- AssignButton / ResolveButton

### Data Displayed
| Column | Description |
|--------|-------------|
| Alert ID | Unique identifier |
| Type | Leakage category |
| Client | Affected client |
| Amount | Estimated leakage value |
| Severity | Critical/High/Medium/Low |
| Detected Date | When detected |
| Status | Open/Assigned/Resolved |
| Assignee | Person responsible |

### User Interactions
| Action | Behavior |
|--------|----------|
| Expand row | Show alert details and evidence |
| Assign alert | Assign to team member |
| Resolve alert | Mark as resolved with resolution notes |
| Filter by severity | Show only selected severity |
| Click "Run Detection" | Trigger new leakage scan |
| Export | Download alerts report |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/leakage/alerts/ | GET | List alerts |
| /api/v1/leakage/alerts/summary/ | GET | Summary metrics |
| /api/v1/leakage/alerts/{id}/ | GET | Alert details |
| /api/v1/leakage/alerts/{id}/assign/ | POST | Assign alert |
| /api/v1/leakage/detect/ | POST | Trigger detection |
| /api/v1/leakage/trend/ | GET | Trend chart data |

---

## 16. Leakage Detection — Resolve

### Page Name
Resolve Leakage Alert

### Layout Description
Full-page detail view with alert information (left), evidence panel (center), and resolution form (right).

### Components Used
- AlertDetailPanel
- EvidenceViewer (data tables, calculations)
- ResolutionForm (action taken, amount recovered, notes)
- RootCauseSelector
- PreventionActionInput
- TimelineWidget (alert lifecycle)
- SubmitResolutionButton

### Data Displayed
- Alert details and detection method
- Supporting evidence (data points that triggered alert)
- Related transactions
- Historical similar alerts
- Resolution options (recover, write-off, false positive)

### User Interactions
| Action | Behavior |
|--------|----------|
| Review evidence | View data supporting the alert |
| Select root cause | Categorize the leakage cause |
| Enter recovered amount | Log amount recovered |
| Mark false positive | Dismiss alert with reason |
| Submit resolution | Close alert with resolution |
| Add prevention action | Create follow-up task |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/leakage/alerts/{id}/ | GET | Full alert detail |
| /api/v1/leakage/alerts/{id}/evidence/ | GET | Evidence data |
| /api/v1/leakage/alerts/{id}/resolve/ | POST | Submit resolution |
| /api/v1/leakage/alerts/{id}/history/ | GET | Similar alerts |

---

## 17. Collections — Aging Report

### Page Name
Collections Aging

### Layout Description
Stacked bar chart at top showing aging buckets. Summary cards below. Main content is aging detail table grouped by client.

### Components Used
- AgingBucketChart (stacked bar: Current, 1-30, 31-60, 61-90, 90+)
- SummaryCards (Total Outstanding, Overdue, DSO, Collection Rate)
- AgingTable (grouped by client, expandable)
- ClientFilter / AmountRangeFilter
- DunningActionButton
- ExportButton

### Data Displayed
| Bucket | Description |
|--------|-------------|
| Current | Not yet due |
| 1–30 days | 1 to 30 days past due |
| 31–60 days | 31 to 60 days past due |
| 61–90 days | 61 to 90 days past due |
| 90+ days | More than 90 days past due |

Per client: invoice breakdown, total outstanding, last payment date, contact info.

### User Interactions
| Action | Behavior |
|--------|----------|
| Click bucket in chart | Filter table to that bucket |
| Expand client row | Show individual invoices |
| Click "Send Reminder" | Trigger dunning reminder |
| Export report | Download aging report |
| Click client name | Navigate to client profile |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/collections/aging/ | GET | Aging report data |
| /api/v1/collections/aging/summary/ | GET | Summary metrics |
| /api/v1/collections/dunning/{invoice_id}/ | POST | Send reminder |
| /api/v1/collections/aging/export/ | GET | Export report |

---

## 18. Collections — Forecast

### Page Name
Cash Collection Forecast

### Layout Description
Line chart showing projected cash inflows over next 90 days. Below, a table with expected payments by week. Scenario selector allows optimistic/base/pessimistic views.

### Components Used
- CashForecastLineChart (3 scenarios)
- ScenarioSelector (Optimistic, Base, Pessimistic)
- WeeklyForecastTable
- AssumptionsPanel (payment probability assumptions)
- RefreshForecastButton
- DateRangeSelector (30/60/90 day horizon)

### Data Displayed
- Projected cash inflows by week
- Probability-weighted expected payments
- Scenario comparison (optimistic vs base vs pessimistic)
- Historical accuracy of past forecasts
- Key assumptions used

### User Interactions
| Action | Behavior |
|--------|----------|
| Select scenario | Update chart to show selected scenario |
| Change horizon | Adjust forecast period |
| Refresh forecast | Regenerate forecast with latest data |
| Hover chart | Show weekly detail tooltip |
| Export | Download forecast data |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/collections/forecast/ | GET | Forecast data |
| /api/v1/collections/forecast/generate/ | POST | Regenerate forecast |
| /api/v1/collections/forecast/accuracy/ | GET | Historical accuracy |

---

## 19. Reports — Generate

### Page Name
Report Generator

### Layout Description
Form-based layout with report type selector, parameter inputs, and preview panel. Available report templates shown as cards.

### Components Used
- ReportTemplateCards (grid of available reports)
- ParameterForm (dynamic based on report type)
- DateRangePicker
- ClientMultiSelect
- FormatSelector (PDF, Excel, CSV)
- PreviewButton
- GenerateButton
- ReportPreviewPanel

### Data Displayed
- Available report templates with descriptions
- Report parameters (varies by type)
- Preview of report output
- Generation progress indicator
- Recent generated reports list

### Report Types Available
- Revenue Recognition Summary
- Client Profitability Report
- Leakage Detection Summary
- Collections Aging Report
- Cash Forecast Report
- Contract Status Report
- Compliance Audit Report
- Executive Dashboard Report

### User Interactions
| Action | Behavior |
|--------|----------|
| Select report template | Load parameter form |
| Set parameters | Configure report scope |
| Click Preview | Show report preview |
| Click Generate | Generate final report |
| Download | Download generated report |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/reports/templates/ | GET | Available templates |
| /api/v1/reports/preview/ | POST | Preview report |
| /api/v1/reports/generate/ | POST | Generate report |
| /api/v1/reports/{id}/download/ | GET | Download report |

---

## 20. Reports — Schedule

### Page Name
Report Scheduling

### Layout Description
Table of scheduled reports with add/edit capability. Each row shows schedule details and next run time.

### Components Used
- ScheduledReportsTable
- AddScheduleButton
- ScheduleForm (report type, frequency, recipients, format)
- CronExpressionBuilder (visual)
- RecipientMultiSelect
- ToggleSwitch (active/paused)
- RunHistoryModal

### Data Displayed
| Column | Description |
|--------|-------------|
| Report Name | Template name |
| Frequency | Daily/Weekly/Monthly/Quarterly |
| Next Run | Next scheduled execution |
| Recipients | Email recipients list |
| Format | Output format |
| Status | Active/Paused |
| Last Run | Last execution result |

### User Interactions
| Action | Behavior |
|--------|----------|
| Add schedule | Open schedule creation form |
| Edit schedule | Modify existing schedule |
| Toggle active | Pause/resume schedule |
| View history | Show past executions |
| Run now | Execute report immediately |
| Delete schedule | Remove scheduled report |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/reports/schedules/ | GET | List schedules |
| /api/v1/reports/schedules/ | POST | Create schedule |
| /api/v1/reports/schedules/{id}/ | PATCH | Update schedule |
| /api/v1/reports/schedules/{id}/ | DELETE | Delete schedule |
| /api/v1/reports/schedules/{id}/run/ | POST | Run immediately |
| /api/v1/reports/schedules/{id}/history/ | GET | Execution history |

---

## 21. Alerts — List

### Page Name
Alerts Center

### Layout Description
Notification-center style layout with filter tabs at top (All, Critical, Unread, Resolved). Alert cards in a scrollable list with action buttons.

### Components Used
- FilterTabs (All, Critical, High, Medium, Resolved)
- AlertCard (icon, title, message, timestamp, actions)
- MarkReadButton
- BulkActionToolbar
- AlertDetailModal
- Pagination / InfiniteScroll

### Data Displayed
- Alert title and description
- Severity level with color coding
- Timestamp (relative and absolute)
- Source module (Leakage, Compliance, Collections, etc.)
- Read/unread status
- Related entity link

### User Interactions
| Action | Behavior |
|--------|----------|
| Click alert | Open detail modal |
| Mark as read | Update read status |
| Resolve alert | Mark as resolved |
| Filter by tab | Show filtered alerts |
| Bulk mark read | Mark multiple as read |
| Click related link | Navigate to source entity |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/alerts/ | GET | List alerts (paginated) |
| /api/v1/alerts/{id}/read/ | POST | Mark as read |
| /api/v1/alerts/{id}/resolve/ | POST | Resolve alert |
| /api/v1/alerts/bulk-read/ | POST | Bulk mark read |

---

## 22. Alerts — Rules

### Page Name
Alert Rules Configuration

### Layout Description
Table of configured alert rules with add/edit forms. Each rule defines conditions that trigger alerts.

### Components Used
- RulesTable (list of configured rules)
- AddRuleButton
- RuleBuilderForm (condition builder)
- ConditionGroup (AND/OR logic)
- ThresholdInput
- RecipientSelector
- ChannelSelector (email, in-app, webhook)
- ToggleSwitch (enabled/disabled)

### Data Displayed
| Column | Description |
|--------|-------------|
| Rule Name | Descriptive name |
| Module | Source module |
| Condition | Trigger condition summary |
| Severity | Alert severity level |
| Recipients | Who receives the alert |
| Channels | Notification channels |
| Status | Enabled/Disabled |
| Last Triggered | Most recent trigger |

### User Interactions
| Action | Behavior |
|--------|----------|
| Add rule | Open rule builder form |
| Edit rule | Modify existing rule |
| Toggle rule | Enable/disable rule |
| Delete rule | Remove rule |
| Test rule | Run rule against current data |
| Clone rule | Duplicate for modification |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/alerts/rules/ | GET | List rules |
| /api/v1/alerts/rules/ | POST | Create rule |
| /api/v1/alerts/rules/{id}/ | PATCH | Update rule |
| /api/v1/alerts/rules/{id}/ | DELETE | Delete rule |
| /api/v1/alerts/rules/{id}/test/ | POST | Test rule |

---

## 23. Settings — Organization

### Page Name
Organization Settings

### Layout Description
Form-based settings page with sections: General Info, Fiscal Year, Currency, Branding, Subscription.

### Components Used
- SettingsForm
- LogoUploader
- CurrencySelector
- FiscalYearConfig (start month)
- TimezoneSelector
- SaveButton
- BrandColorPicker

### Data Displayed
- Organization name and details
- Logo and branding
- Default currency and locale
- Fiscal year configuration
- Timezone setting
- Subscription plan and usage

### User Interactions
| Action | Behavior |
|--------|----------|
| Edit fields | Update organization info |
| Upload logo | Change organization logo |
| Set fiscal year | Configure fiscal year start |
| Change currency | Update default currency |
| Save | Persist settings changes |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/settings/organization/ | GET | Get settings |
| /api/v1/settings/organization/ | PATCH | Update settings |
| /api/v1/settings/organization/logo/ | POST | Upload logo |

---

## 24. Settings — Users

### Page Name
User Management

### Layout Description
User list table with invite button. User detail panel shows role assignment and permissions.

### Components Used
- UsersTable (name, email, role, status, last active)
- InviteUserButton
- InviteModal (email, role selection)
- UserDetailPanel
- RoleSelector
- PermissionsChecklist
- DeactivateButton
- ResetPasswordButton

### Data Displayed
- User list with status
- Role assignments
- Last active timestamp
- Pending invitations
- Permission details per user

### User Interactions
| Action | Behavior |
|--------|----------|
| Invite user | Send invitation email |
| Change role | Update user role |
| Deactivate user | Disable account |
| Reset password | Trigger password reset |
| View permissions | Show role permissions |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/settings/users/ | GET | List users |
| /api/v1/settings/users/invite/ | POST | Send invite |
| /api/v1/settings/users/{id}/ | PATCH | Update user |
| /api/v1/settings/users/{id}/deactivate/ | POST | Deactivate |
| /api/v1/settings/users/{id}/reset-password/ | POST | Reset password |

---

## 25. Settings — Integrations

### Page Name
Integration Settings

### Layout Description
Grid of integration cards showing available and connected services. Each card shows connection status and configure button.

### Components Used
- IntegrationCard (logo, name, status, configure button)
- ConnectButton / DisconnectButton
- ConfigurationModal (per integration)
- WebhookURLInput
- TestConnectionButton
- SyncStatusIndicator

### Available Integrations
- Accounting: QuickBooks, Xero, Tally
- CRM: Salesforce, HubSpot
- HRMS: BambooHR, Darwinbox
- Communication: Slack, Microsoft Teams
- Storage: Google Drive, OneDrive
- Payment: Razorpay, Stripe

### User Interactions
| Action | Behavior |
|--------|----------|
| Connect integration | Initiate OAuth flow |
| Configure | Open integration settings |
| Test connection | Verify connectivity |
| Disconnect | Remove integration |
| View sync status | Show last sync details |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/settings/integrations/ | GET | List integrations |
| /api/v1/settings/integrations/{id}/connect/ | POST | Connect |
| /api/v1/settings/integrations/{id}/disconnect/ | POST | Disconnect |
| /api/v1/settings/integrations/{id}/test/ | POST | Test connection |
| /api/v1/settings/integrations/{id}/sync/ | POST | Trigger sync |

---

## 26. Settings — Notifications

### Page Name
Notification Preferences

### Layout Description
Table/form layout with notification types as rows and channels as columns. Users toggle which notifications they receive via which channel.

### Components Used
- NotificationPreferencesMatrix
- ChannelToggle (Email, In-App, Slack)
- DigestFrequencySelector (Instant, Daily, Weekly)
- QuietHoursConfig
- SavePreferencesButton
- TestNotificationButton

### Data Displayed
| Category | Notification Types |
|----------|-------------------|
| Contracts | New, Expiring, Compliance Issue |
| Invoices | Generated, Overdue, Paid |
| Leakage | New Alert, Resolved, Weekly Summary |
| Collections | Payment Received, Overdue, Dunning Sent |
| System | Scheduled Reports Ready, Integration Errors |

### User Interactions
| Action | Behavior |
|--------|----------|
| Toggle channel | Enable/disable notification channel |
| Set digest frequency | Choose notification batching |
| Set quiet hours | Configure do-not-disturb period |
| Test notification | Send test notification |
| Save | Persist preferences |

### API Calls
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /api/v1/settings/notifications/ | GET | Get preferences |
| /api/v1/settings/notifications/ | PATCH | Update preferences |
| /api/v1/settings/notifications/test/ | POST | Send test |
