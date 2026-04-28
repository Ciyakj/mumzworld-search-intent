"""Search intent parser using LLM - supports OpenRouter and Groq."""
import os
import json
from typing import Optional, Literal
import requests
from schema import SearchIntent
from dotenv import load_dotenv

load_dotenv()

# Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openrouter").lower()  # "openrouter" or "groq"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# System prompt optimized for search intent parsing
SYSTEM_PROMPT = """You are an expert search intent parser for Mumzworld, a major e-commerce platform for mothers in the Middle East (serves English and Arabic speakers).

Your task: Parse user search queries in English and/or Arabic (including code-switching and dialects) into structured search intent.

CRITICAL RULES:
1. NEVER translate Arabic to English for the user - they are the inputs, keep them as-is in intent_normalized
2. DO normalize the intent: clarify vague phrases, standardize dialect variations
3. Always try to extract: product category, age range (if child-related), budget, urgency
4. Confidence: Be honest about uncertainty. Lower confidence when:
   - Input is vague or ambiguous
   - Multiple interpretations exist
   - Dialect is hard to parse
   - Budget/age mentions are implicit or unclear
5. Ask clarifying questions when:
   - Intent is genuinely ambiguous (multiple valid interpretations)
   - Child age range is critical but missing
   - Out of scope (e.g., asking for medical advice not product recommendations)
6. out_of_scope cases:
   - Medical diagnosis requests ("أبني عنده ألم في البطن" = asking for diagnosis)
   - Requests for non-retail services
   - Price comparisons across retailers (not searching for products to buy)

PRODUCT CATEGORIES (use these when applicable):
- infant_nutrition (formula, foods)
- clothing (baby clothes, shoes)
- gear (strollers, car seats, carriers)
- nursery (furniture, bedding)
- toys (age-appropriate toys)
- health_hygiene (diapers, wipes, bathing)
- books (children's books)
- gifts (general gift searches)
- nursing (maternity, nursing supplies)
- skincare (baby/mom skincare)
- other

ARABIC DIALECTS to detect:
- gulf_arabic (خليجي) - used in UAE, Saudi, Kuwait
- egyptian_arabic (مصري)
- levantine_arabic (شامي)
- modern_standard_arabic (فصحى)

LANGUAGE PURITY:
- If input query is in Arabic, clarifying_question must be in Arabic
- If input query is in English, clarifying_question must be in English
- NEVER mix languages (no Russian, French, or any other language in responses)
- intent_normalized should preserve the language of the original query

Return ONLY valid JSON matching this schema:
{
  "raw_input": "...",
  "intent_normalized": "...",
  "product_category": "...",
  "age_range_months": {"min": X, "max": Y} or null,
  "budget_aed": {"min": X, "max": Y} or null,
  "urgency": "standard|urgent|gift_soon",
  "confidence_score": 0.0-1.0,
  "clarifying_question": "..." or null,
  "languages_detected": ["ar", "en"],
  "dialect_detected": "gulf_arabic|egyptian_arabic|levantine_arabic|modern_standard_arabic|null",
  "is_out_of_scope": true|false,
  "out_of_scope_reason": "..." or null
}
"""


def parse_intent_groq(user_query: str) -> SearchIntent:
    """Parse using Groq API."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY environment variable not set")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",  # Latest Llama model on Groq
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"Parse this search query:\n\n{user_query}"
            }
        ],
        "temperature": 0.3,
        "max_tokens": 500,
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Groq API request failed: {str(e)}")
    
    try:
        data = response.json()
        
        if "error" in data:
            raise ValueError(f"Groq API error: {data['error']}")
        
        if not data.get("choices") or not data["choices"][0].get("message"):
            raise ValueError("Unexpected Groq API response format")
        
        response_text = data["choices"][0]["message"]["content"].strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        parsed_json = json.loads(response_text)
        intent = SearchIntent(**parsed_json)
        return intent
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse Groq response as JSON: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to parse intent with Groq: {str(e)}")


def parse_intent_openrouter(user_query: str) -> SearchIntent:
    """Parse using OpenRouter API."""
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    
    url = "https://openrouter.io/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/mumzworld/search-intent-engine",
        "X-Title": "Mumzworld Search Intent Parser",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "meta-llama/llama-3.3-70b-instruct:free",
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": f"Parse this search query:\n\n{user_query}"
            }
        ],
        "temperature": 0.3,
        "max_tokens": 500,
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ValueError(f"OpenRouter API request failed: {str(e)}")
    
    try:
        data = response.json()
        
        if "error" in data:
            raise ValueError(f"OpenRouter API error: {data['error']}")
        
        if not data.get("choices") or not data["choices"][0].get("message"):
            raise ValueError("Unexpected OpenRouter API response format")
        
        response_text = data["choices"][0]["message"]["content"].strip()
        
        # Extract JSON from response
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        parsed_json = json.loads(response_text)
        intent = SearchIntent(**parsed_json)
        return intent
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse OpenRouter response as JSON: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to parse intent with OpenRouter: {str(e)}")


def parse_intent(user_query: str) -> SearchIntent:
    """
    Parse user search query into structured intent using LLM.
    
    Uses provider specified in LLM_PROVIDER environment variable ("openrouter" or "groq").
    
    Args:
        user_query: Raw user input in Arabic, English, or code-switched
        
    Returns:
        SearchIntent: Structured intent object
        
    Raises:
        ValueError: If API fails or response is invalid JSON
    """
    if not user_query or not user_query.strip():
        raise ValueError("Query cannot be empty")
    
    if LLM_PROVIDER == "groq":
        return parse_intent_groq(user_query)
    elif LLM_PROVIDER == "openrouter":
        return parse_intent_openrouter(user_query)
    else:
        raise ValueError(f"Unknown LLM provider: {LLM_PROVIDER}. Use 'groq' or 'openrouter'.")


def batch_parse(queries: list[str]) -> list[SearchIntent]:
    """Parse multiple queries."""
    return [parse_intent(q) for q in queries]
