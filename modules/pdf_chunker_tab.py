"""
PDF Chunker Tab - Split PDFs by chapters or custom page ranges.
Single file processing with auto and manual modes.
"""

import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional, List

from .constants import COLORS
from .ui_components import DropZone, LogArea
from .pdf_operations.pdf_chapter_detector import detect_chapters, Chapter
from .pdf_operations.pdf_splitter import (
    split_pdf_by_ranges, parse_range_string, PageRange, sanitize_filename
)


class PDFChunkerTab(ttk.Frame):
    """Tab for splitting PDF files by chapters or page ranges."""

    def __init__(self, parent: ttk.Notebook, root: tk.Tk):
        super().__init__(parent)
        self.root = root
        self.current_file: Optional[Path] = None
        self.password: Optional[str] = None
        self.detected_chapters: List[Chapter] = []
        self.original_chapters: List[Chapter] = []  # Store original for reset
        self.selected_chapters = {}
        self.is_processing = False
        self.split_mode = tk.StringVar(value="auto")

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        self._create_header(main_frame)

        # Drop zone for single file
        self.drop_zone = DropZone(
            main_frame, self.root,
            height=80,
            on_files_dropped=self._handle_file_dropped,
            on_click=self._browse_file,
            single_file=True
        )
        self.drop_zone.pack(fill=tk.X, pady=(0, 10))

        # File info label
        self.file_label = ttk.Label(main_frame, text="No file selected", style="Subtitle.TLabel")
        self.file_label.pack(fill=tk.X, pady=(0, 10))

        # Mode selection
        self._create_mode_selector(main_frame)

        # Content area for mode-specific UI
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Auto mode: Chapter list
        self.auto_frame = ttk.Frame(self.content_frame)
        self._create_auto_mode_ui()

        # Manual mode: Range input
        self.manual_frame = ttk.Frame(self.content_frame)
        self._create_manual_mode_ui()

        # Show auto mode by default
        self.auto_frame.pack(fill=tk.BOTH, expand=True)

        # Options row
        self._create_options_row(main_frame)

        # Log area
        self.log_area = LogArea(main_frame, height=4)
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def _create_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(header_frame, text="Chunk PDF", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            header_frame, text="Split by chapters or page ranges", style="Subtitle.TLabel"
        ).pack(side=tk.LEFT, padx=(10, 0), pady=(4, 0))

    def _create_mode_selector(self, parent):
        mode_frame = ttk.Frame(parent)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(mode_frame, text="Split Mode:", style="Subtitle.TLabel").pack(side=tk.LEFT)

        ttk.Radiobutton(
            mode_frame, text="Auto (by chapters)",
            variable=self.split_mode, value="auto",
            command=self._on_mode_change
        ).pack(side=tk.LEFT, padx=(15, 10))

        ttk.Radiobutton(
            mode_frame, text="Manual (page ranges)",
            variable=self.split_mode, value="manual",
            command=self._on_mode_change
        ).pack(side=tk.LEFT)

    def _create_auto_mode_ui(self):
        """Setup UI for auto mode (chapter list)."""
        ttk.Label(
            self.auto_frame, text="Detected Chapters:", style="Subtitle.TLabel"
        ).pack(anchor=tk.W, pady=(0, 5))

        # Treeview for chapter list
        tree_frame = tk.Frame(self.auto_frame, bg=COLORS["bg_secondary"], padx=2, pady=2)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("title", "pages")
        self.chapter_tree = ttk.Treeview(tree_frame, columns=columns, show="tree headings", height=5)

        self.chapter_tree.heading("#0", text="")
        self.chapter_tree.heading("title", text="Chapter")
        self.chapter_tree.heading("pages", text="Pages")

        self.chapter_tree.column("#0", width=30, stretch=False)
        self.chapter_tree.column("title", width=350)
        self.chapter_tree.column("pages", width=100)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.chapter_tree.yview)
        self.chapter_tree.config(yscrollcommand=scrollbar.set)

        self.chapter_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.chapter_tree.bind("<Button-1>", self._on_tree_click)

        # Select/Deselect buttons
        btn_frame = ttk.Frame(self.auto_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(btn_frame, text="Select All", command=self._select_all, width=12).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Deselect All", command=self._deselect_all, width=12).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Button(btn_frame, text="Merge Selected", command=self._merge_selected, width=14).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(btn_frame, text="Reset", command=self._reset_chapters, width=8).pack(side=tk.LEFT, padx=(5, 0))

        self.detection_label = ttk.Label(btn_frame, text="", style="Subtitle.TLabel")
        self.detection_label.pack(side=tk.RIGHT)

    def _create_manual_mode_ui(self):
        """Setup UI for manual mode (page range input)."""
        ttk.Label(
            self.manual_frame,
            text="Enter page ranges (e.g., 1-10, 11-25, 26-end):",
            style="Subtitle.TLabel"
        ).pack(anchor=tk.W, pady=(0, 5))

        self.range_entry = ttk.Entry(self.manual_frame, font=("Consolas", 11))
        self.range_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            self.manual_frame,
            text="Separate ranges with commas. Use 'end' for the last page.",
            style="Subtitle.TLabel"
        ).pack(anchor=tk.W)

        self.range_preview = ttk.Label(self.manual_frame, text="", style="Subtitle.TLabel")
        self.range_preview.pack(anchor=tk.W, pady=(10, 0))

        self.range_entry.bind("<KeyRelease>", self._update_range_preview)

    def _create_options_row(self, parent):
        options_frame = ttk.Frame(parent)
        options_frame.pack(fill=tk.X, pady=(0, 15))

        pwd_frame = ttk.Frame(options_frame)
        pwd_frame.pack(side=tk.LEFT)

        ttk.Label(pwd_frame, text="Password:", style="Subtitle.TLabel").pack(side=tk.LEFT)
        self.password_entry = ttk.Entry(pwd_frame, show="*", width=25)
        self.password_entry.pack(side=tk.LEFT, padx=(8, 0))

        btn_frame = ttk.Frame(options_frame)
        btn_frame.pack(side=tk.RIGHT)

        ttk.Button(btn_frame, text="Clear", command=self._clear_file, width=8).pack(side=tk.LEFT, padx=(0, 8))
        self.process_btn = ttk.Button(
            btn_frame, text="Chunk PDF", command=self._process_file, style="Accent.TButton"
        )
        self.process_btn.pack(side=tk.LEFT)

    def _on_mode_change(self):
        if self.split_mode.get() == "auto":
            self.manual_frame.pack_forget()
            self.auto_frame.pack(fill=tk.BOTH, expand=True)
        else:
            self.auto_frame.pack_forget()
            self.manual_frame.pack(fill=tk.BOTH, expand=True)

    def _handle_file_dropped(self, files: list):
        """Handle file dropped onto the drop zone."""
        for f in files:
            path = Path(f)
            if path.suffix.lower() == ".pdf":
                self._load_file(path)
                break

    def _browse_file(self):
        if self.is_processing:
            return

        file = filedialog.askopenfilename(
            title="Select PDF File",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        if file:
            self._load_file(Path(file))

    def _load_file(self, path: Path):
        """Load a PDF file and detect chapters."""
        self.current_file = path
        self.file_label.configure(text=f"File: {path.name}")
        self.log_area.log(f"Loaded: {path.name}", "info")

        self.password = self.password_entry.get() or None
        chapters, method = detect_chapters(path, self.password)

        self.detected_chapters = chapters
        self.original_chapters = chapters.copy()  # Save for reset
        self._update_chapter_tree()

        if method.startswith("error"):
            self.log_area.log(f"Detection {method}", "error")
            self.detection_label.configure(text="Error detecting chapters")
        elif chapters:
            self.log_area.log(f"Found {len(chapters)} chapter(s) via {method}", "success")
            self.detection_label.configure(text=f"Found via: {method}")
        else:
            self.log_area.log("No chapters detected, use manual mode", "warning")
            self.detection_label.configure(text="No chapters found")

    def _update_chapter_tree(self):
        for item in self.chapter_tree.get_children():
            self.chapter_tree.delete(item)

        self.selected_chapters.clear()

        for i, chapter in enumerate(self.detected_chapters):
            pages = f"pp. {chapter.start_page + 1}-{chapter.end_page + 1}"
            item_id = self.chapter_tree.insert("", tk.END, text="[X]", values=(chapter.title, pages))
            self.selected_chapters[item_id] = True

    def _on_tree_click(self, event):
        region = self.chapter_tree.identify("region", event.x, event.y)
        if region == "tree":
            item = self.chapter_tree.identify_row(event.y)
            if item:
                self.selected_chapters[item] = not self.selected_chapters.get(item, True)
                check_text = "[X]" if self.selected_chapters[item] else "[ ]"
                self.chapter_tree.item(item, text=check_text)

    def _select_all(self):
        for item in self.chapter_tree.get_children():
            self.selected_chapters[item] = True
            self.chapter_tree.item(item, text="[X]")

    def _deselect_all(self):
        for item in self.chapter_tree.get_children():
            self.selected_chapters[item] = False
            self.chapter_tree.item(item, text="[ ]")

    def _merge_selected(self):
        """Merge selected chapters into a single chapter."""
        # Use treeview selection (highlighted rows via Ctrl+Click/Shift+Click)
        selected_items = self.chapter_tree.selection()

        if len(selected_items) < 2:
            messagebox.showinfo("Merge", "Select at least 2 chapters to merge.\nUse Ctrl+Click or Shift+Click to select multiple rows.")
            return

        # Get indices from selected items
        all_items = list(self.chapter_tree.get_children())
        selected_indices = sorted([all_items.index(item) for item in selected_items])

        # Get chapters to merge
        chapters_to_merge = [self.detected_chapters[i] for i in selected_indices]

        # Create merged chapter
        first_title = chapters_to_merge[0].title
        merged = Chapter(
            title=f"{first_title} (+{len(chapters_to_merge)-1} more)",
            start_page=min(c.start_page for c in chapters_to_merge),
            end_page=max(c.end_page for c in chapters_to_merge),
            level=0
        )

        # Build new chapter list: keep non-selected, replace selected with merged
        new_chapters = []
        merge_inserted = False
        for i, chapter in enumerate(self.detected_chapters):
            if i in selected_indices:
                if not merge_inserted:
                    new_chapters.append(merged)
                    merge_inserted = True
            else:
                new_chapters.append(chapter)

        self.detected_chapters = new_chapters
        self._update_chapter_tree()
        self.log_area.log(f"Merged {len(chapters_to_merge)} chapters", "success")

    def _reset_chapters(self):
        """Reset chapters to original detected state."""
        if not self.original_chapters:
            return
        self.detected_chapters = self.original_chapters.copy()
        self._update_chapter_tree()
        self.log_area.log("Reset to original chapters", "info")

    def _update_range_preview(self, event=None):
        if not self.current_file:
            self.range_preview.configure(text="Load a PDF first")
            return

        range_str = self.range_entry.get()
        if not range_str:
            self.range_preview.configure(text="")
            return

        from pypdf import PdfReader
        try:
            reader = PdfReader(str(self.current_file))
            total = len(reader.pages)
            ranges, error = parse_range_string(range_str, total)

            if error:
                self.range_preview.configure(text=f"Error: {error}")
            else:
                parts = [f"{r.name}: pages {r.start+1}-{r.end+1}" for r in ranges]
                self.range_preview.configure(text=" | ".join(parts))
        except Exception as e:
            self.range_preview.configure(text=f"Error: {str(e)}")

    def _clear_file(self):
        self.current_file = None
        self.detected_chapters.clear()
        self.original_chapters.clear()
        self.file_label.configure(text="No file selected")
        self._update_chapter_tree()
        self.range_entry.delete(0, tk.END)
        self.range_preview.configure(text="")
        self.detection_label.configure(text="")
        self.log_area.log("Cleared", "info")

    def _process_file(self):
        if not self.current_file:
            messagebox.showwarning("No File", "Please select a PDF file first.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            return

        self.password = self.password_entry.get() or None
        self.is_processing = True
        self.drop_zone.set_enabled(False)
        self.process_btn.configure(state=tk.DISABLED, text="Processing...")

        if self.split_mode.get() == "auto":
            self._process_auto_mode(Path(output_dir))
        else:
            self._process_manual_mode(Path(output_dir))

    def _process_auto_mode(self, output_path: Path):
        selected_indices = [
            i for i, item in enumerate(self.chapter_tree.get_children())
            if self.selected_chapters.get(item, True)
        ]

        if not selected_indices:
            messagebox.showwarning("No Chapters", "Please select at least one chapter.")
            self._reset_process_btn()
            return

        ranges = [
            PageRange(
                start=self.detected_chapters[i].start_page,
                end=self.detected_chapters[i].end_page,
                name=f"ch{i+1:02d}_{sanitize_filename(self.detected_chapters[i].title)}"
            )
            for i in selected_indices
        ]

        self._execute_split(output_path, ranges)

    def _process_manual_mode(self, output_path: Path):
        range_str = self.range_entry.get()
        if not range_str:
            messagebox.showwarning("No Ranges", "Please enter page ranges.")
            self._reset_process_btn()
            return

        from pypdf import PdfReader
        try:
            reader = PdfReader(str(self.current_file))
            total = len(reader.pages)
            ranges, error = parse_range_string(range_str, total)

            if error:
                messagebox.showerror("Invalid Ranges", error)
                self._reset_process_btn()
                return

            self._execute_split(output_path, ranges)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._reset_process_btn()

    def _execute_split(self, output_path: Path, ranges: List[PageRange]):
        file_copy = self.current_file
        password_copy = self.password

        def process():
            self.root.after(0, lambda: self.log_area.log(f"Splitting into {len(ranges)} part(s)...", "info"))

            created, errors = split_pdf_by_ranges(
                file_copy, output_path, ranges, password_copy, file_copy.stem
            )

            for f in created:
                self.root.after(0, lambda p=f: self.log_area.log(f"  Created: {p.name}", "success"))

            for e in errors:
                self.root.after(0, lambda err=e: self.log_area.log(f"  Error: {err}", "error"))

            def finish():
                self._reset_process_btn()
                if created and not errors:
                    messagebox.showinfo("Complete", f"Created {len(created)} file(s) successfully!")
                elif created:
                    messagebox.showwarning("Partial", f"Created {len(created)} file(s) with some errors.")
                else:
                    messagebox.showerror("Failed", "Failed to create any files.")

            self.root.after(0, finish)

        threading.Thread(target=process, daemon=True).start()

    def _reset_process_btn(self):
        self.is_processing = False
        self.drop_zone.set_enabled(True)
        self.process_btn.configure(state=tk.NORMAL, text="Chunk PDF")

    def redraw_drop_zone(self):
        """Redraw drop zone on resize."""
        self.drop_zone.redraw()
