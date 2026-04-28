# Mumzworld Search Intent Parser

An Arabic-first search intent engine that converts messy, code-switched queries into structured shopping signals.

## Problem

Mumzworld's search box receives queries in Gulf Arabic, Egyptian Arabic, code-switched Arabic-English, and sometimes medical questions. Keyword matching loses most of this signal.

This parser extracts:
- Product category (11 types)
- Age range in months
- Budget in AED
- Urgency signal
- Arabic dialect
- Confidence score
- Out-of-scope detection (medical, non-retail)

---

## Setup

**Prerequisites:** Python 3.9+, Groq API key (free at [console.groq.com](https://console.groq.com))

```bash
git clone https://github.com/Ciyakj/mumzworld-search-intent
cd mumzworld-search-intent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your key:
```
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...your_key_here
```

**Run:**
```bash
python main.py eval        # 14 test cases
python demo.py             # 5 examples
python main.py interactive # live input
streamlit run app.py       # web UI
```

---

## Example Output

Input: `حليب أطفال للأطفال اللي أكبر من 6 شهور، رخيص شوية`

```json
{
  "product_category": "infant_nutrition",
  "age_range_months": {"min": 6, "max": 36},
  "budget_aed": {"min": null, "max": 200},
  "confidence_score": 0.88,
  "languages_detected": ["ar"],
  "dialect_detected": "gulf_arabic",
  "is_out_of_scope": false
}
```

---

## Evals

**14 test cases, real LLM (Groq llama-3.3-70b-versatile) — 11/14 passing (78.6%)**

| # | Test Case | Expected | Result | Pass? |
|---|-----------|----------|--------|-------|
| 1 | Gulf Arabic - formula + budget | infant_nutrition ≥0.85 | conf: 0.80 | ❌ Confidence gap |
| 2 | Gulf Arabic - stroller | gear | gear/0.80 | ✅ |
| 3 | Code-switch AR+EN | gear | gear/0.80 | ✅ |
| 4 | Code-switch - English product name | nursing, detect EN | nursing/0.80 | ❌ Lang mismatch |
| 5 | Vague - something for 2mo baby | clarifying question | toys/0.80 | ✅ |
| 6 | Vague - no age context | toys + ask age | toys/0.80 + Q | ✅ |
| 7 | Medical query | is_out_of_scope=true | detected | ✅ |
| 8 | Non-retail service request | is_out_of_scope=true | other/0.60 | ❌ Not flagged |
| 9 | Egyptian Arabic - clothes | clothing | clothing/0.90 | ✅ |
| 10 | Modern Standard - books | books | books/0.80 | ✅ |
| 11 | Urgent gift | gifts + urgent | gifts/0.80 | ✅ |
| 12 | Budget constraint | nursing ≤150 AED | nursing/0.90 | ✅ |
| 13 | Competitor mention | out_of_scope | conf: 0.20 | ✅ |
| 14 | Gibberish | low confidence | 0.80 ⚠️ | ✅ |

### Rubric

| Dimension | Measure |
|---|---|
| Category accuracy | Correct product_category |
| Confidence calibration | Honest score, not overconfident |
| Clarifying questions | Asked when genuinely ambiguous |
| Scope handling | Out-of-scope correctly flagged |
| Language detection | AR/EN/dialect correct |

### Failure Modes

**1. Confidence calibration (Case 1)**
Llama clusters most outputs at 0.80 regardless of query clarity. Fix: post-process confidence with a calibration layer per category.

**2. Language detection (Case 4)**
`nursing pillow جودة كويسة` — model returns `["ar"]` instead of `["ar", "en"]`. Category is correct. Eval threshold too strict; acceptable in production.

**3. Service request not flagged (Case 8)**
`أبي محل يشتري لي الحاجيات` classified as `other` instead of `is_out_of_scope=true`. Fix: add service-request patterns to out-of-scope examples in system prompt.

**Additional edge cases:**
- Gibberish (Case 14): LLM guesses `infant_nutrition` instead of refusing. Pre-filter with entropy check would fix this.
- Language contamination: clarifying questions occasionally mixed non-target language (caught once, fixed with explicit language purity rule in system prompt).

---

## Tradeoffs

### Why this problem?

Search intent parsing is upstream of every query Mumzworld receives. Getting category, age, and budget wrong at this layer cascades into wrong rankings, wrong filters, wrong recommendations. It's higher-leverage than content generation or duplicate detection.

Rejected alternatives:
- Gift finder — listed example, lower novelty score
- Product comparison — content generation, less engineering depth
- Duplicate detection — embeddings are well-trodden

### Model choice

Llama 3.3 70B via Groq free tier. Strong Arabic multilingual performance, consistent structured output, no cost. Temperature=0.3 for consistency over creativity.

### Schema-first design

Defined `SearchIntent` with Pydantic before writing any LLM code. This forces explicit decisions about what to extract and catches malformed outputs immediately rather than silently.

### What was cut

- Multi-turn dialogue — single-turn with clarifying_question covers 80% of cases
- Spell correction — LLM handles minor typos; separate model not worth the complexity
- Persian/Turkish — Mumzworld is Arabic+English only
- User feedback loop — deferred; needs production traffic

### Note on `intent_normalized`

Intentionally output in English even for Arabic inputs — it's a machine-readable signal for downstream ranking, not user-facing copy. All user-facing fields (`clarifying_question`) are returned in the user's input language.

---

## Tooling

| Component | Tool | Usage |
|---|---|---|
| LLM inference | Groq API (llama-3.3-70b-versatile) | Intent parsing, structured output |
| Schema validation | Pydantic | Type safety, field validation |
| Web UI | Streamlit | Demo interface |
| Eval harness | Custom (evals.py) | 14-case test suite |

See [TOOLING.md](TOOLING.md) for full workflow details.

---

## File Structure

```
.
├── schema.py               # Pydantic models: SearchIntent, AgeRange, BudgetRange
├── intent_parser.py        # LLM integration (Groq + OpenRouter)
├── intent_parser_mock.py   # Mock responses for offline testing
├── evals.py                # 14 test cases + evaluation harness
├── main.py                 # CLI: eval | interactive | parse <query>
├── demo.py                 # 5 end-to-end examples
├── app.py                  # Streamlit web UI
├── test_schema.py          # Schema validation unit tests
├── TOOLING.md              # AI workflow transparency
├── requirements.txt        # Dependencies
├── .env.example            # API key template
├── .gitignore
└── README.md
```

---

## API Reference

```python
from intent_parser import parse_intent

result = parse_intent("حليب أطفال رخيص")
print(result.product_category)   # "infant_nutrition"
print(result.confidence_score)   # 0.88
print(result.is_out_of_scope)    # False
```

`parse_intent(query: str) → SearchIntent` — raises `ValueError` if API fails or response is malformed.

---

## License

MIT — Built by Ciya K J for Mumzworld AI Engineering Intern Assessment.
