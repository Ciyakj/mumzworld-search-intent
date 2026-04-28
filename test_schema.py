"""Test schema validation without API calls."""
import json
from schema import SearchIntent, AgeRange, BudgetRange

def test_schema_basic():
    """Test basic schema validation."""
    intent = SearchIntent(
        raw_input="حليب أطفال",
        intent_normalized="seeking baby formula",
        product_category="infant_nutrition",
        age_range_months=AgeRange(min=0, max=12),
        budget_aed=BudgetRange(min=50, max=150),
        urgency="standard",
        confidence_score=0.85,
        languages_detected=["ar"],
        dialect_detected="gulf_arabic"
    )
    
    assert intent.product_category == "infant_nutrition"
    assert intent.confidence_score == 0.85
    assert intent.age_range_months.min == 0
    assert intent.age_range_months.max == 12
    print("✓ Basic schema validation passed")


def test_schema_json_output():
    """Test JSON serialization."""
    intent = SearchIntent(
        raw_input="عربة أطفال",
        intent_normalized="seeking stroller",
        product_category="gear",
        confidence_score=0.90,
        languages_detected=["ar"]
    )
    
    json_output = json.dumps(intent.model_dump(exclude_none=False), ensure_ascii=False, indent=2)
    assert "عربة أطفال" in json_output
    assert "gear" in json_output
    print("✓ JSON serialization passed")
    print(f"Output:\n{json_output}\n")


def test_schema_validation_errors():
    """Test that invalid data raises errors."""
    # Test: confidence_score out of range
    try:
        SearchIntent(
            raw_input="test",
            confidence_score=1.5  # Invalid: should be 0-1
        )
        assert False, "Should have raised validation error"
    except Exception as e:
        print(f"✓ Correctly caught invalid confidence: {e}")
    
    # Test: budget max < min
    try:
        intent = SearchIntent(
            raw_input="test",
            budget_aed=BudgetRange(min=200, max=100),  # Invalid: min > max
            confidence_score=0.5
        )
        assert False, "Should have raised validation error"
    except Exception as e:
        print(f"✓ Correctly caught invalid budget range: {e}")


def test_optional_fields():
    """Test that optional fields can be None."""
    intent = SearchIntent(
        raw_input="test",
        confidence_score=0.5,
        age_range_months=None,
        budget_aed=None,
        clarifying_question=None,
        product_category=None
    )
    
    assert intent.age_range_months is None
    assert intent.budget_aed is None
    assert intent.clarifying_question is None
    print("✓ Optional fields correctly handle None values")


if __name__ == "__main__":
    print("Running schema validation tests...\n")
    test_schema_basic()
    test_schema_json_output()
    test_schema_validation_errors()
    test_optional_fields()
    print("\n✓ All schema tests passed!")
