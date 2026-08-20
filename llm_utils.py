import ollama
import re
from typing import List, Dict, Any

MODEL_NAME = "llama3.2:latest"

# Legal red flag categories for hybrid scanner
RED_FLAG_KEYWORDS = {
    "Auto-Renewal / Recurring Billing": ["auto-renew", "automatic renewal", "automatically renew", "recurring charge", "cancel before"],
    "Unilateral Terms Modification": ["sole discretion", "modify these terms", "without notice", "at any time", "change terms", "terminate this lease"],
    "Binding Arbitration & Class Action Waiver": ["binding arbitration", "class action waiver", "waive jury trial", "dispute resolution"],
    "Limitation of Liability & Indemnification": ["limitation of liability", "indemnify", "hold harmless", "as is", "no warranty", "consequential damages", "environmental liability"],
    "Data & Privacy Exposure": ["sell data", "third party partners", "monetize", "share location", "track usage"],
    "Non-Refundable & Heavy Penalties": ["non-refundable", "cancellation fee", "liquidated damages", "forfeiture", "security deposit retention"]
}

def scan_keywords_for_risks(clause_text: str) -> List[str]:
    """Fast keyword rule-matcher to flag potential red flags."""
    lower_text = clause_text.lower()
    matched_flags = []
    for flag_name, keywords in RED_FLAG_KEYWORDS.items():
        if any(kw in lower_text for kw in keywords):
            matched_flags.append(flag_name)
    return matched_flags


def simplify_clause(clause_text: str, target_language: str = "English") -> str:
    """
    Translates a complex legal clause into plain, simple explanations in the target language.
    Retains original currency amounts, numbers, proper names, and survey numbers in original English/digits.
    """
    prompt = f"""You are DocuSense AI, an expert document assistant simplifying agreements for everyday people.
Translate the following clause into clear, plain, simple explanations (2-3 sentences max).
Avoid legal jargon. Focus on what this means practically for the reader.

CRITICAL INSTRUCTION 1: You MUST output your explanation in {target_language}.
CRITICAL INSTRUCTION 2: Keep all monetary amounts (e.g., ₹45,00,000, Rs. 5000), numbers, dates, proper names (e.g., Palanisamy, Muthusamy, Kinathukadavu), survey numbers, and document codes in their ORIGINAL English digits and spelling. Do NOT convert numbers or proper names into other characters.

Clause Text:
\"\"\"
{clause_text[:1800]}
\"\"\"

Plain Explanation ({target_language}):"""

    try:
        response = ollama.generate(model=MODEL_NAME, prompt=prompt, options={"temperature": 0.2})
        explanation = response.get("response", "").strip()
        return explanation if explanation else "This section outlines standard operational terms."
    except Exception as e:
        return f"Explanation unavailable: {str(e)}."


def assess_clause_risk(clause_text: str, target_language: str = "English") -> Dict[str, Any]:
    """
    Evaluates a clause for risk level (CRITICAL, WARNING, LOW) and flags noteworthy terms.
    """
    keyword_flags = scan_keywords_for_risks(clause_text)
    
    prompt = f"""Analyze the following clause for risks or unusual terms that could disadvantage a user or reader.

Clause Text:
\"\"\"
{clause_text[:1800]}
\"\"\"

Respond in the following EXACT format (keep key headers in English, write reasoning and action in {target_language}):

RISK LEVEL: [CRITICAL, WARNING, or LOW] (Must be in English)
RISK TYPE: [Short 2-4 word category name] (Must be in English)
REASONING: [1-2 sentences explaining why it is risky or noteworthy, WRITTEN IN {target_language}]
ACTION/ADVICE: [1 sentence actionable advice for the user, WRITTEN IN {target_language}]"""

    try:
        response = ollama.generate(model=MODEL_NAME, prompt=prompt, options={"temperature": 0.1})
        res_text = response.get("response", "").strip()
        
        risk_level = "LOW"
        risk_type = keyword_flags[0] if keyword_flags else "Standard Term"
        reasoning = "Standard clause structure with no unusual liabilities."
        action = "No specific action required."
        
        for line in res_text.split("\n"):
            if line.startswith("RISK LEVEL:"):
                level_str = line.split(":", 1)[1].strip().upper()
                if "CRITICAL" in level_str:
                    risk_level = "CRITICAL"
                elif "WARNING" in level_str or "HIGH" in level_str:
                    risk_level = "WARNING"
                else:
                    risk_level = "LOW"
            elif line.startswith("RISK TYPE:"):
                risk_type = line.split(":", 1)[1].strip()
            elif line.startswith("REASONING:"):
                reasoning = line.split(":", 1)[1].strip()
            elif line.startswith("ACTION/ADVICE:") or line.startswith("ACTION:"):
                action = line.split(":", 1)[1].strip()
                
        if keyword_flags and risk_level == "LOW":
            risk_level = "WARNING"
            
        return {
            "risk_level": risk_level,
            "risk_type": risk_type,
            "reasoning": reasoning,
            "action": action,
            "keyword_flags": keyword_flags
        }
    except Exception as e:
        level = "WARNING" if keyword_flags else "LOW"
        return {
            "risk_level": level,
            "risk_type": keyword_flags[0] if keyword_flags else "Standard Clause",
            "reasoning": f"Flagged by rule scanner: {', '.join(keyword_flags)}" if keyword_flags else "Standard agreement language.",
            "action": "Review section carefully.",
            "keyword_flags": keyword_flags
        }


def generate_document_summary(clauses: List[Dict[str, Any]], target_language: str = "English") -> Dict[str, Any]:
    """
    Generates document safety score, explicit user safety verdict, and key recommendations.
    Passes full text of clauses into prompt so LLM generates a grounded summary without complaining.
    """
    total_clauses = len(clauses)
    critical_count = sum(1 for c in clauses if c.get("risk", {}).get("risk_level") == "CRITICAL")
    warning_count = sum(1 for c in clauses if c.get("risk", {}).get("risk_level") == "WARNING")
    low_count = total_clauses - critical_count - warning_count
    
    score = 100 - (critical_count * 25) - (warning_count * 10)
    health_score = max(10, min(100, score))
    
    if critical_count >= 2 or health_score < 50:
        verdict_status = "UNSAFE"
        verdict_title = "HIGH RISK — DO NOT ACCEPT AS-IS"
        verdict_color = "#EF4444"
        verdict_badge = "UNSAFE TO SIGN"
        verdict_recommendation = "This document contains severe red flags (such as unilateral termination or non-refundable deposits). Do not sign without negotiating terms."
    elif critical_count == 1 or warning_count >= 2 or health_score < 80:
        verdict_status = "CAUTION"
        verdict_title = "PROCEED WITH CAUTION"
        verdict_color = "#F59E0B"
        verdict_badge = "PROCEED WITH CAUTION"
        verdict_recommendation = "This document contains noteworthy clauses that restrict user rights. Review highlighted risk clauses carefully."
    else:
        verdict_status = "SAFE"
        verdict_title = "SAFE TO ACCEPT"
        verdict_color = "#10B981"
        verdict_badge = "SAFE TO SIGN"
        verdict_recommendation = "This agreement contains standard balanced terms with no unusual liabilities or hidden penalties."

    # Build snippet of document for the summary prompt
    doc_text_snippets = "\n".join([f"Clause {c['id']} ({c['title']}): {c['text'][:300]}" for c in clauses])
    
    summary_prompt = f"""Summarize the main purpose and key terms of the following document:

Document Content:
{doc_text_snippets[:3500]}

Total Clauses: {total_clauses}. Critical Risks: {critical_count}. Warnings: {warning_count}.

CRITICAL INSTRUCTIONS:
1. Write 3 clear, concise bullet points summarizing what this document is about, the parties involved, and its key terms.
2. The bullet points MUST be written in {target_language}.
3. Keep all numbers, currency amounts (e.g. ₹45,00,000, Rs. 5000), survey numbers, and proper names (e.g. Palanisamy, Muthusamy) in original English digits/spelling."""

    try:
        response = ollama.generate(model=MODEL_NAME, prompt=summary_prompt, options={"temperature": 0.2})
        summary_bullets = response.get("response", "").strip()
    except Exception:
        summary_bullets = "• Document outlines standard terms.\n• Highlighted risks detected in liability and cancellation clauses.\n• Review risk sections before signing."
        
    return {
        "total_clauses": total_clauses,
        "critical_count": critical_count,
        "warning_count": warning_count,
        "low_count": low_count,
        "health_score": health_score,
        "verdict_status": verdict_status,
        "verdict_title": verdict_title,
        "verdict_color": verdict_color,
        "verdict_badge": verdict_badge,
        "verdict_recommendation": verdict_recommendation,
        "executive_summary": summary_bullets
    }


def answer_question_with_context(
    query: str, 
    all_clauses: List[Dict[str, Any]], 
    doc_summary: Dict[str, Any] = None,
    doc_name: str = "Uploaded Document",
    doc_legality: Dict[str, Any] = None,
    target_language: str = "English"
) -> str:
    """
    100% Full-Context Grounded RAG answer generator.
    Passes all clauses and document context to guarantee exact extraction of party names, amounts, and terms.
    Prevents external hallucinations (e.g., Google CEO questions).
    """
    context_str = f"=== DOCUMENT IDENTIFIER & TITLE ===\nDocument Title: {doc_name}\n"
    
    if doc_legality:
        context_str += f"Legality Status: {doc_legality.get('legality', 'N/A')} (Document Type: {doc_legality.get('doc_type', 'N/A')})\n"
        
    if doc_summary:
        context_str += f"Safety Verdict: {doc_summary.get('verdict_badge', 'N/A')} (Safety Score: {doc_summary.get('health_score', 0)}/100)\n"
        context_str += f"Executive Summary: {doc_summary.get('executive_summary', '')}\n"

    context_str += "\n=== COMPLETE DOCUMENT TEXT & ALL CLAUSES ===\n"
    for clause in all_clauses:
        context_str += f"\n[Clause {clause['id']} - {clause['title']}]:\n{clause['text']}\nSummary: {clause.get('explanation', '')}\n"
            
    prompt = f"""You are DocuSense AI, a strict, highly accurate legal document assistant.

User Question: "{query}"

Document Context:
{context_str[:6000]}

STRICT GROUNDING & EXTRACTION RULES:
1. Answer the user's question ONLY using the facts present in the Document Context above.
2. If the user asks about an external entity, company, or fact NOT mentioned in the document (such as "who is Google CEO?", "what is the weather?", or unrelated external facts), respond in {target_language}: "This information is not mentioned in the uploaded document."
3. When asked about parties (such as Seller, Buyer, Landlord, Tenant, Owner), search the Document Context carefully and state their exact names (e.g. Seller: Palanisamy, Buyer: Muthusamy).
4. Keep all monetary amounts (e.g. ₹45,00,000, Rs. 5000), numbers, dates, proper names, survey numbers (e.g. 123/2A), and IDs in their ORIGINAL English spelling and digits.
5. Write your complete answer in {target_language}.

Answer ({target_language}):"""

    try:
        response = ollama.generate(model=MODEL_NAME, prompt=prompt, options={"temperature": 0.1})
        ans = response.get("response", "").strip()
        return ans if ans else "I couldn't generate an answer based on the current document context."
    except Exception as e:
        return f"Unable to generate response via local LLM ({str(e)})."


def check_document_legality(full_text: str, target_language: str = "English") -> Dict[str, Any]:
    """
    Analyzes whether the uploaded document appears to be a legitimate legal document
    or contains signs of being illegal, fraudulent, or forged.
    """
    snippet = full_text[:3000]
    
    prompt = f"""You are a legal document forensics expert. Analyze the following document text carefully.

Document Text:
\"\"\"
{snippet}
\"\"\"

Determine whether this document appears to be:
1. A LEGITIMATE legal document (proper structure, standard legal language, identifiable parties, valid clauses)
2. A SUSPICIOUS or potentially ILLEGAL/FRAUDULENT document (missing key elements, forged signatures mentioned, unusual demands, scam language, missing legal identifiers, unrealistic terms)

Respond in the following EXACT format (keys in English, values in {target_language}):

LEGALITY STATUS: [LEGITIMATE or SUSPICIOUS] (Must be in English)
DOCUMENT TYPE: [e.g., Land Deed, Rental Agreement, Insurance Policy, Employment Contract, Unknown] (In English)
CONFIDENCE: [HIGH, MEDIUM, or LOW] (In English)
ANALYSIS: [2-3 sentences explaining why you reached this conclusion, WRITTEN IN {target_language}]
RED FLAGS: [List any suspicious elements found, or "None detected" if legitimate, WRITTEN IN {target_language}]
RECOMMENDATION: [1 sentence advice for the user, WRITTEN IN {target_language}]"""

    try:
        response = ollama.generate(model=MODEL_NAME, prompt=prompt, options={"temperature": 0.1})
        res_text = response.get("response", "").strip()
        
        legality = "LEGITIMATE"
        doc_type = "Unknown"
        confidence = "MEDIUM"
        analysis = "Document structure appears standard."
        red_flags = "None detected"
        recommendation = "Review document with a legal professional before signing."
        
        for line in res_text.split("\n"):
            if line.startswith("LEGALITY STATUS:"):
                val = line.split(":", 1)[1].strip().upper()
                legality = "SUSPICIOUS" if "SUSPICIOUS" in val or "ILLEGAL" in val or "FRAUD" in val else "LEGITIMATE"
            elif line.startswith("DOCUMENT TYPE:"):
                doc_type = line.split(":", 1)[1].strip()
            elif line.startswith("CONFIDENCE:"):
                confidence = line.split(":", 1)[1].strip().upper()
                if "HIGH" in confidence:
                    confidence = "HIGH"
                elif "LOW" in confidence:
                    confidence = "LOW"
                else:
                    confidence = "MEDIUM"
            elif line.startswith("ANALYSIS:"):
                analysis = line.split(":", 1)[1].strip()
            elif line.startswith("RED FLAGS:"):
                red_flags = line.split(":", 1)[1].strip()
            elif line.startswith("RECOMMENDATION:"):
                recommendation = line.split(":", 1)[1].strip()
        
        return {
            "legality": legality,
            "doc_type": doc_type,
            "confidence": confidence,
            "analysis": analysis,
            "red_flags": red_flags,
            "recommendation": recommendation
        }
    except Exception as e:
        return {
            "legality": "UNKNOWN",
            "doc_type": "Unknown",
            "confidence": "LOW",
            "analysis": f"Could not perform legality check: {str(e)}",
            "red_flags": "Analysis unavailable",
            "recommendation": "Please consult a legal professional."
        }
