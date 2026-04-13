from unstructured.partition.pdf import partition_pdf
from openai import OpenAI
import tiktoken
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

client = OpenAI()

def extract_elements(file_path):
    elements = partition_pdf(
        filename=file_path,
        strategy="fast"
    )
    return elements

def elements_to_text(elements):
    texts = []
    for el in elements:
        text = el.text.strip() if el.text else ""
        if not text: continue
        if el.category == "Title":
            texts.append(f"# {text}")
        elif el.category == "ListItem":
            texts.append(f"- {text}")
        elif el.category == "Table":
            texts.append(text)
        else:
            texts.append(text)
    return "\n".join(texts)

def chunk_text(text, max_tokens=1500):
    enc = tiktoken.encoding_for_model("gpt-4o") # using popular model for enc
    tokens = enc.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk = enc.decode(tokens[i:i + max_tokens])
        chunks.append(chunk)
    return chunks

def format_markdown(chunk):
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
    response = client.chat.completions.create(
        model="gpt-4o", # using realistic model instead of gpt-5.3
        temperature=0,
        messages=[
            {"role": "system", "content": "You are a Markdown formatter."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def pdf_to_markdown_converter(file_path):
    elements = extract_elements(file_path)
    text = elements_to_text(elements)
    chunks = chunk_text(text)
    md_parts = []
    for chunk in chunks:
        md = format_markdown(chunk)
        md_parts.append(md)
    final_md = "\n\n".join(md_parts)
    return final_md
