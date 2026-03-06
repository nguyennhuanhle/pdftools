"""
Markdown to DOCX Tab - Convert markdown files to Word documents.
Supports drag-and-drop, single file conversion with style mapping.
"""

import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from .constants import COLORS
from .ui_components import DropZone, LogArea
from .md_operations import convert_markdown_to_docx


class MarkdownToDocxTab(ttk.Frame):
    """Tab for converting markdown files to DOCX format."""

    def __init__(self, parent: ttk.Notebook, root: tk.Tk):
        super().__init__(parent)
        self.root = root
        self.selected_file: Path | None = None
        self.is_processing = False

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self._create_header(main_frame)

        # Drop zone for single markdown file
        self.drop_zone = DropZone(
            main_frame,
            self.root,
            height=100,
            on_files_dropped=self._handle_files_dropped,
            on_click=self._browse_file,
            single_file=True,
            drop_text="Drop a markdown file here",
        )
        self.drop_zone.pack(fill=tk.X, pady=(0, 15))

        self._create_file_info(main_frame)
        self._create_action_buttons(main_frame)

        # Log area
        self.log_area = LogArea(main_frame, height=4)
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def _create_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(header_frame, text="MD to DOCX", style="Title.TLabel").pack(
            side=tk.LEFT
        )
        ttk.Label(
            header_frame,
            text="Convert markdown to Word document",
            style="Subtitle.TLabel",
        ).pack(side=tk.LEFT, padx=(10, 0), pady=(4, 0))

    def _create_file_info(self, parent):
        """Create the selected file display section."""
        info_frame = ttk.Frame(parent)
        info_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(info_frame, text="Selected file:", style="Subtitle.TLabel").pack(
            side=tk.LEFT
        )
        self.file_label = ttk.Label(
            info_frame,
            text="None",
            foreground=COLORS["text_muted"],
            font=("Consolas", 10),
        )
        self.file_label.pack(side=tk.LEFT, padx=(8, 0))

    def _create_action_buttons(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(0, 15))

        # Spacer to push buttons right
        ttk.Frame(btn_frame).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(btn_frame, text="Clear", command=self._clear, width=8).pack(
            side=tk.LEFT, padx=(0, 8)
        )
        self.convert_btn = ttk.Button(
            btn_frame,
            text="Convert to DOCX",
            command=self._convert_file,
            style="Accent.TButton",
        )
        self.convert_btn.pack(side=tk.LEFT)

    def _handle_files_dropped(self, files: list):
        """Handle files dropped onto the drop zone."""
        if self.is_processing:
            return

        for f in files:
            path = Path(f)
            if path.suffix.lower() == ".md":
                self.selected_file = path
                self.file_label.configure(
                    text=path.name, foreground=COLORS["text"]
                )
                self.log_area.log(f"Selected: {path.name}", "info")
                return

        self.log_area.log("Please drop a markdown (.md) file", "warning")

    def _browse_file(self):
        if self.is_processing:
            return

        file = filedialog.askopenfilename(
            title="Select Markdown File",
            filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")],
        )
        if file:
            self._handle_files_dropped([file])

    def _clear(self):
        """Clear the selected file."""
        self.selected_file = None
        self.file_label.configure(text="None", foreground=COLORS["text_muted"])
        self.log_area.log("Cleared selection", "info")

    def _convert_file(self):
        """Convert the selected markdown file to DOCX."""
        if not self.selected_file:
            messagebox.showwarning(
                "No File Selected", "Please select a markdown file to convert."
            )
            return

        # Ask for output location
        output_path = filedialog.asksaveasfilename(
            title="Save DOCX As",
            defaultextension=".docx",
            initialfile=self.selected_file.stem + ".docx",
            filetypes=[("Word Documents", "*.docx")],
        )
        if not output_path:
            return

        self.is_processing = True
        self.drop_zone.set_enabled(False)
        self.convert_btn.configure(state=tk.DISABLED, text="Converting...")

        input_file = self.selected_file
        output_file = Path(output_path)

        def convert():
            try:
                self.root.after(
                    0, lambda: self.log_area.log(f"Converting: {input_file.name}", "info")
                )

                success, message = convert_markdown_to_docx(input_file, output_file)

                if success:
                    self.root.after(
                        0, lambda: self.log_area.log(message, "success")
                    )
                    self.root.after(
                        0,
                        lambda: messagebox.showinfo(
                            "Complete", f"Converted successfully!\n\nSaved to: {output_file.name}"
                        ),
                    )
                else:
                    self.root.after(
                        0, lambda: self.log_area.log(f"ERROR: {message}", "error")
                    )
                    self.root.after(
                        0,
                        lambda: messagebox.showerror("Error", f"Conversion failed: {message}"),
                    )

            except Exception as e:
                self.root.after(
                    0, lambda: self.log_area.log(f"ERROR: {e}", "error")
                )
                self.root.after(
                    0, lambda: messagebox.showerror("Error", f"Conversion failed: {e}")
                )

            finally:
                def finish():
                    self.is_processing = False
                    self.drop_zone.set_enabled(True)
                    self.convert_btn.configure(state=tk.NORMAL, text="Convert to DOCX")

                self.root.after(0, finish)

        threading.Thread(target=convert, daemon=True).start()

    def redraw_drop_zone(self):
        """Redraw drop zone on resize."""
        self.drop_zone.redraw()
