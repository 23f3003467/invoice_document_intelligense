"""
Steps 2 & 3: Classification + Extraction.
Both are just LLM calls that MUST return valid JSON matching our schema.
The trick that makes this reliable: a strict system prompt + Pydantic
validation on the way out, with a retry if parsing fails.
"""

import os
import json
from openai import OpenAI
from models import ClassificationResult, DOC_TYPES, FIELD_SCHEMAS
from pydantic import BaseModel, ValidationError

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"
)

MODEL = "llama3.2:3b" 


class LLMProcessingError(Exception):
    """Raised when the model's output can't be parsed/validated after a retry."""
    pass

def _call_for_json(system_prompt: str,user_content: str,max_tokens: int = 500) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_content
            }
        ]
    )

    raw = response.choices[0].message.content.strip()

    return json.loads(raw)

def _call_with_retry(
    system_prompt: str,
    user_content: str,
    schema: type[BaseModel],
    max_tokens: int = 500
) -> BaseModel:

    last_error = None

    for attempt in range(2):
        try:
            data = _call_for_json(
                system_prompt,
                user_content,
                max_tokens
            )

            return schema(**data)

        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e

            # On retry, tell the model exactly what went wrong
            user_content = (
                f"{user_content}\n\n"
                f"Your previous response was invalid ({e}). "
                f"Return ONLY valid JSON matching the required keys, "
                f"nothing else."
            )

        except Exception as e:
            raise LLMProcessingError(
                f"LLM call failed: {e}"
            ) from e

    raise LLMProcessingError(
        f"Model output failed validation after 2 attempts: {last_error}"
    )


def classify_document(text: str) -> ClassificationResult:
    system_prompt = f"""You classify business documents.
Return ONLY a JSON object, no other text, with exactly these keys:
- doc_type: one of {DOC_TYPES}
- confidence: float between 0 and 1
- reasoning: one short sentence

Nothing else. No markdown, no preamble."""

    data = _call_for_json(system_prompt, text[:6000])
    return ClassificationResult(**data)



def extract_fields(text: str, doc_type: str) -> dict:
    schema = FIELD_SCHEMAS.get(doc_type, FIELD_SCHEMAS["other"])
    field_names = list(schema.model_fields.keys())
 
    system_prompt = f"""You extract structured fields from a {doc_type} document.
Return ONLY a JSON object, no other text, with exactly these keys
(use null for anything not present in the document — never invent values):
{field_names}s
 
Nothing else. No markdown, no preamble."""
 
    user_content = f"Document text:\n{text[:6000]}"
    result = _call_with_retry(system_prompt, user_content, schema, max_tokens=400)
    return result.model_dump()




