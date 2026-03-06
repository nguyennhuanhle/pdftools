"""
TTK style configuration for modern dark theme UI.
"""

from tkinter import ttk
from .constants import COLORS


def setup_styles():
    """Configure ttk styles for modern look."""
    style = ttk.Style()
    style.theme_use("clam")

    # Frame styles
    style.configure("TFrame", background=COLORS["bg"])
    style.configure("Card.TFrame", background=COLORS["bg_card"])

    # Label styles
    style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI", 10))
    style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLORS["text"])
    style.configure("Subtitle.TLabel", font=("Segoe UI", 10), foreground=COLORS["text_muted"])
    style.configure("Drop.TLabel", font=("Segoe UI", 11), foreground=COLORS["text_muted"])
    style.configure("Count.TLabel", font=("Segoe UI", 9, "bold"), foreground=COLORS["accent"])

    # Button styles
    style.configure(
        "TButton",
        font=("Segoe UI", 10),
        padding=(12, 6),
        background=COLORS["bg_secondary"],
        foreground=COLORS["text"],
    )
    style.map("TButton",
        background=[("active", COLORS["bg_card"]), ("pressed", COLORS["border"])],
    )

    style.configure(
        "Accent.TButton",
        font=("Segoe UI", 10, "bold"),
        padding=(16, 8),
        background=COLORS["accent"],
        foreground="white",
    )
    style.map("Accent.TButton",
        background=[("active", COLORS["accent_hover"]), ("disabled", COLORS["border"])],
    )

    # Entry style
    style.configure(
        "TEntry",
        fieldbackground=COLORS["bg_secondary"],
        foreground=COLORS["text"],
        insertcolor=COLORS["text"],
        padding=6,
    )

    # Progressbar style
    style.configure(
        "TProgressbar",
        background=COLORS["accent"],
        troughcolor=COLORS["bg_secondary"],
        borderwidth=0,
        thickness=4,
    )

    # LabelFrame style
    style.configure(
        "TLabelframe",
        background=COLORS["bg"],
        foreground=COLORS["text_muted"],
    )
    style.configure(
        "TLabelframe.Label",
        background=COLORS["bg"],
        foreground=COLORS["text_muted"],
        font=("Segoe UI", 9)
    )

    # Notebook styles for tabs
    style.configure(
        "TNotebook",
        background=COLORS["bg"],
        borderwidth=0,
    )
    style.configure(
        "TNotebook.Tab",
        background=COLORS["bg_secondary"],
        foreground=COLORS["text_muted"],
        padding=(16, 8),
        font=("Segoe UI", 10),
    )
    style.map("TNotebook.Tab",
        background=[("selected", COLORS["bg_card"])],
        foreground=[("selected", COLORS["text"])],
    )

    # Radiobutton styles
    style.configure(
        "TRadiobutton",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=("Segoe UI", 10),
    )

    # Checkbutton styles
    style.configure(
        "TCheckbutton",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=("Segoe UI", 10),
    )
