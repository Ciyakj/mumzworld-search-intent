"""Streamlit UI for Mumzworld Search Intent Parser."""
import streamlit as st
import json
import sys
import os

# Page config
st.set_page_config(
    page_title="Mumzworld Search Intent Parser",
    page_icon="🛍️",
    layout="wide",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans+Arabic:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans Arabic', sans-serif;
}

/* Background */
.stApp {
    background: #0a0e1a;
    color: #e8eaf0;
}

/* Header */
.main-header {
    background: linear-gradient(135deg, #1a1f35 0%, #0f1525 100%);
    border: 1px solid #2a3050;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.main-header h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px;
    font-weight: 600;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.3px;
}
.main-header p {
    font-size: 13px;
    color: #6b7280;
    margin: 4px 0 0 0;
}
.badge {
    display: inline-block;
    background: #1e3a5f;
    color: #60a5fa;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 4px;
    margin-left: 8px;
    border: 1px solid #2d5a9e;
}

/* Input area */
.stTextArea textarea {
    background: #111827 !important;
    border: 1px solid #2a3050 !important;
    border-radius: 8px !important;
    color: #e8eaf0 !important;
    font-family: 'IBM Plex Sans Arabic', sans-serif !important;
    font-size: 16px !important;
    direction: rtl;
}
.stTextArea textarea:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15) !important;
}

/* Button */
.stButton > button {
    background: #2563eb !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    padding: 10px 28px !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #1d4ed8 !important;
    transform: translateY(-1px) !important;
}

/* Result cards */
.result-card {
    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 12px;
}
.result-card.success { border-left: 3px solid #10b981; }
.result-card.warning { border-left: 3px solid #f59e0b; }
.result-card.danger  { border-left: 3px solid #ef4444; }
.result-card.info    { border-left: 3px solid #3b82f6; }

.field-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.field-value {
    font-size: 15px;
    font-weight: 600;
    color: #f9fafb;
}
.field-value.mono {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
}

/* Confidence bar */
.conf-bar-bg {
    background: #1f2937;
    border-radius: 4px;
    height: 6px;
    margin-top: 8px;
    overflow: hidden;
}
.conf-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.6s ease;
}

/* Tag pills */
.tag {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-family: 'IBM Plex Mono', monospace;
    margin-right: 6px;
}
.tag-blue  { background: #1e3a5f; color: #60a5fa; border: 1px solid #2d5a9e; }
.tag-green { background: #064e3b; color: #34d399; border: 1px solid #065f46; }
.tag-red   { background: #450a0a; color: #f87171; border: 1px solid #7f1d1d; }
.tag-amber { background: #451a03; color: #fbbf24; border: 1px solid #78350f; }
.tag-gray  { background: #1f2937; color: #9ca3af; border: 1px solid #374151; }

/* Example queries */
.example-btn {
    background: #1a1f35;
    border: 1px solid #2a3050;
    border-radius: 8px;
    padding: 10px 14px;
    cursor: pointer;
    font-size: 13px;
    color: #9ca3af;
    transition: all 0.15s;
    display: block;
    width: 100%;
    text-align: right;
    direction: rtl;
    margin-bottom: 6px;
}
.example-btn:hover { border-color: #3b82f6; color: #e8eaf0; }

/* Scope banner */
.out-of-scope-banner {
    background: #450a0a;
    border: 1px solid #7f1d1d;
    border-radius: 8px;
    padding: 14px 18px;
    color: #fca5a5;
    font-size: 14px;
    margin-bottom: 12px;
}
.in-scope-banner {
    background: #064e3b;
    border: 1px solid #065f46;
    border-radius: 8px;
    padding: 14px 18px;
    color: #6ee7b7;
    font-size: 14px;
    margin-bottom: 12px;
}

/* Divider */
hr { border-color: #1f2937 !important; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0d1120 !important;
    border-right: 1px solid #1f2937 !important;
}

/* JSON block */
.json-block {
    background: #0d1120;
    border: 1px solid #1f2937;
    border-radius: 8px;
    padding: 16px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    color: #9ca3af;
    overflow-x: auto;
    white-space: pre;
}
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <div>
    <h1>🛍️ Mumzworld Search Intent Parser <span class="badge">Arabic-First</span></h1>
    <p>Converts messy, code-switched Arabic queries into structured shopping signals · Powered by Llama 3.3 70B via Groq</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    provider = st.selectbox("LLM Provider", ["groq", "openrouter"], index=0)
    
    if provider == "groq":
        api_key = st.text_input("Groq API Key", type="password",
                                 value=os.getenv("GROQ_API_KEY", ""),
                                 placeholder="gsk_...")
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            os.environ["LLM_PROVIDER"] = "groq"
    else:
        api_key = st.text_input("OpenRouter API Key", type="password",
                                 value=os.getenv("OPENROUTER_API_KEY", ""),
                                 placeholder="sk-or-...")
        if api_key:
            os.environ["OPENROUTER_API_KEY"] = api_key
            os.environ["LLM_PROVIDER"] = "openrouter"

    use_mock = not bool(api_key)
    
    if use_mock:
        st.warning("⚠️ No API key — using mock responses")
    else:
        st.success("✅ Real LLM connected")

    st.markdown("---")
    st.markdown("### 💡 Example Queries")
    
    examples = [
        ("Gulf Arabic", "حليب أطفال للأطفال اللي أكبر من 6 شهور، رخيص شوية"),
        ("Code-switch", "أبي high chair للطفل عمره 8 months، مش مكلّف كتير"),
        ("Budget", "nursing bra تحت 150 درهم، مريحة وجودة كويسة"),
        ("Vague", "شيء حلو للطفل اللي عمره شهرين"),
        ("Medical (OOS)", "الطفل عنده حمى وسعال، شو الحل؟"),
        ("English", "stroller for newborn under 500 AED"),
    ]
    
    for label, query in examples:
        if st.button(f"{label}: {query[:30]}…", key=f"ex_{label}"):
            st.session_state["query_input"] = query

    st.markdown("---")
    st.markdown("""
    <div style="font-size:11px; color:#4b5563; line-height:1.6;">
    <b style="color:#6b7280">What it extracts:</b><br>
    • Product category (11 types)<br>
    • Age range (months)<br>
    • Budget (AED)<br>
    • Urgency signal<br>
    • Arabic dialect<br>
    • Confidence score<br>
    • Out-of-scope detection
    </div>
    """, unsafe_allow_html=True)

# ── Main content ──────────────────────────────────────────────────────────────
col_input, col_output = st.columns([1, 1], gap="large")

with col_input:
    st.markdown("#### 🔍 Search Query Input")
    
    default_query = st.session_state.get("query_input", "")
    query = st.text_area(
        "Enter query in Arabic, English, or mixed",
        value=default_query,
        height=120,
        placeholder="اكتب استعلامك هنا... / Type your query here...",
        label_visibility="collapsed"
    )

    parse_btn = st.button("→ Parse Intent", use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📊 Eval Suite")
    run_evals_btn = st.button("▶ Run 14 Test Cases", use_container_width=True)

with col_output:
    st.markdown("#### 📦 Structured Output")
    
    if parse_btn and query.strip():
        with st.spinner("Parsing..."):
            try:
                if use_mock:
                    from intent_parser_mock import parse_intent_mock as parse_intent
                else:
                    from intent_parser import parse_intent
                
                result = parse_intent(query)
                
                # ── Scope banner
                if result.is_out_of_scope:
                    st.markdown(f"""
                    <div class="out-of-scope-banner">
                        ⚠️ <b>Out of Scope</b> — {result.out_of_scope_reason or "Not a product search"}
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div class="in-scope-banner">
                        ✅ <b>In Scope</b> — Product search detected
                    </div>""", unsafe_allow_html=True)

                # ── Category + Confidence
                cat = result.product_category or "—"
                conf = result.confidence_score
                conf_color = "#10b981" if conf >= 0.8 else "#f59e0b" if conf >= 0.5 else "#ef4444"
                conf_pct = int(conf * 100)

                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""
                    <div class="result-card info">
                        <div class="field-label">Category</div>
                        <div class="field-value">{cat}</div>
                    </div>""", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class="result-card {'success' if conf >= 0.8 else 'warning' if conf >= 0.5 else 'danger'}">
                        <div class="field-label">Confidence</div>
                        <div class="field-value">{conf_pct}%</div>
                        <div class="conf-bar-bg">
                            <div class="conf-bar-fill" style="width:{conf_pct}%; background:{conf_color};"></div>
                        </div>
                    </div>""", unsafe_allow_html=True)

                # ── Age + Budget
                c3, c4 = st.columns(2)
                with c3:
                    age = result.age_range_months
                    age_str = f"{age.min}–{age.max} mo" if age and age.min and age.max else \
                              f"{age.min}+ mo" if age and age.min else "—"
                    st.markdown(f"""
                    <div class="result-card info">
                        <div class="field-label">Age Range</div>
                        <div class="field-value">{age_str}</div>
                    </div>""", unsafe_allow_html=True)
                with c4:
                    bud = result.budget_aed
                    bud_str = f"≤{bud.max} AED" if bud and bud.max else \
                              f"≥{bud.min} AED" if bud and bud.min else "—"
                    st.markdown(f"""
                    <div class="result-card info">
                        <div class="field-label">Budget</div>
                        <div class="field-value">{bud_str}</div>
                    </div>""", unsafe_allow_html=True)

                # ── Languages + Dialect + Urgency
                langs = " ".join([f'<span class="tag tag-blue">{l.upper()}</span>' 
                                   for l in (result.languages_detected or [])])
                dialect = result.dialect_detected or "—"
                urgency = result.urgency or "standard"
                urg_color = "tag-amber" if urgency != "standard" else "tag-gray"

                st.markdown(f"""
                <div class="result-card info" style="margin-top:0">
                    <div style="display:flex; gap:24px; flex-wrap:wrap;">
                        <div>
                            <div class="field-label">Languages</div>
                            <div style="margin-top:6px">{langs}</div>
                        </div>
                        <div>
                            <div class="field-label">Dialect</div>
                            <div style="margin-top:6px"><span class="tag tag-blue">{dialect}</span></div>
                        </div>
                        <div>
                            <div class="field-label">Urgency</div>
                            <div style="margin-top:6px"><span class="tag {urg_color}">{urgency}</span></div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)

                # ── Clarifying question
                if result.clarifying_question:
                    st.markdown(f"""
                    <div class="result-card warning">
                        <div class="field-label">💬 Clarifying Question</div>
                        <div class="field-value" style="font-size:14px; margin-top:6px; direction:rtl; text-align:right;">
                            {result.clarifying_question}
                        </div>
                    </div>""", unsafe_allow_html=True)

                # ── Raw JSON
                with st.expander("{ } Raw JSON", expanded=False):
                    st.code(json.dumps(result.model_dump(exclude_none=False), 
                                       indent=2, ensure_ascii=False), 
                            language="json")

            except Exception as e:
                st.error(f"Parse error: {e}")

    elif parse_btn:
        st.info("Enter a query first.")
    else:
        st.markdown("""
        <div style="text-align:center; padding: 60px 20px; color: #374151;">
            <div style="font-size: 40px; margin-bottom: 12px;">🔍</div>
            <div style="font-size: 14px; color: #4b5563;">
                Enter a query on the left and click <b>Parse Intent</b>
            </div>
            <div style="font-size: 12px; color: #374151; margin-top: 8px;">
                Supports Arabic, English, and code-switching
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Eval Suite ────────────────────────────────────────────────────────────────
if run_evals_btn:
    st.markdown("---")
    st.markdown("#### 📋 Eval Results — 14 Test Cases (Real LLM)")
    
    try:
        import io
        from contextlib import redirect_stdout

        if use_mock:
            from intent_parser_mock import parse_intent_mock as parse_intent
            import evals
            evals.parse_intent = parse_intent
        
        from evals import EVAL_CASES, EvalResult, parse_intent as eval_parse

        passed = 0
        rows = []

        progress = st.progress(0)
        for i, case in enumerate(EVAL_CASES):
            try:
                intent = eval_parse(case.query)
                result = EvalResult(case, intent)
            except Exception as e:
                result = EvalResult(case, None, e)
            
            is_pass = result.is_pass()
            if is_pass:
                passed += 1
            
            rows.append({
                "#": i + 1,
                "Test Case": case.name,
                "Category": intent.product_category if result.intent else "ERROR",
                "Conf": f"{intent.confidence_score:.2f}" if result.intent else "—",
                "Pass": "✅" if is_pass else "❌",
                "Note": result.get_failure_reason() if not is_pass else "—"
            })
            progress.progress((i + 1) / len(EVAL_CASES))

        total = len(EVAL_CASES)
        pct = 100 * passed / total

        # Summary
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Pass Rate", f"{pct:.1f}%")
        sc2.metric("Passed", f"{passed}/{total}")
        sc3.metric("Failed", f"{total - passed}/{total}")

        # Table
        import pandas as pd
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"Eval error: {e}")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; font-size:11px; color:#374151; padding: 8px 0 16px;">
    Mumzworld AI Engineering Intern Assessment · Arabic-First Search Intent Parser · 
    <span style="font-family: 'IBM Plex Mono', monospace;">llama-3.3-70b · Groq free tier</span>
</div>
""", unsafe_allow_html=True)
