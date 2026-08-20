from sample_data import get_sample_clauses
from llm_utils import simplify_clause, assess_clause_risk, generate_document_summary, answer_question_with_context
from rag_utils import ClauseVectorStore

def test_pipeline():
    print("Testing ClauseGuard AI Enhanced Q&A Assistant...")
    clauses = get_sample_clauses()
    
    analyzed_clauses = []
    for c in clauses:
        c_copy = dict(c)
        c_copy["explanation"] = simplify_clause(c["text"])
        c_copy["risk"] = assess_clause_risk(c["text"])
        analyzed_clauses.append(c_copy)
        
    vstore = ClauseVectorStore()
    vstore.build_index(analyzed_clauses)
    summary = generate_document_summary(analyzed_clauses)
    
    # Test broad query 1: "what is document saying?"
    q1 = "what is document saying?"
    ret1 = vstore.search(q1, top_k=4)
    ans1 = answer_question_with_context(q1, ret1, doc_summary=summary, doc_name="Sample SaaS ToS")
    print(f"\n--- QUERY 1: '{q1}' ---")
    print(ans1)
    
    # Test broad query 2: "is it safe to accept?"
    q2 = "is it safe to accept?"
    ret2 = vstore.search(q2, top_k=4)
    ans2 = answer_question_with_context(q2, ret2, doc_summary=summary, doc_name="Sample SaaS ToS")
    print(f"\n--- QUERY 2: '{q2}' ---")
    print(ans2)

if __name__ == "__main__":
    test_pipeline()
