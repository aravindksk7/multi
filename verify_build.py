"""
Build verification test - comprehensive system check.
"""
import sys

def test_imports():
    """Test all critical imports."""
    print("Testing imports...")
    try:
        from app.main import app
        from app.config import settings
        from app.database import Base, get_db
        from app.models import ComparisonJob, JobStatus
        from app.schemas import XMLCompareRequest, JobResponse
        from app.services.xml_compare import compare_xml
        from app.services.job_service import JobService
        from app.api.xml_compare import router as api_router
        from app.api.web import router as web_router
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_xml_comparison():
    """Test XML comparison engine."""
    print("\nTesting XML comparison engine...")
    try:
        from app.services.xml_compare import compare_xml
        
        baseline = '<root><item id="1">test</item></root>'
        current = '<root><item id="1">changed</item><item id="2">new</item></root>'
        
        result = compare_xml(baseline, current)
        
        assert 'summary' in result
        assert 'differences' in result
        assert result['summary']['total_differences'] > 0
        assert result['summary']['status'] in ['PASSED', 'FAILED']
        
        print(f"✓ Comparison engine works (found {result['summary']['total_differences']} differences)")
        return True
    except Exception as e:
        print(f"✗ Comparison test failed: {e}")
        return False


def test_fastapi_app():
    """Test FastAPI application."""
    print("\nTesting FastAPI application...")
    try:
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        
        print(f"✓ FastAPI app works (health check passed)")
        return True
    except Exception as e:
        print(f"✗ FastAPI test failed: {e}")
        return False


def test_database_models():
    """Test database models."""
    print("\nTesting database models...")
    try:
        from app.models import ComparisonJob, JobStatus
        from app.database import Base
        
        # Check model has required attributes
        assert hasattr(ComparisonJob, 'id')
        assert hasattr(ComparisonJob, 'baseline_xml')
        assert hasattr(ComparisonJob, 'current_xml')
        assert hasattr(ComparisonJob, 'status')
        assert hasattr(ComparisonJob, 'summary')
        assert hasattr(ComparisonJob, 'differences')
        
        # Check enum
        assert hasattr(JobStatus, 'QUEUED')
        assert hasattr(JobStatus, 'RUNNING')
        assert hasattr(JobStatus, 'COMPLETED')
        assert hasattr(JobStatus, 'FAILED')
        
        print("✓ Database models are properly defined")
        return True
    except Exception as e:
        print(f"✗ Database model test failed: {e}")
        return False


def test_api_schemas():
    """Test Pydantic schemas."""
    print("\nTesting API schemas...")
    try:
        from app.schemas import XMLCompareRequest, JobResponse
        
        # Test request validation
        request = XMLCompareRequest(
            baseline_xml='<root/>',
            current_xml='<root/>',
            suite_name='Test Suite'
        )
        assert request.baseline_xml == '<root/>'
        assert request.suite_name == 'Test Suite'
        
        print("✓ API schemas work correctly")
        return True
    except Exception as e:
        print(f"✗ Schema test failed: {e}")
        return False


def test_templates_exist():
    """Test that templates exist."""
    print("\nTesting templates...")
    try:
        import os
        
        templates_dir = 'app/templates'
        required_templates = [
            'base.html',
            'index.html',
            'new_comparison.html',
            'jobs_list.html',
            'job_detail.html'
        ]
        
        for template in required_templates:
            path = os.path.join(templates_dir, template)
            assert os.path.exists(path), f"Missing template: {template}"
        
        print(f"✓ All {len(required_templates)} templates exist")
        return True
    except Exception as e:
        print(f"✗ Template test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("="*70)
    print(" "*15 + "BUILD VERIFICATION TEST")
    print("="*70)
    
    tests = [
        test_imports,
        test_xml_comparison,
        test_database_models,
        test_api_schemas,
        test_templates_exist,
        test_fastapi_app,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "="*70)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("="*70)
    
    if all(results):
        print("\n✓✓✓ BUILD VERIFICATION SUCCESSFUL ✓✓✓")
        print("\nThe Test Tool Platform is ready to use!")
        print("\nNext steps:")
        print("  1. Ensure MySQL is running")
        print("  2. Create database: CREATE DATABASE testtool_db;")
        print("  3. Run migrations: alembic upgrade head")
        print("  4. Start server: python -m uvicorn app.main:app --reload")
        print("  5. Open browser: http://localhost:8000")
        return 0
    else:
        print("\n✗✗✗ BUILD VERIFICATION FAILED ✗✗✗")
        print("\nSome tests failed. Please check the errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
