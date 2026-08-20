SAMPLE_TOS_TEXT = """
TERMS OF SERVICE AND USER AGREEMENT

Section 1. Acceptance of Terms
By accessing or using the platform ("Service"), you agree to be bound by these Terms of Service. If you do not agree to all terms, you must immediately cease all use of the platform.

Section 2. Automatic Renewal and Recurring Charges
All subscription plans to the Service will automatically renew at the end of each billing cycle (monthly or annually) at the then-current standard rate without prior notice. Your payment method will be charged automatically unless you cancel your subscription at least thirty (30) days prior to the renewal date via written email notice to support.

Section 3. Unilateral Modification of Agreement
We reserve the right, in our sole and absolute discretion, to modify, amend, update, or replace any part of these Terms of Service at any time without prior written notice to you. Your continued use of or access to the Service following the posting of any changes constitutes binding acceptance of those changes.

Section 4. Limitation of Liability and Hold Harmless
To the maximum extent permitted by applicable law, in no event shall the company, its affiliates, directors, employees, or agents be liable for any direct, indirect, incidental, special, consequential, or punitive damages, or any loss of profits or revenues, whether incurred directly or indirectly. You agree to indemnify, defend, and hold harmless the company against any and all third-party claims arising from your use of the Service.

Section 5. Mandatory Binding Arbitration and Class Action Waiver
Any dispute, controversy, or claim arising out of or relating to this agreement shall be settled exclusively by final and binding individual arbitration rather than in court. You explicitly waive any right to participate as a plaintiff or class member in any class action lawsuit, class-wide arbitration, or representative proceeding against us.

Section 6. Data Collection and Third-Party Data Monetization
We collect diagnostic, usage, metadata, and uploaded content logs from your sessions. You grant us a worldwide, royalty-free, perpetual license to anonymize, aggregate, analyze, and share or monetize this data with our trusted third-party advertising and analytics partners.

Section 7. Cancellation and Non-Refundable Payments
All fees and charges paid under this agreement are strictly non-refundable under any circumstances, including partial subscription periods or unutilized API call quotas. Account termination does not relieve you of the obligation to pay accrued fees.
"""

SAMPLE_LAND_POLICY_TEXT = """
SAMPLE LAND SALE AGREEMENT
Illustrative Property Transaction — Kinathukadavu Parcel

1. PARTIES TO THE AGREEMENT
SELLER: Palanisamy, S/o Kamaraguru, Age: 56 years, Occupation: Agriculturist. Address: 12, Kamaraj Street, Kinathukadavu, Coimbatore District - 641105. Identification: DEMO-SELLER-001.
BUYER: Muthusamy, S/o Muthuvel, Age: 45 years, Occupation: Agriculturist. Address: 7, Valluvar Street, Kinathukadavu, Coimbatore District - 641105. Identification: DEMO-BUYER-001.

2. PROPERTY LOCATION & DETAILS
District: Coimbatore, Taluk: Kinathukadavu, Sub-Registrar Office: Kinathukadavu.
Village: Kinathukadavu, Survey Number: 123/2A, Subdivision: 2, Extent: 2.50 Acres, Patta Number: PATTA-DEMO-1234.

3. PROPERTY BOUNDARIES
North: Agricultural land of R. Gopal.
South: 30-foot village access road.
East: Agricultural land of S. Murugesan.
West: Open agricultural field and irrigation channel.

4. DETAILED PROPERTY DESCRIPTION & ACCESS
Agricultural wet land parcel situated in Kinathukadavu, Coimbatore. Survey reference 123/2A measuring 2.50 Acres with 30-foot access road, open irrigation channel, and agricultural electricity connection.

5. CONSIDERATION AND PAYMENT TERMS
Proposed Sale Consideration: ₹45,00,000 (Rupees Forty-Five Lakh only).
Amount Paid in Advance: ₹10,00,000.
Balance Amount Payable: ₹35,00,000.
Mode of Payment: Bank transfer / RTGS. Transaction Date: 20 August 2026.

6. SELLER'S DECLARATION & TITLE WARRANTY
The Seller Palanisamy declares that the property is proposed to be transferred free from undisclosed encumbrances, subject to independent title verification. Possession shall be handed over only upon full receipt of balance ₹35,00,000 and complete statutory registration.

7. BUYER'S DECLARATION & DUE DILIGENCE
The Buyer Muthusamy agrees to independently verify all survey measurements, encumbrance certificates, tax receipts, and statutory approvals prior to final execution and registration.

8. TAXES, STAMP DUTY & STATUTORY CHARGES
All stamp duty fees, registration charges, legal expenses, and statutory duties shall be borne by the Buyer as per Tamil Nadu Registration rules.
"""

def get_sample_clauses(doc_type="tos"):
    """Generates pre-parsed clause list for sample contracts."""
    raw_text = SAMPLE_LAND_POLICY_TEXT if doc_type == "land" else SAMPLE_TOS_TEXT
    sections = raw_text.strip().split("\n\n")
    clauses = []
    for idx, sec in enumerate(sections, 1):
        lines = sec.strip().split("\n")
        title = lines[0] if lines else f"Section {idx}"
        text = sec.strip()
        clauses.append({
            "id": idx,
            "title": title,
            "header": title,
            "text": text,
            "body": "\n".join(lines[1:]) if len(lines) > 1 else text,
            "word_count": len(text.split())
        })
    return clauses
