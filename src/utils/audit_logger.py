"""
Enterprise Audit Logger for LexAgent
Emits structured JSON compliance audit logs for regulatory legal chain-of-custody.
"""

import os
import json
import time
import uuid
import logging
from typing import Dict, Any

class EnterpriseAuditLogger:
    """Enterprise Audit Logger producing structured JSON log records for Splunk/CloudWatch ingestion."""
    
    def __init__(self, log_file: str = "logs/enterprise_audit.jsonl"):
        self.log_file = log_file
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
    def log_event(
        self,
        event_type: str,
        user_id: str,
        tenant_id: str,
        query: str,
        status: str,
        metadata: Dict[str, Any]
    ) -> str:
        """Writes an immutable JSON audit log record to disk."""
        transaction_id = f"tx_{uuid.uuid4().hex[:12]}"
        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "transaction_id": transaction_id,
            "event_type": event_type,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "query": query,
            "status": status,
            "metadata": metadata
        }
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
            
        return transaction_id

# Global Instance
audit_logger = EnterpriseAuditLogger()
