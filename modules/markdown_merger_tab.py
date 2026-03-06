"""
Markdown Merger Tab - Combine multiple markdown files into a single output.
Supports drag-and-drop, reordering, and custom separators.
"""

import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from .constants import COLORS
from .ui_components import DropZone, LogArea


class MarkdownMergerTab(ttk.Frame):
    """Tab for merging multiple markdown files into one."""

    def __init__(self, parent: ttk.Notebook, root: tk.Tk):
        super().__init__(parent)
        self.root = root
        self.files_to_merge: list[Path] = []
        self.is_processing = False

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface."""
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self._create_header(main_frame)

        # Drop zone for markdown files
        self.drop_zone = DropZone(
            main_frame, self.root,
            height=100,
            on_files_dropped=self._handle_files_dropped,
            on_click=self._browse_files,
            single_file=False,
            drop_text="Drop markdown files here"
        )
        self.drop_zone.pack(fill=tk.X, pady=(0, 15))

        self._create_file_list(main_frame)
        self._create_reorder_buttons(main_frame)
        self._create_options_row(main_frame)
        self._create_action_buttons(main_frame)

        # Log area
        self.log_area = LogArea(main_frame, height=4)
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def _create_header(self, parent):
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))

        ttk.Label(header_frame, text="Merge Markdown", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            header_frame, text="Combine multiple .md files", style="Subtitle.TLabel"
        ).pack(side=tk.LEFT, padx=(10, 0), pady=(4, 0))

    def _create_file_list(self, parent):
        list_section = ttk.Frame(parent)
        list_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        list_header = ttk.Frame(list_section)
        list_header.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(list_header, text="Files to merge", style="Subtitle.TLabel").pack(side=tk.LEFT)
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

    def _create_reorder_buttons(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(btn_frame, text="Move Up", command=self._move_up, width=10).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Move Down", command=self._move_down, width=10).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Remove", command=self._remove_selected, width=10).pack(side=tk.LEFT)

    def _create_options_row(self, parent):
        options_frame = ttk.Frame(parent)
        options_frame.pack(fill=tk.X, pady=(0, 10))

        # Separator input
        sep_frame = ttk.Frame(options_frame)
        sep_frame.pack(side=tk.LEFT)

        ttk.Label(sep_frame, text="Separator:", style="Subtitle.TLabel").pack(side=tk.LEFT)
        self.separator_entry = ttk.Entry(sep_frame, width=15)
        self.separator_entry.insert(0, "---")
        self.separator_entry.pack(side=tk.LEFT, padx=(8, 0))

        # Add filename headers checkbox
        self.add_headers_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            options_frame,
            text="Add filename headers",
            variable=self.add_headers_var
        ).pack(side=tk.LEFT, padx=(20, 0))

    def _create_action_buttons(self, parent):
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(fill=tk.X, pady=(0, 15))

        # Spacer to push buttons right
        ttk.Frame(btn_frame).pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Button(btn_frame, text="Clear", command=self._clear_all, width=8).pack(side=tk.LEFT, padx=(0, 8))
        self.merge_btn = ttk.Button(
            btn_frame, text="Merge Files", command=self._merge_files, style="Accent.TButton"
        )
        self.merge_btn.pack(side=tk.LEFT)

    def _handle_files_dropped(self, files: list):
        """Handle files dropped onto the drop zone."""
        added = 0
        for f in files:
            path = Path(f)
            if path.suffix.lower() == ".md" and path not in self.files_to_merge:
                self.files_to_merge.append(path)
                added += 1

        self._update_listbox()
        if added > 0:
            self.log_area.log(f"Added {added} file(s)", "info")

    def _browse_files(self):
        if self.is_processing:
            return

        files = filedialog.askopenfilenames(
            title="Select Markdown Files",
            filetypes=[("Markdown Files", "*.md"), ("All Files", "*.*")]
        )
        self._handle_files_dropped(files)

    def _update_listbox(self):
        """Refresh the listbox display with current file order."""
        self.file_listbox.delete(0, tk.END)
        for i, path in enumerate(self.files_to_merge, 1):
            self.file_listbox.insert(tk.END, f"  {i}. {path.name}")
        self._update_count()

    def _update_count(self):
        count = len(self.files_to_merge)
        self.count_label.configure(text=f"{count} file{'s' if count != 1 else ''}")

    def _move_up(self):
        """Move selected item up in the list."""
        selection = self.file_listbox.curselection()
        if not selection or selection[0] == 0:
            return

        idx = selection[0]
        self.files_to_merge[idx], self.files_to_merge[idx - 1] = (
            self.files_to_merge[idx - 1], self.files_to_merge[idx]
        )
        self._update_listbox()
        self.file_listbox.selection_set(idx - 1)

    def _move_down(self):
        """Move selected item down in the list."""
        selection = self.file_listbox.curselection()
        if not selection or selection[0] >= len(self.files_to_merge) - 1:
            return

        idx = selection[0]
        self.files_to_merge[idx], self.files_to_merge[idx + 1] = (
            self.files_to_merge[idx + 1], self.files_to_merge[idx]
        )
        self._update_listbox()
        self.file_listbox.selection_set(idx + 1)

    def _remove_selected(self, event=None):
        """Remove selected files from the list."""
        selected = list(self.file_listbox.curselection())
        if not selected:
            return

        selected.reverse()
        for idx in selected:
            del self.files_to_merge[idx]

        self._update_listbox()
        self.log_area.log(f"Removed {len(selected)} file(s)", "info")

    def _clear_all(self):
        """Clear all files from the list."""
        self.files_to_merge.clear()
        self._update_listbox()
        self.log_area.log("Cleared file list", "info")

    def _merge_files(self):
        """Merge all files into a single output file."""
        if len(self.files_to_merge) < 2:
            messagebox.showwarning("Not Enough Files", "Please add at least 2 markdown files to merge.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Save Merged Markdown As",
            defaultextension=".md",
            initialfile="merged.md",
            filetypes=[("Markdown Files", "*.md")]
        )
        if not output_path:
            return

        self.is_processing = True
        self.drop_zone.set_enabled(False)
        self.merge_btn.configure(state=tk.DISABLED, text="Merging...")

        files_copy = list(self.files_to_merge)
        separator = self.separator_entry.get() or "---"
        add_headers = self.add_headers_var.get()
        output = Path(output_path)

        def merge():
            try:
                merged_content = []

                for i, file_path in enumerate(files_copy):
                    self.root.after(0, lambda p=file_path: self.log_area.log(f"Reading: {p.name}", "info"))

                    try:
                        content = file_path.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        content = file_path.read_text(encoding="latin-1")

                    section = []
                    if add_headers:
                        section.append(f"## {file_path.stem}\n")
                    section.append(content.strip())
                    merged_content.append("\n".join(section))

                final_content = f"\n\n{separator}\n\n".join(merged_content)
                output.write_text(final_content, encoding="utf-8")

                self.root.after(0, lambda: self.log_area.log(f"Saved: {output.name}", "success"))
                self.root.after(0, lambda: messagebox.showinfo("Complete", f"Merged {len(files_copy)} files successfully!"))

            except Exception as e:
                self.root.after(0, lambda: self.log_area.log(f"ERROR: {e}", "error"))
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to merge files: {e}"))

            finally:
                def finish():
                    self.is_processing = False
                    self.drop_zone.set_enabled(True)
                    self.merge_btn.configure(state=tk.NORMAL, text="Merge Files")

                self.root.after(0, finish)

        threading.Thread(target=merge, daemon=True).start()

    def redraw_drop_zone(self):
        """Redraw drop zone on resize."""
        self.drop_zone.redraw()
