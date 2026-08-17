"""Pydantic request/response models for the API."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, Literal, Optional


class PredictRequest(BaseModel):
    """Churn prediction request body.

    All fields are optional (with sensible defaults for missing features).
    The trained model uses OneHotEncoder(handle_unknown='ignore') so unseen
    categories will be treated as zeros.
    """

    tenure_months: Optional[int] = Field(default=0, ge=0, le=100, alias="tenure")
    monthly_charges: Optional[float] = Field(default=50.0, ge=0, le=200)
    total_charges: Optional[float] = Field(default=600.0, ge=0)
    contract_type: Optional[Literal["month-to-month", "one year", "two year"]] = Field(
        default="month-to-month", alias="contract"
    )
    payment_method: Optional[Literal["electronic_check", "mailed_check", "bank_transfer", "credit_card"]] = Field(
        default="electronic_check", alias="payment_method"
    )
    internet_service: Optional[Literal["DSL", "Fiber optic", "No"]] = Field(default="Fiber optic")
    gender: Optional[Literal["Male", "Female"]] = Field(default="Male")
    senior_citizen: Optional[int] = Field(default=0, ge=0, le=1)
    partner: Optional[Literal["Yes", "No"]] = Field(default="No")
    dependents: Optional[Literal["Yes", "No"]] = Field(default="No")
    phone_service: Optional[Literal["Yes", "No"]] = Field(default="Yes")
    multiple_lines: Optional[Literal["Yes", "No", "No phone service"]] = Field(default="No")
    online_security: Optional[Literal["Yes", "No", "No internet service"]] = Field(default="No")
    online_backup: Optional[Literal["Yes", "No", "No internet service"]] = Field(default="No")
    device_protection: Optional[Literal["Yes", "No", "No internet service"]] = Field(default="No")
    tech_support: Optional[Literal["Yes", "No", "No internet service"]] = Field(default="No")
    streaming_tv: Optional[Literal["Yes", "No", "No internet service"]] = Field(default="No")
    streaming_movies: Optional[Literal["Yes", "No", "No internet service"]] = Field(default="No")
    paperless_billing: Optional[Literal["Yes", "No"]] = Field(default="Yes")

    class Config:
        populate_by_name = True


class PredictResponse(BaseModel):
    """Churn prediction response."""

    prediction: Literal["churn", "no_churn"]
    probability: float = Field(ge=0.0, le=1.0)
    model_version: str
    model_stage: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: Literal["healthy", "degraded", "unhealthy"]
    db_connected: bool
    model_loaded: bool
    model_name: Optional[str] = None
    model_version: Optional[str] = None
    model_stage: Optional[str] = None


class ModelInfoResponse(BaseModel):
    """Detailed model information."""

    name: str
    version: str
    stage: str
    run_id: Optional[str] = None
    metrics: Dict[str, float] = {}