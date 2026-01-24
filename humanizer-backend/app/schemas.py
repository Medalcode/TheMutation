from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ToneEnum(str, Enum):
    academico = "academico"
    ejecutivo = "ejecutivo"
    tecnico = "tecnico"
    neutral = "neutral"


class TextoInput(BaseModel):
    texto: str = Field(..., min_length=1, max_length=10000)
    tono: Optional[ToneEnum] = ToneEnum.neutral
    max_tokens: Optional[int] = Field(None, ge=16, le=4096)
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)
    top_p: Optional[float] = Field(None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None


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
    model_metadata: Optional[Dict[str, Any]] = None
    requested_tone: ToneEnum
    warnings: Optional[list[str]] = None
    diff: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
