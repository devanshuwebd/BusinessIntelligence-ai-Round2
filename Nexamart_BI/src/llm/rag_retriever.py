from pathlib import Path


def retrieve_policy_context(driver_type: str, docs_dir: str | Path = "docs") -> str:
    mapping = {
        "marketing_efficiency": "marketing_policy.pdf",
        "stockout_hours": "inventory_policy.pdf",
        "price_mix": "pricing_policy.pdf",
        "region": "regional_rules.pdf",
    }
    path = Path(docs_dir) / mapping.get(driver_type, "inventory_policy.pdf")
    if not path.exists():
        return "No policy document found for this driver."
    try:
        from pypdf import PdfReader
        return "\n".join(page.extract_text() or "" for page in PdfReader(str(path)).pages)[:4000]
    except Exception as exc:
        return f"Policy retrieval unavailable: {type(exc).__name__}"
