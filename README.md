# PDF Tools

A modern desktop application for PDF & document manipulation — clean metadata, split chapters, merge Markdown, and convert between formats.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)

**Created by Mr Le Nguyen Nhu Anh** — [edtechcorner.com](https://edtechcorner.com)

### ⬇️ [Download PDFTools.exe for Windows](https://github.com/nguyennhuanhle/pdftools/releases/latest/download/PDFTools.exe)

> No Python required — just download and double-click to run!

---

## Features

### 🧹 Clean PDF
- Remove all PDF metadata (title, author, subject, keywords, creator, producer, dates)
- Handle password-protected & AES-encrypted PDFs
- Drag & drop support
- Batch processing multiple files
- Color-coded activity log

### ✂️ Chunk PDF
- **Auto Mode**: Split by chapters detected from PDF outline/bookmarks or pattern matching
- **Manual Mode**: Split by custom page ranges (e.g., `1-10, 11-25, 26-end`)
- Chapter detection from PDF bookmarks (primary) with fallback pattern detection
- Selectable chapters with checkboxes
- Real-time page range validation and preview

### 📝 Merge Markdown
- Merge multiple `.md` files into a single document
- Drag & drop support
- Reorder files before merging
- Preview merged output

### 📄 MD → DOCX
- Convert Markdown files to Word (.docx) format
- Preserve formatting, headings, lists, code blocks
- Batch conversion support
- Drag & drop support

### 📑 PDF → DOCX
- Convert PDF files to editable Word (.docx) format
- Preserve layout and formatting
- Batch conversion support
- Drag & drop support

### 📋 PDF → MD
- Convert PDF files to Markdown format
- Intelligent text extraction with structure preservation
- Batch conversion support
- Drag & drop support

---

## Installation

### Option 1: Windows Executable (Recommended)

Download `PDFTools.exe` from the [Releases](../../releases) page — **no Python required**.

Double-click to run. That's it! ✨

### Option 2: Run from Source

#### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

#### Setup

1. Clone the repository:
```bash
git clone https://github.com/nguyennhuanhle/pdftools.git
cd pdftools
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

---

## Usage

### Windows Executable
Double-click `PDFTools.exe`.

### From Source

**Windows:**
```bash
start.bat
```

**Or run directly:**
```bash
python app.py
```

### How to Use

1. **Select a tab** for the tool you need (Clean, Chunk, Merge, Convert)
2. **Add files**: Drag & drop files onto the window, or click the drop zone to browse
3. **Password** (optional): Enter password if PDFs are encrypted
4. **Process**: Click the action button
5. **Save**: Choose output location when prompted

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Delete` / `Backspace` | Remove selected files from list |

---

## Build Executable

To build `PDFTools.exe` from source:

```bash
build.bat
```

This will:
1. Install PyInstaller (if not present)
2. Bundle all dependencies including Python runtime
3. Output `dist\PDFTools.exe` (~90 MB)

> **Note:** The exe is large because it includes the entire Python runtime and all libraries. First launch may take a few seconds to unpack.

---

## What Gets Removed (Clean PDF)

### Metadata Fields
- Title, Author, Subject, Keywords
- Creator (application that created the PDF)
- Producer (PDF library used)
- Creation Date, Modification Date

### Restrictions
- Encrypted PDFs are decrypted (requires password if set)

---

## Project Structure

```
pdf-cleaner/
├── app.py                              # Entry point with tabbed interface
├── version.py                          # Version, author & license info
├── requirements.txt                    # Python dependencies
├── start.bat                           # Windows launcher (source)
├── build.bat                           # Build executable script
├── build.spec                          # PyInstaller configuration
├── file_version_info.txt               # Windows exe metadata
├── modules/
│   ├── __init__.py
│   ├── constants.py                    # Colors and metadata fields
│   ├── ui_styles_configuration.py      # TTK theme styles
│   ├── ui_components.py                # Reusable UI widgets
│   ├── pdf_cleaner_tab.py              # Clean PDF tab
│   ├── pdf_chunker_tab.py              # Chunk PDF tab
│   ├── markdown_merger_tab.py          # Merge Markdown tab
│   ├── markdown_to_docx_tab.py         # MD → DOCX tab
│   ├── pdf_to_docx_tab.py              # PDF → DOCX tab
│   ├── pdf_to_md_tab.py                # PDF → MD tab
│   ├── pdf_operations/
│   │   ├── __init__.py
│   │   ├── pdf_metadata_remover.py     # Metadata removal logic
│   │   ├── pdf_chapter_detector.py     # Chapter detection
│   │   ├── pdf_splitter.py             # PDF splitting logic
│   │   ├── pdf_to_docx_converter.py    # PDF to DOCX conversion
│   │   └── pdf_to_md_converter.py      # PDF to Markdown conversion
│   └── md_operations/
│       ├── __init__.py
│       └── markdown_to_docx_converter.py  # Markdown to DOCX conversion
├── LICENSE                             # MIT License
└── README.md                           # This file
```

---

## Dependencies

| Package | Purpose |
|---------|---------|
| [pypdf](https://github.com/py-pdf/pypdf) | PDF reading, writing & metadata manipulation |
| [cryptography](https://github.com/pyca/cryptography) | AES decryption for encrypted PDFs |
| [tkinterdnd2](https://github.com/pmgagne/tkinterdnd2) | Drag & drop support |
| [python-docx](https://github.com/python-openxml/python-docx) | Word document creation |
| [markdown](https://github.com/Python-Markdown/markdown) | Markdown parsing |
| [pdf2docx](https://github.com/ArtifexSoftware/pdf2docx) | PDF to DOCX conversion |
| [pymupdf4llm](https://github.com/pymupdf/pymupdf4llm) | PDF to Markdown conversion |
| tkinter | GUI framework (included with Python) |

---

## License

MIT License — see [LICENSE](LICENSE) file for details.

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
