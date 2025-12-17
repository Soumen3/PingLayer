# PingLayer Backend

**Multi-tenant WhatsApp Campaign Automation & Analytics Platform**

Built with FastAPI, PostgreSQL, and Redis.

---

## 📋 Project Overview

PingLayer is a SaaS platform similar to Aisensy or WATI that allows multiple companies to:
- Register and manage their accounts
- Create bulk WhatsApp campaigns
- Track message delivery status
- Monitor smart-link clicks with analytics
- View campaign performance dashboards

### Current Phase: Phase 1 (Portfolio/Zero-Cost Version)
- ✅ Multi-tenant architecture
- ✅ JWT authentication
- ✅ Campaign management
- ✅ Smart link tracking
- ✅ Analytics foundation
- 🔄 Mock WhatsApp sending (no real API calls yet)

---

## 🏗️ Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.10+)
- **Database**: PostgreSQL
- **Cache/Queue**: Redis
- **ORM**: SQLAlchemy 2.0
- **Auth**: JWT (python-jose)
- **Validation**: Pydantic

### Design Principles
- **Modular Monolith**: Feature-based modules for scalability
- **Multi-tenant**: Complete data isolation per company
- **Production-ready**: Proper error handling, logging, rate limiting
- **Clean Architecture**: Business logic in services, thin routers

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # Settings & environment config
│   ├── database.py             # SQLAlchemy setup
│   │
│   ├── core/                   # Shared core functionality
│   │   ├── security.py         # JWT & password hashing
│   │   ├── dependencies.py     # Auth dependencies
│   │   ├── rate_limiter.py     # API rate limiting
│   │   └── logging.py          # Centralized logging
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── company.py
│   │   ├── campaign.py
│   │   ├── recipient.py
│   │   ├── message_log.py
│   │   ├── smart_link.py
│   │   ├── click_event.py
│   │   └── integration.py
│   │
│   ├── schemas/                # Pydantic schemas (TODO)
│   │
│   ├── modules/                # Feature modules
│   │   ├── auth/               # Registration & login
│   │   ├── companies/          # Company management
│   │   ├── campaigns/          # Campaign CRUD & sending
│   │   ├── smartlinks/         # Click tracking
│   │   ├── analytics/          # Metrics & aggregations
│   │   ├── whatsapp/           # WhatsApp integration (later)
│   │   └── mock_sender/        # Mock message sender
│   │
│   ├── workers/                # Background workers (TODO)
│   └── utils/                  # Utilities (TODO)
│
├── alembic/                    # Database migrations
├── tests/                      # Tests (TODO)
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Redis 6+

### Installation

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy example env file
   cp .env.example .env
   
   # Edit .env and update:
   # - DATABASE_URL (PostgreSQL connection string)
   # - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_urlsafe(32))")
   # - REDIS_URL (if not using default)
   ```

5. **Create database**
   ```bash
   # Using psql
   psql -U postgres
   CREATE DATABASE pinglayer;
   \q
   ```

6. **Initialize database tables**
   ```bash
   # Option 1: Using Python
   python -c "from app.database import init_db; init_db()"
   
   # Option 2: Using Alembic (recommended for production)
   alembic upgrade head
   ```

7. **Run the application**
   ```bash
   # Development mode (with auto-reload)
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Or using Python
   python -m app.main
   ```

8. **Access the API**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/health

---

## 🗄️ Database Models

### Core Models

1. **Company** - Multi-tenant organization
   - `id`, `name`, `slug`, `plan`, `is_active`
   - One-to-Many: Users, Campaigns, Integrations

2. **User** - Platform users
   - `id`, `email`, `hashed_password`, `company_id`, `is_admin`
   - Email is unique per company (not globally)

3. **Campaign** - WhatsApp campaigns
   - `id`, `name`, `company_id`, `status`, `message_template`
   - Status: draft, scheduled, sending, completed, failed
   - Tracks: total_recipients, sent_count, delivered_count, failed_count

4. **Recipient** - Campaign recipients
   - `id`, `campaign_id`, `phone_number`, `custom_data`
   - Unique constraint: (campaign_id, phone_number)

5. **MessageLog** - Individual message tracking
   - `id`, `campaign_id`, `recipient_id`, `status`, `whatsapp_message_id`
   - Status: pending, sent, delivered, read, failed

6. **SmartLink** - Trackable URLs
   - `id`, `campaign_id`, `short_code`, `destination_url`, `click_count`
   - Generates short URLs like: http://localhost:8000/s/abc123

7. **ClickEvent** - Click analytics
   - `id`, `smart_link_id`, `ip_address`, `user_agent`, `device_type`, `country`
   - Tracks: device, browser, OS, location

8. **Integration** - WhatsApp API credentials
   - `id`, `company_id`, `type`, `api_key`, `phone_number_id`
   - Type: whatsapp, telegram, sms

---

## 🔐 Authentication

### JWT-based Authentication

1. **Register** (TODO: implement endpoint)
   ```
   POST /api/auth/register
   {
     "email": "user@company.com",
     "password": "SecurePass123",
     "full_name": "John Doe",
     "company_name": "Acme Corp"
   }
   ```

2. **Login** (TODO: implement endpoint)
   ```
   POST /api/auth/login
   {
     "email": "user@company.com",
     "password": "SecurePass123"
   }
   
   Response:
   {
     "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "token_type": "bearer"
   }
   ```

3. **Use token in requests**
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
   ```

### Multi-tenant Security
- Every request extracts `company_id` from JWT token
- All queries automatically filter by `company_id`
- No cross-company data access possible

---

## 📊 Key Features

### ✅ Implemented
- Configuration management (Pydantic Settings)
- Database setup (SQLAlchemy + PostgreSQL)
- All ORM models with relationships
- JWT authentication & password hashing
- Multi-tenant dependencies
- Request logging & error handling
- Rate limiting (in-memory)
- Health check endpoint

### 🔄 Next Steps (To Implement)
1. **Pydantic Schemas** - Request/response validation
2. **Auth Module** - Register, login, logout endpoints
3. **Companies Module** - Company CRUD
4. **Campaigns Module** - Create, list, send campaigns
5. **Mock Sender** - Simulate WhatsApp sending
6. **Smart Links Module** - Create links, track clicks
7. **Analytics Module** - Campaign metrics & dashboards
8. **Background Workers** - Async campaign sending
9. **Utilities** - GeoIP, User-Agent parsing

---

## 🧪 Testing

```bash
# Run tests (TODO)
pytest

# With coverage
pytest --cov=app tests/
```

---

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT signing key (32+ chars) | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `ENVIRONMENT` | Environment (development/production) | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiry | `1440` (24h) |
| `RATE_LIMIT_PER_MINUTE` | API rate limit | `60` |

---

## 🔧 Development

### Code Style
```bash
# Format code
black app/

# Lint
flake8 app/
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## 📚 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎯 Roadmap

### Phase 1 (Current)
- [x] Core architecture
- [x] Database models
- [x] Authentication foundation
- [ ] API endpoints
- [ ] Mock WhatsApp sender
- [ ] Basic analytics

### Phase 2 (Future)
- [ ] Real WhatsApp Business API integration
- [ ] Scheduled campaigns
- [ ] Template management
- [ ] Advanced analytics
- [ ] Webhook handling

### Phase 3 (Future)
- [ ] Multi-channel (Telegram, SMS)
- [ ] A/B testing
- [ ] Subscription billing
- [ ] Team management
- [ ] API rate limiting (Redis-based)

---

## 🤝 Contributing

This is a portfolio project. Contributions are welcome!

---

## 📄 License

MIT License

---

## 👨‍💻 Author

Built with ❤️ as a portfolio project to demonstrate production-grade backend development.
