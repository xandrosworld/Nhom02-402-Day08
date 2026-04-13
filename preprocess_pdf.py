"""
preprocess_pdf.py — Feature: PDF → Markdown (Hoàng Nam # PLN)
==============================================================
Mục tiêu:
  Gọi AI (Gemini Vision hoặc GPT-4o Vision) để convert file PDF
  sang Markdown có cấu trúc trước khi đưa vào index.py.

Tại sao cần:
  - PDF raw extract mất cấu trúc (heading, bảng, bullet)
  - Markdown giữ được heading → chunking theo section tốt hơn
  - AI Vision đọc được cả bảng, hình, layout phức tạp

Output:
  - Mỗi file PDF → 1 file .md trong data/docs/markdown/
  - index.py đọc .md thay vì .txt

Usage:
  python preprocess_pdf.py                      # Convert tất cả PDF trong data/pdf/
  python preprocess_pdf.py --file data/pdf/x.pdf  # Convert 1 file
"""

import os
import argparse
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CẤU HÌNH
# =============================================================================

PDF_INPUT_DIR  = Path(__file__).parent / "data" / "pdf"       # Thư mục chứa PDF gốc
MD_OUTPUT_DIR  = Path(__file__).parent / "data" / "docs"      # Output Markdown (index.py đọc từ đây)

PROVIDER = os.getenv("LLM_PROVIDER", "gemini")   # "gemini" hoặc "openai"


# =============================================================================
# STEP 1: ĐỌC PDF → BASE64 (để gửi cho Vision model)
# =============================================================================

def pdf_to_images_base64(pdf_path: Path):
    """
    Convert PDF sang list base64 images (mỗi trang 1 ảnh).

    TODO (PLN):
    Cài: pip install pdf2image pillow
    Cần poppler:
      - Windows: tải từ https://github.com/oschwartz10612/poppler-windows/releases
      - Mac: brew install poppler

    from pdf2image import convert_from_path
    import base64, io

    pages = convert_from_path(str(pdf_path), dpi=150)
    result = []
    for page in pages:
        buffer = io.BytesIO()
        page.save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode()
        result.append(b64)
    return result
    """
    raise NotImplementedError("TODO (PLN): Implement pdf_to_images_base64()")


# =============================================================================
# STEP 2: GỌI AI VISION → MARKDOWN
# =============================================================================

def call_vision_gemini(images_b64: list, filename: str) -> str:
    """
    Gọi Gemini Vision để convert list ảnh PDF → Markdown.

    TODO (PLN):
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")

    parts = []
    for b64 in images_b64:
        parts.append({"inline_data": {"mime_type": "image/png", "data": b64}})

    parts.append({"text": VISION_PROMPT.format(filename=filename)})
    response = model.generate_content(parts)
    return response.text
    """
    raise NotImplementedError("TODO (PLN): Implement call_vision_gemini()")


def call_vision_openai(images_b64: list, filename: str) -> str:
    """
    Gọi GPT-4o Vision để convert list ảnh PDF → Markdown.

    TODO (PLN):
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    content = [{"type": "text", "text": VISION_PROMPT.format(filename=filename)}]
    for b64 in images_b64:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{b64}"}
        })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": content}],
        max_tokens=4096,
    )
    return response.choices[0].message.content
    """
    raise NotImplementedError("TODO (PLN): Implement call_vision_openai()")


VISION_PROMPT = """Convert this document page to clean Markdown.
Preserve all headings (use ##, ###), bullet points, tables, and numbered lists.
Keep all policy details, dates, numbers exactly as written.
Add metadata header at the top:
Source: {filename}
---
Then the Markdown content below.
Do not add any commentary or explanation."""


# =============================================================================
# STEP 3: PIPELINE CHÍNH
# =============================================================================

def convert_pdf_to_markdown(pdf_path: Path, output_dir: Path = MD_OUTPUT_DIR) -> Path:
    """
    Pipeline: PDF file → Markdown file.

    TODO (PLN):
    1. Gọi pdf_to_images_base64() để convert PDF → images
    2. Gọi call_vision_gemini() hoặc call_vision_openai() tuỳ PROVIDER
    3. Lưu kết quả vào output_dir / [filename].md
    4. Return path của file .md đã tạo
    """
    print(f"Converting: {pdf_path.name}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / (pdf_path.stem + ".md")

    # TODO (PLN): Implement
    raise NotImplementedError("TODO (PLN): Implement convert_pdf_to_markdown()")

    return output_path


def convert_all_pdfs(input_dir: Path = PDF_INPUT_DIR, output_dir: Path = MD_OUTPUT_DIR):
    """
    Convert tất cả PDF trong input_dir → Markdown trong output_dir.
    """
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"Không tìm thấy file PDF trong {input_dir}")
        print("Tạo thư mục data/pdf/ và đặt PDF vào đó.")
        return

    print(f"Tìm thấy {len(pdf_files)} file PDF:")
    for f in pdf_files:
        print(f"  - {f.name}")

    print()
    for pdf_path in pdf_files:
        try:
            out = convert_pdf_to_markdown(pdf_path, output_dir)
            print(f"  ✓ {pdf_path.name} → {out.name}")
        except Exception as e:
            print(f"  ✗ {pdf_path.name}: {e}")

    print(f"\nHoàn thành! Markdown files tại: {output_dir}")


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert PDF → Markdown bằng AI Vision")
    parser.add_argument("--file", type=str, help="Convert 1 file PDF cụ thể")
    args = parser.parse_args()

    if args.file:
        pdf_path = Path(args.file)
        if not pdf_path.exists():
            print(f"File không tồn tại: {pdf_path}")
        else:
            convert_pdf_to_markdown(pdf_path)
    else:
        convert_all_pdfs()
