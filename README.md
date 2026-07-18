# RevRecog AI + ClientMargin360

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://djangoproject.com)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-3178c6.svg)](https://typescriptlang.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-2088FF.svg)](https://github.com/features/actions)

**RevRecog AI** is an intelligent revenue recognition engine that automates ASC 606 / IFRS 15 compliance for B2B service companies. **ClientMargin360** provides real-time client profitability analytics, margin tracking, and leakage detection powered by AI.

Built for Denave's P&L optimization workflow as part of the Finmark.ai platform.

---

## Features

### RevRecog AI
- **Automated Revenue Recognition** — AI-driven classification of revenue streams per ASC 606 five-step model
- **Contract Intelligence** — NLP-powered contract parsing to extract performance obligations, transaction prices, and variable consideration
- **Multi-Period Allocation** — Automatic allocation of revenue across reporting periods based on standalone selling prices
- **Milestone & Percentage-of-Completion** — Support for output and input methods with real-time progress tracking
- **Audit Trail** — Complete history of recognition events with reversal capability
- **Compliance Reporting** — Auto-generated disclosures for ASC 606 / IFRS 15 requirements

### ClientMargin360
- **Real-Time Profitability Dashboard** — Per-client, per-project, and per-service-line margin visibility
- **Revenue Leakage Detection** — AI identifies unbilled work, scope creep, rate erosion, and contract non-compliance
- **Predictive Margin Analytics** — ML models forecast margin trends and flag at-risk accounts
- **Collections Intelligence** — Aging analysis with AI-powered collection priority scoring
- **Cost Attribution Engine** — Multi-dimensional cost allocation (direct, indirect, shared services)
- **Custom Reporting** — PDF/Excel export with scheduled distribution

---

## Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Framework | Django 4.2 + Django REST Framework |
| Database | PostgreSQL 15 |
| Cache/Queue | Redis 7 |
| Task Queue | Celery 5.3 + Celery Beat |
| AI/ML | OpenAI GPT-4, LangChain, spaCy, scikit-learn |
| Vector Store | ChromaDB |
| Document Processing | PyPDF2, Tesseract OCR, pdf2image |
| Report Generation | ReportLab, WeasyPrint |
| API Documentation | drf-spectacular (OpenAPI 3.0) |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 18 + TypeScript |
| Build Tool | Vite 5 |
| Routing | React Router v6 |
| State Management | Zustand |
| Data Fetching | TanStack React Query |
| UI Components | Headless UI + Heroicons |
| Styling | Tailwind CSS 3.4 |
| Charts | Recharts |
| Forms | React Hook Form + Zod |
| Tables | TanStack React Table |

### Infrastructure
| Component | Technology |
|-----------|-----------|
| Cloud | AWS (ECS, RDS, ElastiCache, S3, CloudFront) |
| CI/CD | GitHub Actions |
| Containerization | Docker + Docker Compose |
| Monitoring | CloudWatch, Flower (Celery) |

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### 1. Clone the Repository
```bash
git clone https://github.com/finmark-ai/revrecog-clientmargin360.git
cd revrecog-clientmargin360
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Configure your environment variables
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 3. Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

### 4. Start Background Services
```bash
# Terminal 1: Celery Worker
celery -A config worker -l info

# Terminal 2: Celery Beat (Scheduled Tasks)
celery -A config beat -l info

# Terminal 3: Flower (Task Monitoring)
celery -A config flower
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React/TS)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ RevRecog │ │ Margin   │ │ Leakage  │ │ Collections      │   │
│  │ Dashboard│ │ Analytics│ │ Detector │ │ Intelligence     │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
└─────────────────────────────┬───────────────────────────────────┘
                              │ REST API (JWT Auth)
┌─────────────────────────────┴───────────────────────────────────┐
│                     Backend (Django/DRF)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │Contracts │ │ Billing  │ │Recognition│ │ Profitability    │   │
│  │ Service  │ │ Service  │ │  Engine   │ │ Engine           │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐   │
│  │ AI/ML    │ │ Leakage  │ │Collections│ │ Reports &        │   │
│  │ Engine   │ │ Detector │ │ Manager   │ │ Analytics        │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘   │
└──────┬──────────────┬──────────────┬────────────────────────────┘
       │              │              │
┌──────┴──────┐ ┌────┴────┐ ┌──────┴──────┐
│ PostgreSQL  │ │  Redis  │ │  ChromaDB   │
│  (Primary)  │ │ (Cache) │ │  (Vectors)  │
└─────────────┘ └─────────┘ └─────────────┘
```

---

## Development Setup

### Environment Variables
Create a `.env` file in the backend directory:
```env
DJANGO_SETTINGS_MODULE=config.settings.development
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgres://user:pass@localhost:5432/revrecog_db
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=your-openai-key
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
```

### Running Tests
```bash
# Backend
cd backend
pytest --cov=apps --cov-report=html

# Frontend
cd frontend
npm run test
npm run test:coverage
```

### Code Quality
```bash
# Backend
flake8 .
black --check .
isort --check .

# Frontend
npm run lint
npm run type-check
```

---

## Deployment Guide

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### AWS ECS Deployment
1. Build and push Docker images to ECR
2. Update ECS task definitions
3. Deploy via GitHub Actions CI/CD pipeline

### Environment Requirements (Production)
- AWS ECS Fargate (Backend)
- AWS RDS PostgreSQL 15 (Database)
- AWS ElastiCache Redis 7 (Cache/Queue)
- AWS S3 + CloudFront (Static/Media)
- AWS ALB (Load Balancer)

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the coding standards:
   - Backend: PEP 8, Black formatting, type hints
   - Frontend: ESLint + Prettier, TypeScript strict mode
4. Write tests for new features (minimum 80% coverage)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Commit Convention
We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` — New feature
- `fix:` — Bug fix
- `docs:` — Documentation
- `refactor:` — Code refactoring
- `test:` — Adding tests
- `chore:` — Maintenance

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2024 Finmark.ai

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
