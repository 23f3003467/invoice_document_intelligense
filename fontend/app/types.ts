// Mirrors the Pydantic models in the backend's models.py.
// Keeping these in sync by hand is fine at this scale — if the project
// grows, generate this from the FastAPI OpenAPI schema instead.

export interface ClassificationResult {
  doc_type: "invoice" | "contract" | "id_document" | "receipt" | "other";
  confidence: number;
  reasoning: string;
}

export interface ProcessedDocument {
  id: number;
  filename: string;
  classification: ClassificationResult;
  fields: Record<string, string | null>;
  flagged: boolean;
  flag_reason: string | null;
}

export interface HistoryRow {
  id: number;
  filename: string;
  doc_type: string;
  confidence: number;
  fields_json: string;
  flagged: number;
  flag_reason: string | null;
  created_at: string;
}
