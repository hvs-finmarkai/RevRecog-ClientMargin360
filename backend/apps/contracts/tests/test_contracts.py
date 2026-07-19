from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.clients.models import Client
from apps.contracts.models import Contract
from apps.users.models import Organization

User = get_user_model()


class ContractTestMixin:
    def create_fixtures(self):
        self.org = Organization.objects.create(
            name='Test Org',
            domain='testorg.com',
        )
        self.user = User.objects.create_user(
            email='contracts@finmark.ai',
            password='TestPass123!',
            first_name='Contract',
            last_name='Tester',
            organization=self.org,
        )
        self.client_obj = Client.objects.create(
            organization=self.org,
            name='Acme Corp',
            industry='technology',
            status='active',
        )

    def authenticate(self):
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(token.access_token)}')

    def create_contract(self, **kwargs):
        defaults = {
            'organization': self.org,
            'client': self.client_obj,
            'contract_number': f'CTR-{Contract.objects.count() + 1:04d}',
            'title': 'Test Contract',
            'billing_model': 'fixed_price',
            'total_value': Decimal('5000000.00'),
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=365),
            'status': 'active',
        }
        defaults.update(kwargs)
        return Contract.objects.create(**defaults)


class ContractCreateTests(ContractTestMixin, APITestCase):
    def setUp(self):
        self.create_fixtures()
        self.authenticate()
        self.url = '/api/v1/contracts/contracts/'

    def test_create_contract(self):
        payload = {
            'client': str(self.client_obj.id),
            'title': 'New Contract',
            'billing_model': 'time_and_material',
            'total_value': '3000000.00',
            'start_date': str(date.today()),
            'end_date': str(date.today() + timedelta(days=180)),
            'status': 'draft',
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ContractListTests(ContractTestMixin, APITestCase):
    def setUp(self):
        self.create_fixtures()
        self.authenticate()
        self.url = '/api/v1/contracts/contracts/'

    def test_list_contracts(self):
        self.create_contract(contract_number='CTR-0001')
        self.create_contract(contract_number='CTR-0002')
        self.create_contract(contract_number='CTR-0003')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        if isinstance(results, list):
            self.assertEqual(len(results), 3)
        else:
            self.assertEqual(results['count'], 3)

    def test_contract_detail(self):
        contract = self.create_contract(contract_number='CTR-DETAIL-001')
        detail_url = f'{self.url}{contract.id}/'
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['contract_number'], 'CTR-DETAIL-001')

    def test_contract_filter_by_status(self):
        self.create_contract(contract_number='CTR-ACTIVE-1', status='active')
        self.create_contract(contract_number='CTR-ACTIVE-2', status='active')
        self.create_contract(contract_number='CTR-EXPIRED-1', status='expired')
        response = self.client.get(self.url, {'status': 'active'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data.get('results', response.data)
        if isinstance(results, list):
            self.assertTrue(all(c['status'] == 'active' for c in results))
        else:
            self.assertTrue(all(c['status'] == 'active' for c in results))


class ContractAuthTests(ContractTestMixin, APITestCase):
    def setUp(self):
        self.create_fixtures()
        self.url = '/api/v1/contracts/contracts/'

    def test_unauthenticated_access(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
