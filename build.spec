# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PDF Tools.
Builds a single-file Windows executable with all dependencies bundled.
"""

import os
import sys

# Find tkinterdnd2 tkdnd directory for drag-drop support
import tkinterdnd2
tkdnd_path = os.path.join(os.path.dirname(tkinterdnd2.__file__), 'tkdnd')

# Find pymupdf for PDF operations
import pymupdf
pymupdf_path = os.path.dirname(pymupdf.__file__)

# Import version info
sys.path.insert(0, os.path.abspath('.'))
from version import __version__, __author__, __copyright__, __app_name__, __description__

# Parse version tuple (e.g. "1.0.0" -> (1, 0, 0, 0))
ver_parts = [int(x) for x in __version__.split('.')]
while len(ver_parts) < 4:
    ver_parts.append(0)
ver_tuple = tuple(ver_parts[:4])

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Bundle tkdnd DLLs for drag-and-drop support
        (tkdnd_path, os.path.join('tkinterdnd2', 'tkdnd')),
    ],
    hiddenimports=[
        'tkinterdnd2',
        'tkinterdnd2.TkinterDnD',
        'pypdf',
        'cryptography',
        'docx',
        'markdown',
        'pdf2docx',
        'pymupdf',
        'pymupdf4llm',
        'cffi',
        '_cffi_backend',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDFTools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,    # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='file_version_info.txt',
)
