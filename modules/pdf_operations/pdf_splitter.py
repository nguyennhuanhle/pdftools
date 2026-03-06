"""
PDF splitting module.
Splits PDFs by page ranges into separate files.
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass

from pypdf import PdfReader, PdfWriter


@dataclass
class PageRange:
    """Represents a range of pages to extract."""
    start: int      # 0-indexed
    end: int        # 0-indexed, inclusive
    name: str       # Output file suffix


def parse_range_string(range_str: str, total_pages: int) -> Tuple[List[PageRange], Optional[str]]:
    """
    Parse a page range string into PageRange objects.

    Args:
        range_str: String like "1-10, 11-25, 26-end"
        total_pages: Total number of pages in the PDF

    Returns:
        Tuple of (list of PageRange objects, error message if any)

    Examples:
        "1-10, 11-25, 26-end" -> [(0,9), (10,24), (25,last)]
        "1-5" -> [(0,4)]
        "10-end" -> [(9, last)]
    """
    if not range_str.strip():
        return ([], "Empty range string")

    ranges = []
    parts = [p.strip() for p in range_str.split(',')]

    for i, part in enumerate(parts):
        if not part:
            continue

        # Handle single page: "5"
        if re.match(r'^\d+$', part):
            page = int(part)
            if page < 1 or page > total_pages:
                return ([], f"Page {page} out of range (1-{total_pages})")
            ranges.append(PageRange(
                start=page - 1,
                end=page - 1,
                name=f"part{i+1:02d}"
            ))
            continue

        # Handle range: "1-10" or "26-end"
        match = re.match(r'^(\d+)\s*-\s*(end|\d+)$', part, re.IGNORECASE)
        if not match:
            return ([], f"Invalid range format: '{part}'")

        start = int(match.group(1))
        end_str = match.group(2).lower()

        if end_str == 'end':
            end = total_pages
        else:
            end = int(end_str)

        # Validate range
        if start < 1:
            return ([], f"Start page must be >= 1, got {start}")
        if end > total_pages:
            return ([], f"End page {end} exceeds total pages ({total_pages})")
        if start > end:
            return ([], f"Start page {start} > end page {end}")

        ranges.append(PageRange(
            start=start - 1,  # Convert to 0-indexed
            end=end - 1,
            name=f"part{i+1:02d}"
        ))

    if not ranges:
        return ([], "No valid ranges found")

    return (ranges, None)


def split_pdf_by_ranges(
    input_path: Path,
    output_dir: Path,
    ranges: List[PageRange],
    password: Optional[str] = None,
    base_name: Optional[str] = None
) -> Tuple[List[Path], List[str]]:
    """
    Split a PDF into multiple files based on page ranges.

    Args:
        input_path: Source PDF file path
        output_dir: Directory for output files
        ranges: List of PageRange objects
        password: Optional password for encrypted PDFs
        base_name: Base name for output files (default: input file stem)

    Returns:
        Tuple of (list of created file paths, list of error messages)
    """
    created_files = []
    errors = []

    if not base_name:
        base_name = input_path.stem

    try:
        reader = PdfReader(str(input_path))

        # Handle encryption
        if reader.is_encrypted:
            if password:
                reader.decrypt(password)
            else:
                try:
                    reader.decrypt("")
                except Exception:
                    return ([], ["Encrypted PDF requires password"])

        total_pages = len(reader.pages)
        output_dir.mkdir(parents=True, exist_ok=True)

        for page_range in ranges:
            # Validate range against actual pages
            if page_range.start >= total_pages:
                errors.append(f"Start page {page_range.start+1} exceeds total ({total_pages})")
                continue
            if page_range.end >= total_pages:
                page_range.end = total_pages - 1

            # Create output file
            output_name = f"{base_name}_{page_range.name}.pdf"
            output_path = output_dir / output_name

            try:
                writer = PdfWriter()
                for page_num in range(page_range.start, page_range.end + 1):
                    writer.add_page(reader.pages[page_num])

                with open(output_path, "wb") as f:
                    writer.write(f)

                created_files.append(output_path)

            except Exception as e:
                errors.append(f"Failed to create {output_name}: {str(e)}")

        return (created_files, errors)

    except Exception as e:
        return ([], [f"Failed to read PDF: {str(e)}"])


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be safe for use as a filename.

    Args:
        name: Original string

    Returns:
        Sanitized filename-safe string
    """
    # Replace invalid characters with underscore
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', name)
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip(' .')
    # Limit length
    if len(sanitized) > 50:
        sanitized = sanitized[:50]
    return sanitized or "untitled"
