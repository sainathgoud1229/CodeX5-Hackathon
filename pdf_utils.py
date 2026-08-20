import re
import pdfplumber
from pypdf import PdfReader
from typing import List, Dict, Any
from PIL import Image
import numpy as np


def extract_text_from_pdf(pdf_file_or_path) -> List[Dict[str, Any]]:
    """
    Extracts text page by page from a PDF file object or file path.
    Returns a list of page dicts with page_number and text.
    """
    pages_data = []
    
    try:
        with pdfplumber.open(pdf_file_or_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                pages_data.append({
                    "page_number": i + 1,
                    "text": text
                })
    except Exception as e:
        # Fallback to PyPDF if pdfplumber fails
        try:
            reader = PdfReader(pdf_file_or_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                pages_data.append({
                    "page_number": i + 1,
                    "text": text
                })
        except Exception as py_err:
            raise RuntimeError(f"Failed to parse PDF document: {str(e)} | PyPDF error: {str(py_err)}")

    return pages_data


def extract_text_from_image(image_file_or_path) -> str:
    """
    Extracts text from an image file using EasyOCR (no external install needed).
    Suppresses EasyOCR verbose output to avoid Windows charmap encoding errors.
    """
    import io
    import sys
    import os
    
    # Fix Windows console encoding — EasyOCR prints unicode progress bars (█)
    # that crash on Windows' default cp1252 encoding
    os.environ["PYTHONIOENCODING"] = "utf-8"
    
    try:
        img = Image.open(image_file_or_path)
        # Convert to RGB if necessary (handles RGBA, grayscale, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        img_array = np.array(img)
        
        # Redirect stdout/stderr to suppress EasyOCR's progress bar unicode chars
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.TextIOWrapper(io.BytesIO(), encoding='utf-8')
        sys.stderr = io.TextIOWrapper(io.BytesIO(), encoding='utf-8')
        
        try:
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False, verbose=False)
            results = reader.readtext(img_array, detail=0, paragraph=True)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        
        text = "\n".join(results)
        
        if not text.strip():
            raise RuntimeError("No readable text found in the image. Please upload a clearer image.")
        
        return text
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from image: {str(e)}")


def parse_clauses_from_text(full_raw_text: str) -> List[Dict[str, Any]]:
    """
    Ingests raw text and parses it into discrete, numbered clauses or logical section chunks.
    """
    # Regex pattern for legal headers and section numbers
    HEADER_PATTERN = re.compile(
        r'(?m)^(?:\d+\.\d*|\([a-z0-9]+\)|Section\s+\d+|SECTION\s+\d+|Article\s+[IVXLCDM\d]+|ARTICLE\s+[IVXLCDM\d]+|Clause\s+\d+|CLAUSE\s+\d+)\s*[:\.\-—]?',
        re.IGNORECASE
    )
    
    # Try regex splitting first
    split_matches = list(HEADER_PATTERN.finditer(full_raw_text))
    
    clauses = []
    if len(split_matches) >= 3:
        for i in range(len(split_matches)):
            start_pos = split_matches[i].start()
            end_pos = split_matches[i+1].start() if i + 1 < len(split_matches) else len(full_raw_text)
            
            clause_str = full_raw_text[start_pos:end_pos].strip()
            if len(clause_str) < 20:
                continue
                
            # Extract header/title line
            lines = clause_str.split("\n")
            header_line = lines[0].strip() if lines else f"Clause {i+1}"
            body_text = "\n".join(lines[1:]).strip() if len(lines) > 1 else clause_str
            
            title = header_line[:60] if len(header_line) <= 60 else header_line[:57] + "..."
            
            clauses.append({
                "id": len(clauses) + 1,
                "title": title,
                "header": header_line,
                "text": clause_str,
                "body": body_text if body_text else clause_str,
                "word_count": len(clause_str.split())
            })
            
    # Fallback to paragraph-based chunking if clear section patterns were not found
    if len(clauses) < 3:
        clauses = []
        raw_paragraphs = full_raw_text.split("\n\n")
        
        current_chunk = ""
        chunk_idx = 1
        
        for para in raw_paragraphs:
            cleaned_p = para.strip()
            if not cleaned_p:
                continue
            
            if len(current_chunk) + len(cleaned_p) < 400:
                current_chunk += ("\n\n" + cleaned_p if current_chunk else cleaned_p)
            else:
                if len(current_chunk) >= 40:
                    first_line = current_chunk.split("\n")[0].strip()
                    title = first_line[:50] + "..." if len(first_line) > 50 else (first_line or f"Section {chunk_idx}")
                    clauses.append({
                        "id": chunk_idx,
                        "title": f"Section {chunk_idx}: {title}",
                        "header": title,
                        "text": current_chunk,
                        "body": current_chunk,
                        "word_count": len(current_chunk.split())
                    })
                    chunk_idx += 1
                current_chunk = cleaned_p
                
        if current_chunk and len(current_chunk) >= 40:
            first_line = current_chunk.split("\n")[0].strip()
            title = first_line[:50] + "..." if len(first_line) > 50 else (first_line or f"Section {chunk_idx}")
            clauses.append({
                "id": chunk_idx,
                "title": f"Section {chunk_idx}: {title}",
                "header": title,
                "text": current_chunk,
                "body": current_chunk,
                "word_count": len(current_chunk.split())
            })

    # Final fallback: if still no clauses, treat the whole text as one chunk
    if not clauses and len(full_raw_text.strip()) >= 20:
        clauses.append({
            "id": 1,
            "title": "Section 1: Full Document Text",
            "header": "Full Document Text",
            "text": full_raw_text.strip(),
            "body": full_raw_text.strip(),
            "word_count": len(full_raw_text.strip().split())
        })

    return clauses


def parse_clauses_from_pdf(pdf_file_or_path) -> List[Dict[str, Any]]:
    """
    Ingests a PDF and parses it into discrete, numbered clauses or logical section chunks.
    """
    pages_data = extract_text_from_pdf(pdf_file_or_path)
    
    full_text_with_pages = []
    for page in pages_data:
        p_num = page["page_number"]
        for line in page["text"].split("\n"):
            full_text_with_pages.append((p_num, line))
            
    full_raw_text = "\n".join([line for _, line in full_text_with_pages])
    return parse_clauses_from_text(full_raw_text)
