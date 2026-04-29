from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ToneEnum(str, Enum):
    academico = "academico"
    ejecutivo = "ejecutivo"
    tecnico = "tecnico"
    neutral = "neutral"


class TextoInput(BaseModel):
    texto: str = Field(..., min_length=1, max_length=10000)
    tono: ToneEnum | None = ToneEnum.neutral
    max_tokens: int | None = Field(None, ge=16, le=4096)
    temperature: float | None = Field(None, ge=0.0, le=1.0)
    top_p: float | None = Field(None, ge=0.0, le=1.0)
    apply_rules: bool | None = Field(True)
    rules_probability: float | None = Field(1.0, ge=0.0, le=1.0)
    rules_seed: int | None = None
    metadata: dict[str, Any] | None = None


class Metrics(BaseModel):
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    sentence_count: int
    word_count: int
    avg_words_per_sentence: float
    percent_complex_words: float


class HumanizerResponse(BaseModel):
    humanized_text: str
    metrics: Metrics
    model_metadata: dict[str, Any] | None = None
    requested_tone: ToneEnum
    warnings: list[str] | None = None
    diff: str | None = None


class ErrorResponse(BaseModel):
    error: str
    detail: dict[str, Any] | None = None
    request_id: str | None = None
