"""
Data shapes for the pipeline.
Each document type gets its OWN field schema instead of one generic shape —
an invoice and a contract don't share meaningful fields, so pretending
they do just produces mostly-null data. FIELD_SCHEMAS maps doc_type to
the Pydantic model used to validate that type's extraction.
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Type


DOC_TYPES = ["invoice", "contract", "id_document", "receipt", "other"]


class ClassificationResult(BaseModel):
    doc_type: Literal["invoice", "contract", "id_document", "receipt", "other"]
    confidence: float = Field(ge=0, le=1)
    reasoning: str


class InvoiceFields(BaseModel):
    invoice_number: Optional[str] = None
    vendor_name: Optional[str] = None
    amount: Optional[str] = None
    date_issued: Optional[str] = None
    due_date: Optional[str] = None


class ReceiptFields(BaseModel):
    merchant_name: Optional[str] = None
    amount: Optional[str] = None
    date: Optional[str] = None
    payment_method: Optional[str] = None


class ContractFields(BaseModel):
    contract_title: Optional[str] = None
    party_a: Optional[str] = None
    party_b: Optional[str] = None
    effective_date: Optional[str] = None
    contract_value: Optional[str] = None


class IdDocumentFields(BaseModel):
    full_name: Optional[str] = None
    id_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    expiry_date: Optional[str] = None
    nationality: Optional[str] = None


class OtherFields(BaseModel):
    title_or_subject: Optional[str] = None
    summary: Optional[str] = None
    date: Optional[str] = None
    amount: Optional[str] = None
    other_notes: Optional[str] = None


FIELD_SCHEMAS: Dict[str, Type[BaseModel]] = {
    "invoice": InvoiceFields,
    "receipt": ReceiptFields,
    "contract": ContractFields,
    "id_document": IdDocumentFields,
    "other": OtherFields,
}


class ProcessedDocument(BaseModel):
    id: Optional[int] = None
    filename: str
    classification: ClassificationResult
    # Stored as a plain dict since the shape varies by doc_type —
    # the specific Pydantic model above is only used during extraction
    # to validate the LLM's output before it gets here.
    fields: Dict[str, Optional[str]]
    flagged: bool
    flag_reason: Optional[str] = None