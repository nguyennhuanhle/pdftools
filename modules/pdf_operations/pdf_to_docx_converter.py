"""
PDF to DOCX converter module.
Converts PDF files to Word documents using pdf2docx.
"""

from pathlib import Path

from pdf2docx import Converter


def convert_pdf_to_docx(input_path: Path, output_path: Path) -> tuple[bool, str]:
    """
    Convert a PDF file to DOCX format.

    Args:
        input_path: Path to input PDF file
        output_path: Path for output DOCX file

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        cv = Converter(str(input_path))
        cv.convert(str(output_path))
        cv.close()

        return True, f"Successfully converted to {output_path.name}"

    except Exception as e:
        return False, str(e)
