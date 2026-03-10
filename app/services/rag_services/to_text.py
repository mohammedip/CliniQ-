from llama_parse import LlamaParse
import os
import re
from dotenv import load_dotenv

load_dotenv()


def clean_markdown(text: str) -> str:
    # Remove page headers like "Guide des Protocoles - 2025 8"
    text = re.sub(r'Guide des Protocoles\s*-\s*\d{4}\s*\d*\n?', '', text)

    # Remove page numbers standing alone on a line
    text = re.sub(r'^\s*\d{1,3}\s*$', '', text, flags=re.MULTILINE)

    # Remove excessive blank lines (more than 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove horizontal rules that add noise
    text = re.sub(r'\n---+\n', '\n\n', text)

    # Clean up table separators that become noise
    text = re.sub(r'\|[\s\|]+\|', '', text)

    return text.strip()


def get_text():
    pdf_path = "/core/docs/guide-des-protocoles.pdf"
    md_output = "/core/docs/manual.md"

    print(f"Checking for file: {pdf_path}")
    if not os.path.exists(pdf_path):
        print(f"ERROR: {pdf_path} not found!")
        return

    parser = LlamaParse(
        api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
        result_type="markdown",
        language="fr",
        verbose=True,
        premium_mode=True,
        parsing_instruction="""
        This is a French medical protocol guide.
        Extract all text content clearly.
        Preserve bullet points and numbered lists.
        Keep section headers.
        Convert tables to readable text where possible.
        Do not add extra formatting.
        """
    )

    documents = parser.load_data(pdf_path)

    with open(md_output, "w", encoding="utf-8") as f:
        for doc in documents:
            cleaned = clean_markdown(doc.text)
            f.write(cleaned)
            f.write("\n\n")

    print(f"✅ Markdown saved to {md_output}")
    print(f"Total pages: {len(documents)}")


if __name__ == "__main__":
    get_text()