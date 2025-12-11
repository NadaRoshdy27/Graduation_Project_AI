"""
Pydantic models for API request/response validation.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class CustomerRecommendRequest(BaseModel):
    """Request model for customer product recommendations."""
    customer_id: int = Field(..., description="Customer ID", ge=1)
    top_k: int = Field(5, description="Number of recommendations to return", ge=1, le=50)


class ProductRecommendation(BaseModel):
    """Single product recommendation."""
    product_id: int
    name: str
    category: str
    subcategory: str
    price: float
    score: float = Field(..., description="Recommendation score")


class CustomerRecommendResponse(BaseModel):
    """Response model for customer product recommendations."""
    customer_id: int
    recommendations: List[ProductRecommendation]
    total_recommendations: int


class OwnerRecommendRequest(BaseModel):
    """Request model for brand owner raw material recommendations."""
    owner_id: int = Field(..., description="Brand owner ID", ge=1)
    top_k: int = Field(5, description="Number of recommendations to return", ge=1, le=50)


class MaterialRecommendation(BaseModel):
    """Single raw material recommendation."""
    material_id: int
    name: str
    category: str
    unit_cost: float
    score: float = Field(..., description="Recommendation score")
    reason: Optional[str] = Field(None, description="Reason for recommendation")


class OwnerRecommendResponse(BaseModel):
    """Response model for brand owner raw material recommendations."""
    owner_id: int
    recommendations: List[MaterialRecommendation]
    total_recommendations: int


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    app_name: str
    version: str
    models_loaded: dict


class RetrainResponse(BaseModel):
    """Model retraining response."""
    status: str
    message: str
    models_retrained: List[str]


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
