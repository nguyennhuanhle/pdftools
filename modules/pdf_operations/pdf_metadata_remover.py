"""
PDF metadata removal functionality.
Removes all standard metadata fields and handles encrypted PDFs.
"""

from pathlib import Path
from typing import Optional, Tuple, List

from pypdf import PdfReader, PdfWriter

from ..constants import METADATA_FIELDS


def remove_pdf_metadata(
    input_path: Path,
    output_path: Path,
    password: Optional[str] = None
) -> Tuple[bool, List[str], Optional[str]]:
    """
    Remove metadata from a PDF file.

    Args:
        input_path: Source PDF file path
        output_path: Destination PDF file path
        password: Optional password for encrypted PDFs

    Returns:
        Tuple of (success, removed_fields, error_message)
    """
    try:
        reader = PdfReader(str(input_path))

        # Handle encrypted PDFs
        if reader.is_encrypted:
            if password:
                reader.decrypt(password)
            else:
                try:
                    reader.decrypt("")
                except Exception:
                    return (False, [], "Encrypted, password required")

        # Track removed metadata fields
        removed_metadata = []
        if reader.metadata:
            for field in METADATA_FIELDS:
                value = reader.metadata.get(field)
                if value:
                    removed_metadata.append(field.lstrip('/'))

        # Create new PDF without metadata
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        # Set empty metadata
        writer.add_metadata({
            "/Title": "", "/Author": "", "/Subject": "",
            "/Keywords": "", "/Creator": "", "/Producer": "",
        })

        # Write output file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            writer.write(f)

        return (True, removed_metadata, None)

    except Exception as e:
        return (False, [], str(e))
