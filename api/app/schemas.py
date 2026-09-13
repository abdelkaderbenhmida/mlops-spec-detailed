# TODO: medium - Add type hints where missing
# TODO: low - Add comprehensive docstring
# TODO: low - Add error handling for edge cases
"""Pydantic request/response models for the predictive maintenance API."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, Literal, Optional


class PredictRequest(BaseModel):
    """Predictive maintenance prediction request.

    Equipment sensor data for failure prediction within 30 days.
    """

    equipment_type: Literal["pump", "motor", "compressor", "turbine"] = Field(
        default="pump", description="Type of industrial equipment"
    )
    age_months: int = Field(default=60, ge=1, le=300, description="Equipment age in months")
    operating_hours: float = Field(default=20000.0, ge=0, le=200000, description="Total operating hours")
    maintenance_history: int = Field(default=5, ge=0, le=100, description="Number of past maintenance events")
    sensor_temp: float = Field(default=70.0, ge=0, le=200, description="Temperature sensor reading (°C)")
    sensor_vibration: float = Field(default=1.0, ge=0, le=15, description="Vibration level (mm/s RMS)")
    sensor_pressure: float = Field(default=35.0, ge=0, le=100, description="Pressure sensor reading (bar)")
    sensor_humidity: float = Field(default=50.0, ge=0, le=100, description="Humidity sensor reading (%)")

    class Config:
        populate_by_name = True


class PredictResponse(BaseModel):
    """Predictive maintenance prediction response."""

    prediction: Literal["failure", "no_failure"]
    probability: float = Field(ge=0.0, le=1.0)
    risk_level: str = Field(description="Risk tier: critical, high, medium, low")
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
