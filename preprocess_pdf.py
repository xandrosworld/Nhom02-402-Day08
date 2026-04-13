"""PDF to Markdown utility with both CLI and Web modes. - Phạm Lê Hoàng Nam

Features:
1) CLI mode: convert one PDF (local path or URL) or all PDFs in a folder.
2) Web mode: upload PDF from browser and render Markdown in the UI.

Examples:
  python preprocess_pdf.py --file "D:/docs/policy.pdf"
  python preprocess_pdf.py --file "https://example.com/policy.pdf"
  python preprocess_pdf.py --serve
"""

import argparse
import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*_args, **_kwargs):
        return False

ROOT_DIR = Path(__file__).resolve().parent
load_dotenv(ROOT_DIR / ".env")
load_dotenv(ROOT_DIR / "pdf_to_md_app" / ".env")


# =============================================================================
# CONFIG
# =============================================================================

PDF_INPUT_DIR = ROOT_DIR / "data" / "pdf"
MD_OUTPUT_DIR = ROOT_DIR / "docs" / "markdown"
TEMPLATE_DIR = ROOT_DIR / "pdf_to_md_app" / "templates"

ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", os.getenv("LLM_MODEL", "claude-sonnet-4-6"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


# =============================================================================
# CORE CONVERTER LOGIC (migrated from pdf_to_md_app/converter.py)
# =============================================================================

def _openai_client():
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Thiếu OPENAI_API_KEY trong môi trường (.env).")
    return OpenAI(api_key=api_key)


def _anthropic_client():
    from anthropic import Anthropic

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("Thiếu ANTHROPIC_API_KEY trong môi trường (.env).")
    return Anthropic(api_key=api_key)


def extract_elements(file_path: Path):
    from unstructured.partition.pdf import partition_pdf

    return partition_pdf(filename=str(file_path), strategy="fast")


def elements_to_text(elements) -> str:
    texts = []
    for el in elements:
        text = el.text.strip() if getattr(el, "text", None) else ""
        if not text:
            continue

        category = getattr(el, "category", "")
        if category == "Title":
            texts.append(f"# {text}")
        elif category == "ListItem":
            texts.append(f"- {text}")
        else:
            texts.append(text)

    return "\n".join(texts)


def chunk_text(text: str, max_tokens: int = 1500) -> list[str]:
    import tiktoken

    try:
        encoder = tiktoken.encoding_for_model(OPENAI_MODEL)
    except KeyError:
        encoder = tiktoken.get_encoding("cl100k_base")

    tokens = encoder.encode(text)
    return [encoder.decode(tokens[i : i + max_tokens]) for i in range(0, len(tokens), max_tokens)]


def format_markdown(chunk: str) -> str:
    prompt = f"""
Convert the following content into clean Markdown.

Requirements:
- Keep headings (#, ##, ###)
- Convert lists properly
- Format tables into Markdown tables
- Preserve code blocks using ```
- Preserve math using LaTeX ($...$ or $$...$$)
- Keep links and references
- DO NOT hallucinate

Content:
{chunk}
"""

    # Ưu tiên Anthropic trước; nếu thiếu key hoặc gọi lỗi thì fallback sang OpenAI.
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if anthropic_key:
        try:
            response = _anthropic_client().messages.create(
                model=ANTHROPIC_MODEL,
                max_tokens=4000,
                temperature=0,
                system="You are a Markdown formatter.",
                messages=[{"role": "user", "content": prompt}],
            )
            parts = []
            for block in response.content:
                text = getattr(block, "text", "")
                if text:
                    parts.append(text)
            result = "\n".join(parts).strip()
            if result:
                return result
        except Exception as exc:
            print(f"Anthropic failed, fallback to OpenAI: {exc}")

    response = _openai_client().chat.completions.create(
        model=OPENAI_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a Markdown formatter."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""


def pdf_to_markdown_text(file_path: Path) -> str:
    elements = extract_elements(file_path)
    text = elements_to_text(elements)
    chunks = chunk_text(text)

    md_parts = [format_markdown(chunk) for chunk in chunks]
    return "\n\n".join(md_parts).strip()


# =============================================================================
# FILE HELPERS
# =============================================================================

def _is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _download_pdf(url: str) -> Path:
    import requests

    parsed = urlparse(url)
    filename = Path(parsed.path).name or "downloaded.pdf"
    if not filename.lower().endswith(".pdf"):
        filename = f"{filename}.pdf"

    temp_path = Path(tempfile.gettempdir()) / filename
    response = requests.get(url, timeout=60)
    response.raise_for_status()

    temp_path.write_bytes(response.content)
    return temp_path


def _resolve_pdf_input(pdf_input: str) -> tuple[Path, bool]:
    if _is_url(pdf_input):
        return _download_pdf(pdf_input), True

    path = Path(pdf_input)
    if not path.exists():
        raise FileNotFoundError(f"File không tồn tại: {pdf_input}")
    return path, False


# =============================================================================
# PIPELINE
# =============================================================================

def convert_pdf_to_markdown(pdf_input: str, output_dir: Path = MD_OUTPUT_DIR) -> Path:
    pdf_path, is_temp_download = _resolve_pdf_input(pdf_input)
    try:
        print(f"Converting: {pdf_path.name}")
        markdown_content = pdf_to_markdown_text(pdf_path)

        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{pdf_path.stem}.md"
        output_path.write_text(markdown_content, encoding="utf-8")

        print(f"Saved: {output_path}")
        return output_path
    finally:
        if is_temp_download and pdf_path.exists():
            pdf_path.unlink(missing_ok=True)


def convert_all_pdfs(input_dir: Path = PDF_INPUT_DIR, output_dir: Path = MD_OUTPUT_DIR) -> None:
    pdf_files = sorted(input_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"Không tìm thấy file PDF trong {input_dir}")
        return

    print(f"Tìm thấy {len(pdf_files)} file PDF trong {input_dir}.")
    for pdf_path in pdf_files:
        try:
            convert_pdf_to_markdown(str(pdf_path), output_dir)
        except Exception as exc:
            print(f"Lỗi với {pdf_path.name}: {exc}")


# =============================================================================
# WEB APP (migrated from pdf_to_md_app/app.py)
# =============================================================================

def create_app():
    from flask import Flask, jsonify, render_template, request

    app = Flask(__name__, template_folder=str(TEMPLATE_DIR))

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/convert", methods=["POST"])
    def convert():
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]
        if not file or not file.filename:
            return jsonify({"error": "No selected file"}), 400

        if not file.filename.lower().endswith(".pdf"):
            return jsonify({"error": "Invalid file format, must be PDF"}), 400

        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                file.save(tmp.name)
                temp_path = Path(tmp.name)

            markdown_content = pdf_to_markdown_text(temp_path)
            return jsonify({"markdown": markdown_content})
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)

    return app


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="PDF -> Markdown (CLI + Web)")
    parser.add_argument("--file", type=str, help="Đường dẫn local hoặc URL đến file PDF")
    parser.add_argument("--input-dir", type=str, default=str(PDF_INPUT_DIR), help="Thư mục chứa nhiều PDF")
    parser.add_argument("--output-dir", type=str, default=str(MD_OUTPUT_DIR), help="Thư mục lưu Markdown")
    parser.add_argument("--serve", action="store_true", help="Chạy web upload PDF")
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()

    if args.serve:
        app = create_app()
        app.run(host=args.host, port=args.port, debug=True)
        return

    output_dir = Path(args.output_dir)
    if args.file:
        convert_pdf_to_markdown(args.file, output_dir)
    else:
        convert_all_pdfs(Path(args.input_dir), output_dir)


if __name__ == "__main__":
    main()
