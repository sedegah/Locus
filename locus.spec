# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from pathlib import Path
import customtkinter

# Locate CustomTkinter assets (themes JSON & images)
CTK_PATH = Path(customtkinter.__file__).parent

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[
        # Python 3.14 is pre-release — PyInstaller doesn't auto-resolve the DLL path,
        # so we bundle it explicitly alongside all required VC runtime DLLs.
        (r'C:\Users\sedki\AppData\Local\Python\pythoncore-3.14-64\python314.dll', '.'),
        (r'C:\Users\sedki\AppData\Local\Python\pythoncore-3.14-64\python3.dll', '.'),
        (r'C:\Users\sedki\AppData\Local\Python\pythoncore-3.14-64\vcruntime140.dll', '.'),
        (r'C:\Users\sedki\AppData\Local\Python\pythoncore-3.14-64\vcruntime140_1.dll', '.'),
    ],
    datas=[
        # Bundle CustomTkinter built-in themes & images
        (str(CTK_PATH / 'assets'), 'customtkinter/assets'),
        ('assets', 'assets'),
    ],
    hiddenimports=[
        # CustomTkinter
        'customtkinter',
        'PIL._tkinter_finder',
        # Matplotlib backends
        'matplotlib.backends.backend_tkagg',
        'matplotlib.backends.backend_agg',
        'matplotlib.backends._backend_tk',
        'matplotlib.figure',
        # SymPy
        'sympy',
        # App modules
        'ui',
        'ui.app',
        'ui.sidebar',
        'ui.graph_panel',
        'ui.controls',
        'ui.themes',
        'graphing',
        'graphing.renderer',
        'graphing.animations',
        'graphing.sampling',
        'graphing.scaling',
        'math_engine',
        'math_engine.parser',
        'math_engine.analyzer',
        'symbolic',
        'symbolic.derivatives',
    ],
    hookspath=[],
    hooksconfig={
        "matplotlib": {
            "backends": ["TkAgg"],  # Force-include TkAgg so the canvas works in the exe
        },
    },
    runtime_hooks=[],
    excludes=['tkinter.test', 'test', '_pytest', 'pytest'],
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
    name='Locus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,          # No terminal window (windowed app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='ui/assets/locus.ico',  # Uncomment if you add an icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Locus',
)
