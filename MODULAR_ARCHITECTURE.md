# Modular Architecture Guide

## Overview

The Test Tool Platform has been refactored into a **modular architecture** where each feature is encapsulated in its own module with clear separation of concerns.

## Architecture Principles

1. **Feature-Based Modules**: Each major feature (XML comparison, FIX messaging) is a self-contained module
2. **Separation of Concerns**: Models, services, schemas, and APIs are cleanly separated
3. **Independent Deployment**: Modules can be enabled/disabled independently
4. **Shared Infrastructure**: Common database and configuration layer
5. **Extensibility**: New modules can be added without modifying existing code

## Project Structure

```
multi/
├── app/
│   ├── modules/                    # Feature modules
│   │   ├── __init__.py
│   │   ├── xml_compare/           # XML Comparison Module
│   │   │   ├── __init__.py
│   │   │   ├── models.py          # ComparisonJob model
│   │   │   ├── schemas.py         # Pydantic schemas
│   │   │   ├── service.py         # XMLComparator service
│   │   │   └── job_service.py     # Job management
│   │   └── fix_messaging/         # FIX Protocol Module
│   │       ├── __init__.py
│   │       ├── models.py          # FixMessage model
│   │       ├── schemas.py         # Pydantic schemas
│   │       └── service.py         # FixMessagingService
│   ├── api/                       # API routes
│   │   ├── xml_compare.py         # XML API endpoints
│   │   ├── fix_messaging.py       # FIX API endpoints
│   │   └── web.py                 # Web UI routes
│   ├── services/                  # Legacy services
│   │   ├── xml_compare.py        # (kept for compatibility)
│   │   └── job_service.py        # (kept for compatibility)
│   ├── templates/                 # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   └── ...
│   ├── config.py                  # Application configuration
│   ├── database.py                # Database session management
│   ├── main.py                    # FastAPI app entry point
│   ├── models.py                  # Model re-exports (compatibility)
│   └── schemas.py                 # Schema re-exports (compatibility)
├── alembic/                       # Database migrations
│   └── versions/
│       ├── 001_initial_migration.py
│       └── 002_add_fix_messages.py
├── tests/
│   ├── test_xml_compare.py        # XML module tests
│   ├── test_api.py                # XML API tests
│   └── test_fix_messaging.py      # FIX module tests
├── requirements.txt
└── README.md
```

## Module Anatomy

Each module follows a consistent structure:

### 1. Models (`models.py`)
- SQLAlchemy ORM models
- Database table definitions
- Enums and constants
- Model relationships

### 2. Schemas (`schemas.py`)
- Pydantic request/response models
- Data validation
- API documentation
- Serialization/deserialization

### 3. Service (`service.py`)
- Business logic
- Core functionality
- External integrations
- Error handling

### 4. API Routes (`app/api/<module>.py`)
- FastAPI route definitions
- Request handlers
- Response formatting
- Dependency injection

## Module: XML Comparison

### Purpose
Compare XML documents and track differences with XPath-based identification.

### Components

**Models:**
- `ComparisonJob`: Stores comparison jobs
- `JobStatus`: Job status enum (QUEUED, RUNNING, COMPLETED, FAILED)
- `DiffType`: Difference types (ADDED, REMOVED, CHANGED)

**Service:**
- `XMLComparator`: Core comparison engine
  - `parse_xml()`: Parse XML strings
  - `compare()`: Compare two XML documents
  - `build_node_map()`: Create node mappings
  - `compare_nodes()`: Deep comparison logic

**Schemas:**
- `XMLCompareRequest`: Create comparison job
- `JobResponse`: Job details
- `JobListResponse`: Paginated job list

**API Endpoints:**
- `POST /api/xml-compare/jobs`: Create comparison
- `GET /api/xml-compare/jobs/{id}`: Get job details
- `GET /api/xml-compare/jobs`: List jobs
- `DELETE /api/xml-compare/jobs/{id}`: Delete job

### Database Tables
- `comparison_jobs`: Job storage with metadata, XML content, and results

## Module: FIX Messaging

### Purpose
Create, send, and manage FIX protocol messages for financial trading systems.

### Components

**Models:**
- `FixMessage`: Stores FIX messages
- `FixMessageStatus`: Message status enum
- `FixMessageType`: Common FIX message types

**Service:**
- `FixMessagingService`: FIX message management
  - `create_fix_message()`: Build and send FIX message
  - `_build_fix_message()`: Construct FIX format
  - `get_message()`: Retrieve message
  - `list_messages()`: Query messages
  - `delete_message()`: Remove message

**Schemas:**
- `SendFixMessageRequest`: Send FIX message
- `FixMessageResponse`: Message details
- `FixMessageListResponse`: Paginated message list
- `FixSessionConfig`: Session configuration

**API Endpoints:**
- `POST /api/fix/messages`: Send FIX message
- `GET /api/fix/messages/{id}`: Get message details
- `GET /api/fix/messages`: List messages
- `DELETE /api/fix/messages/{id}`: Delete message

### Database Tables
- `fix_messages`: Message storage with header, body, and status

## Shared Infrastructure

### Database Layer (`app/database.py`)
- SQLAlchemy engine and session management
- Base declarative class
- Session dependency injection

### Configuration (`app/config.py`)
- Environment-based settings
- Database URL configuration
- Application parameters

### Main Application (`app/main.py`)
- FastAPI app initialization
- CORS middleware
- Router registration
- Health check endpoint

## Adding a New Module

### Step 1: Create Module Structure

```bash
mkdir app/modules/my_module
touch app/modules/my_module/__init__.py
touch app/modules/my_module/models.py
touch app/modules/my_module/schemas.py
touch app/modules/my_module/service.py
```

### Step 2: Define Models

```python
# app/modules/my_module/models.py
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class MyModel(Base):
    __tablename__ = "my_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False)
```

### Step 3: Define Schemas

```python
# app/modules/my_module/schemas.py
from pydantic import BaseModel
from datetime import datetime

class MyRequest(BaseModel):
    name: str

class MyResponse(BaseModel):
    id: int
    name: str
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### Step 4: Implement Service

```python
# app/modules/my_module/service.py
from sqlalchemy.orm import Session
from .models import MyModel
from .schemas import MyRequest

class MyService:
    def create_item(self, request: MyRequest, db: Session) -> MyModel:
        item = MyModel(name=request.name)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
```

### Step 5: Create API Routes

```python
# app/api/my_module.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.modules.my_module import MyService, MyRequest, MyResponse

router = APIRouter(prefix="/api/my-module", tags=["My Module"])
service = MyService()

@router.post("/items", response_model=MyResponse)
async def create_item(request: MyRequest, db: Session = Depends(get_db)):
    return service.create_item(request, db)
```

### Step 6: Register Routes

```python
# app/main.py
from app.api.my_module import router as my_module_router

app.include_router(my_module_router)
```

### Step 7: Create Migration

```bash
alembic revision -m "Add my_module table"
```

Edit the migration file:

```python
def upgrade():
    op.create_table(
        'my_table',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('my_table')
```

Run migration:

```bash
alembic upgrade head
```

### Step 8: Write Tests

```python
# tests/test_my_module.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_item():
    response = client.post("/api/my-module/items", json={"name": "test"})
    assert response.status_code == 201
    assert response.json()["name"] == "test"
```

## Module Dependencies

### Internal Dependencies
- Modules can depend on shared infrastructure (database, config)
- Modules should NOT depend on each other directly
- Use service injection for cross-module communication

### External Dependencies
- Add module-specific dependencies to `requirements.txt`
- Document optional dependencies
- Use feature flags to enable/disable modules

## Best Practices

1. **Single Responsibility**: Each module handles one feature
2. **Loose Coupling**: Modules communicate through well-defined APIs
3. **High Cohesion**: Related functionality stays together
4. **Testability**: Each module has independent tests
5. **Documentation**: Each module has its own guide
6. **Versioning**: Module versions can evolve independently
7. **Configuration**: Module-specific config in separate sections

## Module Communication

### Direct API Calls
```python
# From one module to another via HTTP
import httpx
response = httpx.post("http://localhost:8000/api/other-module/action")
```

### Shared Database
```python
# Query another module's data
from app.modules.other_module.models import OtherModel
items = db.query(OtherModel).all()
```

### Service Injection
```python
# Inject services as dependencies
from app.modules.other_module.service import OtherService

def my_function(other_service: OtherService = Depends()):
    return other_service.do_something()
```

## Testing Strategy

### Unit Tests
Test individual functions and methods:
```bash
pytest tests/test_xml_compare.py -v
```

### Integration Tests
Test API endpoints:
```bash
pytest tests/test_api.py -v
```

### Module Tests
Test entire module:
```bash
pytest tests/test_fix_messaging.py -v
```

### Full Suite
Test all modules:
```bash
pytest tests/ -v
```

## Performance Considerations

1. **Database Indexes**: Add indexes for common queries
2. **Caching**: Cache frequently accessed data
3. **Async Operations**: Use async for I/O operations
4. **Connection Pooling**: Configure database pool size
5. **Lazy Loading**: Load related data only when needed

## Security

1. **Input Validation**: Use Pydantic schemas
2. **SQL Injection**: Use parameterized queries
3. **Authentication**: Add auth middleware per module
4. **Authorization**: Role-based access control
5. **Rate Limiting**: Protect endpoints from abuse

## Deployment

### Single Deployment
Deploy all modules together:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Selective Modules
Enable only specific modules via environment variables:
```bash
ENABLED_MODULES=xml_compare,fix_messaging uvicorn app.main:app
```

### Microservices
Deploy each module as separate service (future enhancement).

## Migration from Monolithic

If you have a monolithic codebase:

1. Identify feature boundaries
2. Create module directories
3. Move models to module
4. Move services to module
5. Update imports
6. Create module `__init__.py`
7. Update tests
8. Run full test suite
9. Update documentation

## Current Modules

1. **xml_compare**: XML document comparison (28 tests)
2. **fix_messaging**: FIX protocol messaging (8 tests)

## Future Modules

Potential modules to add:

- **api_testing**: REST API test automation
- **performance**: Load testing and metrics
- **reporting**: Custom report generation
- **notifications**: Alert and notification system
- **workflow**: Test workflow automation
- **data_generation**: Test data creation

## Module Metrics

Track module health:
- Test coverage per module
- API response times
- Error rates
- Usage statistics
- Dependencies
- Code quality scores

## Conclusion

The modular architecture provides:
- ✅ Clear separation of concerns
- ✅ Easy to add new features
- ✅ Independent testing
- ✅ Flexible deployment
- ✅ Better maintainability
- ✅ Scalable growth

Each module is self-contained, well-tested, and documented, making the platform easy to extend and maintain.
