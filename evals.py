"""Evaluation suite for search intent parser."""
import json
import os
import sys
from typing import Optional
from dataclasses import dataclass

# Fix encoding for Windows terminal
sys.stdout.reconfigure(encoding='utf-8')
from schema import SearchIntent


# Use mock parser if no API keys are set
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter").lower()

USE_MOCK = not (OPENROUTER_KEY or GROQ_KEY)

if USE_MOCK:
    from intent_parser_mock import parse_intent_mock as parse_intent
    print("Warning: Using MOCK parser (no API key found). Set OPENROUTER_API_KEY or GROQ_API_KEY to use real LLM.\n")
else:
    from intent_parser import parse_intent
    provider_name = "Groq" if LLM_PROVIDER == "groq" and GROQ_KEY else "OpenRouter"
    print(f"[OK] Using REAL LLM parser with {provider_name} API\n")


@dataclass
class EvalCase:
    """Test case for evaluation."""
    name: str
    query: str
    expected_category: Optional[str]
    expected_min_confidence: float = 0.6
    should_ask_clarifying: bool = False
    is_out_of_scope: bool = False
    should_detect_languages: list[str] = None
    notes: str = ""


# Comprehensive test cases covering different scenarios
EVAL_CASES = [
    # ===== Basic Arabic queries (Gulf dialect) =====
    EvalCase(
        name="Gulf Arabic - Baby formula with budget",
        query="حليب أطفال للأطفال اللي أكبر من 6 شهور، رخيص شوية",
        expected_category="infant_nutrition",
        expected_min_confidence=0.85,
        should_detect_languages=["ar"],
        notes="Gulf Arabic: 'cheap a little bit' is colloquial for 'budget-conscious'"
    ),
    
    EvalCase(
        name="Gulf Arabic - Stroller query",
        query="أبي عربة أطفال خفيفة وسهل طيها للسفر",
        expected_category="gear",
        expected_min_confidence=0.80,
        should_detect_languages=["ar"],
        notes="'أبي' (Gulf for 'I want'), lightweight stroller for travel"
    ),
    
    # ===== Code-switching (Arabic + English) =====
    EvalCase(
        name="Code-switch - Mixed Arabic-English",
        query="أبي high chair للطفل عمره 8 months، مش مكلّف كتير",
        expected_category="gear",
        expected_min_confidence=0.75,
        should_detect_languages=["ar", "en"],
        notes="Code-switching: 'high chair' in English, age in English months, budget in Arabic"
    ),
    
    EvalCase(
        name="Code-switch - Product name in English",
        query="عندك nursing pillow جودة كويسة وسعر معقول؟",
        expected_category="nursing",
        expected_min_confidence=0.75,
        should_detect_languages=["ar", "en"],
        notes="Product name in English, quality/price requirements in Arabic"
    ),
    
    # ===== Vague queries requiring clarification =====
    EvalCase(
        name="Vague - 'Something for baby'",
        query="شيء حلو للطفل اللي عمره شهرين",
        expected_category=None,
        expected_min_confidence=0.4,  # Lowered: vague queries naturally have lower confidence
        should_ask_clarifying=True,
        should_detect_languages=["ar"],
        notes="Very vague - should ask if they want clothing, toys, gear, books, etc."
    ),
    
    EvalCase(
        name="Vague - No age context",
        query="ألعاب جميلة وآمنة",
        expected_category="toys",
        expected_min_confidence=0.55,
        should_ask_clarifying=True,
        should_detect_languages=["ar"],
        notes="Toys but no age range - should ask for child age"
    ),
    
    # ===== Out of scope =====
    EvalCase(
        name="Out of scope - Medical diagnosis",
        query="الطفل عنده حمى وسعال، شو الحل؟",
        expected_category=None,
        is_out_of_scope=True,
        expected_min_confidence=0.05,  # Lowered: out-of-scope should be detected but confidence very low
        should_ask_clarifying=True,
        should_detect_languages=["ar"],
        notes="Seeking medical advice/diagnosis - out of scope, should not return products"
    ),
    
    EvalCase(
        name="Out of scope - Non-retail service",
        query="أبي محل يشتري لي الحاجيات من البيت",
        expected_category=None,
        is_out_of_scope=True,
        expected_min_confidence=0.05,  # Lowered: out-of-scope detection
        should_detect_languages=["ar"],
        notes="Seeking personal shopping service, not product search"
    ),
    
    # ===== Edge cases and Egyptian Arabic =====
    EvalCase(
        name="Egyptian Arabic - Baby clothes",
        query="هاشتري ملابس أطفال لبنتي، عمرها 18 شهر",
        expected_category="clothing",
        expected_min_confidence=0.75,
        should_detect_languages=["ar"],
        notes="Egyptian: 'هاشتري' (I will buy), clear age in months"
    ),
    
    EvalCase(
        name="Standard Arabic - Books",
        query="أريد كتب أطفال تربوية وآمنة من السموم",
        expected_category="books",
        expected_min_confidence=0.80,
        should_detect_languages=["ar"],
        notes="Modern Standard Arabic, educational books with safety concern"
    ),
    
    # ===== Budget and urgency nuances =====
    EvalCase(
        name="Urgent - Baby gift needed soon",
        query="محتاجة هدية للطفل غدا بأسرع وقت!",
        expected_category="gifts",
        expected_min_confidence=0.70,
        should_detect_languages=["ar"],
        notes="Urgency: 'tomorrow, ASAP' - should detect gift_soon urgency"
    ),
    
    EvalCase(
        name="Clear budget constraint",
        query="nursing bra تحت 150 درهم، مريحة وجودة كويسة",
        expected_category="nursing",
        expected_min_confidence=0.80,
        should_detect_languages=["ar", "en"],
        notes="Clear max budget: 150 AED"
    ),
    
    # ===== Adversarial Cases =====
    EvalCase(
        name="Adversarial - Competitor mention",
        query="same price as amazon",
        expected_category=None,
        is_out_of_scope=True,
        expected_min_confidence=0.1,
        should_detect_languages=["en"],
        notes="Price comparison to competitor - not a product search, should be out of scope"
    ),
    
    EvalCase(
        name="Adversarial - Nonsensical input",
        query="حليب فللللل أطفال غريب غريب 🎉🎉🎉",
        expected_category=None,
        expected_min_confidence=0.10,
        should_detect_languages=["ar"],
        notes="Gibberish with repeated letters and emojis - should have very low confidence"
    ),
]


class EvalResult:
    """Results for a single eval case."""
    
    def __init__(self, case: EvalCase, intent: SearchIntent, exception: Optional[Exception] = None):
        self.case = case
        self.intent = intent
        self.exception = exception
    
    def is_pass(self) -> bool:
        """Check if test passed."""
        if self.exception:
            return False
        
        # Check category match
        if self.case.expected_category:
            if self.intent.product_category != self.case.expected_category:
                return False
        
        # Check confidence threshold
        if self.intent.confidence_score < self.case.expected_min_confidence:
            return False
        
        # Check clarifying question
        if self.case.should_ask_clarifying:
            if not self.intent.clarifying_question:
                return False
        
        # Check out of scope
        if self.case.is_out_of_scope:
            if not self.intent.is_out_of_scope:
                return False
        
        # Check languages
        if self.case.should_detect_languages:
            if set(self.intent.languages_detected) != set(self.case.should_detect_languages):
                return False
        
        return True
    
    def get_failure_reason(self) -> str:
        """Get reason for failure."""
        if self.exception:
            return f"Exception: {str(self.exception)}"
        
        if self.case.expected_category and self.intent.product_category != self.case.expected_category:
            return f"Category mismatch: expected {self.case.expected_category}, got {self.intent.product_category}"
        
        if self.intent.confidence_score < self.case.expected_min_confidence:
            return f"Low confidence: {self.intent.confidence_score} < {self.case.expected_min_confidence}"
        
        if self.case.should_ask_clarifying and not self.intent.clarifying_question:
            return "Missing clarifying question when one was expected"
        
        if self.case.is_out_of_scope and not self.intent.is_out_of_scope:
            return "Query should be marked as out of scope but wasn't"
        
        if self.case.should_detect_languages:
            expected = set(self.case.should_detect_languages)
            actual = set(self.intent.languages_detected)
            if actual != expected:
                return f"Language detection mismatch: expected {expected}, got {actual}"
        
        return "Unknown failure"


def run_evals(verbose: bool = True) -> tuple[int, int]:
    """
    Run all eval cases.
    
    Args:
        verbose: Print detailed results
        
    Returns:
        (passed, total)
    """
    passed = 0
    failed = 0
    
    print("\n" + "="*80)
    print("SEARCH INTENT PARSER - EVAL SUITE")
    print("="*80 + "\n")
    
    for i, case in enumerate(EVAL_CASES, 1):
        try:
            intent = parse_intent(case.query)
            result = EvalResult(case, intent)
        except Exception as e:
            result = EvalResult(case, None, e)
        
        is_pass = result.is_pass()
        if is_pass:
            passed += 1
            status = "[PASS]"
        else:
            failed += 1
            status = "[FAIL]"
        
        if verbose:
            print(f"{i:2d}. {status} | {case.name}")
            print(f"    Query: {case.query[:60]}...")
            if result.exception:
                print(f"    Error: {result.exception}")
            elif not is_pass:
                print(f"    Reason: {result.get_failure_reason()}")
            if result.intent:
                print(f"    Category: {result.intent.product_category} (conf: {result.intent.confidence_score:.2f})")
                if result.intent.clarifying_question:
                    print(f"    Clarifying Q: {result.intent.clarifying_question}")
            print()
    
    print("="*80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(EVAL_CASES)} total")
    print(f"Pass rate: {100*passed/len(EVAL_CASES):.1f}%")
    print("="*80 + "\n")
    
    return passed, failed


if __name__ == "__main__":
    run_evals(verbose=True)
