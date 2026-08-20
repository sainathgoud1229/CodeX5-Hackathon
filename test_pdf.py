from sample_data import get_sample_clauses
from pdf_generator import create_audit_pdf

def test_pdf():
    clauses = get_sample_clauses()
    for c in clauses:
        c["explanation"] = "Sample plain English explanation for testing PDF build."
        c["risk"] = {
            "risk_level": "WARNING" if c["id"] % 2 == 0 else "LOW",
            "risk_type": "Sample Risk Category",
            "action": "Check clause terms carefully."
        }
        
    summary = {
        "health_score": 85,
        "total_clauses": len(clauses),
        "critical_count": 1,
        "warning_count": 3,
        "low_count": 4,
        "executive_summary": "• Document contains standard terms.\n• Moderate risk flagged in cancellation section."
    }
    
    pdf_bytes = create_audit_pdf("Test Document.pdf", summary, clauses)
    print(f"PDF generated successfully! Size: {len(pdf_bytes)} bytes.")

if __name__ == "__main__":
    test_pdf()
