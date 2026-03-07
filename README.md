# demo-hack

A Django web application boilerplate refactored for the AgroNet backend architecture.

## Requirements

- Python 3.10+
- pip

## Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/akannkereuwem1/demo-hack.git
   cd demo-hack
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**

   ```bash
   cd backend
   python manage.py migrate
   ```

5. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   The application will be available at http://127.0.0.1:8000/

## Project Structure

The project has been refactored to comply with `AGENTS.md` specifying a clear separation for the MVP AgroNet backend features:

```
demo-hack/
├── backend/
│   ├── apps/
│   │   ├── ai/          # AI price prediction & image classification
│   │   ├── orders/      # Offer negotiation and life-cycle state machine
│   │   ├── payments/    # Integration with Interswitch payments
│   │   ├── products/    # Produce listings by Farmers for Buyers
│   │   └── users/       # Authenticaton and RBAC for Farmers/Buyers
│   ├── config/          # Django configuration (settings, urls, asgi, wsgi)
│   ├── tests/           # Integration tests
│   ├── utils/           # Shared utility tools and helpers
│   └── manage.py        # Django management script
├── AGENTS.md            # Agent operational rules and context
├── requirements.txt     # Python dependencies
└── README.md
```

## Deliverables for Issue #5
- [x] Initialized the core apps `users`, `products`, `orders`, `payments`, `ai`
- [x] Abstracted base directories (`config`, `tests`, `utils`) under `backend/` folder
- [x] Configured `settings.py` so standard absolute imports are available
- [x] Passed structural validation (`manage.py check`)
