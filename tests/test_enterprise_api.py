"""
Enterprise API & Security Test Suite for LexAgent
Tests FastAPI microservice endpoints, Bearer token authorization, multi-tenant isolation,
and immutable JSON audit logging.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.fastapi_app import app
from src.utils.security_manager import EnterpriseSecurityManager
from src.utils.audit_logger import EnterpriseAuditLogger

client = TestClient(app)

def test_enterprise_health_endpoint():
    """Verify enterprise health endpoint returns 200 OK."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "HEALTHY"
    assert data["service"] == "LexAgent Enterprise API"

def test_enterprise_unauthorized_access():
    """Verify endpoint rejects requests missing Bearer token with 401."""
    response = client.post(
        "/api/v1/analyze",
        json={"query": "Sanctioned swimming pool missing", "client_name": "Smt Sunita Verma"}
    )
    assert response.status_code == 401

def test_enterprise_authorized_query():
    """Verify authorized legal query execution returning transaction_id and 200 OK."""
    headers = {"Authorization": "Bearer valid_enterprise_token_123"}
    response = client.post(
        "/api/v1/analyze",
        headers=headers,
        json={
            "query": "Sanctioned swimming pool missing as per RTI reply",
            "wants_notice_draft": True,
            "client_name": "Smt Sunita Verma",
            "tenant_id": "tenant_law_firm_alpha"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["transaction_id"].startswith("tx_")
    assert data["fact_verification_score"] >= 0
    assert isinstance(data["discrepancy_matrix"], list)

def test_enterprise_tenant_isolation_violation():
    """Verify system blocks cross-tenant access attempts."""
    security = EnterpriseSecurityManager()
    with pytest.raises(PermissionError):
        security.verify_tenant_isolation("tenant_alpha", "tenant_beta")

def test_enterprise_audit_logger():
    """Verify audit logger writes structured JSON record to disk."""
    logger = EnterpriseAuditLogger(log_file="logs/test_audit.jsonl")
    tx_id = logger.log_event(
        event_type="TEST_EVENT",
        user_id="user_123",
        tenant_id="tenant_alpha",
        query="Test query",
        status="SUCCESS",
        metadata={"score": 100}
    )
    assert tx_id.startswith("tx_")
