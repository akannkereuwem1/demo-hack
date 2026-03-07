# demo-hack

A Django web application boilerplate.

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
   python manage.py migrate
   ```

5. **Create a superuser** (optional)

   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**

   ```bash
   python manage.py runserver
   ```

   The application will be available at http://127.0.0.1:8000/

## Project Structure

```
demo-hack/
├── core/               # Main application
│   ├── migrations/     # Database migrations
│   ├── admin.py        # Admin site configuration
│   ├── apps.py         # App configuration
│   ├── models.py       # Database models
│   ├── tests.py        # Unit tests
│   └── views.py        # View functions
├── myproject/          # Django project configuration
│   ├── asgi.py         # ASGI entry point
│   ├── settings.py     # Project settings
│   ├── urls.py         # URL configuration
│   └── wsgi.py         # WSGI entry point
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── README.md
```

## Running Tests

```bash
python manage.py test
```
