# Tooling

## Models and Tools Used

| Tool | Model/Version | Purpose |
|---|---|---|
| Groq API | llama-3.3-70b-versatile | Primary LLM inference |
| OpenRouter | llama-3.3-70b-instruct:free | Fallback provider |
| Pydantic | v2.5 | Schema validation |
| Streamlit | 1.28+ | Web UI |

---

## How I Used Them

**Groq API**
Single-shot inference with temperature=0.3 for consistent outputs. The task was structured enough that a carefully designed system prompt worked reliably without few-shot examples. Added fallback handling for markdown-wrapped JSON responses.

**Pydantic**
Schema-first: defined `SearchIntent` before writing LLM code. Field validators catch impossible states (e.g., budget max < min). Serialization via `model_dump()`.

---

## Development Workflow

1. **Schema design** — defined output fields before any LLM calls
2. **System prompt** — started minimal, added dialect list, out-of-scope patterns, language purity rule iteratively
3. **Eval-first** — wrote 14 test cases before calling the implementation "done"
4. **Failure-driven refinement** — each failing eval case pointed to a specific prompt gap

---

## Prompt Evolution

Initial prompt had no out-of-scope handling → model returned products for medical queries.

Added:
- Explicit out-of-scope categories (medical diagnosis, delivery services)
- Arabic dialect list with examples
- Language purity rule (clarifying questions must match input language)
- Confidence guidance per query type

Key prompt parameters:
```python
"temperature": 0.3      # consistency over creativity
"max_tokens": 500       # enough for JSON + reasoning
"model": "llama-3.3-70b-versatile"
```

Core system prompt is included in `intent_parser.py`. 

---

## What Worked

- Low temperature (0.3) gave consistent outputs across runs
- Explicit dialect list in system prompt → accurate gulf/egyptian/levantine detection
- Schema validation caught 2-3 cases where LLM returned wrong field types

## What Didn't

- Few-shot examples didn't improve accuracy — one-shot was sufficient
- OpenRouter returned 405 errors on initial setup (wrong endpoint format) — switched to Groq
- Confidence field returned spurious values when asked for "a number between 0 and 1" — better to embed confidence reasoning in the prompt itself
