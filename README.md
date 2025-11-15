# Test Tool Platform - Modular Testing Framework

A comprehensive modular platform for test automation tools, featuring XML report comparison and FIX protocol messaging, built with Python, FastAPI, and SQLAlchemy.

## Features

### XML Comparison Module
- **XML Deep Comparison**: Compare two XML documents with XPath-based difference tracking
- **Web UI**: User-friendly interface for uploading and comparing XML reports
- **REST API**: Programmatic access for automation and integration
- **Database Storage**: All comparison results stored with full history
- **Filtering & Search**: Query jobs by status, suite name, environment, and date range
- **Detailed Diff Reports**: Track added, removed, and changed elements with full context

### FIX Protocol Messaging Module
- **FIX Message Creation**: Build and send FIX 4.4 protocol messages
- **Order Management**: Support for NewOrderSingle, OrderCancel, and other message types
- **Message History**: Store and query all sent FIX messages
- **REST API**: Send messages and track status programmatically
- **SimpleFIX Library**: Pure Python implementation, no C++ dependencies

## Tech Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: SQLite (default) / MySQL / MariaDB
- **Migrations**: Alembic
- **Templating**: Jinja2
- **HTTP Server**: Uvicorn
- **Testing**: pytest
- **FIX Protocol**: SimpleFIX

## Modular Architecture

The platform uses a feature-based modular architecture where each major feature is a self-contained module:

- `app/modules/xml_compare/` - XML comparison functionality
- `app/modules/fix_messaging/` - FIX protocol messaging

See [MODULAR_ARCHITECTURE.md](MODULAR_ARCHITECTURE.md) for detailed architecture documentation.

## Project Structure

```
multi/
├── app/
│   ├── modules/                    # Feature modules
│   │   ├── xml_compare/           # XML Comparison Module
│   │   │   ├── models.py          # Database models
│   │   │   ├── schemas.py         # Pydantic schemas
│   │   │   ├── service.py         # Business logic
│   │   │   └── job_service.py
│   │   └── fix_messaging/         # FIX Protocol Module
│   │       ├── models.py
│   │       ├── schemas.py
│   │       └── service.py
│   ├── api/
│   │   ├── web.py                 # Web UI routes
│   │   ├── xml_compare.py         # XML REST API
│   │   └── fix_messaging.py       # FIX REST API
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── new_comparison.html
│   │   ├── jobs_list.html
│   │   └── job_detail.html
│   ├── config.py                  # Application configuration
│   ├── database.py                # Database setup
│   ├── models.py                  # Model exports
│   └── main.py                    # FastAPI app entry point
├── alembic/
│   ├── versions/
│   │   ├── 001_initial_migration.py
│   │   └── 002_add_fix_messages.py
│   └── env.py
├── tests/
│   ├── conftest.py
│   ├── test_xml_compare.py        # XML tests (9 tests)
│   ├── test_api.py                # XML API tests (11 tests)
│   └── test_fix_messaging.py      # FIX tests (8 tests)
├── requirements.txt
├── alembic.ini
├── .env.example
├── README.md
├── FIX_MESSAGING_GUIDE.md         # FIX Protocol documentation
├── MODULAR_ARCHITECTURE.md        # Architecture guide
└── SQLITE_BACKEND.md              # SQLite setup guide
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip and virtualenv
- (Optional) MySQL 8.0+ or MariaDB 10.5+ for production use

**Note**: SQLite is used by default for easy setup. No database server required!

### Setup Steps

1. **Clone or navigate to the project directory**

```powershell
cd c:\multi
```

2. **Create and activate virtual environment**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. **Install dependencies**

```powershell
pip install -r requirements.txt
```

4. **Configure environment variables**

Copy `.env.example` to `.env` and update with your settings:

```powershell
cp .env.example .env
```

Edit `.env` (SQLite is default, no changes needed):

```ini
# SQLite (default - no database setup required)
DATABASE_URL=sqlite:///./testtool.db

# Or use MySQL for production
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/testtool_db

APP_NAME=Test Tool Platform
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

5. **Run database migrations**

```powershell
alembic upgrade head
```

**That's it!** SQLite database will be created automatically.

### Optional: MySQL Setup

If you prefer MySQL for production:

1. Install pymysql: `pip install pymysql cryptography`
2. Create database:

```powershell
# Connect to MySQL and create database
mysql -u root -p
```

```sql
CREATE DATABASE testtool_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

3. Update `.env` with MySQL URL
4. Run migrations: `alembic upgrade head`

## Quick Start (SQLite)

Use the provided start script for instant setup:

```powershell
.\start_sqlite.ps1
```

This will:
- Create virtual environment (if needed)
- Install dependencies
- Set up SQLite database
- Run migrations
- Start the server

## Running the Application

### Development Server

```powershell
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the start script (SQLite)
.\start_sqlite.ps1

# Or using the original start script (MySQL)
.\start.ps1
```

The application will be available at:
- **Web UI**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Usage

### Web Interface

1. **Home Page**: Navigate to http://localhost:8000
2. **Create Comparison**: Click "New Comparison" or visit http://localhost:8000/compare/new
3. **Upload XML**: Paste or upload baseline and current XML files
4. **Add Metadata** (optional): Enter suite name, environment, and run ID
5. **Compare**: Click "Compare XMLs" to run the comparison
6. **View Results**: See detailed diff report with XPath-based changes
7. **Browse Jobs**: Visit http://localhost:8000/jobs to see all comparison jobs

### REST API

#### Create a Comparison Job

```bash
curl -X POST "http://localhost:8000/api/xml-compare/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "baseline_xml": "<testsuite><testcase name=\"TC1\" status=\"pass\"/></testsuite>",
    "current_xml": "<testsuite><testcase name=\"TC1\" status=\"fail\"/></testsuite>",
    "suite_name": "Regression Suite",
    "environment": "staging",
    "run_id": "run-123"
  }'
```

Response:
```json
{
  "id": 1,
  "status": "COMPLETED",
  "suite_name": "Regression Suite",
  "environment": "staging",
  "run_id": "run-123",
  "summary": {
    "added": 0,
    "removed": 0,
    "changed": 1,
    "total_differences": 1,
    "status": "FAILED"
  },
  "differences": [
    {
      "type": "CHANGED",
      "path": "/testsuite/testcase[@name='TC1']/@status",
      "baseline_value": "pass",
      "current_value": "fail",
      "description": "Attribute 'status' changed"
    }
  ],
  "created_at": "2025-11-15T10:30:00",
  "started_at": "2025-11-15T10:30:00",
  "completed_at": "2025-11-15T10:30:01",
  "error_message": null
}
```

#### Get Job Details

```bash
curl -X GET "http://localhost:8000/api/xml-compare/jobs/1"
```

#### List Jobs with Filtering

```bash
# List all jobs
curl -X GET "http://localhost:8000/api/xml-compare/jobs"

# Filter by status
curl -X GET "http://localhost:8000/api/xml-compare/jobs?status=COMPLETED"

# Filter by suite and environment
curl -X GET "http://localhost:8000/api/xml-compare/jobs?suite_name=Regression%20Suite&environment=staging"

# Pagination
curl -X GET "http://localhost:8000/api/xml-compare/jobs?page=2&page_size=10"
```

#### Delete a Job

```bash
curl -X DELETE "http://localhost:8000/api/xml-compare/jobs/1"
```

## XML Comparison Logic

The comparison engine provides:

### Features

- **Deep Comparison**: Recursively compares all elements, attributes, and text content
- **XPath Identification**: Uses XPath expressions to identify changed elements
- **Normalization**: Ignores insignificant whitespace and attribute order
- **Change Types**:
  - `ADDED`: Elements present only in current XML
  - `REMOVED`: Elements present only in baseline XML
  - `CHANGED`: Elements with different attributes or text content

### Example Comparison

**Baseline XML:**
```xml
<testsuite name="Suite" tests="2">
    <testcase name="TC1" time="1.23" status="pass">
        <result>PASSED</result>
    </testcase>
    <testcase name="TC2" time="0.56" status="pass">
        <result>PASSED</result>
    </testcase>
</testsuite>
```

**Current XML:**
```xml
<testsuite name="Suite" tests="3">
    <testcase name="TC1" time="1.50" status="pass">
        <result>PASSED</result>
    </testcase>
    <testcase name="TC2" time="0.56" status="fail">
        <result>FAILED</result>
    </testcase>
    <testcase name="TC3" time="2.00" status="pass">
        <result>PASSED</result>
    </testcase>
</testsuite>
```

**Detected Differences:**
- `CHANGED`: `/testsuite/@tests` (2 → 3)
- `CHANGED`: `/testsuite/testcase[@name='TC1']/@time` (1.23 → 1.50)
- `CHANGED`: `/testsuite/testcase[@name='TC2']/@status` (pass → fail)
- `CHANGED`: `/testsuite/testcase[@name='TC2']/result/text()` (PASSED → FAILED)
- `ADDED`: `/testsuite/testcase[@name='TC3']`

## FIX Protocol Messaging

The platform includes FIX protocol support for financial message sending.

### Send a FIX Message

```bash
curl -X POST "http://localhost:8000/api/fix/messages" \
  -H "Content-Type: application/json" \
  -d '{
    "msg_type": "D",
    "sender_comp_id": "SENDER",
    "target_comp_id": "TARGET",
    "cl_ord_id": "ORDER123",
    "symbol": "AAPL",
    "side": "1",
    "order_qty": "100",
    "ord_type": "2",
    "price": "150.50",
    "time_in_force": "0"
  }'
```

### List FIX Messages

```bash
curl -X GET "http://localhost:8000/api/fix/messages"
```

### FIX Message Types Supported

- **D**: NewOrderSingle - Submit new order
- **F**: OrderCancelRequest - Cancel order
- **0**: Heartbeat - Connection heartbeat
- **A**: Logon - Session logon
- And more...

See [FIX_MESSAGING_GUIDE.md](FIX_MESSAGING_GUIDE.md) for complete FIX protocol documentation.

## Testing

### Run All Tests (28 tests)

```powershell
pytest
```

### Run Module-Specific Tests

```powershell
# XML comparison tests (9 tests)
pytest tests/test_xml_compare.py

# XML API tests (11 tests)
pytest tests/test_api.py

# FIX messaging tests (8 tests)
pytest tests/test_fix_messaging.py
```

### Run with Coverage

```powershell
pytest --cov=app --cov-report=html
```

### Test Coverage

The test suite includes:
- **XML Module**: Comparison engine, API endpoints, edge cases (20 tests)
- **FIX Module**: Message creation, listing, filtering, deletion (8 tests)
- **Total**: 28 passing tests

## Database Migrations

### Create a New Migration

```powershell
alembic revision --autogenerate -m "Description of changes"
```

### Apply Migrations

```powershell
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>
```

### Rollback Migrations

```powershell
# Downgrade one revision
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>
```

### View Migration History

```powershell
alembic history
alembic current
```

## API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI Schema**: http://localhost:8000/api/openapi.json

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | MySQL connection string | `mysql+pymysql://root:password@localhost:3306/testtool_db` |
| `APP_NAME` | Application name | `Test Tool Platform` |
| `DEBUG` | Debug mode | `True` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |

### Database Configuration

The platform supports MySQL and MariaDB. To switch databases, update the `DATABASE_URL` in `.env`:

**MySQL:**
```ini
DATABASE_URL=mysql+pymysql://user:password@host:3306/database
```

**MariaDB:**
```ini
DATABASE_URL=mysql+pymysql://user:password@host:3306/database
```

**SQLite (for testing):**
```ini
DATABASE_URL=sqlite:///./testtool.db
```

## Troubleshooting

### Common Issues

**1. Database Connection Error**
```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server...")
```
- Verify MySQL is running
- Check DATABASE_URL in `.env`
- Ensure database exists

**2. Import Errors**
```
ModuleNotFoundError: No module named 'fastapi'
```
- Activate virtual environment: `.\venv\Scripts\Activate.ps1`
- Install dependencies: `pip install -r requirements.txt`

**3. Migration Errors**
```
alembic.util.exc.CommandError: Target database is not up to date.
```
- Run migrations: `alembic upgrade head`

**4. Template Not Found**
```
jinja2.exceptions.TemplateNotFound: base.html
```
- Ensure you're running from project root: `cd c:\multi`
- Verify `app/templates/` directory exists

## Production Deployment

### Recommended Setup

1. **Use Production Database**: Configure MySQL with appropriate credentials
2. **Disable Debug Mode**: Set `DEBUG=False` in `.env`
3. **Use Production Server**: Deploy with Gunicorn + Uvicorn workers
4. **Add Reverse Proxy**: Use Nginx or Apache as reverse proxy
5. **Enable HTTPS**: Configure SSL/TLS certificates
6. **Set Up Monitoring**: Use tools like Prometheus, Grafana
7. **Configure Backups**: Regular database backups

### Production Server Command

```powershell
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Future Enhancements

- [ ] File upload support (instead of paste)
- [ ] Background job processing with Celery
- [ ] Export diff reports (PDF, CSV)
- [ ] Email notifications for job completion
- [ ] User authentication and authorization
- [ ] Comparison history and trending
- [ ] Custom diff rules and configurations
- [ ] Support for other file formats (JSON, YAML)

## License

This project is for educational and internal use.

## Support

For issues and questions, please check the API documentation at `/api/docs` or review the test files for usage examples.
