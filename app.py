import streamlit as st
import pandas as pd
import io

from theme import apply_custom_theme
from pdf_utils import parse_clauses_from_pdf, parse_clauses_from_text, extract_text_from_image
from llm_utils import (
    simplify_clause,
    assess_clause_risk,
    generate_document_summary,
    answer_question_with_context,
    check_document_legality
)
from rag_utils import ClauseVectorStore
from sample_data import get_sample_clauses
from pdf_generator import create_audit_pdf

# Page Config
st.set_page_config(
    page_title="DocuSense AI — Simple & Honest Policy Companion",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Clean Styling
apply_custom_theme()

# Initialize Session State
if "clauses" not in st.session_state:
    st.session_state.clauses = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = ClauseVectorStore()
if "doc_summary" not in st.session_state:
    st.session_state.doc_summary = None
if "doc_legality" not in st.session_state:
    st.session_state.doc_legality = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "doc_name" not in st.session_state:
    st.session_state.doc_name = ""
if "processed" not in st.session_state:
    st.session_state.processed = False
if "target_language" not in st.session_state:
    st.session_state.target_language = "English"

def process_document(clauses_list, doc_title="Uploaded Document", target_language="English"):
    """Runs pipeline: simplification, risk scan, vector indexing."""
    st.session_state.doc_name = doc_title
    progress_bar = st.progress(0, text="Initializing processing pipeline...")
    
    analyzed_clauses = []
    total = len(clauses_list)
    
    for idx, clause in enumerate(clauses_list):
        progress_bar.progress(
            int((idx / total) * 80),
            text=f"Analyzing Clause {idx+1}/{total}: {clause['title']}"
        )
        
        # Plain English (or translated) simplification
        explanation = simplify_clause(clause["text"], target_language)
        
        # Risk assessment
        risk_info = assess_clause_risk(clause["text"], target_language)
        
        clause_obj = dict(clause)
        clause_obj["explanation"] = explanation
        clause_obj["risk"] = risk_info
        analyzed_clauses.append(clause_obj)
        
    progress_bar.progress(85, text="Building FAISS vector index...")
    v_store = ClauseVectorStore()
    v_store.build_index(analyzed_clauses)
    
    progress_bar.progress(95, text="Generating safety verdict & summary...")
    summary = generate_document_summary(analyzed_clauses, target_language)
    
    progress_bar.progress(98, text="Running legal document authenticity & legality analysis...")
    full_doc_text = "\n\n".join([c["text"] for c in analyzed_clauses])
    legality_info = check_document_legality(full_doc_text, target_language)
    
    st.session_state.clauses = analyzed_clauses
    st.session_state.vector_store = v_store
    st.session_state.doc_summary = summary
    st.session_state.doc_legality = legality_info
    st.session_state.processed = True
    st.session_state.chat_history = []
    st.session_state.target_language = target_language
    
    progress_bar.progress(100, text="Analysis Complete!")
    st.rerun()


# Sidebar Navigation & System Status
with st.sidebar:
    st.markdown("""
        <div style='padding: 0.5rem 0 1rem 0; text-align: center;'>
            <h2 style='color: #F8FAFC; margin-bottom: 0; font-size: 1.5rem;'>🛡️ DocuSense AI</h2>
            <p style='color: #38BDF8; font-size: 0.82rem; margin-top: 0.2rem; font-weight: 600;'>Simple & Honest Policy Companion</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🌐 Output Language")
    selected_language = st.selectbox(
        "Select your preferred language",
        ["English", "Telugu", "Tamil", "Malayalam", "Hindi", "Spanish", "French"],
        index=["English", "Telugu", "Tamil", "Malayalam", "Hindi", "Spanish", "French"].index(st.session_state.target_language)
    )
    
    st.markdown("---")
    
    st.markdown("### 🖥️ Local Engine Status")
    st.markdown("""
        <div style='background: #1E293B; border: 1px solid #334155; border-radius: 8px; padding: 0.75rem; font-size: 0.8rem;'>
            <span style='color: #10B981; font-weight: 700;'>● 100% Offline / Local</span><br/>
            <span style='color: #CBD5E1;'>• LLM: llama3.2:latest</span><br/>
            <span style='color: #CBD5E1;'>• Embeddings: nomic-embed-text</span><br/>
            <span style='color: #CBD5E1;'>• Vector Search: FAISS</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("### 🚀 Quick Demo Datasets")
    if st.button("⚡ Load Sample SaaS Terms of Service", use_container_width=True):
        sample_clauses = get_sample_clauses(doc_type="tos")
        process_document(sample_clauses, "Sample SaaS Terms of Service", selected_language)
        
    if st.button("🌾 Load Sample Land & Lease Policy", use_container_width=True):
        sample_clauses = get_sample_clauses(doc_type="land")
        process_document(sample_clauses, "Agricultural & Land Lease Agreement", selected_language)

    st.markdown("---")
    
    if st.session_state.processed:
        s = st.session_state.doc_summary
        st.markdown("### 📄 Safety Verdict")
        st.markdown(f"""
            <div style='background: #1E293B; border: 1px solid {s["verdict_color"]}; border-radius: 8px; padding: 0.75rem; text-align: center;'>
                <span style='color: {s["verdict_color"]}; font-weight: 800; font-size: 0.95rem;'>{s["verdict_badge"]}</span><br/>
                <span style='color: #F8FAFC; font-size: 1.4rem; font-weight: 800;'>{s["health_score"]}/100</span><br/>
                <span style='color: #94A3B8; font-size: 0.78rem;'>Policy Safety Score</span>
            </div>
        """, unsafe_allow_html=True)


# Main Content Header
st.markdown("<h1 class='main-title'>DocuSense AI</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Understand Land Agreements, Property Policies, Contracts & Terms in Plain Language.</p>", unsafe_allow_html=True)


# Main Tabs Navigation
tab_upload, tab_analysis, tab_risks, tab_qa, tab_report = st.tabs([
    "📤 Upload Document",
    "📜 Plain Explainer",
    "🚨 Risk Scanner",
    "💬 Ask Questions",
    "📊 Safety Verdict & Export"
])


# ==========================================
# TAB 1: UPLOAD & PROCESSING
# ==========================================
with tab_upload:
    st.markdown("### Upload Policy or Land Document")
    
    col_u1, col_u2 = st.columns([2, 1])
    
    with col_u1:
        st.markdown("##### Choose an input method:")
        input_method = st.radio("Input Method", ["PDF File", "Image File (OCR)", "Paste Raw Text"], horizontal=True, label_visibility="collapsed")
        
        if input_method == "PDF File":
            uploaded_file = st.file_uploader("Upload PDF File (Land Documents, Lease Agreements, Terms of Service)", type=["pdf"])
            if uploaded_file is not None:
                if st.button("🔍 Ingest & Analyze PDF", type="primary", use_container_width=True):
                    with st.spinner("Extracting text & chunking clauses from PDF..."):
                        parsed_clauses = parse_clauses_from_pdf(uploaded_file)
                        if parsed_clauses:
                            process_document(parsed_clauses, uploaded_file.name, selected_language)
                        else:
                            st.error("Could not extract readable text from the uploaded PDF.")
                            
        elif input_method == "Image File (OCR)":
            uploaded_img = st.file_uploader("Upload Image of Document (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])
            if uploaded_img is not None:
                if st.button("🔍 Extract Text & Analyze Image", type="primary", use_container_width=True):
                    with st.spinner("Running OCR on image..."):
                        try:
                            raw_text = extract_text_from_image(uploaded_img)
                            parsed_clauses = parse_clauses_from_text(raw_text)
                            if parsed_clauses:
                                process_document(parsed_clauses, uploaded_img.name, selected_language)
                            else:
                                st.error("No meaningful clauses could be extracted from the image text.")
                        except Exception as e:
                            st.error(f"OCR Failed: {str(e)}")
                            
        elif input_method == "Paste Raw Text":
            raw_text_input = st.text_area("Paste your contract or policy text here", height=200)
            if raw_text_input:
                if st.button("🔍 Analyze Text", type="primary", use_container_width=True):
                    with st.spinner("Chunking clauses from text..."):
                        parsed_clauses = parse_clauses_from_text(raw_text_input)
                        if parsed_clauses:
                            process_document(parsed_clauses, "Pasted Text Document", selected_language)
                        else:
                            st.error("Could not detect any clauses. Please paste a larger document with clear sections.")

    with col_u2:
        st.markdown("""
            <div class='clean-card'>
                <h4 style='color: #38BDF8; margin-top:0;'>✨ Supported Documents</h4>
                <ul style='color: #94A3B8; font-size: 0.85rem; padding-left: 1.1rem; line-height: 1.6;'>
                    <li><b>Land & Property Agreements:</b> Lease policies, land deeds, tenant contracts.</li>
                    <li><b>SaaS & Tech Policies:</b> Terms of Service, Privacy Policies.</li>
                    <li><b>Contracts & Agreements:</b> Employment policies, service contracts.</li>
                </ul>
                <h4 style='color: #38BDF8; margin-top:1rem;'>🌐 Translation</h4>
                <p style='color: #94A3B8; font-size: 0.85rem;'>Select your preferred language in the sidebar (Telugu, Tamil, Malayalam, etc.) to get explanations in your native tongue.</p>
            </div>
        """, unsafe_allow_html=True)

    if st.session_state.processed:
        s = st.session_state.doc_summary
        leg = st.session_state.doc_legality or {}
        
        leg_badge_color = "#10B981" if leg.get("legality") == "LEGITIMATE" else "#EF4444"
        leg_badge_title = "✅ LEGITIMATE LEGAL DOCUMENT" if leg.get("legality") == "LEGITIMATE" else "🚨 SUSPICIOUS / POTENTIALLY FRAUDULENT DOCUMENT"
        
        st.markdown(f"""
            <div class='clean-card' style='border-left: 4px solid {s["verdict_color"]}; margin-top: 1rem;'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <h4 style='margin: 0; color: #F8FAFC;'>Active Document: {st.session_state.doc_name}</h4>
                    <span style='background: {leg_badge_color}22; border: 1px solid {leg_badge_color}; color: {leg_badge_color}; padding: 4px 12px; border-radius: 20px; font-weight: 700; font-size: 0.82rem;'>{leg_badge_title}</span>
                </div>
                <p style='color: {s["verdict_color"]}; font-weight: 700; margin: 0.4rem 0 0.2rem 0;'>{s["verdict_title"]}</p>
                <p style='color: #94A3B8; font-size: 0.88rem; margin: 0;'>{s["verdict_recommendation"]}</p>
                
                <div style='background: #0F172A; border-radius: 6px; padding: 0.75rem; margin-top: 0.8rem;'>
                    <h5 style='color: #38BDF8; margin: 0 0 0.4rem 0;'>⚖️ Legality & Authenticity Forensics ({st.session_state.target_language})</h5>
                    <p style='color: #E2E8F0; font-size: 0.85rem; margin: 0;'><b>Document Type:</b> {leg.get('doc_type', 'Unknown')} | <b>Confidence:</b> {leg.get('confidence', 'MEDIUM')}</p>
                    <p style='color: #E2E8F0; font-size: 0.85rem; margin: 0.3rem 0 0 0;'><b>Analysis:</b> {leg.get('analysis', '')}</p>
                    <p style='color: #F59E0B; font-size: 0.85rem; margin: 0.3rem 0 0 0;'><b>Red Flags:</b> {leg.get('red_flags', 'None')}</p>
                </div>
                
                <p style='color: #64748B; font-size: 0.78rem; margin-top: 0.5rem; text-align: right;'>Output Language: <b>{st.session_state.target_language}</b></p>
            </div>
        """, unsafe_allow_html=True)


# ==========================================
# TAB 2: CLAUSE EXPLAINER
# ==========================================
with tab_analysis:
    if not st.session_state.processed:
        st.info("💡 Upload a document to view explanations.")
    else:
        st.markdown(f"### 📜 Clause-by-Clause Explanations ({st.session_state.target_language})")
        
        search_query = st.text_input("🔍 Search clauses by topic, word, or clause number...", "")
        
        filtered_clauses = st.session_state.clauses
        if search_query:
            filtered_clauses = [
                c for c in filtered_clauses 
                if search_query.lower() in c["title"].lower() or search_query.lower() in c["text"].lower() or search_query.lower() in c["explanation"].lower()
            ]
            
        st.caption(f"Showing {len(filtered_clauses)} of {len(st.session_state.clauses)} clauses")
        
        for clause in filtered_clauses:
            risk_level = clause["risk"]["risk_level"]
            badge_class = "badge-critical" if risk_level == "CRITICAL" else ("badge-warning" if risk_level == "WARNING" else "badge-low")
            
            with st.expander(f"**{clause['title']}** — ({clause['word_count']} words)", expanded=(risk_level != "LOW")):
                col_c1, col_c2 = st.columns(2)
                
                with col_c1:
                    st.markdown("##### 📄 Original Clause Text")
                    st.markdown(f"```text\n{clause['text']}\n```")
                    
                with col_c2:
                    st.markdown(f"##### 💡 {st.session_state.target_language} Explanation")
                    st.markdown(f"<div style='background: #0F172A; border-left: 3px solid #38BDF8; padding: 0.8rem; border-radius: 6px; font-size: 0.9rem;'>{clause['explanation']}</div>", unsafe_allow_html=True)
                    st.markdown("<br/>", unsafe_allow_html=True)
                    st.markdown(f"**Risk Level:** <span class='{badge_class}'>{risk_level}</span> | **Category:** {clause['risk']['risk_type']}", unsafe_allow_html=True)
                    st.caption(f"💡 **Guidance:** {clause['risk']['action']}")


# ==========================================
# TAB 3: RISK INTELLIGENCE
# ==========================================
with tab_risks:
    if not st.session_state.processed:
        st.info("💡 Upload a document to view detected risks and red flags.")
    else:
        st.markdown("### 🚨 Risk Scanner & Highlighted Red Flags")
        
        s = st.session_state.doc_summary
        
        verdict_css = "verdict-unsafe" if s["verdict_status"] == "UNSAFE" else ("verdict-caution" if s["verdict_status"] == "CAUTION" else "verdict-safe")
        st.markdown(f"""
            <div class='{verdict_css}'>
                <h3 style='margin: 0; color: {s["verdict_color"]};'>{s["verdict_title"]}</h3>
                <p style='font-size: 0.92rem; margin-top: 0.4rem;'><b>Recommendation:</b> {s["verdict_recommendation"]}</p>
            </div>
        """, unsafe_allow_html=True)
        
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        
        with col_r1:
            st.markdown(f"<div class='kpi-container'><div class='kpi-val' style='color:#EF4444;'>{s['critical_count']}</div><div class='kpi-lbl'>Critical Flags</div></div>", unsafe_allow_html=True)
        with col_r2:
            st.markdown(f"<div class='kpi-container'><div class='kpi-val' style='color:#F59E0B;'>{s['warning_count']}</div><div class='kpi-lbl'>Warning Flags</div></div>", unsafe_allow_html=True)
        with col_r3:
            st.markdown(f"<div class='kpi-container'><div class='kpi-val' style='color:#10B981;'>{s['low_count']}</div><div class='kpi-lbl'>Standard Clauses</div></div>", unsafe_allow_html=True)
        with col_r4:
            st.markdown(f"<div class='kpi-container'><div class='kpi-val' style='color:{s['verdict_color']};'>{s['health_score']}/100</div><div class='kpi-lbl'>Safety Score</div></div>", unsafe_allow_html=True)
            
        st.markdown("<br/>", unsafe_allow_html=True)
        
        risk_filter = st.radio("Filter by Risk Severity:", ["All Flagged Terms", "CRITICAL Only", "WARNING Only"], horizontal=True)
        
        flagged_list = [c for c in st.session_state.clauses if c["risk"]["risk_level"] in ["CRITICAL", "WARNING"]]
        
        if risk_filter == "CRITICAL Only":
            flagged_list = [c for c in flagged_list if c["risk"]["risk_level"] == "CRITICAL"]
        elif risk_filter == "WARNING Only":
            flagged_list = [c for c in flagged_list if c["risk"]["risk_level"] == "WARNING"]
            
        if not flagged_list:
            st.success("🎉 No high-severity risks matching the selected filter!")
        else:
            for clause in flagged_list:
                r = clause["risk"]
                badge_class = "badge-critical" if r["risk_level"] == "CRITICAL" else "badge-warning"
                
                st.markdown(f"""
                    <div class='clean-card'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <h4 style='color: #F8FAFC; margin: 0;'>{clause['title']}</h4>
                            <span class='{badge_class}'>{r['risk_level']} RISK</span>
                        </div>
                        <p style='color: #38BDF8; font-weight: 600; margin-top: 0.4rem; font-size: 0.88rem;'>Category: {r['risk_type']}</p>
                        <p style='color: #E2E8F0; font-size: 0.9rem;'><b>Why It's Risky:</b> {r['reasoning']}</p>
                        <p style='color: #94A3B8; font-size: 0.85rem;'><b>Action Guidance:</b> {r['action']}</p>
                    </div>
                """, unsafe_allow_html=True)


# ==========================================
# TAB 4: Q&A AI ASSISTANT (RAG)
# ==========================================
with tab_qa:
    if not st.session_state.processed:
        st.info("💡 Upload a document to enable the interactive Q&A assistant.")
    else:
        st.markdown("### 💬 Ask Questions About Your Document")
        st.caption("Ask anything about your document, land policy, or contract. DocuSense AI uses local FAISS vector search to give grounded answers with clause citations.")
        
        st.markdown("##### 💡 Suggested Questions (Click to ask instantly)")
        col_q1, col_q2, col_q3, col_q4 = st.columns(4)
        prompt_to_run = None
        
        with col_q1:
            if st.button("📋 Summarize Document", use_container_width=True):
                prompt_to_run = "What is this document saying and what is its main purpose?"
        with col_q2:
            if st.button("🛡️ Is it safe to sign?", use_container_width=True):
                prompt_to_run = "Is it safe to accept or sign this policy? Tell me the score and verdict."
        with col_q3:
            if st.button("🌾 Land / Rent Rules", use_container_width=True):
                prompt_to_run = "What are the rules regarding rent, land usage, eviction, or security deposits?"
        with col_q4:
            if st.button("🙋 Who is Seller/Owner?", use_container_width=True):
                prompt_to_run = "Who is the seller, owner, or landlord in this agreement?"

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("##### ✏️ Enter Your Custom Question Below")
        
        with st.form(key="qa_form", clear_on_submit=False):
            custom_question = st.text_input(
                "Question",
                placeholder=f"e.g., Who is the seller, owner, or buyer? What is the sale price and survey number?",
                label_visibility="collapsed"
            )
            col_b1, col_b2 = st.columns([1, 3])
            with col_b1:
                submit_question = st.form_submit_button("🔍 Ask AI Question", type="primary", use_container_width=True)

        selected_query = prompt_to_run if prompt_to_run else (custom_question if submit_question and custom_question else None)
        
        # Display Chat History
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                
        if selected_query:
            st.session_state.chat_history.append({"role": "user", "content": selected_query})
            with st.chat_message("user"):
                st.markdown(selected_query)
                
            with st.chat_message("assistant"):
                with st.spinner("Searching full document & generating grounded answer..."):
                    answer = answer_question_with_context(
                        selected_query, 
                        all_clauses=st.session_state.clauses,
                        doc_summary=st.session_state.doc_summary,
                        doc_name=st.session_state.doc_name,
                        doc_legality=st.session_state.doc_legality,
                        target_language=st.session_state.target_language
                    )
                    st.markdown(answer)
                    
                    with st.expander("📌 Source Document Reference"):
                        for c in st.session_state.clauses:
                            st.markdown(f"**[{c['title']}]**")
                            st.caption(c['text'][:250] + "...")
                                
            st.session_state.chat_history.append({"role": "assistant", "content": answer})
            st.rerun()


# ==========================================
# TAB 5: EXECUTIVE SUMMARY & VERDICT
# ==========================================
with tab_report:
    if not st.session_state.processed:
        st.info("💡 Upload a document to view the safety verdict and download audit reports.")
    else:
        st.markdown("### 📊 Executive Summary & User Safety Verdict")
        
        s = st.session_state.doc_summary
        
        verdict_css = "verdict-unsafe" if s["verdict_status"] == "UNSAFE" else ("verdict-caution" if s["verdict_status"] == "CAUTION" else "verdict-safe")
        st.markdown(f"""
            <div class='{verdict_css}'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <h2 style='margin: 0; color: {s["verdict_color"]};'>{s["verdict_title"]}</h2>
                    <span style='font-size: 1.6rem; font-weight: 800; color: {s["verdict_color"]};'>Safety Score: {s["health_score"]}/100</span>
                </div>
                <p style='font-size: 0.95rem; margin-top: 0.6rem;'><b>Safety Verdict:</b> {s["verdict_recommendation"]}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"#### Key Takeaways ({st.session_state.target_language})")
        st.markdown(f"<div class='clean-card' style='font-size: 0.92rem; line-height: 1.6;'>{s['executive_summary']}</div>", unsafe_allow_html=True)
        
        st.markdown("#### Clause Classification Breakdown")
        
        table_data = []
        for c in st.session_state.clauses:
            table_data.append({
                "Clause ID": f"Clause {c['id']}",
                "Section Header": c["title"],
                "Risk Level": c["risk"]["risk_level"],
                "Risk Category": c["risk"]["risk_type"],
                "Summary": c["explanation"]
            })
        df_summary = pd.DataFrame(table_data)
        st.dataframe(df_summary, use_container_width=True)
        
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("#### 📥 Export Full Audit Report")
        
        report_text = f"""# DOCUSENSE AI — EXECUTIVE AUDIT REPORT
Document: {st.session_state.doc_name}
Language: {st.session_state.target_language}
SAFETY VERDICT: {s['verdict_badge']} ({s['health_score']}/100)
RECOMMENDATION: {s['verdict_recommendation']}

Total Clauses Analyzed: {s['total_clauses']} (Critical: {s['critical_count']}, Warnings: {s['warning_count']})

## EXECUTIVE SUMMARY
{s['executive_summary']}

## DETAILED CLAUSE ANALYSIS
"""
        for c in st.session_state.clauses:
            report_text += f"""
--------------------------------------------------
[{c['risk']['risk_level']} RISK] {c['title']}
Category: {c['risk']['risk_type']}
Explanation: {c['explanation']}
Action Advice: {c['risk']['action']}
Original Text Snippet: {c['text'][:200]}...
"""
            
        col_d1, col_d2 = st.columns(2)
        
        with col_d1:
            st.download_button(
                label="📄 Download Report (.md)",
                data=report_text,
                file_name=f"DocuSense_Audit_{st.session_state.doc_name}.md",
                mime="text/markdown",
                use_container_width=True
            )
            
        with col_d2:
            try:
                pdf_bytes = create_audit_pdf(st.session_state.doc_name, s, st.session_state.clauses, doc_legality=st.session_state.doc_legality)
                st.download_button(
                    label="📕 Download PDF Report (.pdf)",
                    data=pdf_bytes,
                    file_name=f"DocuSense_Audit_{st.session_state.doc_name}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF generation error: {str(e)}")
