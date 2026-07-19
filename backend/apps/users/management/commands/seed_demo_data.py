from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.users.models import Organization, Role, User
from apps.clients.models import Client
from apps.contracts.models import Contract
from apps.billing.models import RateCard, RateCardItem, BillingPeriod
from apps.invoices.models import Invoice, InvoiceLineItem
from apps.recognition.models import RevenueSchedule, RevenueEntry
from apps.leakage.models import LeakageDetection
from apps.profitability.models import ProfitabilitySnapshot, MarginCalculation
from apps.ai_engine.models import AIRecommendation
from apps.collections_mgmt.models import Receivable, AgingBucket, CollectionSchedule
from apps.notifications.models import Notification


class Command(BaseCommand):
    help = "Seed demo data for Finmark.ai RevRecog AI + ClientMargin360"

    def handle(self, *args, **options):
        if Organization.objects.filter(name="Finmark.ai").exists():
            self.stdout.write(self.style.WARNING("Demo data already exists. Skipping."))
            return

        with transaction.atomic():
            org = self._create_organization()
            roles = self._create_roles(org)
            users = self._create_users(org, roles)
            clients = self._create_clients(org)
            contracts = self._create_contracts(org, clients)
            self._create_rate_cards(clients, contracts)
            billing_periods = self._create_billing_periods(contracts)
            invoices = self._create_invoices(org, clients, contracts)
            self._create_revenue_schedules_and_entries(contracts)
            self._create_leakage_detections(org, clients, contracts)
            self._create_profitability_snapshots(clients)
            self._create_margin_calculations(clients, contracts)
            self._create_ai_recommendations(clients, contracts)
            self._create_receivables_and_aging(org, clients, invoices)
            self._create_notifications(org, users)
            self._create_collection_schedules(clients, users)

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))

    def _create_organization(self):
        self.stdout.write("Creating organization...")
        org = Organization.objects.create(
            name="Finmark.ai",
            domain="finmark.ai",
            subscription_plan="enterprise",
            is_active=True,
            address="Plot 58, Sector 44, Gurgaon, Haryana 122003",
            phone="+919876543210",
            tax_id="07AABCD1234E1Z5",
            timezone="Asia/Kolkata",
            currency="INR",
        )
        return org

    def _create_roles(self, org):
        self.stdout.write("Creating roles...")
        role_data = [
            ("Admin", "Full system access", True),
            ("Finance Manager", "Financial operations and reporting", True),
            ("Accounts Executive", "Invoice and billing management", True),
            ("Operations Head", "Operations oversight and contract management", True),
            ("Client Partner", "Client relationship management", True),
        ]
        roles = {}
        for name, desc, is_system in role_data:
            roles[name] = Role.objects.create(
                name=name,
                description=desc,
                organization=org,
                is_system_role=is_system,
            )
        return roles

    def _create_users(self, org, roles):
        self.stdout.write("Creating users...")
        users_data = [
            ("admin@finmark.ai", "Rajesh", "Kumar", "Admin", True),
            ("finance@finmark.ai", "Priya", "Sharma", "Finance Manager", False),
            ("ops@finmark.ai", "Amit", "Patel", "Operations Head", False),
        ]
        users = []
        for email, first, last, role_name, is_staff in users_data:
            user = User.objects.create_user(
                email=email,
                password="Demo@12345",
                first_name=first,
                last_name=last,
                organization=org,
                role=roles[role_name],
                is_staff=is_staff,
                is_active=True,
            )
            users.append(user)
        return users

    def _create_clients(self, org):
        self.stdout.write("Creating clients...")
        clients_data = [
            ("Bharti Airtel Ltd", "telecom", "net_30", "Mumbai"),
            ("Reliance Jio Infocomm", "telecom", "net_45", "Mumbai"),
            ("Vodafone Idea Ltd", "telecom", "net_60", "Mumbai"),
            ("HDFC Bank Ltd", "bfsi", "net_30", "Mumbai"),
            ("ICICI Bank Ltd", "bfsi", "net_45", "Mumbai"),
            ("State Bank of India", "bfsi", "net_60", "Delhi"),
            ("Infosys Ltd", "technology", "net_30", "Bangalore"),
            ("Wipro Technologies", "technology", "net_30", "Bangalore"),
            ("Tech Mahindra Ltd", "technology", "net_45", "Pune"),
            ("HCL Technologies", "technology", "net_30", "Noida"),
            ("Hindustan Unilever", "retail", "net_30", "Mumbai"),
            ("ITC Limited", "retail", "net_45", "Kolkata"),
            ("Nestle India Ltd", "retail", "net_30", "Gurgaon"),
            ("Maruti Suzuki India", "automotive", "net_60", "Gurgaon"),
            ("Tata Motors Ltd", "automotive", "net_45", "Mumbai"),
            ("Mahindra & Mahindra", "automotive", "net_30", "Mumbai"),
            ("Bajaj Finance Ltd", "bfsi", "net_30", "Pune"),
            ("Axis Bank Ltd", "bfsi", "net_45", "Mumbai"),
        ]
        clients = []
        for name, industry, terms, city in clients_data:
            client = Client.objects.create(
                organization=org,
                name=name,
                legal_name=name,
                industry=industry,
                payment_terms=terms,
                city=city,
                state="Maharashtra" if city == "Mumbai" else "Haryana" if city == "Gurgaon" else "Karnataka" if city == "Bangalore" else "Delhi" if city == "Delhi" else "West Bengal" if city == "Kolkata" else "Maharashtra",
                country="India",
                status="active",
                credit_limit=Decimal("50000000.00"),
                risk_score=Decimal("35.00"),
                health_score=Decimal("78.00"),
            )
            clients.append(client)
        return clients

    def _create_contracts(self, org, clients):
        self.stdout.write("Creating contracts...")
        today = date.today()
        contracts_data = [
            (clients[0], "CTR-2024-001", "Airtel Field Sales Enablement", "time_and_material", Decimal("45000000.00"), Decimal("3750000.00")),
            (clients[1], "CTR-2024-002", "Jio Retail Expansion Program", "milestone", Decimal("72000000.00"), Decimal("6000000.00")),
            (clients[3], "CTR-2024-003", "HDFC Lead Generation Campaign", "retainer", Decimal("36000000.00"), Decimal("3000000.00")),
            (clients[6], "CTR-2024-004", "Infosys Campus Hiring Drive", "time_and_material", Decimal("18000000.00"), Decimal("1500000.00")),
            (clients[7], "CTR-2024-005", "Wipro Channel Partner Mgmt", "outcome_based", Decimal("54000000.00"), Decimal("4500000.00")),
            (clients[10], "CTR-2024-006", "HUL Rural Distribution Push", "hybrid", Decimal("96000000.00"), Decimal("8000000.00")),
            (clients[13], "CTR-2024-007", "Maruti Dealer Network Audit", "milestone", Decimal("24000000.00"), Decimal("2000000.00")),
            (clients[14], "CTR-2024-008", "Tata Motors EV Promotion", "retainer", Decimal("30000000.00"), Decimal("2500000.00")),
            (clients[4], "CTR-2024-009", "ICICI Cross-Sell Analytics", "time_and_material", Decimal("42000000.00"), Decimal("3500000.00")),
            (clients[16], "CTR-2024-010", "Bajaj Finance DSA Network", "hybrid", Decimal("60000000.00"), Decimal("5000000.00")),
        ]
        contracts = []
        for client, number, title, billing_model, total, monthly in contracts_data:
            contract = Contract.objects.create(
                organization=org,
                client=client,
                contract_number=number,
                title=title,
                billing_model=billing_model,
                currency="INR",
                total_value=total,
                monthly_value=monthly,
                start_date=today - timedelta(days=180),
                end_date=today + timedelta(days=185),
                payment_terms="net_30",
                status="active",
                asc606_compliant=True,
                signed_date=today - timedelta(days=185),
            )
            contracts.append(contract)
        return contracts

    def _create_rate_cards(self, clients, contracts):
        self.stdout.write("Creating rate cards...")
        today = date.today()
        tm_contracts = [c for c in contracts if c.billing_model == "time_and_material"]
        roles_rates = [
            ("Field Sales Executive", Decimal("450.00"), Decimal("3600.00"), Decimal("72000.00")),
            ("Team Lead", Decimal("750.00"), Decimal("6000.00"), Decimal("120000.00")),
            ("Regional Manager", Decimal("1200.00"), Decimal("9600.00"), Decimal("192000.00")),
            ("Data Analyst", Decimal("900.00"), Decimal("7200.00"), Decimal("144000.00")),
            ("Campaign Manager", Decimal("1050.00"), Decimal("8400.00"), Decimal("168000.00")),
        ]
        for contract in tm_contracts:
            rc = RateCard.objects.create(
                client=contract.client,
                contract=contract,
                name=f"Rate Card - {contract.client.name}",
                effective_from=today - timedelta(days=180),
                effective_to=today + timedelta(days=185),
                currency="INR",
                status="active",
            )
            for role_name, hourly, daily, monthly in roles_rates:
                RateCardItem.objects.create(
                    rate_card=rc,
                    role_name=role_name,
                    hourly_rate=hourly,
                    daily_rate=daily,
                    monthly_rate=monthly,
                    overtime_multiplier=Decimal("1.50"),
                    minimum_hours=Decimal("160.00"),
                )

    def _create_billing_periods(self, contracts):
        self.stdout.write("Creating billing periods...")
        today = date.today()
        periods = []
        for contract in contracts:
            for i in range(6):
                start = (today.replace(day=1) - timedelta(days=30 * (5 - i))).replace(day=1)
                if start.month == 12:
                    end = start.replace(year=start.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    end = start.replace(month=start.month + 1, day=1) - timedelta(days=1)
                status = "closed" if i < 5 else "open"
                bp = BillingPeriod.objects.create(
                    contract=contract,
                    period_start=start,
                    period_end=end,
                    status=status,
                    total_billable_amount=contract.monthly_value,
                )
                periods.append(bp)
        return periods

    def _create_invoices(self, org, clients, contracts):
        self.stdout.write("Creating invoices...")
        today = date.today()
        statuses = ["paid", "paid", "paid", "paid", "paid", "paid", "paid", "paid",
                    "sent", "sent", "sent", "sent", "sent",
                    "overdue", "overdue", "overdue", "overdue",
                    "draft", "draft", "draft"]
        invoices = []
        for idx in range(20):
            contract = contracts[idx % len(contracts)]
            client = contract.client
            days_back = (20 - idx) * 9
            inv_date = today - timedelta(days=days_back)
            due_date = inv_date + timedelta(days=30)
            subtotal = contract.monthly_value
            igst = subtotal * Decimal("0.18")
            total = subtotal + igst
            tds_amount = subtotal * Decimal("0.02")
            net_receivable = total - tds_amount

            inv = Invoice.objects.create(
                organization=org,
                client=client,
                contract=contract,
                invoice_number=f"INV-2024-{idx + 1:03d}",
                invoice_date=inv_date,
                due_date=due_date,
                subtotal=subtotal,
                tax_amount=igst,
                cgst=Decimal("0.00"),
                sgst=Decimal("0.00"),
                igst=igst,
                total_amount=total,
                tds_applicable=True,
                tds_rate=Decimal("2.00"),
                tds_amount=tds_amount,
                net_receivable=net_receivable,
                status=statuses[idx],
                currency="INR",
                billing_period_start=inv_date.replace(day=1),
                billing_period_end=due_date,
            )

            InvoiceLineItem.objects.create(
                invoice=inv,
                description=f"Professional services - {contract.title}",
                quantity=Decimal("1.00"),
                unit="months",
                rate=subtotal,
                amount=subtotal,
                tax_rate=Decimal("18.00"),
                tax_amount=igst,
                sort_order=1,
            )
            invoices.append(inv)
        return invoices

    def _create_revenue_schedules_and_entries(self, contracts):
        self.stdout.write("Creating revenue schedules and entries...")
        today = date.today()
        for contract in contracts:
            schedule = RevenueSchedule.objects.create(
                contract=contract,
                total_amount=contract.total_value,
                recognized_amount=contract.monthly_value * 5,
                deferred_amount=contract.total_value - (contract.monthly_value * 5),
                start_date=contract.start_date,
                end_date=contract.end_date,
                pattern="straight_line",
                status="active",
                completion_percentage=Decimal("50.00"),
            )
            for i in range(6):
                period_start = (today.replace(day=1) - timedelta(days=30 * (5 - i))).replace(day=1)
                if period_start.month == 12:
                    period_end = period_start.replace(year=period_start.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    period_end = period_start.replace(month=period_start.month + 1, day=1) - timedelta(days=1)
                RevenueEntry.objects.create(
                    schedule=schedule,
                    period_start=period_start,
                    period_end=period_end,
                    amount=contract.monthly_value,
                    entry_type="recognized",
                    status="posted",
                    posted_date=period_end,
                )

    def _create_leakage_detections(self, org, clients, contracts):
        self.stdout.write("Creating leakage detections...")
        leakages = [
            (clients[0], contracts[0], "unbilled_hours", Decimal("450000.00"), "high", "120 unbilled hours for field executives in March"),
            (clients[1], contracts[1], "missed_milestone", Decimal("1200000.00"), "critical", "Q1 milestone delivery not invoiced"),
            (clients[3], contracts[2], "rate_escalation_missed", Decimal("360000.00"), "medium", "Annual 8% rate escalation not applied since January"),
            (clients[6], contracts[3], "unbilled_hours", Decimal("225000.00"), "medium", "Weekend overtime hours not captured in billing"),
            (clients[7], contracts[4], "scope_creep", Decimal("890000.00"), "high", "Additional deliverables outside SOW not billed"),
            (clients[10], contracts[5], "unbilled_hours", Decimal("680000.00"), "high", "Rural deployment travel time not included"),
            (clients[13], contracts[6], "missed_milestone", Decimal("500000.00"), "medium", "Phase 2 audit completion not invoiced"),
            (clients[14], contracts[7], "rate_escalation_missed", Decimal("250000.00"), "low", "CPI adjustment of 5.4% pending"),
            (clients[4], contracts[8], "unbilled_hours", Decimal("315000.00"), "medium", "Analytics platform setup hours missing"),
            (clients[16], contracts[9], "scope_creep", Decimal("720000.00"), "high", "DSA training modules delivered but unbilled"),
            (clients[0], contracts[0], "billing_delay", Decimal("375000.00"), "medium", "April billing delayed by 15 days"),
            (clients[1], contracts[1], "expenses_not_billed", Decimal("185000.00"), "low", "Travel and logistics expenses pending"),
            (clients[3], contracts[2], "undercharging", Decimal("900000.00"), "high", "Below-market rates for senior resources"),
            (clients[6], contracts[3], "discount_overuse", Decimal("270000.00"), "medium", "Volume discount applied incorrectly"),
            (clients[10], contracts[5], "contract_expiry_missed", Decimal("800000.00"), "critical", "Auto-renewal window missed for premium clause"),
        ]
        for client, contract, dtype, amount, severity, desc in leakages:
            LeakageDetection.objects.create(
                organization=org,
                client=client,
                contract=contract,
                detection_type=dtype,
                amount=amount,
                description=desc,
                severity=severity,
                status="open",
            )

    def _create_profitability_snapshots(self, clients):
        self.stdout.write("Creating profitability snapshots...")
        today = date.today()
        for rank, client in enumerate(clients, 1):
            revenue = Decimal("30000000.00") + Decimal(str(rank * 1500000))
            cost = revenue * Decimal("0.65")
            margin_pct = Decimal("35.00") - Decimal(str(rank))
            ProfitabilitySnapshot.objects.create(
                client=client,
                snapshot_date=today,
                trailing_12m_revenue=revenue,
                trailing_12m_cost=cost,
                trailing_12m_margin_pct=margin_pct,
                trend_direction="improving" if rank <= 6 else "stable" if rank <= 12 else "declining",
                rank=rank,
                active_contracts=2 if rank <= 10 else 1,
                total_headcount=Decimal(str(25 - rank)),
                revenue_per_head=revenue / Decimal(str(max(25 - rank, 1))),
            )

    def _create_margin_calculations(self, clients, contracts):
        self.stdout.write("Creating margin calculations...")
        today = date.today()
        for contract in contracts:
            for i in range(6):
                period_start = (today.replace(day=1) - timedelta(days=30 * (5 - i))).replace(day=1)
                if period_start.month == 12:
                    period_end = period_start.replace(year=period_start.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    period_end = period_start.replace(month=period_start.month + 1, day=1) - timedelta(days=1)
                revenue = contract.monthly_value
                direct_costs = revenue * Decimal("0.55")
                overhead = revenue * Decimal("0.12")
                MarginCalculation.objects.create(
                    client=contract.client,
                    contract=contract,
                    period_start=period_start,
                    period_end=period_end,
                    revenue=revenue,
                    direct_costs=direct_costs,
                    allocated_overhead=overhead,
                )

    def _create_ai_recommendations(self, clients, contracts):
        self.stdout.write("Creating AI recommendations...")
        recommendations = [
            (clients[0], contracts[0], "reprice", "Reprice Airtel T&M Rates", "Market analysis shows 12% underpricing vs peers. Recommend rate revision.", Decimal("5400000.00"), Decimal("0.87")),
            (clients[3], contracts[2], "restructure", "Restructure HDFC Retainer", "Switch to performance model for 18% margin uplift.", Decimal("6480000.00"), Decimal("0.82")),
            (clients[7], contracts[4], "exit", "Exit Wipro Channel Contract", "Sustained negative margins. Recommend graceful exit.", Decimal("-2700000.00"), Decimal("0.76")),
            (clients[10], contracts[5], "reprice", "HUL Rural Premium Pricing", "Rural deployment costs justify 15% premium on current rates.", Decimal("14400000.00"), Decimal("0.91")),
            (clients[13], contracts[6], "restructure", "Maruti Milestone Optimization", "Consolidate milestones to reduce admin overhead by 20%.", Decimal("4800000.00"), Decimal("0.79")),
            (clients[1], contracts[1], "reprice", "Jio Expansion Rate Adjustment", "Volume growth justifies renegotiation at higher tier.", Decimal("8640000.00"), Decimal("0.85")),
            (clients[16], contracts[9], "restructure", "Bajaj DSA Model Redesign", "Hybrid to pure performance for better margin alignment.", Decimal("7200000.00"), Decimal("0.83")),
        ]
        for client, contract, rtype, title, desc, impact, confidence in recommendations:
            AIRecommendation.objects.create(
                client=client,
                contract=contract,
                recommendation_type=rtype,
                title=title,
                description=desc,
                expected_impact_amount=impact,
                expected_impact_pct=Decimal("12.00"),
                confidence_score=confidence,
                priority="high",
                status="pending",
                model_version="v2.1.0",
                reasoning={"factors": ["margin_trend", "market_benchmark", "client_health"]},
                action_items=["Schedule review meeting", "Prepare proposal", "Get finance approval"],
            )

    def _create_receivables_and_aging(self, org, clients, invoices):
        self.stdout.write("Creating receivables and aging data...")
        today = date.today()
        for inv in invoices:
            if inv.status in ("sent", "overdue", "partially_paid"):
                aging = (today - inv.due_date).days if today > inv.due_date else 0
                if aging <= 0:
                    status = "current"
                elif aging <= 30:
                    status = "overdue_30"
                elif aging <= 60:
                    status = "overdue_60"
                elif aging <= 90:
                    status = "overdue_90"
                else:
                    status = "overdue_90_plus"
                Receivable.objects.create(
                    invoice=inv,
                    client=inv.client,
                    amount=inv.net_receivable,
                    amount_collected=Decimal("0.00"),
                    due_date=inv.due_date,
                    status=status,
                    aging_days=max(aging, 0),
                )

        AgingBucket.objects.create(
            organization=org,
            as_of_date=today,
            current_amount=Decimal("12500000.00"),
            days_30=Decimal("8750000.00"),
            days_60=Decimal("4200000.00"),
            days_90=Decimal("2100000.00"),
            days_90_plus=Decimal("950000.00"),
            client_count=12,
            invoice_count=20,
        )

    def _create_notifications(self, org, users):
        self.stdout.write("Creating notifications...")
        admin_user = users[0]
        notifications_data = [
            ("Invoice INV-2024-014 is overdue", "Invoice for Maruti Suzuki overdue by 15 days. Amount: ₹23.6L", "warning", "invoice"),
            ("Leakage Alert: Unbilled Hours", "120 unbilled hours detected for Airtel field team.", "alert", "leakage"),
            ("Contract CTR-2024-005 expiring", "Wipro contract expires in 30 days. Renewal action needed.", "warning", "contract"),
            ("AI Recommendation: Reprice Airtel", "New pricing recommendation generated with 87% confidence.", "info", "ai_insight"),
            ("Payment Received: HDFC Bank", "Payment of ₹35.4L received against INV-2024-003.", "success", "payment"),
            ("Margin Alert: Wipro below threshold", "Net margin dropped to 8.2% - below 15% threshold.", "alert", "escalation"),
            ("New Contract Uploaded", "CTR-2024-010 for Bajaj Finance uploaded and parsed.", "info", "contract"),
            ("Collection Follow-up Due", "Vodafone Idea - ₹42L outstanding, follow-up scheduled.", "warning", "collection"),
            ("Monthly Report Ready", "June 2024 P&L and margin report generated.", "info", "system"),
            ("Approval Required: Credit Note", "Credit note CN-2024-005 for ₹3.2L pending approval.", "alert", "approval"),
        ]
        for title, message, ntype, category in notifications_data:
            Notification.objects.create(
                organization=org,
                user=admin_user,
                title=title,
                message=message,
                type=ntype,
                category=category,
                priority=3,
            )

    def _create_collection_schedules(self, clients, users):
        self.stdout.write("Creating collection schedules...")
        today = date.today()
        finance_user = users[1]
        schedules_data = [
            (clients[0], "weekly", 1, Decimal("4500000.00")),
            (clients[1], "weekly", 2, Decimal("7200000.00")),
            (clients[2], "bi_weekly", 1, Decimal("3800000.00")),
            (clients[3], "monthly", 1, Decimal("3000000.00")),
            (clients[4], "weekly", 1, Decimal("4200000.00")),
            (clients[10], "bi_weekly", 2, Decimal("9600000.00")),
            (clients[13], "weekly", 3, Decimal("2400000.00")),
            (clients[14], "monthly", 1, Decimal("3000000.00")),
        ]
        for client, freq, level, outstanding in schedules_data:
            CollectionSchedule.objects.create(
                client=client,
                frequency=freq,
                next_followup_date=today + timedelta(days=3),
                assigned_to=finance_user,
                escalation_level=level,
                total_outstanding=outstanding,
                last_contact_date=today - timedelta(days=7),
                last_contact_outcome="Promised payment by next week",
            )
