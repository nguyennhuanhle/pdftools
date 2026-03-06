"""
PDF chapter/section detection module.
Detects chapters from PDF outline (bookmarks) or pattern matching.
"""

import re
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass

from pypdf import PdfReader


@dataclass
class Chapter:
    """Represents a detected chapter/section in a PDF."""
    title: str
    start_page: int  # 0-indexed
    end_page: int    # 0-indexed, inclusive
    level: int = 0   # Nesting level (0 = top level)


def detect_from_outline(reader: PdfReader) -> List[Chapter]:
    """
    Detect chapters from PDF outline/bookmarks.

    Args:
        reader: PdfReader instance

    Returns:
        List of Chapter objects from outline
    """
    chapters = []
    total_pages = len(reader.pages)

    if not reader.outline:
        return chapters

    def process_outline(outline_items, level=0):
        """Recursively process outline items."""
        items_with_pages = []

        for item in outline_items:
            if isinstance(item, list):
                # Nested outline - process recursively
                items_with_pages.extend(process_outline(item, level + 1))
            else:
                # Get page number from destination
                try:
                    page_num = reader.get_destination_page_number(item)
                    if page_num is not None:
                        title = item.title if hasattr(item, 'title') else str(item)
                        items_with_pages.append((title, page_num, level))
                except Exception:
                    continue

        return items_with_pages

    # Get all outline items with page numbers
    outline_data = process_outline(reader.outline)

    # Convert to chapters with end pages
    for i, (title, start_page, level) in enumerate(outline_data):
        # End page is start of next chapter minus 1, or last page
        if i + 1 < len(outline_data):
            end_page = outline_data[i + 1][1] - 1
        else:
            end_page = total_pages - 1

        # Ensure end_page is at least start_page
        end_page = max(end_page, start_page)

        chapters.append(Chapter(
            title=title.strip(),
            start_page=start_page,
            end_page=end_page,
            level=level
        ))

    return chapters


def detect_from_patterns(reader: PdfReader) -> List[Chapter]:
    """
    Detect chapters by searching for patterns in page text.
    Fallback when no outline is available.

    Args:
        reader: PdfReader instance

    Returns:
        List of Chapter objects from pattern matching
    """
    patterns = [
        r'^(Chapter\s+\d+[.:]*\s*.*)$',
        r'^(CHAPTER\s+\d+[.:]*\s*.*)$',
        r'^(Part\s+\d+[.:]*\s*.*)$',
        r'^(PART\s+\d+[.:]*\s*.*)$',
        r'^(Section\s+\d+[.:]*\s*.*)$',
        r'^(SECTION\s+\d+[.:]*\s*.*)$',
    ]

    combined_pattern = '|'.join(patterns)
    chapter_positions = []
    total_pages = len(reader.pages)

    # Search first ~50 lines of each page for chapter headings
    for page_num, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
            lines = text.split('\n')[:50]  # Check first 50 lines

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                match = re.match(combined_pattern, line, re.IGNORECASE | re.MULTILINE)
                if match:
                    # Get the matched group
                    title = next(g for g in match.groups() if g)
                    chapter_positions.append((title.strip(), page_num))
                    break  # One chapter per page max

        except Exception:
            continue

    # Convert to chapters with end pages
    chapters = []
    for i, (title, start_page) in enumerate(chapter_positions):
        if i + 1 < len(chapter_positions):
            end_page = chapter_positions[i + 1][1] - 1
        else:
            end_page = total_pages - 1

        end_page = max(end_page, start_page)

        chapters.append(Chapter(
            title=title,
            start_page=start_page,
            end_page=end_page,
            level=0
        ))

    return chapters


def detect_chapters(
    pdf_path: Path,
    password: Optional[str] = None
) -> Tuple[List[Chapter], str]:
    """
    Detect chapters in a PDF using outline first, then pattern matching.

    Args:
        pdf_path: Path to PDF file
        password: Optional password for encrypted PDFs

    Returns:
        Tuple of (chapters list, detection method used)
    """
    try:
        reader = PdfReader(str(pdf_path))

        # Handle encryption
        if reader.is_encrypted:
            if password:
                reader.decrypt(password)
            else:
                try:
                    reader.decrypt("")
                except Exception:
                    return ([], "error: password required")

        # Try outline detection first (most reliable)
        chapters = detect_from_outline(reader)
        if chapters:
            return (chapters, "outline")

        # Fall back to pattern detection
        chapters = detect_from_patterns(reader)
        if chapters:
            return (chapters, "pattern")

        return ([], "none detected")

    except Exception as e:
        return ([], f"error: {str(e)}")
