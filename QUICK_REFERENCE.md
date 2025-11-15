# Quick Reference - Test Tool Platform

## Installation (First Time)

```powershell
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment template
Copy-Item .env.example .env

# 5. Edit .env with your database credentials
notepad .env

# 6. Create MySQL database
mysql -u root -p
# Then run: CREATE DATABASE testtool_db;

# 7. Run migrations
alembic upgrade head
```

## Daily Usage

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start server
python -m uvicorn app.main:app --reload

# Or use the quick start script
.\start.ps1
```

## URLs

- **Home**: http://localhost:8000
- **New Comparison**: http://localhost:8000/compare/new
- **Jobs List**: http://localhost:8000/jobs
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

## API Quick Reference

### Create Comparison Job
```bash
POST /api/xml-compare/jobs
Content-Type: application/json

{
  "baseline_xml": "<xml>...</xml>",
  "current_xml": "<xml>...</xml>",
  "suite_name": "optional",
  "environment": "optional",
  "run_id": "optional"
}
```

### Get Job Details
```bash
GET /api/xml-compare/jobs/{job_id}
```

### List Jobs
```bash
GET /api/xml-compare/jobs?status=COMPLETED&page=1&page_size=20
```

### Delete Job
```bash
DELETE /api/xml-compare/jobs/{job_id}
```

## PowerShell API Examples

```powershell
# Create job
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/xml-compare/jobs" `
  -Method Post `
  -Body (@{
    baseline_xml = (Get-Content examples/baseline.xml -Raw)
    current_xml = (Get-Content examples/current.xml -Raw)
    suite_name = "Test Suite"
  } | ConvertTo-Json) `
  -ContentType "application/json"

# Get job
Invoke-RestMethod -Uri "http://localhost:8000/api/xml-compare/jobs/$($response.id)"

# List jobs
Invoke-RestMethod -Uri "http://localhost:8000/api/xml-compare/jobs?page=1&page_size=10"
```

## Database Commands

```powershell
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history

# View current version
alembic current
```

## Testing

```powershell
# Run all tests
pytest

# Run specific test file
pytest tests/test_xml_compare.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=html
```

## Common Issues

### Database Connection Error
- Check MySQL is running
- Verify .env DATABASE_URL
- Ensure database exists

### Module Not Found
- Activate virtual environment: `.\venv\Scripts\Activate.ps1`
- Reinstall: `pip install -r requirements.txt`

### Template Not Found
- Run from project root: `cd c:\multi`
- Check app/templates/ directory exists

### Port Already in Use
- Change PORT in .env
- Or kill process: `Get-Process -Name python | Stop-Process`

## Project Structure

```
c:\multi/
├── app/                  # Application code
│   ├── api/             # API routes
│   ├── services/        # Business logic
│   ├── templates/       # HTML templates
│   ├── config.py        # Configuration
│   ├── database.py      # Database setup
│   ├── models.py        # Data models
│   ├── schemas.py       # API schemas
│   └── main.py          # App entry point
├── alembic/             # Database migrations
├── tests/               # Test suite
├── examples/            # Sample XML files
├── requirements.txt     # Dependencies
├── .env                 # Environment config
└── README.md           # Full documentation
```

## Environment Variables

```ini
DATABASE_URL=mysql+pymysql://user:pass@host:3306/db
APP_NAME=Test Tool Platform
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## Useful Commands

```powershell
# View logs in real-time
uvicorn app.main:app --reload --log-level debug

# Check Python version
python --version

# List installed packages
pip list

# Update all packages
pip install --upgrade -r requirements.txt

# Create backup
alembic downgrade -1
# Export database
mysqldump -u root -p testtool_db > backup.sql
```

## Status Codes

- `QUEUED` - Job created but not started
- `RUNNING` - Comparison in progress
- `COMPLETED` - Successfully completed
- `FAILED` - Error occurred

## Difference Types

- `ADDED` - Element only in current XML
- `REMOVED` - Element only in baseline XML
- `CHANGED` - Element exists but values differ

## Getting Help

1. Check README.md for detailed docs
2. View API docs at /api/docs
3. Check examples/ directory
4. Review test files for usage examples
