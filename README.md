# AgroNet Backend

A strict Django REST Framework (DRF) mobile backend API built for AgroNet, connecting farmers directly to buyers by removing middlemen from the agricultural supply chain.

## Requirements

- Python 3.10+
- PostgreSQL
- pip

## Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/akannkereuwem1/demo-hack.git
   cd demo-hack
   ```

2. **Activate the shared virtual environment**
   ```bash
   # Windows
   C:\Users\WELCOME\Desktop\workspace\demo-hack-env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   uv add -r requirements.txt
   ```

4. **Environment Configuration**
   Copy the example environment file or setup your `.env` with the necessary configuration details like `DATABASE_URL` and `DJANGO_SECRET_KEY`.

5. **Apply database migrations**
   ```bash
   cd backend
   python manage.py migrate
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   The application will be available at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Project Structure

The project complies with the explicit separation of MVP features for the AgroNet backend as detailed in `AGENTS.md`.

```
demo-hack/
├── backend/
│   ├── apps/
│   │   ├── ai/          # AI price prediction & image classification
│   │   ├── orders/      # Offer negotiation and life-cycle state machine
│   │   ├── payments/    # Integration with Interswitch payments
│   │   ├── products/    # Produce listings by Farmers for Buyers
│   │   └── users/       # Authentication and RBAC for Farmers/Buyers
│   ├── config/          # Django configuration (settings, urls, asgi, wsgi)
│   ├── tests/           # Integration tests
│   ├── utils/           # Shared utility tools and helpers
│   └── manage.py        # Django management script
├── docs/                # Project documentation and issue walk-throughs
├── AGENTS.md            # Agent operational rules and context
├── requirements.txt     # Python dependencies
└── README.md
```

## Authentication

All authentication uses JWT (Bearer tokens). Register or login to receive tokens:

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/users/register/` | Public | Register a new farmer or buyer |
| POST | `/api/users/login/` | Public | Login and receive JWT tokens |
| GET | `/api/users/profile/` | Bearer JWT | Get authenticated user's profile |

**Example login request:**
```bash
curl -X POST http://127.0.0.1:8000/api/users/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'
```

**Using the token:**
```bash
curl http://127.0.0.1:8000/api/users/profile/ \
  -H "Authorization: Bearer <access_token>"
```

## Documentation

Instead of tracking issues directly in the README, specific documentation for major feature implementations and setups can be found in the `docs/` directory. Each issue folder contains an `implementation-plan.md` and a `walkthrough.md` detailing the architectural decisions and execution steps.

- [Database Configuration Setup](docs/issue-4-configure-postgresql/)
- [Project Structure Initialization](docs/issue-5-project-structure/)
- [Logging Setup](docs/issue-7-setup-logging/)
- [Deployment for Railway/Fly.io](docs/issue-8-deployment/)
- [Mobile Backend DRF API Refactoring](docs/issue-18-refactoring/)
- [Authentication System](docs/issue-20-authentication/)

## Agent Rules

This repository follows strict guidelines and iterative limits explicitly designed for Agent-driven development. Please refer to [`AGENTS.md`](./AGENTS.md) for more details.
