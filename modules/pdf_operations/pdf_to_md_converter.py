"""
PDF to Markdown converter module.
Converts PDF files to Markdown using pymupdf4llm.
"""

from pathlib import Path

import pymupdf4llm


def convert_pdf_to_markdown(input_path: Path, output_path: Path) -> tuple[bool, str]:
    """
    Convert a PDF file to Markdown format.

    Args:
        input_path: Path to input PDF file
        output_path: Path for output Markdown file

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        md_text = pymupdf4llm.to_markdown(str(input_path))

        output_path.write_text(md_text, encoding="utf-8")

        return True, f"Successfully converted to {output_path.name}"

    except Exception as e:
        return False, str(e)
