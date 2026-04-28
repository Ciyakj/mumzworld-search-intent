"""Schema definitions for search intent parsing."""
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class AgeRange(BaseModel):
    """Age range in months."""
    min: Optional[int] = Field(None, ge=0, le=240, description="Minimum age in months")
    max: Optional[int] = Field(None, ge=0, le=240, description="Maximum age in months")

    @validator("max")
    def max_gte_min(cls, v, values):
        if v is not None and "min" in values and values["min"] is not None:
            if v < values["min"]:
                raise ValueError("max must be >= min")
        return v


class BudgetRange(BaseModel):
    """Budget range in AED."""
    min: Optional[float] = Field(None, ge=0, description="Minimum budget in AED")
    max: Optional[float] = Field(None, ge=0, description="Maximum budget in AED")

    @validator("max")
    def max_gte_min(cls, v, values):
        if v is not None and "min" in values and values["min"] is not None:
            if v < values["min"]:
                raise ValueError("max must be >= min")
        return v


class SearchIntent(BaseModel):
    """Structured search intent extracted from user input."""
    
    raw_input: str = Field(..., description="Original user input")
    
    intent_normalized: Optional[str] = Field(
        None,
        description="Normalized, clarified intent in English"
    )
    
    product_category: Optional[str] = Field(
        None,
        description="Inferred product category (e.g., 'infant_nutrition', 'clothing', 'toys')"
    )
    
    age_range_months: Optional[AgeRange] = Field(
        None,
        description="Inferred age range of child in months"
    )
    
    budget_aed: Optional[BudgetRange] = Field(
        None,
        description="Inferred budget in AED"
    )
    
    urgency: Optional[str] = Field(
        "standard",
        description="Urgency level: 'standard', 'urgent', 'gift_soon'"
    )
    
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="How confident we are in this parsing (0.0 to 1.0)"
    )
    
    clarifying_question: Optional[str] = Field(
        None,
        description="Follow-up question if intent is ambiguous or out of scope"
    )
    
    languages_detected: List[str] = Field(
        default_factory=list,
        description="Languages detected (e.g., ['ar', 'en'])"
    )
    
    dialect_detected: Optional[str] = Field(
        None,
        description="Detected Arabic dialect or 'modern_standard_arabic'"
    )
    
    is_out_of_scope: bool = Field(
        default=False,
        description="Whether this query falls outside Mumzworld scope"
    )
    
    out_of_scope_reason: Optional[str] = Field(
        None,
        description="Reason if out_of_scope is True"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "raw_input": "حليب أطفال للأطفال اللي أكبر من 6 شهور، رخيص شوية",
                "intent_normalized": "seeking baby formula for infants 6+ months, budget-conscious",
                "product_category": "infant_nutrition",
                "age_range_months": {"min": 6, "max": 36},
                "budget_aed": {"min": None, "max": 200},
                "urgency": "standard",
                "confidence_score": 0.92,
                "clarifying_question": None,
                "languages_detected": ["ar"],
                "dialect_detected": "gulf_arabic",
                "is_out_of_scope": False,
                "out_of_scope_reason": None
            }
        }
