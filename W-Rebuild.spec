# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for W-Rebuild - Windows Workspace Configuration Backup & Restore Tool
Creates a Windows executable with all dependencies for complete workspace backup and restoration
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all PySide6 modules
pyside6_modules = collect_submodules('PySide6')

a = Analysis(
    ['src\\ui\\main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src\\core', 'src\\core'),
        ('src\\cli', 'src\\cli'),
        ('docs', 'docs'),
        ('README.md', '.'),
        ('LICENSE', '.'),
        ('requirements.txt', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'psutil',
        'yaml',
        'win32api',
        'win32con',
        'win32file',
        'pywintypes',
    ] + pyside6_modules,
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
    [],
    exclude_binaries=True,
    name='W-Rebuild',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application, no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if you have one
    version='version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='W-Rebuild',
)
