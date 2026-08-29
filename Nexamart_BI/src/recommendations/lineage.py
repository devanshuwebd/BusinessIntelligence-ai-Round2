from datetime import datetime, timezone
from typing import Any


def generate_evidence_lineage(kpi_name: str, source_metadata: dict[str, Any], evidence_ids: list[str], method: str, contract_version: str = "2.0") -> dict[str, Any]:
    return {
        "insight_target": kpi_name,
        "source_metadata": source_metadata,
        "evidence_ids": evidence_ids,
        "calculation_method": method,
        "contract_version": contract_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
