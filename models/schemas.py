"""
Pydantic models for ETAF v2 scoring service
Defines request and response schemas for the scoring API
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator

class ChannelMetadata(BaseModel):
    """Channel metadata for source intent scoring"""
    source: Optional[str] = Field(None, description="Source channel name")
    verified: Optional[bool] = Field(False, description="Whether source is verified")
    follower_count: Optional[int] = Field(None, description="Number of followers")
    historical_accuracy: Optional[float] = Field(None, description="Historical accuracy score 0-1")
    
class ScoringRequest(BaseModel):
    """Request model for message scoring"""
    message_text: str = Field(..., description="Text content to score", min_length=1)
    lang: str = Field(..., description="Language code: 'ar' for Arabic, 'fa' for Farsi")
    channel_metadata: Optional[ChannelMetadata] = Field(
        default_factory=ChannelMetadata, 
        description="Channel metadata for source intent analysis"
    )
    
    @validator('lang')
    def validate_language(cls, v):
        if v not in ['ar', 'fa']:
            raise ValueError('Language must be "ar" (Arabic) or "fa" (Farsi)')
        return v
    
    @validator('message_text')
    def validate_message_text(cls, v):
        if not v.strip():
            raise ValueError('Message text cannot be empty')
        return v.strip()

class ETAFComponents(BaseModel):
    """ETAF scoring components breakdown"""
    temporal: int = Field(..., description="Temporal component score (0-100)", ge=0, le=100)
    operational: int = Field(..., description="Operational component score (0-100)", ge=0, le=100)
    specificity: int = Field(..., description="Specificity component score (0-100)", ge=0, le=100)
    source_intent: int = Field(..., description="Source intent component score (0-100)", ge=0, le=100)

class ScoringResponse(BaseModel):
    """Response model for message scoring"""
    etaf_score: int = Field(..., description="Total ETAF score", ge=0, le=400)
    level: str = Field(..., description="Threat level: Low, Medium, High, Critical")
    components: ETAFComponents = Field(..., description="Breakdown of ETAF components")
    rationale: str = Field(..., description="Human-readable explanation of the score")
    
    @validator('level')
    def validate_level(cls, v):
        valid_levels = ['Low', 'Medium', 'High', 'Critical']
        if v not in valid_levels:
            raise ValueError(f'Level must be one of: {", ".join(valid_levels)}')
        return v
    
    @validator('etaf_score')
    def validate_etaf_score(cls, v, values):
        # Ensure total score matches sum of components
        if 'components' in values:
            components = values['components']
            expected_total = (
                components.temporal + 
                components.operational + 
                components.specificity + 
                components.source_intent
            )
            if abs(v - expected_total) > 5:  # Allow small rounding differences
                raise ValueError(f'Total score {v} does not match component sum {expected_total}')
        return v

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Specific error code")