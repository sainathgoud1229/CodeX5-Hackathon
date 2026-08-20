"""
Generate PROMPT_ENGINEERING_GUIDE.pdf
Professional PDF with all 8 prompts in ROLE/CONTEXT/TASK/FORMAT/CONSTRAINT format.
Uses ReportLab with Segoe UI font for Unicode support.
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ─── Font Registration ─────────────────────────────────────────────────────────
FONT_DIR = r"C:\Windows\Fonts"
FONTS = {
    "SegoeUI":       "segoeui.ttf",
    "SegoeUI-Bold":  "segoeuib.ttf",
    "SegoeUI-Italic":"segoeuii.ttf",
}
for name, filename in FONTS.items():
    path = os.path.join(FONT_DIR, filename)
    if os.path.exists(path):
        try:
            pdfmetrics.registerFont(TTFont(name, path))
        except Exception:
            pass

BODY_FONT   = "SegoeUI"       if "SegoeUI"       in pdfmetrics.getRegisteredFontNames() else "Helvetica"
BOLD_FONT   = "SegoeUI-Bold"  if "SegoeUI-Bold"  in pdfmetrics.getRegisteredFontNames() else "Helvetica-Bold"
ITALIC_FONT = "SegoeUI-Italic"if "SegoeUI-Italic" in pdfmetrics.getRegisteredFontNames() else "Helvetica-Oblique"

# ─── Colour Palette ────────────────────────────────────────────────────────────
DARK_BG      = colors.HexColor("#0F1923")
ACCENT       = colors.HexColor("#00D4FF")
ACCENT2      = colors.HexColor("#6C63FF")
WHITE        = colors.HexColor("#FFFFFF")
LIGHT_GRAY   = colors.HexColor("#F5F7FA")
MID_GRAY     = colors.HexColor("#E2E8F0")
DARK_TEXT    = colors.HexColor("#1A202C")
MUTED        = colors.HexColor("#718096")
ROW_DARK     = colors.HexColor("#EBF4FF")
ROW_LIGHT    = colors.HexColor("#FFFFFF")
HEADER_BG    = colors.HexColor("#1E3A5F")
SECTION_BG   = colors.HexColor("#F0F7FF")
SUMM_HDR     = colors.HexColor("#2D3748")

# ─── Styles ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

S_TITLE = ParagraphStyle("title",
    fontName=BOLD_FONT, fontSize=22, textColor=WHITE,
    leading=28, spaceAfter=4, alignment=1)

S_SUBTITLE = ParagraphStyle("subtitle",
    fontName=ITALIC_FONT, fontSize=11, textColor=colors.HexColor("#A0C4FF"),
    leading=16, spaceAfter=2, alignment=1)

S_TEAM = ParagraphStyle("team",
    fontName=BOLD_FONT, fontSize=10, textColor=colors.HexColor("#FFD700"),
    leading=14, spaceAfter=0, alignment=1)

S_SECTION = ParagraphStyle("section",
    fontName=BOLD_FONT, fontSize=13, textColor=DARK_BG,
    leading=18, spaceBefore=8, spaceAfter=4)

S_BODY = ParagraphStyle("body",
    fontName=BODY_FONT, fontSize=9, textColor=DARK_TEXT,
    leading=13, spaceAfter=2)

S_CODE = ParagraphStyle("code",
    fontName="Courier", fontSize=8, textColor=colors.HexColor("#C53030"),
    leading=11, spaceAfter=2)

S_FOOTER = ParagraphStyle("footer",
    fontName=ITALIC_FONT, fontSize=8, textColor=MUTED,
    leading=11, alignment=1)

S_SUMM_HDR = ParagraphStyle("summ_hdr",
    fontName=BOLD_FONT, fontSize=9, textColor=WHITE, leading=12)

S_SUMM_BODY = ParagraphStyle("summ_body",
    fontName=BODY_FONT, fontSize=8, textColor=DARK_TEXT, leading=11)

# ─── Prompt Data ───────────────────────────────────────────────────────────────
PROMPTS = [
    {
        "number": 1,
        "title": "Project Kickoff & Initial Architecture",
        "fields": [
            ("ROLE",       "You are an expert Python full-stack AI developer specializing in local LLM pipelines and Streamlit applications."),
            ("CONTEXT",    "SRM IST Hack & Fest AI Innovation Hackathon (Day 4). Problem Statement 1.2: Contract & Policy Clause Explainer. Ollama local models: llama3.2:latest and nomic-embed-text:latest. No internet APIs — 100% offline and local."),
            ("TASK",       "Convert an existing Stitch MCP UI design (ClauseGuard AI) into a fully functional Streamlit application with PDF upload, document processing, clause analysis, RAG-powered Q&A, and risk detection."),
            ("FORMAT",     "Python code using Streamlit for UI, PyPDF2 for PDF reading, and Ollama REST API for LLM calls. Modular files: app.py, llm_utils.py, pdf_utils.py, rag_utils.py."),
            ("CONSTRAINT", "Must work 100% offline. No OpenAI, no Hugging Face API, no paid services. Only Ollama local models."),
        ]
    },
    {
        "number": 2,
        "title": "PDF Audit Report Export",
        "fields": [
            ("ROLE",       "You are a Python developer with expertise in ReportLab PDF generation and Streamlit download buttons."),
            ("CONTEXT",    "DocuSense AI currently only exports audit reports as .md (Markdown) files. Users need a downloadable PDF format for professional presentation."),
            ("TASK",       "Add a PDF export button to the Streamlit application that generates a professional audit report using ReportLab and allows the user to download it."),
            ("FORMAT",     "Create a new pdf_generator.py module. Add a st.download_button in app.py. The PDF must include document summary, clauses, risk scores, and safety verdict."),
            ("CONSTRAINT", "Do not change any existing business logic. Only add the PDF generation layer. The PDF must be readable on Windows without installing additional font software."),
        ]
    },
    {
        "number": 3,
        "title": "Enterprise UI Redesign & Safety Verdict System",
        "fields": [
            ("ROLE",       "You are a senior UI/UX designer and Streamlit developer who builds professional, enterprise-grade data dashboards."),
            ("CONTEXT",    "The current Stitch-based theme uses generic colors that look unprofessional. The summary tab needs a clear Accept/Reject recommendation for any policy or document."),
            ("TASK",       "Redesign the entire UI with a professional dark theme. Add a Policy Safety Score (0-100%) and a Safety Verdict banner (SAFE TO SIGN, PROCEED WITH CAUTION, UNSAFE TO SIGN) based on risk score analysis. Fix the Q&A tab so it actually returns answers from the document."),
            ("FORMAT",     "Custom CSS injected via st.markdown(). Safety verdict displayed as a styled banner. Score shown as st.metric and st.progress."),
            ("CONSTRAINT", "Colors must look professional — no primary red/blue/green. Use dark backgrounds (#0F1923, #1A2332) with accent gradients. Q&A must use the uploaded document as its only source — no hallucination."),
        ]
    },
    {
        "number": 4,
        "title": "Multi-Input Support, Indic Language Translation & Rebranding",
        "fields": [
            ("ROLE",       "You are a multilingual AI engineer experienced with Indic language NLP, Streamlit UI components, and RAG pipelines."),
            ("CONTEXT",    "DocuSense AI currently only accepts PDF files. Many users are non-English speakers from South India who cannot understand English legal documents. The app is named ClauseGuard AI which is hard to remember."),
            ("TASK",       "1. Rename the app to DocuSense AI. 2. Add three input modes: PDF upload, Image upload (OCR), and raw text paste. 3. Add language selection (English, Telugu, Tamil, Malayalam, Hindi, Spanish, French). 4. Translate all outputs to the selected language. 5. Add a text input box in the Q&A tab for custom questions."),
            ("FORMAT",     "Language selector as st.radio or styled pill buttons. Translation call added to all LLM functions in llm_utils.py. Raw text input as st.text_area in the document upload section."),
            ("CONSTRAINT", "Numbers, currency (Rs.45,00,000), proper names (Palanisamy, Muthusamy), survey numbers (123/2A), and document IDs must always remain in original English digits — never translated or transliterated."),
        ]
    },
    {
        "number": 5,
        "title": "EasyOCR Engine & Document Legality Forensics",
        "fields": [
            ("ROLE",       "You are a computer vision and OCR specialist with expertise in Python image processing and Windows system compatibility."),
            ("CONTEXT",    "The app was using Tesseract-OCR which is not installed. When switching to EasyOCR, a Windows console encoding crash occurs: 'charmap' codec can't encode character in position 12. Users also need the app to detect if an uploaded document is legally valid or fraudulent."),
            ("TASK",       "1. Replace Tesseract with EasyOCR. 2. Fix the Windows CP1252 encoding crash by wrapping stdout/stderr with UTF-8 TextIOWrapper and setting verbose=False. 3. Add a check_document_legality() function that analyzes the document for mandatory legal fields and returns a legality verdict."),
            ("FORMAT",     "Fix in pdf_utils.py using io.TextIOWrapper. New function check_document_legality() in llm_utils.py returning a dict with: verdict, confidence_score, present_fields, missing_fields, and risk_flags. Display in a new Legality Check card in app.py."),
            ("CONSTRAINT", "EasyOCR must not produce any Unicode errors on Windows. The legality verdict must be derived strictly from the uploaded document content only — not from general knowledge."),
        ]
    },
    {
        "number": 6,
        "title": "RAG Grounding Fix, Indic PDF Font Support & Sample Deed",
        "fields": [
            ("ROLE",       "You are an expert in LLM prompt engineering, RAG grounding, ReportLab PDF typography, and Indian legal document formats."),
            ("CONTEXT",    "When a user asks 'Who is the CEO of Google?' after uploading a land deed, the model hallucinated a Tamil answer. Also, the PDF report generates black rectangle glyphs instead of Indic script because Helvetica doesn't support Unicode. The sample document needs a realistic South Indian land sale agreement."),
            ("TASK",       "1. Enforce strict RAG grounding: if a question cannot be answered from the uploaded document, the model must respond 'This information is not mentioned in the uploaded document.' 2. Fix PDF Indic font rendering by registering Windows Segoe UI TTF font. 3. Sanitize emoji characters from PDF titles. 4. Update sample_data.py with a Kinathukadavu Land Sale Agreement (Palanisamy to Muthusamy, Rs.45,00,000, 2.50 Acres, Survey 123/2A)."),
            ("FORMAT",     "Grounding rules added as system instructions in every LLM prompt in llm_utils.py. Font registered in pdf_generator.py header. Sample text as a multi-line string constant in sample_data.py."),
            ("CONSTRAINT", "The model must NEVER fabricate information not in the uploaded document. Currency amounts, names, and survey numbers must stay in their original English/numeric form even when output language is Tamil, Telugu, or Malayalam."),
        ]
    },
    {
        "number": 7,
        "title": "Q&A UI Overhaul, Full-Context RAG & README Overhaul",
        "fields": [
            ("ROLE",       "You are a senior full-stack developer and technical documentation writer specializing in Streamlit UX and GitHub README standards."),
            ("CONTEXT",    "Users cannot find the Q&A text box in the app. The RAG answers are incomplete because chunk-based retrieval splits seller/buyer names across chunk boundaries. The README file needs to be overhauled with team details, system architecture, and feature documentation for hackathon submission."),
            ("TASK",       "1. Make the Q&A text input box clearly visible and prominent in Tab 4. 2. Switch from chunk-based retrieval to full-context passing (all clauses + full text) for short documents (1-10 pages). 3. Completely overhaul README.md with: Team 2 member roster table, Mermaid architecture diagram, feature matrix table, and step-by-step setup guide."),
            ("FORMAT",     "Q&A as a visible st.form with st.text_input and st.form_submit_button. README in GitHub-flavored Markdown with Mermaid code block for the architecture diagram."),
            ("CONSTRAINT", "Do not change any analysis logic or LLM model settings. Only UI layout and context passing method. Full-context passing must preserve all monetary values and proper names in original form."),
        ]
    },
    {
        "number": 8,
        "title": "Prompt History Export for Evaluation",
        "fields": [
            ("ROLE",       "You are a technical documentation specialist extracting conversation history for academic evaluation and hackathon submission."),
            ("CONTEXT",    "All development prompts used during DocuSense AI's hackathon build session need to be documented for evaluation and PDF conversion. The user needs a clean, structured text file of all 8 development stages."),
            ("TASK",       "Extract all user prompts from the conversation in chronological order, group them by development stage, and write them to a clean .txt file (project_prompts_history.txt) in the project directory."),
            ("FORMAT",     "Plain text file with stage headers separated by dashed lines. Each stage labeled with 'Stage N: [Title]' and followed by the original prompt text. Unicode-safe (UTF-8 encoding)."),
            ("CONSTRAINT", "Output must be a .txt file only — no .md, no .pdf. Include the original unedited user prompts with typos preserved so it reflects authentic development history."),
        ]
    },
]

SUMMARY_ROWS = [
    ("1", "Project Kickoff",           "Build full Streamlit RAG app",             "100% offline, Ollama only"),
    ("2", "PDF Export",                "Add downloadable PDF audit report",         "No logic changes"),
    ("3", "UI Redesign",               "Professional dark theme + Safety Verdict",  "No generic colors"),
    ("4", "Multi-Input & Translation", "OCR + Text paste + Indic languages",        "Preserve numbers/names in English"),
    ("5", "EasyOCR + Legality",        "Fix OCR crash + Document fraud check",      "No Windows encoding errors"),
    ("6", "RAG Grounding + PDF Fonts", "Stop hallucination + Fix Indic glyphs",     "Strict document-only answers"),
    ("7", "Q&A UI + README",           "Visible Q&A box + Full docs overhaul",      "No logic changes"),
    ("8", "Prompt Export",             "Extract all prompts to .txt",               "Plain text only"),
]

# ─── Helper: Draw Header/Footer on every page ──────────────────────────────────
def on_page(canvas, doc):
    W, H = A4
    # Header bar
    canvas.saveState()
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, H - 1.5*cm, W, 1.5*cm, fill=1, stroke=0)
    canvas.setFont(BOLD_FONT, 10)
    canvas.setFillColor(WHITE)
    canvas.drawString(1.5*cm, H - 1.0*cm, "DocuSense AI — Prompt Engineering Guide")
    canvas.setFont(BODY_FONT, 9)
    canvas.setFillColor(ACCENT)
    canvas.drawRightString(W - 1.5*cm, H - 1.0*cm, "Team 2 | SRM IST Hack & Fest 2026")
    # Footer bar
    canvas.setFillColor(DARK_BG)
    canvas.rect(0, 0, W, 0.9*cm, fill=1, stroke=0)
    canvas.setFont(ITALIC_FONT, 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(1.5*cm, 0.3*cm, "Confidential — For Evaluation Purposes Only")
    canvas.setFillColor(ACCENT)
    canvas.drawRightString(W - 1.5*cm, 0.3*cm, f"Page {doc.page}")
    canvas.restoreState()

# ─── Build PDF ─────────────────────────────────────────────────────────────────
OUTPUT = r"c:\Users\SAINATH\github projects\hackathon\PROMPT_ENGINEERING_GUIDE.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=1.5*cm, rightMargin=1.5*cm,
    topMargin=2.0*cm, bottomMargin=1.5*cm,
)

story = []

# ── Cover Block ───────────────────────────────────────────────────────────────
cover_data = [[
    Paragraph("📋  DocuSense AI", S_TITLE),
]]
cover_bg = Table(cover_data, colWidths=[doc.width])
cover_bg.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), DARK_BG),
    ("TOPPADDING",    (0,0), (-1,-1), 18),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ("LEFTPADDING",   (0,0), (-1,-1), 12),
    ("RIGHTPADDING",  (0,0), (-1,-1), 12),
    ("ROUNDEDCORNERS", [8]),
]))
story.append(cover_bg)

sub_data = [[Paragraph("Prompt Engineering Guide", S_SUBTITLE)]]
sub_table = Table(sub_data, colWidths=[doc.width])
sub_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), DARK_BG),
    ("TOPPADDING",    (0,0), (-1,-1), 2),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ("LEFTPADDING",   (0,0), (-1,-1), 12),
    ("RIGHTPADDING",  (0,0), (-1,-1), 12),
]))
story.append(sub_table)

sub2_data = [[Paragraph("All 8 Project Prompts  ·  ROLE · CONTEXT · TASK · FORMAT · CONSTRAINT Structure", S_SUBTITLE)]]
sub2_table = Table(sub2_data, colWidths=[doc.width])
sub2_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), DARK_BG),
    ("TOPPADDING",    (0,0), (-1,-1), 2),
    ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ("LEFTPADDING",   (0,0), (-1,-1), 12),
    ("RIGHTPADDING",  (0,0), (-1,-1), 12),
]))
story.append(sub2_table)

team_data = [[Paragraph("Team 2  |  Hack & Fest AI Innovation Hackathon  |  SRM IST 2026", S_TEAM)]]
team_table = Table(team_data, colWidths=[doc.width])
team_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), DARK_BG),
    ("TOPPADDING",    (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 18),
    ("LEFTPADDING",   (0,0), (-1,-1), 12),
    ("RIGHTPADDING",  (0,0), (-1,-1), 12),
]))
story.append(team_table)
story.append(Spacer(1, 0.5*cm))

# ── Each Prompt ───────────────────────────────────────────────────────────────
FIELD_COLORS = {
    "ROLE":       colors.HexColor("#6C63FF"),
    "CONTEXT":    colors.HexColor("#00A8D4"),
    "TASK":       colors.HexColor("#00C896"),
    "FORMAT":     colors.HexColor("#F6AD55"),
    "CONSTRAINT": colors.HexColor("#FC5C65"),
}

for p in PROMPTS:
    block = []

    # Section header
    hdr_data = [[Paragraph(f"Prompt {p['number']}  —  {p['title']}", S_SECTION)]]
    hdr_table = Table(hdr_data, colWidths=[doc.width])
    hdr_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), SECTION_BG),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("RIGHTPADDING",  (0,0), (-1,-1), 10),
        ("LINEBELOW",     (0,0), (-1,-1), 2, ACCENT),
    ]))
    block.append(hdr_table)
    block.append(Spacer(1, 0.15*cm))

    # Fields table
    col_w = [2.5*cm, doc.width - 2.5*cm]
    rows = []
    for i, (field, value) in enumerate(p["fields"]):
        fc = FIELD_COLORS.get(field, DARK_BG)
        field_cell = Paragraph(field, ParagraphStyle("fc",
            fontName=BOLD_FONT, fontSize=8.5, textColor=WHITE, leading=12))
        value_cell = Paragraph(value, S_BODY)
        rows.append([field_cell, value_cell])

    tbl = Table(rows, colWidths=col_w, repeatRows=0)
    tbl_style = [
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("TOPPADDING",    (0,0), (-1,-1), 7),
        ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("GRID",          (0,0), (-1,-1), 0.4, MID_GRAY),
        ("LINEAFTER",     (0,0), (0,-1), 2, colors.HexColor("#CBD5E0")),
    ]
    for i, (field, _) in enumerate(p["fields"]):
        fc = FIELD_COLORS.get(field, DARK_BG)
        tbl_style.append(("BACKGROUND", (0,i), (0,i), fc))
        bg = ROW_DARK if i % 2 == 0 else ROW_LIGHT
        tbl_style.append(("BACKGROUND", (1,i), (1,i), bg))

    tbl.setStyle(TableStyle(tbl_style))
    block.append(tbl)
    block.append(Spacer(1, 0.4*cm))

    story.append(KeepTogether(block))

story.append(HRFlowable(width="100%", thickness=1.5, color=ACCENT, spaceAfter=0.4*cm))

# ── Summary Table ─────────────────────────────────────────────────────────────
summ_hdr_data = [[Paragraph("Summary Table — All Prompts at a Glance", S_SECTION)]]
summ_hdr_tbl = Table(summ_hdr_data, colWidths=[doc.width])
summ_hdr_tbl.setStyle(TableStyle([
    ("BACKGROUND",    (0,0), (-1,-1), SUMM_HDR),
    ("TOPPADDING",    (0,0), (-1,-1), 8),
    ("BOTTOMPADDING", (0,0), (-1,-1), 8),
    ("LEFTPADDING",   (0,0), (-1,-1), 10),
    ("RIGHTPADDING",  (0,0), (-1,-1), 10),
    ("LINEBELOW",     (0,0), (-1,-1), 2, ACCENT2),
]))
story.append(summ_hdr_tbl)
story.append(Spacer(1, 0.15*cm))

summ_col_w = [0.8*cm, 3.5*cm, 6.0*cm, 5.5*cm]
summ_head  = [
    Paragraph("#",              ParagraphStyle("sh", fontName=BOLD_FONT, fontSize=9, textColor=WHITE)),
    Paragraph("Stage",          ParagraphStyle("sh", fontName=BOLD_FONT, fontSize=9, textColor=WHITE)),
    Paragraph("Core Ask",       ParagraphStyle("sh", fontName=BOLD_FONT, fontSize=9, textColor=WHITE)),
    Paragraph("Key Constraint", ParagraphStyle("sh", fontName=BOLD_FONT, fontSize=9, textColor=WHITE)),
]
summ_rows = [summ_head]
for n, stage, ask, constraint in SUMMARY_ROWS:
    summ_rows.append([
        Paragraph(n,          S_SUMM_BODY),
        Paragraph(stage,      S_SUMM_BODY),
        Paragraph(ask,        S_SUMM_BODY),
        Paragraph(constraint, S_SUMM_BODY),
    ])

summ_tbl = Table(summ_rows, colWidths=summ_col_w, repeatRows=1)
summ_style = [
    ("BACKGROUND",    (0,0), (-1,0), DARK_BG),
    ("GRID",          (0,0), (-1,-1), 0.4, MID_GRAY),
    ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ("TOPPADDING",    (0,0), (-1,-1), 5),
    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ("LEFTPADDING",   (0,0), (-1,-1), 6),
    ("RIGHTPADDING",  (0,0), (-1,-1), 6),
]
for i in range(1, len(summ_rows)):
    bg = colors.HexColor("#F7FAFC") if i % 2 == 0 else WHITE
    summ_style.append(("BACKGROUND", (0,i), (-1,i), bg))

summ_tbl.setStyle(TableStyle(summ_style))
story.append(summ_tbl)

story.append(Spacer(1, 0.5*cm))
story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
story.append(Spacer(1, 0.2*cm))
story.append(Paragraph(
    "Generated for DocuSense AI — Team 2, SRM IST Hack &amp; Fest 2026 &nbsp;|&nbsp; Confidential Evaluation Document",
    S_FOOTER
))

# ── Build ─────────────────────────────────────────────────────────────────────
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated successfully: {OUTPUT}")
