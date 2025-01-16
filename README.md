# jobs_manager

A Django-based jobs/quotes/work management system customized for **Morris Sheetmetal** needs. Inspired by [django-timepiece](https://github.com/lincolnloop/django-timepiece), with added features such as:

- **CRM** with projects and businesses  
- **User dashboards** with budgeted hours based on project contracts  
- **Time sheets** (daily, weekly, monthly summaries)  
- **Approved and invoiced** time sheet workflows  
- **Monthly payroll** reporting (overtime, paid leave, vacation)  
- **Project invoicing** with hourly summaries  

---

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation (Local)](#installation-local)
- [Settings Module](#settings-module)
- [Database Setup](#database-setup)
- [Environment Variables](#environment-variables)
- [AWS Deployment Notes](#aws-deployment-notes)
- [Running the App](#running-the-app)
- [Fixtures & Xero Sync](#fixtures--xero-sync)
- [License](#license)

---

## Features

1. **CRM**: Tracks companies, projects, and quotes.  
2. **Time Sheets**: Enter, manage, and invoice hours.  
3. **Dashboards**: Visibility into each project’s budget.  
4. **Payroll**: Monthly summaries with overtime/leave.  
5. **Integrations**: Dropbox for file storage, Xero for invoicing/payroll.  

---

## Requirements

- **Python 3.12+**  
- **[Poetry](https://python-poetry.org/)** (manages Python dependencies)  
- **Node.js + npm** (manages JavaScript dependencies, even if lightly used)  
- **MariaDB 11.5.2** (locally or via RDS in production)

---

## Installation (Local)

Follow these steps for a **local development** environment:

1. **Clone the repo**:
   ```bash
   git clone https://github.com/corrin/jobs_manager.git
   cd jobs_manager
   ```
2. **Create a virtual environment**:
   ```bash
   pip install virtualenv
   python -m virtualenv venv
   ```
3. **Install Python dependencies**:
   ```bash
   poetry install
   ```
4. **Install JS dependencies**:
   ```bash
   npm install
   ```
5. **Set up the database** (see [Database Setup](#database-setup)).

6. **Configure environment variables** (see [Environment Variables](#environment-variables)).

7. Activate `venv`:
    
    ```bash
    venv\Scripts\activate # or "source venv\bin\activate" in Linux 
    ```
    
4. **Run migrations**:
    
    ```bash
    python manage.py migrate
    ```
    
5. **Start the development server**:
    
    ```bash
    poetry run python manage.py runserver
    ```
    
    Then open http://127.0.0.1:8000 in your browser.
    

---

## Settings Module

This project uses a **modular settings** approach under the `settings/` directory, with files like:

- `base.py`
- `local.py`
- `production.py`

By default, Django loads `settings/__init__.py`, which imports either `local` or `production` depending on the environment variable `DJANGO_ENV`. For example:

```python
# settings/__init__.py
import os

ENVIRONMENT = os.getenv('DJANGO_ENV', 'local')

if ENVIRONMENT == 'production':
    from .production import *
else:
    from .local import *
```

- **Local development**: `DJANGO_ENV=local`
- **Production**: `DJANGO_ENV=production`

---

## Database Setup

Our application expects a **MariaDB 11.5.2** (or MySQL-compatible) database.

### Local MariaDB Setup

1. Install MariaDB locally (e.g., `sudo apt install mariadb-server` on Ubuntu).
2. Create a database and user:
    
    ```sql
    CREATE DATABASE msm_workflow;
    CREATE USER 'msm_user'@'localhost' IDENTIFIED BY 'your-password';
    GRANT ALL PRIVILEGES ON msm_workflow.* TO 'msm_user'@'localhost';
    FLUSH PRIVILEGES;
    ```
    
3. Update your environment variables (`DB_PASSWORD`, etc.) accordingly.

---

## Environment Variables

Create a file named **`.env`** in the project root (or configure them in your environment). Below are the commonly used vars:

```bash
DEBUG=true
SECRET_KEY=your-django-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# None of these needed for local setup
XERO_CLIENT_ID=your-xero-client-id
XERO_CLIENT_SECRET=your-xero-client-secret
XERO_REDIRECT_URI=https://yourdomain.com/xero/callback
DROPBOX_ACCESS_TOKEN=your-dropbox-access-token

MSM_DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_PORT=your-db-port

```

> Note: You can customize or add others as needed (DJANGO_ENV=production, etc.).
> 

---

## Running the App

1. **Activate virtual environment**:
    
    ```bash
    venv\Scripts\activate # or "source venv\bin\activate" in Linux
    ```
    
2. **Apply migrations**:
    
    ```bash
    python manage.py migrate
    ```
    
3. **Collect static files**:
    
    ```bash
    python manage.py collectstatic
    ```
    
4. **Start the server** (development):
    
    ```bash
    python manage.py runserver
    ```
    
5. **Or run with Gunicorn** (production-like):
    
    ```bash
    gunicorn --bind 0.0.0.0:8000 jobs_manager.wsgi
    ```
    

---

## Fixtures & Xero Sync

- **Fixtures**: The project have fixtures to load initial data (e.g., example clients, test data). Install them by:
    
    ```bash
    python manage.py loaddata fixture_file.json
    
    ```
    
- **Xero Sync**: After the app is running, click the **“Refresh Xero data”** button (in the admin or custom view) to fetch data from Xero (clients, invoices, etc.).

---

## License

This project is proprietary to **Morris Sheetmetal**. For inquiries or usage permissions, contact the repository maintainer.

---

**Enjoy your time managing jobs in `jobs_manager`!**

For any questions or issues, please open an issue on GitHub or reach out to the team.
