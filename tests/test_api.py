"""Tests for API endpoints."""
import pytest
from app.models import JobStatus


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_create_comparison_job(client, sample_xml_baseline, sample_xml_current_changed):
    """Test creating a new comparison job via API."""
    response = client.post(
        "/api/xml-compare/jobs",
        json={
            "baseline_xml": sample_xml_baseline,
            "current_xml": sample_xml_current_changed,
            "suite_name": "Test Suite",
            "environment": "staging",
            "run_id": "run-123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert "id" in data
    assert data["status"] == "COMPLETED"
    assert data["suite_name"] == "Test Suite"
    assert data["environment"] == "staging"
    assert data["run_id"] == "run-123"
    assert data["summary"] is not None
    assert data["summary"]["total_differences"] > 0
    assert data["differences"] is not None


def test_create_job_without_metadata(client, sample_xml_baseline, sample_xml_current_added):
    """Test creating job without optional metadata."""
    response = client.post(
        "/api/xml-compare/jobs",
        json={
            "baseline_xml": sample_xml_baseline,
            "current_xml": sample_xml_current_added
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert data["suite_name"] is None
    assert data["environment"] is None
    assert data["run_id"] is None


def test_create_job_invalid_xml(client):
    """Test creating job with invalid XML."""
    response = client.post(
        "/api/xml-compare/jobs",
        json={
            "baseline_xml": "<?xml version='1.0'?><root></root>",
            "current_xml": "<?xml version='1.0'?><root>"  # Invalid
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Job should be created but marked as FAILED
    assert data["status"] == "FAILED"
    assert data["error_message"] is not None


def test_get_job(client, sample_xml_baseline, sample_xml_current_changed):
    """Test retrieving a job by ID."""
    # First create a job
    create_response = client.post(
        "/api/xml-compare/jobs",
        json={
            "baseline_xml": sample_xml_baseline,
            "current_xml": sample_xml_current_changed
        }
    )
    job_id = create_response.json()["id"]
    
    # Then retrieve it
    response = client.get(f"/api/xml-compare/jobs/{job_id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == job_id
    assert data["status"] == "COMPLETED"
    assert data["differences"] is not None


def test_get_nonexistent_job(client):
    """Test retrieving a job that doesn't exist."""
    response = client.get("/api/xml-compare/jobs/99999")
    assert response.status_code == 404


def test_list_jobs(client, sample_xml_baseline, sample_xml_current_changed):
    """Test listing jobs."""
    # Create multiple jobs
    for i in range(3):
        client.post(
            "/api/xml-compare/jobs",
            json={
                "baseline_xml": sample_xml_baseline,
                "current_xml": sample_xml_current_changed,
                "suite_name": f"Suite {i}"
            }
        )
    
    # List all jobs
    response = client.get("/api/xml-compare/jobs")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 3
    assert len(data["jobs"]) == 3
    assert data["page"] == 1


def test_list_jobs_with_filters(client, sample_xml_baseline, sample_xml_current_changed):
    """Test listing jobs with filters."""
    # Create jobs with different metadata
    client.post(
        "/api/xml-compare/jobs",
        json={
            "baseline_xml": sample_xml_baseline,
            "current_xml": sample_xml_current_changed,
            "suite_name": "Suite A",
            "environment": "staging"
        }
    )
    
    client.post(
        "/api/xml-compare/jobs",
        json={
            "baseline_xml": sample_xml_baseline,
            "current_xml": sample_xml_current_changed,
            "suite_name": "Suite B",
            "environment": "production"
        }
    )
    
    # Filter by suite_name
    response = client.get("/api/xml-compare/jobs?suite_name=Suite A")
    data = response.json()
    
    assert data["total"] == 1
    assert data["jobs"][0]["suite_name"] == "Suite A"


def test_list_jobs_pagination(client, sample_xml_baseline, sample_xml_current_changed):
    """Test job list pagination."""
    # Create 25 jobs
    for i in range(25):
        client.post(
            "/api/xml-compare/jobs",
            json={
                "baseline_xml": sample_xml_baseline,
                "current_xml": sample_xml_current_changed
            }
        )
    
    # Get first page
    response = client.get("/api/xml-compare/jobs?page=1&page_size=10")
    data = response.json()
    
    assert data["total"] == 25
    assert len(data["jobs"]) == 10
    assert data["page"] == 1
    
    # Get second page
    response = client.get("/api/xml-compare/jobs?page=2&page_size=10")
    data = response.json()
    
    assert len(data["jobs"]) == 10
    assert data["page"] == 2


def test_delete_job(client, sample_xml_baseline, sample_xml_current_changed):
    """Test deleting a job."""
    # Create a job
    create_response = client.post(
        "/api/xml-compare/jobs",
        json={
            "baseline_xml": sample_xml_baseline,
            "current_xml": sample_xml_current_changed
        }
    )
    job_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/api/xml-compare/jobs/{job_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/api/xml-compare/jobs/{job_id}")
    assert get_response.status_code == 404


def test_delete_nonexistent_job(client):
    """Test deleting a job that doesn't exist."""
    response = client.delete("/api/xml-compare/jobs/99999")
    assert response.status_code == 404
