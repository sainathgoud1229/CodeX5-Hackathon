import io
import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import List, Dict, Any

# Register Segoe UI font on Windows for clean rendering of non-Latin / Indic scripts
FONT_NAME = 'Helvetica'
FONT_NAME_BOLD = 'Helvetica-Bold'

try:
    segoe_regular = r'C:\Windows\Fonts\segoeui.ttf'
    segoe_bold = r'C:\Windows\Fonts\segoeuib.ttf'
    if os.path.exists(segoe_regular):
        pdfmetrics.registerFont(TTFont('SegoeUI', segoe_regular))
        FONT_NAME = 'SegoeUI'
        if os.path.exists(segoe_bold):
            pdfmetrics.registerFont(TTFont('SegoeUI-Bold', segoe_bold))
            FONT_NAME_BOLD = 'SegoeUI-Bold'
        else:
            FONT_NAME_BOLD = 'SegoeUI'
except Exception:
    FONT_NAME = 'Helvetica'
    FONT_NAME_BOLD = 'Helvetica-Bold'


def clean_text_for_pdf(text: str) -> str:
    """Removes emoji characters and special non-printable symbols that ReportLab cannot render."""
    if not text:
        return ""
    # Strip emojis and problematic unicode symbol ranges
    clean = re.sub(r'[\U00010000-\U0010ffff\u2600-\u27ff\u2300-\u23ff]', '', text)
    # Replace any bullet squares with standard bullet
    clean = clean.replace('■', '•').replace('🛡️', '').replace('🚨', '').replace('⚠️', '').replace('✅', '')
    return clean.strip()


def create_audit_pdf(
    doc_name: str, 
    summary_data: Dict[str, Any], 
    clauses: List[Dict[str, Any]],
    doc_legality: Dict[str, Any] = None
) -> bytes:
    """
    Generates a clean, professional PDF Audit Report.
    Fully handles Indic/Unicode text without black square glyph crashes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName=FONT_NAME_BOLD,
        fontSize=18,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9.5,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=10
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName=FONT_NAME_BOLD,
        fontSize=13,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName=FONT_NAME,
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155')
    )
    
    verdict_style = ParagraphStyle(
        'VerdictText',
        parent=body_style,
        fontName=FONT_NAME_BOLD,
        fontSize=11,
        leading=15
    )
    
    story = []
    
    # Title & Header
    clean_doc_name = clean_text_for_pdf(doc_name)
    story.append(Paragraph("DOCUSENSE AI — EXECUTIVE AUDIT REPORT", title_style))
    story.append(Paragraph(f"Document: <b>{clean_doc_name}</b> | Generated locally via DocuSense AI Companion", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#E2E8F0'), spaceAfter=10))
    
    # Verdict Banner
    verdict_badge = clean_text_for_pdf(summary_data.get('verdict_badge', 'LEGAL AUDIT'))
    health_score = summary_data.get('health_score', 100)
    verdict_rec = clean_text_for_pdf(summary_data.get('verdict_recommendation', 'Review clauses carefully.'))
    v_status = summary_data.get('verdict_status', 'SAFE')
    
    if v_status == 'UNSAFE':
        v_bg = colors.HexColor('#FEF2F2')
        v_border = colors.HexColor('#EF4444')
        v_text_color = '#DC2626'
    elif v_status == 'CAUTION':
        v_bg = colors.HexColor('#FFFBEB')
        v_border = colors.HexColor('#F59E0B')
        v_text_color = '#D97706'
    else:
        v_bg = colors.HexColor('#F0FDF4')
        v_border = colors.HexColor('#10B981')
        v_text_color = '#16A34A'
        
    verdict_content = [
        Paragraph(f"<font color='{v_text_color}'><b>VERDICT: {verdict_badge} (Safety Score: {health_score}/100)</b></font>", verdict_style),
        Spacer(1, 4),
        Paragraph(f"<b>Recommendation:</b> {verdict_rec}", body_style)
    ]
    
    v_table = Table([[verdict_content]], colWidths=[520])
    v_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), v_bg),
        ('BOX', (0,0), (-1,-1), 1.5, v_border),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(v_table)
    story.append(Spacer(1, 10))
    
    # Metrics Table
    metrics_data = [
        [
            Paragraph("<b>Safety Score</b>", body_style),
            Paragraph("<b>Total Clauses</b>", body_style),
            Paragraph("<b>Critical Risks</b>", body_style),
            Paragraph("<b>Warnings</b>", body_style)
        ],
        [
            Paragraph(f"<font size=12 color='{v_text_color}'><b>{health_score}/100</b></font>", body_style),
            Paragraph(f"<font size=11><b>{summary_data.get('total_clauses', 0)}</b></font>", body_style),
            Paragraph(f"<font size=11 color='#DC2626'><b>{summary_data.get('critical_count', 0)}</b></font>", body_style),
            Paragraph(f"<font size=11 color='#D97706'><b>{summary_data.get('warning_count', 0)}</b></font>", body_style)
        ]
    ]
    
    t_metrics = Table(metrics_data, colWidths=[130, 130, 130, 130])
    t_metrics.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_metrics)
    story.append(Spacer(1, 12))
    
    # Executive Summary Section
    story.append(Paragraph("Executive Summary", section_heading))
    raw_summary = summary_data.get('executive_summary', 'No summary available.')
    clean_summary = clean_text_for_pdf(raw_summary).replace('\n', '<br/>')
    story.append(Paragraph(clean_summary, body_style))
    story.append(Spacer(1, 10))
    
    # Detailed Clauses Section
    story.append(Paragraph("Detailed Clause Analysis", section_heading))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#E2E8F0'), spaceAfter=8))
    
    for c in clauses:
        risk_level = c.get('risk', {}).get('risk_level', 'LOW')
        
        if risk_level == 'CRITICAL':
            bg_color = colors.HexColor('#FEF2F2')
            border_color = colors.HexColor('#EF4444')
            badge_text = f"<font color='#DC2626'><b>CRITICAL RISK</b></font>"
        elif risk_level == 'WARNING':
            bg_color = colors.HexColor('#FFFBEB')
            border_color = colors.HexColor('#F59E0B')
            badge_text = f"<font color='#D97706'><b>WARNING</b></font>"
        else:
            bg_color = colors.HexColor('#F0FDF4')
            border_color = colors.HexColor('#10B981')
            badge_text = f"<font color='#16A34A'><b>STANDARD / LOW RISK</b></font>"
            
        clean_title = clean_text_for_pdf(c.get('title', 'Clause'))
        clause_header = f"<b>{clean_title}</b> ({badge_text})"
        category = clean_text_for_pdf(c.get('risk', {}).get('risk_type', 'General'))
        explanation = clean_text_for_pdf(c.get('explanation', 'No explanation generated.'))
        action = clean_text_for_pdf(c.get('risk', {}).get('action', 'N/A'))
        orig_text = clean_text_for_pdf(c.get('text', '')[:300]) + ("..." if len(c.get('text', '')) > 300 else "")
        
        clause_cell_content = [
            Paragraph(clause_header, body_style),
            Spacer(1, 2),
            Paragraph(f"<b>Category:</b> {category}", body_style),
            Paragraph(f"<b>Summary:</b> {explanation}", body_style),
            Paragraph(f"<b>Action Guidance:</b> {action}", body_style),
            Spacer(1, 2),
            Paragraph(f"<i>Original Excerpt:</i> \"{orig_text}\"", ParagraphStyle('Italics', parent=body_style, fontSize=8, fontName=FONT_NAME, textColor=colors.HexColor('#64748B')))
        ]
        
        c_table = Table([[clause_cell_content]], colWidths=[520])
        c_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_color),
            ('BOX', (0,0), (-1,-1), 1, border_color),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        
        story.append(c_table)
        story.append(Spacer(1, 8))
        
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
