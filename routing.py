"""
Step 4: Routing / exception logic.
Plain rules, no AI. Fields are now a dict since the shape varies by
doc_type, so we look things up with .get() and check the keys that
exist for that type rather than assuming one fixed schema.
"""

from models import ClassificationResult
from typing import Optional


def _parse_amount(raw: Optional[str]) -> Optional[float]:
    if not raw:
        return None
    digits = "".join(c for c in raw if c.isdigit() or c == ".")
    try:
        return float(digits)
    except ValueError:
        return None


def evaluate_flags(
    classification: ClassificationResult, fields: dict
) -> tuple[bool, Optional[str]]:
    doc_type = classification.doc_type

    # Rule 1: low classification confidence -> needs a human look
    if classification.confidence < 0.6:
        return True, f"Low classification confidence ({classification.confidence:.2f})"

    # Rule 2: invoices/receipts missing an amount are suspicious
    if doc_type in ("invoice", "receipt") and not fields.get("amount"):
        return True, f"Missing amount on {doc_type}"

    # Rule 3: contracts missing a counterparty; IDs missing an ID number
    if doc_type == "contract" and not fields.get("party_b"):
        return True, "Missing counterparty (party_b) on contract"
    if doc_type == "id_document" and not fields.get("id_number"):
        return True, "Missing ID number on ID document"

    # Rule 4: high-value threshold — adjust to your currency/format
    amount_value = _parse_amount(fields.get("amount") or fields.get("contract_value"))
    if amount_value is not None and amount_value > 10000:
        return True, f"High amount ({amount_value}) — manual review"

    return False, None