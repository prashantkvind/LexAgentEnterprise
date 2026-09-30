"""
Enterprise FastAPI REST Microservice Application for LexAgent
Provides asynchronous REST endpoints, JWT authorization headers, multi-tenant isolation,
and structured audit logging.
"""

import time
from typing import Optional, Dict, Any
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel

from src.agent.controller import LexAgentController
from src.utils.security_manager import EnterpriseSecurityManager
from src.utils.audit_logger import EnterpriseAuditLogger

app = FastAPI(
    title="LexAgent Enterprise API Microservice",
    description="Production-grade Agentic RAG legal microservice with multi-tenant security and audit logging.",
    version="2.0.0-enterprise"
)

# Global instances
controller = LexAgentController()
security_manager = EnterpriseSecurityManager()
audit_logger = EnterpriseAuditLogger()

class LegalQueryRequest(BaseModel):
    query: str
    wants_notice_draft: bool = True
    client_name: str = "Client Advocate"
    tenant_id: str = "tenant_law_firm_alpha"

class LegalQueryResponse(BaseModel):
    transaction_id: str
    status: str
    query: str
    legal_advice: str
    fact_verification_score: int
    discrepancy_matrix: list
    file_path: Optional[str] = None
    execution_time_ms: float

def verify_auth_token(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Dependency injection to validate Enterprise Bearer Token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Bearer token header")
    
    token = authorization.split(" ")[1]
    try:
        return security_manager.validate_bearer_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/api/v1/health")
def health_check():
    """Enterprise Health Check Endpoint."""
    return {
        "status": "HEALTHY",
        "service": "LexAgent Enterprise API",
        "timestamp": time.time(),
        "tier": "Production Enterprise"
    }

@app.get("/api/v1/metrics")
def metrics():
    """Enterprise Metrics Endpoint."""
    return {
        "cache_hits": len(controller._query_cache),
        "vector_count": controller.rag_tool.ingestor.collection.count(),
        "status": "OPERATIONAL"
    }

@app.post("/api/v1/analyze", response_model=LegalQueryResponse)
def analyze_legal_query(
    request: LegalQueryRequest,
    user_payload: Dict[str, Any] = Depends(verify_auth_token)
):
    """Processes legal query through 6-step agentic controller with audit logging and multi-tenant isolation."""
    start_time = time.perf_counter()
    
    # 1. Enforce Multi-Tenant Isolation
    security_manager.verify_tenant_isolation(
        user_tenant=user_payload["tenant_id"],
        requested_tenant=request.tenant_id
    )
    
    # 2. Process query via controller
    state = controller.process_query(
        query=request.query,
        wants_draft=request.wants_notice_draft,
        client_name=request.client_name
    )


    
    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
    
    # 3. Log Immutable Audit Record
    tx_id = audit_logger.log_event(
        event_type="LEGAL_QUERY_EXECUTION",
        user_id=user_payload["sub"],
        tenant_id=request.tenant_id,
        query=request.query,
        status="SUCCESS",
        metadata={
            "grounding_score": state.fact_verification_score,
            "has_draft": bool(state.generated_file_path),
            "execution_ms": elapsed_ms
        }
    )
    
    return LegalQueryResponse(
        transaction_id=tx_id,
        status="SUCCESS",
        query=request.query,
        legal_advice=state.final_advice or state.synthesis_output or "Strategy Generated Successfully",
        fact_verification_score=int(state.fact_verification_score),
        discrepancy_matrix=state.discrepancy_matrix,
        file_path=state.generated_file_path,
        execution_time_ms=elapsed_ms
    )


