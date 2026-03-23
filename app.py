#!/usr/bin/env python3
"""
PDF Tools - Modern GUI application for PDF manipulation.
Features: Metadata removal, PDF chunking by chapters or page ranges.
"""

import tkinter as tk
from tkinter import ttk

from tkinterdnd2 import TkinterDnD

from modules.constants import COLORS
from modules.ui_styles_configuration import setup_styles
from modules.pdf_cleaner_tab import PDFCleanerTab
from modules.pdf_chunker_tab import PDFChunkerTab
from modules.markdown_merger_tab import MarkdownMergerTab
from modules.markdown_to_docx_tab import MarkdownToDocxTab
from modules.pdf_to_docx_tab import PDFToDocxTab
from modules.pdf_to_md_tab import PDFToMdTab
from modules.docx_to_pdf_tab import DocxToPdfTab
from version import __version__, __app_name__, __author__


class PDFToolsApp:
    """Main application with tabbed interface for PDF tools."""

    def __init__(self, root: TkinterDnD.Tk):
        self.root = root
        self.root.title(f"{__app_name__} v{__version__}")
        self.root.geometry("680x640")
        self.root.minsize(580, 560)
        self.root.configure(bg=COLORS["bg"])

        # Setup styles before creating widgets
        setup_styles()

        self._setup_ui()
        self._bind_events()

    def _setup_ui(self):
        """Setup the tabbed interface."""
        # Footer credit bar (pack first so it stays at bottom)
        footer = tk.Frame(self.root, bg=COLORS["bg_secondary"], height=28)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        footer.pack_propagate(False)

        credit_text = f"Created by {__author__} (edtechcorner.com) \u00A9 2026"
        credit_label = tk.Label(
            footer,
            text=credit_text,
            font=("Segoe UI", 9),
            fg=COLORS["text_muted"],
            bg=COLORS["bg_secondary"],
            cursor="hand2",
        )
        credit_label.pack(pady=4)
        credit_label.bind("<Button-1>", lambda e: __import__('webbrowser').open("https://edtechcorner.com"))
        credit_label.bind("<Enter>", lambda e: credit_label.configure(fg=COLORS["accent_hover"]))
        credit_label.bind("<Leave>", lambda e: credit_label.configure(fg=COLORS["text_muted"]))

        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs
        self.clean_tab = PDFCleanerTab(self.notebook, self.root)
        self.chunk_tab = PDFChunkerTab(self.notebook, self.root)
        self.merge_tab = MarkdownMergerTab(self.notebook, self.root)
        self.md_to_docx_tab = MarkdownToDocxTab(self.notebook, self.root)
        self.pdf_to_docx_tab = PDFToDocxTab(self.notebook, self.root)
        self.pdf_to_md_tab = PDFToMdTab(self.notebook, self.root)
        self.docx_to_pdf_tab = DocxToPdfTab(self.notebook, self.root)

        # Add tabs to notebook
        self.notebook.add(self.clean_tab, text="  Clean PDF  ")
        self.notebook.add(self.chunk_tab, text="  Chunk PDF  ")
        self.notebook.add(self.merge_tab, text="  Merge MD  ")
        self.notebook.add(self.md_to_docx_tab, text="  MD → DOCX  ")
        self.notebook.add(self.pdf_to_docx_tab, text="  PDF → DOCX  ")
        self.notebook.add(self.pdf_to_md_tab, text="  PDF → MD  ")
        self.notebook.add(self.docx_to_pdf_tab, text="  DOCX → PDF  ")

    def _bind_events(self):
        """Bind window events."""
        def on_resize(event):
            # Redraw drop zones on resize
            if hasattr(self, 'clean_tab'):
                self.clean_tab.redraw_drop_zone()
            if hasattr(self, 'chunk_tab'):
                self.chunk_tab.redraw_drop_zone()
            if hasattr(self, 'merge_tab'):
                self.merge_tab.redraw_drop_zone()
            if hasattr(self, 'md_to_docx_tab'):
                self.md_to_docx_tab.redraw_drop_zone()
            if hasattr(self, 'pdf_to_docx_tab'):
                self.pdf_to_docx_tab.redraw_drop_zone()
            if hasattr(self, 'pdf_to_md_tab'):
                self.pdf_to_md_tab.redraw_drop_zone()
            if hasattr(self, 'docx_to_pdf_tab'):
                self.docx_to_pdf_tab.redraw_drop_zone()

        self.root.bind("<Configure>", on_resize)


def main():
    """Launch the application."""
    root = TkinterDnD.Tk()
    app = PDFToolsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
