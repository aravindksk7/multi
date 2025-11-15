# Test Tool Platform - XML Report Comparison

A comprehensive web-based platform for comparing XML test reports with deep diff analysis, built with Python, FastAPI, and SQLAlchemy.

## Features

- **XML Deep Comparison**: Compare two XML documents with XPath-based difference tracking
- **Web UI**: User-friendly interface for uploading and comparing XML reports
- **REST API**: Programmatic access for automation and integration
- **Database Storage**: All comparison results stored in MySQL/MariaDB
- **Filtering & Search**: Query jobs by status, suite name, environment, and date range
- **Detailed Diff Reports**: Track added, removed, and changed elements with full context

## Tech Stack

- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: MySQL / MariaDB (configurable)
- **Migrations**: Alembic
- **Templating**: Jinja2
- **HTTP Server**: Uvicorn
- **Testing**: pytest

## Project Structure

```
multi/
├── app/
│   ├── api/
│   │   ├── web.py              # Web UI routes
│   │   └── xml_compare.py      # REST API endpoints
│   ├── services/
│   │   ├── xml_compare.py      # Core XML comparison logic
│   │   └── job_service.py      # Job management service
│   ├── templates/
│   │   ├── base.html           # Base template
│   │   ├── index.html          # Home page
│   │   ├── new_comparison.html # Comparison form
│   │   ├── jobs_list.html      # Jobs listing
│   │   └── job_detail.html     # Job details
│   ├── config.py               # Application configuration
│   ├── database.py             # Database setup
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   └── main.py                 # FastAPI app entry point
├── alembic/
│   ├── versions/
│   │   └── 001_initial_migration.py
│   └── env.py                  # Alembic configuration
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── test_xml_compare.py     # XML comparison tests
│   └── test_api.py             # API endpoint tests
├── requirements.txt            # Python dependencies
├── alembic.ini                 # Alembic configuration
├── .env.example                # Environment variables template
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.11 or higher
- MySQL 8.0+ or MariaDB 10.5+
- pip and virtualenv

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

Edit `.env`:

```ini
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/testtool_db
APP_NAME=Test Tool Platform
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

5. **Create the database**

```powershell
# Connect to MySQL and create database
mysql -u root -p
```

```sql
CREATE DATABASE testtool_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

6. **Run database migrations**

```powershell
alembic upgrade head
```

## Running the Application

### Development Server

```powershell
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python app/main.py
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

## Testing

### Run All Tests

```powershell
pytest
```

### Run Specific Test File

```powershell
pytest tests/test_xml_compare.py
pytest tests/test_api.py
```

### Run with Coverage

```powershell
pytest --cov=app --cov-report=html
```

### Test Coverage

The test suite includes:
- XML comparison engine tests (identical, changed, added, removed elements)
- API endpoint tests (CRUD operations, filtering, pagination)
- Edge cases (invalid XML, whitespace handling, attribute ordering)

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
