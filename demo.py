#!/usr/bin/env python3
"""
Demo script for Mumzworld Search Intent Parser.
Shows 5+ example inputs including one that returns low confidence/uncertainty.

To run this demo:
1. Set your API key in .env (OPENROUTER_API_KEY or GROQ_API_KEY)
2. python demo.py
"""
import json
import sys
from intent_parser import parse_intent

# Fix encoding for Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

# These are the 5 demonstration queries
DEMO_QUERIES = [
    "حليب أطفال للأطفال اللي أكبر من 6 شهور، رخيص شوية",
    "أبي high chair للطفل عمره 8 months، مش مكلّف كتير",
    "شيء حلو للطفل اللي عمره شهرين",  # VAGUE - shows uncertainty
    "الطفل عنده حمى وسعال، شو الحل؟",    # OUT OF SCOPE - shows refusal
    "nursing bra تحت 150 درهم، مريحة وجودة كويسة",
]


def main():
    """Run demo with real LLM."""
    print("\n" + "="*80)
    print("MUMZWORLD SEARCH INTENT PARSER - DEMO")
    print("="*80 + "\n")
    print("Using REAL LLM (Groq llama-3.3-70b-versatile)")
    print("="*80 + "\n")
    
    for i, query in enumerate(DEMO_QUERIES, 1):
        print(f"\n{'='*80}")
        print(f"QUERY #{i}")
        print(f"{'='*80}")
        print(f"\nInput (Arabic): {query}")
        
        try:
            # Using real Groq LLM
            result = parse_intent(query)
            
            # Pretty print JSON
            output = result.model_dump(exclude_none=False)
            print(f"\nStructured Output:\n")
            print(json.dumps(output, indent=2, ensure_ascii=False))
            
            # Highlight key fields
            print(f"\n📊 ANALYSIS:")
            print(f"   Category: {result.product_category or '(Not identified)'}")
            print(f"   Confidence: {result.confidence_score:.0%}")
            if result.age_range_months:
                print(f"   Age Range: {result.age_range_months.min}–{result.age_range_months.max} months")
            else:
                print(f"   Age Range: Not specified")
            if result.budget_aed:
                print(f"   Budget: ≤{result.budget_aed.max or '?'} AED")
            else:
                print(f"   Budget: Not specified")
            print(f"   Urgency: {result.urgency}")
            print(f"   Languages: {', '.join(result.languages_detected)}")
            print(f"   Dialect: {result.dialect_detected}")
            
            if result.is_out_of_scope:
                print(f"\n⚠️  OUT OF SCOPE")
                print(f"   Reason: {result.out_of_scope_reason}")
            
            if result.clarifying_question:
                print(f"\n❓ CLARIFYING QUESTION:")
                print(f"   {result.clarifying_question}")
            
            if result.confidence_score < 0.6:
                print(f"\n⚡ LOW CONFIDENCE - Parser is uncertain about this query")
                
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
    
    print(f"\n{'='*80}")
    print("Demo complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
