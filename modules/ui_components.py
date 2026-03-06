"""
Shared UI components for PDF Tools application.
Contains reusable widgets like drop zones and log areas.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from tkinterdnd2 import DND_FILES

from .constants import COLORS


class DropZone:
    """Reusable drag-and-drop zone widget."""

    def __init__(
        self,
        parent: ttk.Frame,
        root: tk.Tk,
        height: int = 120,
        on_files_dropped: Optional[Callable[[list], None]] = None,
        on_click: Optional[Callable[[], None]] = None,
        single_file: bool = False,
        drop_text: Optional[str] = None
    ):
        self.root = root
        self.on_files_dropped = on_files_dropped
        self.on_click = on_click
        self.single_file = single_file
        self.drop_text = drop_text
        self.is_enabled = True

        self.canvas = tk.Canvas(
            parent,
            height=height,
            bg=COLORS["drop_zone"],
            highlightthickness=2,
            highlightbackground=COLORS["border"],
            relief="flat",
        )
        self.height = height

        self._draw_normal()
        self._setup_bindings()
        self._setup_drag_drop()

    def pack(self, **kwargs):
        self.canvas.pack(**kwargs)

    def _draw_normal(self):
        """Draw normal state."""
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 600
        h = self.height

        padding = 15 if h > 100 else 10
        self.canvas.create_rectangle(
            padding, padding, w - padding, h - padding,
            outline=COLORS["border"], width=2, dash=(8, 4)
        )

        if self.drop_text:
            text = self.drop_text
        else:
            text = "Drop a PDF file here" if self.single_file else "Drop PDF files here"
        y_offset = 0 if h <= 100 else -10

        self.canvas.create_text(
            w // 2, h // 2 + y_offset,
            text=text,
            fill=COLORS["text"],
            font=("Segoe UI", 11 if h > 100 else 10, "bold")
        )

        if h > 100:
            self.canvas.create_text(
                w // 2, h // 2 + 12,
                text="or click to browse",
                fill=COLORS["text_muted"],
                font=("Segoe UI", 9)
            )

    def _draw_active(self):
        """Draw active/hover state."""
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 600
        h = self.height

        self.canvas.configure(bg=COLORS["drop_active"])

        padding = 15 if h > 100 else 10
        self.canvas.create_rectangle(
            padding, padding, w - padding, h - padding,
            outline=COLORS["accent"], width=2
        )

        text = "Release to add file" if self.single_file else "Release to add files"
        self.canvas.create_text(
            w // 2, h // 2,
            text=text,
            fill=COLORS["accent"],
            font=("Segoe UI", 11 if h > 100 else 10, "bold")
        )

    def _setup_bindings(self):
        if self.on_click:
            self.canvas.bind("<Button-1>", lambda e: self.on_click())
        self.canvas.bind("<Enter>", self._on_enter)
        self.canvas.bind("<Leave>", self._on_leave)

    def _on_enter(self, event):
        if self.is_enabled:
            self.canvas.configure(highlightbackground=COLORS["accent"])

    def _on_leave(self, event):
        self.canvas.configure(highlightbackground=COLORS["border"])

    def _setup_drag_drop(self):
        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind("<<Drop>>", self._on_drop)
        self.canvas.dnd_bind("<<DragEnter>>", self._on_drag_enter)
        self.canvas.dnd_bind("<<DragLeave>>", self._on_drag_leave)

    def _on_drop(self, event):
        self._draw_normal()
        self.canvas.configure(bg=COLORS["drop_zone"])

        if self.on_files_dropped:
            files = self.root.tk.splitlist(event.data)
            self.on_files_dropped(list(files))

    def _on_drag_enter(self, event):
        self._draw_active()

    def _on_drag_leave(self, event):
        self._draw_normal()
        self.canvas.configure(bg=COLORS["drop_zone"])

    def redraw(self):
        """Redraw the drop zone (call on resize)."""
        self._draw_normal()

    def set_enabled(self, enabled: bool):
        self.is_enabled = enabled


class LogArea:
    """Reusable log text area with colored messages."""

    def __init__(self, parent: ttk.Frame, height: int = 4):
        self.frame = ttk.LabelFrame(parent, text="Activity Log", padding=8)

        self.text = tk.Text(
            self.frame,
            height=height,
            state=tk.DISABLED,
            wrap=tk.WORD,
            bg=COLORS["bg_secondary"],
            fg=COLORS["text_muted"],
            font=("Consolas", 9),
            borderwidth=0,
            padx=8,
            pady=8,
        )
        scrollbar = ttk.Scrollbar(self.frame, orient=tk.VERTICAL, command=self.text.yview)
        self.text.config(yscrollcommand=scrollbar.set)

        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure tags
        self.text.tag_configure("success", foreground=COLORS["success"])
        self.text.tag_configure("error", foreground=COLORS["error"])
        self.text.tag_configure("info", foreground=COLORS["text"])
        self.text.tag_configure("warning", foreground=COLORS["warning"])

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def log(self, message: str, level: str = "info"):
        """Add message to log with color coding."""
        self.text.configure(state=tk.NORMAL)
        self.text.insert(tk.END, f"{message}\n", level)
        self.text.see(tk.END)
        self.text.configure(state=tk.DISABLED)

    def clear(self):
        """Clear the log."""
        self.text.configure(state=tk.NORMAL)
        self.text.delete("1.0", tk.END)
        self.text.configure(state=tk.DISABLED)
