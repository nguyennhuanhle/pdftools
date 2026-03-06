"""
Shared constants for PDF Cleaner application.
Contains color scheme and metadata field definitions.
"""

# Standard PDF metadata fields to remove
METADATA_FIELDS = [
    "/Title", "/Author", "/Subject", "/Keywords",
    "/Creator", "/Producer", "/CreationDate", "/ModDate",
]

# Modern color scheme
COLORS = {
    "bg": "#1a1a2e",           # Dark background
    "bg_secondary": "#16213e", # Secondary background
    "bg_card": "#0f3460",      # Card background
    "accent": "#e94560",       # Accent/primary color
    "accent_hover": "#ff6b6b", # Accent hover
    "success": "#00d9a5",      # Success green
    "warning": "#ffc107",      # Warning yellow
    "error": "#ff4757",        # Error red
    "text": "#eaeaea",         # Primary text
    "text_muted": "#a0a0a0",   # Muted text
    "border": "#2a2a4a",       # Border color
    "drop_zone": "#1e3a5f",    # Drop zone background
    "drop_active": "#2a4a7f",  # Drop zone when active
}
