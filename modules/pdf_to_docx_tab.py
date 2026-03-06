"""
PDF to DOCX Tab - Convert PDF files to Word documents.
Supports drag-and-drop, batch file conversion.
"""

import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from .constants import COLORS
from .ui_components import DropZone, LogArea
from .pdf_operations import convert_pdf_to_docx


class PDFToDocxTab(ttk.Frame):
    """Tab for converting PDF files to DOCX format."""

    def __init__(self, parent: ttk.Notebook, root: tk.Tk):
        super().__init__(parent)
        self.root = root
        self.files_to_process: list[Path] = []
        self.is_processing = False

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self._create_header(main_frame)

        # Drop zone for multiple PDF files
        self.drop_zone = DropZone(
            main_frame,
            self.root,
            height=120,
            on_files_dropped=self._handle_files_dropped,
            on_click=self._browse_files,
            single_file=False,
            drop_text="Drop PDF files here",
        )
        self.drop_zone.pack(fill=tk.X, pady=(0, 15))

        # File list
        self._create_file_list(main_frame)

        # Action buttons
        self._create_action_buttons(main_frame)

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

        ttk.Label(header_frame, text="PDF to DOCX", style="Title.TLabel").pack(
            side=tk.LEFT
        )
        ttk.Label(
            header_frame,
            text="Convert PDF to Word document",
            style="Subtitle.TLabel",
        ).pack(side=tk.LEFT, padx=(10, 0), pady=(4, 0))

    def _create_file_list(self, parent):
        list_section = ttk.Frame(parent)
        list_section.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        list_header = ttk.Frame(list_section)
        list_header.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(list_header, text="Files to convert", style="Subtitle.TLabel").pack(
            side=tk.LEFT
        )
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
        scrollbar = ttk.Scrollbar(
            list_container, orient=tk.VERTICAL, command=self.file_listbox.yview
        )
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        self.file_listbox.bind("<Delete>", self._remove_selected)
        self.file_listbox.bind("<BackSpace>", self._remove_selected)

    def _create_action_buttons(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(0, 15))

        # Spacer to push buttons right
        ttk.Frame(btn_frame).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(btn_frame, text="Clear", command=self._clear_files, width=8).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        self.convert_btn = ttk.Button(
            btn_frame,
            text="Convert to DOCX",
            command=self._convert_files,
            style="Accent.TButton",
        )
        self.convert_btn.pack(side=tk.LEFT)

    def _handle_files_dropped(self, files: list):
        """Handle files dropped onto the drop zone."""
        if self.is_processing:
            return

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
        elif added == 0 and files:
            self.log_area.log("Please drop PDF (.pdf) files", "warning")

    def _browse_files(self):
        if self.is_processing:
            return

        files = filedialog.askopenfilenames(
            title="Select PDF Files",
            filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")],
        )
        if files:
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

    def _convert_files(self):
        """Convert all PDF files to DOCX."""
        if not self.files_to_process:
            messagebox.showwarning("No Files", "Please add PDF files to convert.")
            return

        if len(self.files_to_process) == 1:
            output_path = filedialog.asksaveasfilename(
                title="Save DOCX As",
                defaultextension=".docx",
                initialfile=self.files_to_process[0].stem + ".docx",
                filetypes=[("Word Documents", "*.docx")],
            )
            if not output_path:
                return
            output_paths = [Path(output_path)]
        else:
            output_dir = filedialog.askdirectory(title="Select Output Directory")
            if not output_dir:
                return
            output_paths = [
                Path(output_dir) / (f.stem + ".docx") for f in self.files_to_process
            ]

        self.is_processing = True
        self.drop_zone.set_enabled(False)
        self.convert_btn.configure(state=tk.DISABLED, text="Converting...")
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))

        files_copy = list(self.files_to_process)
        outputs_copy = list(output_paths)

        def convert():
            total = len(files_copy)
            success_count = 0

            for i, (input_path, output_path) in enumerate(
                zip(files_copy, outputs_copy)
            ):
                self.root.after(
                    0,
                    lambda p=input_path: self.log_area.log(
                        f"Converting: {p.name}", "info"
                    ),
                )

                success, message = convert_pdf_to_docx(input_path, output_path)

                if success:
                    success_count += 1
                    self.root.after(
                        0, lambda m=message: self.log_area.log(f"  {m}", "success")
                    )
                else:
                    self.root.after(
                        0,
                        lambda m=message: self.log_area.log(f"  ERROR: {m}", "error"),
                    )

                progress = ((i + 1) / total) * 100
                self.root.after(0, lambda p=progress: self.progress_var.set(p))

            def finish():
                self.is_processing = False
                self.drop_zone.set_enabled(True)
                self.convert_btn.configure(state=tk.NORMAL, text="Convert to DOCX")
                self.progress_bar.pack_forget()
                self.progress_var.set(0)
                if success_count == total:
                    messagebox.showinfo(
                        "Complete", f"Converted {total} file(s) successfully!"
                    )
                else:
                    messagebox.showwarning(
                        "Partial",
                        f"Converted {success_count}/{total} file(s). Check log.",
                    )

            self.root.after(0, finish)

        threading.Thread(target=convert, daemon=True).start()

    def redraw_drop_zone(self):
        """Redraw drop zone on resize."""
        self.drop_zone.redraw()
