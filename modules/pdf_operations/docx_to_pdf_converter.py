"""
DOCX to PDF converter module.
Converts Word documents to PDF using Microsoft Word COM automation via subprocess,
or LibreOffice as fallback. No external Python packages required.
"""

import subprocess
import shutil
from pathlib import Path


def _convert_with_word(input_path: Path, output_path: Path) -> tuple[bool, str]:
    """Convert using Microsoft Word via PowerShell COM automation."""
    # Use PowerShell to automate Word without needing pywin32
    ps_script = f'''
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {{
    $doc = $word.Documents.Open("{input_path.resolve()}")
    $doc.SaveAs([ref]"{output_path.resolve()}", [ref]17)
    $doc.Close()
}} finally {{
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}}
'''
    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        text=True,
        timeout=120,
    )

    if result.returncode == 0 and output_path.exists():
        return True, f"Successfully converted to {output_path.name}"
    else:
        error = result.stderr.strip() if result.stderr else "Unknown error"
        return False, error


def _convert_with_libreoffice(input_path: Path, output_path: Path) -> tuple[bool, str]:
    """Convert using LibreOffice CLI as fallback."""
    lo_path = shutil.which("soffice")
    if not lo_path:
        return False, "Neither Microsoft Word nor LibreOffice found"

    result = subprocess.run(
        [
            lo_path,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_path.parent),
            str(input_path),
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    # LibreOffice outputs to same name with .pdf extension in outdir
    lo_output = output_path.parent / (input_path.stem + ".pdf")
    if result.returncode == 0 and lo_output.exists():
        if lo_output != output_path:
            lo_output.rename(output_path)
        return True, f"Successfully converted to {output_path.name}"
    else:
        error = result.stderr.strip() if result.stderr else "Conversion failed"
        return False, error


def convert_docx_to_pdf(input_path: Path, output_path: Path) -> tuple[bool, str]:
    """
    Convert a DOCX file to PDF format.
    Tries Microsoft Word first (Windows), falls back to LibreOffice.

    Args:
        input_path: Path to input DOCX file
        output_path: Path for output PDF file

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        # Try Word first (Windows)
        import platform
        if platform.system() == "Windows":
            success, message = _convert_with_word(input_path, output_path)
            if success:
                return success, message

        # Fallback to LibreOffice
        return _convert_with_libreoffice(input_path, output_path)

    except subprocess.TimeoutExpired:
        return False, "Conversion timed out (120s limit)"
    except Exception as e:
        return False, str(e)
