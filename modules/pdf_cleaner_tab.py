"""
PDF Cleaner Tab - Remove metadata and restrictions from PDF files.
Supports batch processing with drag-and-drop.
"""

import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Optional

from .constants import COLORS
from .ui_components import DropZone, LogArea
from .pdf_operations.pdf_metadata_remover import remove_pdf_metadata


class PDFCleanerTab(ttk.Frame):
    """Tab for cleaning PDF metadata and restrictions."""

    def __init__(self, parent: ttk.Notebook, root: tk.Tk):
        super().__init__(parent)
        self.root = root
        self.files_to_process: list[Path] = []
        self.password: Optional[str] = None
        self.is_processing = False

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        self._create_header(main_frame)

        # Drop zone
        self.drop_zone = DropZone(
            main_frame, self.root,
            height=120,
            on_files_dropped=self._handle_files_dropped,
            on_click=self._browse_files,
            single_file=False
        )
        self.drop_zone.pack(fill=tk.X, pady=(0, 15))

        # File list
        self._create_file_list(main_frame)

        # Options row
        self._create_options_row(main_frame)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, variable=self.progress_var, maximum=100, style="TProgressbar"
        )

        # Log area
        self.log_area = LogArea(main_frame, height=4)
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def _create_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(header_frame, text="Clean PDF", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            header_frame, text="Remove metadata & restrictions", style="Subtitle.TLabel"
        ).pack(side=tk.LEFT, padx=(10, 0), pady=(4, 0))

    def _create_file_list(self, parent):
        list_section = ttk.Frame(parent)
        list_section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        list_header = ttk.Frame(list_section)
        list_header.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(list_header, text="Files to process", style="Subtitle.TLabel").pack(side=tk.LEFT)
        self.count_label = ttk.Label(list_header, text="0 files", style="Count.TLabel")
        self.count_label.pack(side=tk.RIGHT)

        list_container = tk.Frame(list_section, bg=COLORS["bg_secondary"], padx=2, pady=2)
        list_container.pack(fill=tk.BOTH, expand=True)

        self.file_listbox = tk.Listbox(
            list_container,
            height=5,
            selectmode=tk.EXTENDED,
            bg=COLORS["bg_secondary"],
            fg=COLORS["text"],
            selectbackground=COLORS["accent"],
            selectforeground="white",
            font=("Consolas", 10),
            borderwidth=0,
            highlightthickness=0,
            activestyle="none",
        )
        scrollbar = ttk.Scrollbar(list_container, orient=tk.VERTICAL, command=self.file_listbox.yview)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.file_listbox.bind("<Delete>", self._remove_selected)
        self.file_listbox.bind("<BackSpace>", self._remove_selected)

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

        ttk.Button(btn_frame, text="Clear", command=self._clear_files, width=8).pack(side=tk.LEFT, padx=(0, 8))
        self.process_btn = ttk.Button(
            btn_frame, text="Clean PDFs", command=self._process_files, style="Accent.TButton"
        )
        self.process_btn.pack(side=tk.LEFT)

    def _handle_files_dropped(self, files: list):
        """Handle files dropped onto the drop zone."""
        added = 0
        for f in files:
            path = Path(f)
            if path.suffix.lower() == ".pdf" and path not in self.files_to_process:
                self.files_to_process.append(path)
                self.file_listbox.insert(tk.END, f"  {path.name}")
                added += 1

        self._update_count()
        if added > 0:
            self.log_area.log(f"Added {added} file(s)", "info")

    def _browse_files(self):
        if self.is_processing:
            return

        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")]
        )
        self._handle_files_dropped(files)

    def _remove_selected(self, event=None):
        selected = list(self.file_listbox.curselection())
        selected.reverse()

        for idx in selected:
            self.file_listbox.delete(idx)
            del self.files_to_process[idx]

        self._update_count()

    def _clear_files(self):
        self.files_to_process.clear()
        self.file_listbox.delete(0, tk.END)
        self._update_count()
        self.log_area.log("Cleared file list", "info")

    def _update_count(self):
        count = len(self.files_to_process)
        self.count_label.configure(text=f"{count} file{'s' if count != 1 else ''}")

    def _process_files(self):
        if not self.files_to_process:
            messagebox.showwarning("No Files", "Please add PDF files to process.")
            return

        self.password = self.password_entry.get() or None

        if len(self.files_to_process) == 1:
            output_path = filedialog.asksaveasfilename(
                title="Save Cleaned PDF As",
                defaultextension=".pdf",
                initialfile=self.files_to_process[0].stem + "_clean.pdf",
                filetypes=[("PDF Files", "*.pdf")]
            )
            if not output_path:
                return
            output_paths = [Path(output_path)]
        else:
            output_dir = filedialog.askdirectory(title="Select Output Directory")
            if not output_dir:
                return
            output_paths = [Path(output_dir) / (f.stem + "_clean.pdf") for f in self.files_to_process]

        self.is_processing = True
        self.drop_zone.set_enabled(False)
        self.process_btn.configure(state=tk.DISABLED, text="Processing...")

        files_copy = list(self.files_to_process)
        outputs_copy = list(output_paths)
        password_copy = self.password

        def process():
            total = len(files_copy)
            success_count = 0

            for i, (input_path, output_path) in enumerate(zip(files_copy, outputs_copy)):
                self.root.after(0, lambda p=input_path: self.log_area.log(f"Processing: {p.name}", "info"))

                success, removed, error = remove_pdf_metadata(input_path, output_path, password_copy)

                if success:
                    success_count += 1
                    if removed:
                        self.root.after(0, lambda r=removed: self.log_area.log(f"  Removed: {', '.join(r)}", "warning"))
                    self.root.after(0, lambda o=output_path: self.log_area.log(f"  Saved: {o.name}", "success"))
                else:
                    self.root.after(0, lambda e=error: self.log_area.log(f"  ERROR: {e}", "error"))

                progress = ((i + 1) / total) * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))

            def finish():
                self.is_processing = False
                self.drop_zone.set_enabled(True)
                self.process_btn.configure(state=tk.NORMAL, text="Clean PDFs")
                if success_count == total:
                    messagebox.showinfo("Complete", f"Processed {total} file(s) successfully!")
                else:
                    messagebox.showwarning("Partial", f"Processed {success_count}/{total} file(s). Check log.")

            self.root.after(0, finish)

        threading.Thread(target=process, daemon=True).start()

    def redraw_drop_zone(self):
        """Redraw drop zone on resize."""
        self.drop_zone.redraw()
