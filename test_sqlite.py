#!/usr/bin/env python3
"""
Quick SQLite Backend Test
Tests the application with SQLite database backend
"""

import sys
import os

# Add app to path
sys.path.insert(0, os.path.dirname(__file__))

def test_sqlite_backend():
    """Test SQLite backend functionality."""
    print("=" * 70)
    print("           SQLite BACKEND TEST")
    print("=" * 70)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Check config uses SQLite
    tests_total += 1
    print("\nTest 1: Checking database configuration...")
    try:
        from app.config import settings
        db_url = settings.DATABASE_URL
        if "sqlite" in db_url.lower():
            print(f"✓ Using SQLite: {db_url}")
            tests_passed += 1
        else:
            print(f"✗ Not using SQLite: {db_url}")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 2: Check database file exists
    tests_total += 1
    print("\nTest 2: Checking database file...")
    try:
        if os.path.exists("testtool.db"):
            size = os.path.getsize("testtool.db")
            print(f"✓ Database exists: testtool.db ({size} bytes)")
            tests_passed += 1
        else:
            print("✗ Database file not found")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 3: Test database connection
    tests_total += 1
    print("\nTest 3: Testing database connection...")
    try:
        from app.database import SessionLocal, engine
        from sqlalchemy import text
        
        with SessionLocal() as session:
            result = session.execute(text("SELECT 1")).scalar()
            if result == 1:
                print("✓ Database connection successful")
                tests_passed += 1
            else:
                print("✗ Unexpected query result")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 4: Test table exists
    tests_total += 1
    print("\nTest 4: Checking comparison_jobs table...")
    try:
        from app.database import SessionLocal
        from sqlalchemy import text
        
        with SessionLocal() as session:
            result = session.execute(
                text("SELECT name FROM sqlite_master WHERE type='table' AND name='comparison_jobs'")
            ).scalar()
            if result == "comparison_jobs":
                print("✓ Table 'comparison_jobs' exists")
                tests_passed += 1
            else:
                print("✗ Table not found")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 5: Test CRUD operations
    tests_total += 1
    print("\nTest 5: Testing CRUD operations...")
    try:
        from app.database import SessionLocal
        from app.models import ComparisonJob, JobStatus
        from datetime import datetime
        
        with SessionLocal() as session:
            # Create
            job = ComparisonJob(
                baseline_xml="<test>baseline</test>",
                current_xml="<test>current</test>",
                summary={"total_changes": 0},
                differences=[],
                status=JobStatus.COMPLETED,
                suite_name="SQLite Test",
                started_at=datetime.now(),
                completed_at=datetime.now()
            )
            session.add(job)
            session.commit()
            job_id = job.id
            
            # Read
            retrieved = session.query(ComparisonJob).filter_by(id=job_id).first()
            if retrieved and retrieved.suite_name == "SQLite Test":
                print(f"✓ CRUD operations work (job ID: {job_id})")
                tests_passed += 1
                
                # Cleanup
                session.delete(retrieved)
                session.commit()
            else:
                print("✗ Failed to retrieve job")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Test 6: Test API with SQLite
    tests_total += 1
    print("\nTest 6: Testing API with SQLite backend...")
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        if response.status_code == 200:
            data = response.json()
            db_status = data.get("database", "unknown")
            print(f"✓ API works with SQLite (DB: {db_status})")
            tests_passed += 1
        else:
            print(f"✗ API returned status {response.status_code}")
    except Exception as e:
        print(f"✗ Failed: {e}")
    
    # Results
    print("\n" + "=" * 70)
    print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
    print("=" * 70)
    
    if tests_passed == tests_total:
        print("\n✓✓✓ SQLite BACKEND WORKS PERFECTLY ✓✓✓")
        print("\nSQLite is now the default database backend!")
        print("No MySQL setup required - ready to use immediately.")
        print("\nQuick start:")
        print("  .\\start_sqlite.ps1")
        return 0
    else:
        print(f"\n✗✗✗ {tests_total - tests_passed} test(s) failed ✗✗✗")
        return 1

if __name__ == "__main__":
    exit_code = test_sqlite_backend()
    sys.exit(exit_code)
