"""Mock evaluator for testing without API calls."""
import json
from schema import SearchIntent, AgeRange, BudgetRange


# Mock responses for each test case (pre-computed to save API calls during testing)
MOCK_RESPONSES = {
    "حليب أطفال للأطفال اللي أكبر من 6 شهور، رخيص شوية": {
        "intent_normalized": "seeking baby formula for infants 6+ months, budget-conscious",
        "product_category": "infant_nutrition",
        "age_range_months": {"min": 6, "max": 36},
        "budget_aed": {"min": None, "max": 200},
        "urgency": "standard",
        "confidence_score": 0.92,
        "languages_detected": ["ar"],
        "dialect_detected": "gulf_arabic",
    },
    "أبي عربة أطفال خفيفة وسهل طيها للسفر": {
        "intent_normalized": "seeking lightweight, foldable baby stroller for travel",
        "product_category": "gear",
        "age_range_months": None,
        "budget_aed": None,
        "urgency": "standard",
        "confidence_score": 0.88,
        "languages_detected": ["ar"],
        "dialect_detected": "gulf_arabic",
    },
    "أبي high chair للطفل عمره 8 months، مش مكلّف كتير": {
        "intent_normalized": "seeking high chair for 8-month-old, budget-conscious",
        "product_category": "gear",
        "age_range_months": {"min": 8, "max": 8},
        "budget_aed": {"min": None, "max": 300},
        "urgency": "standard",
        "confidence_score": 0.85,
        "languages_detected": ["ar", "en"],
        "dialect_detected": "gulf_arabic",
    },
    "عندك nursing pillow جودة كويسة وسعر معقول؟": {
        "intent_normalized": "seeking nursing pillow with good quality and reasonable price",
        "product_category": "nursing",
        "age_range_months": None,
        "budget_aed": {"min": None, "max": 250},
        "urgency": "standard",
        "confidence_score": 0.82,
        "languages_detected": ["ar", "en"],
        "dialect_detected": "gulf_arabic",
    },
    "شيء حلو للطفل اللي عمره شهرين": {
        "intent_normalized": "something for 2-month-old (needs clarification on category)",
        "product_category": None,
        "age_range_months": {"min": 2, "max": 2},
        "budget_aed": None,
        "urgency": "standard",
        "confidence_score": 0.45,
        "clarifying_question": "Are you looking for toys, clothing, books, gear, or health products for your 2-month-old?",
        "languages_detected": ["ar"],
        "dialect_detected": "gulf_arabic",
    },
    "ألعاب جميلة وآمنة": {
        "intent_normalized": "seeking beautiful, safe toys (age range unclear)",
        "product_category": "toys",
        "age_range_months": None,
        "budget_aed": None,
        "urgency": "standard",
        "confidence_score": 0.55,
        "clarifying_question": "What is the age of the child? This helps us recommend age-appropriate toys.",
        "languages_detected": ["ar"],
        "dialect_detected": "gulf_arabic",
    },
    "الطفل عنده حمى وسعال، شو الحل؟": {
        "intent_normalized": None,
        "product_category": None,
        "age_range_months": None,
        "budget_aed": None,
        "urgency": "standard",
        "confidence_score": 0.10,
        "clarifying_question": "This sounds like a medical concern. Please consult a pediatrician. I can help you find health products like thermometers or humidifiers if needed.",
        "languages_detected": ["ar"],
        "dialect_detected": "gulf_arabic",
        "is_out_of_scope": True,
        "out_of_scope_reason": "Seeking medical diagnosis/advice, not product search",
    },
    "أبي محل يشتري لي الحاجيات من البيت": {
        "intent_normalized": None,
        "product_category": None,
        "age_range_months": None,
        "budget_aed": None,
        "urgency": "standard",
        "confidence_score": 0.15,
        "languages_detected": ["ar"],
        "dialect_detected": "gulf_arabic",
        "is_out_of_scope": True,
        "out_of_scope_reason": "Seeking personal shopping service, not product search",
    },
    "هاشتري ملابس أطفال لبنتي، عمرها 18 شهر": {
        "intent_normalized": "seeking children's clothes for 18-month-old daughter",
        "product_category": "clothing",
        "age_range_months": {"min": 18, "max": 18},
        "budget_aed": None,
        "urgency": "standard",
        "confidence_score": 0.90,
        "languages_detected": ["ar"],
        "dialect_detected": "egyptian_arabic",
    },
    "أريد كتب أطفال تربوية وآمنة من السموم": {
        "intent_normalized": "seeking educational children's books, safe from toxins",
        "product_category": "books",
        "age_range_months": None,
        "budget_aed": None,
        "urgency": "standard",
        "confidence_score": 0.85,
        "languages_detected": ["ar"],
        "dialect_detected": "modern_standard_arabic",
    },
    "محتاجة هدية للطفل غدا بأسرع وقت!": {
        "intent_normalized": "seeking gift for child, needed tomorrow ASAP",
        "product_category": "gifts",
        "age_range_months": None,
        "budget_aed": None,
        "urgency": "gift_soon",
        "confidence_score": 0.75,
        "clarifying_question": "What age is the child? This helps us suggest appropriate gift options.",
        "languages_detected": ["ar"],
        "dialect_detected": "gulf_arabic",
    },
    "nursing bra تحت 150 درهم، مريحة وجودة كويسة": {
        "intent_normalized": "seeking nursing bra under 150 AED, comfortable with good quality",
        "product_category": "nursing",
        "age_range_months": None,
        "budget_aed": {"min": None, "max": 150},
        "urgency": "standard",
        "confidence_score": 0.88,
        "languages_detected": ["ar", "en"],
        "dialect_detected": "gulf_arabic",
    },
    "same price as amazon": {
        "intent_normalized": None,
        "product_category": None,
        "age_range_months": None,
        "budget_aed": None,
        "urgency": "standard",
        "confidence_score": 0.15,
        "languages_detected": ["en"],
        "dialect_detected": None,
        "is_out_of_scope": True,
        "out_of_scope_reason": "Price comparison to competitor - not a product search",
    },
    "حليب فللللل أطفال غريب غريب 🎉🎉🎉": {
        "intent_normalized": None,
        "product_category": None,
        "age_range_months": None,
        "budget_aed": None,
        "urgency": "standard",
        "confidence_score": 0.15,
        "clarifying_question": "Your query appears to contain gibberish or unclear text. Could you rephrase?",
        "languages_detected": ["ar"],
        "dialect_detected": "gulf_arabic",
        "is_out_of_scope": False,
    },
}


def parse_intent_mock(user_query: str) -> SearchIntent:
    """
    Mock version of parse_intent that returns pre-computed responses.
    
    This is useful for testing without API calls during development.
    """
    if user_query not in MOCK_RESPONSES:
        raise ValueError(f"No mock response for query: {user_query}")
    
    response_data = MOCK_RESPONSES[user_query].copy()
    response_data["raw_input"] = user_query
    response_data.setdefault("urgency", "standard")
    response_data.setdefault("confidence_score", 0.5)
    response_data.setdefault("languages_detected", [])
    response_data.setdefault("is_out_of_scope", False)
    
    # Handle nested objects
    if response_data.get("age_range_months") and isinstance(response_data["age_range_months"], dict):
        response_data["age_range_months"] = AgeRange(**response_data["age_range_months"])
    if response_data.get("budget_aed") and isinstance(response_data["budget_aed"], dict):
        response_data["budget_aed"] = BudgetRange(**response_data["budget_aed"])
    
    return SearchIntent(**response_data)


def test_mock():
    """Quick test of mock responses."""
    print("Testing mock responses...\n")
    for query in list(MOCK_RESPONSES.keys())[:3]:
        result = parse_intent_mock(query)
        print(f"Query: {query[:50]}...")
        print(f"Category: {result.product_category}, Confidence: {result.confidence_score}\n")
    print("✓ Mock responses loaded successfully!")


if __name__ == "__main__":
    test_mock()
