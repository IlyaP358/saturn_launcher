# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_all

spec_dir = os.getcwd()

datas = [
    (os.path.join(spec_dir, 'saturn-background.png'), '.'),
    (os.path.join(spec_dir, 'saturn_title.png'), '.'),
    (os.path.join(spec_dir, 'logo.png'), '.'),
    (os.path.join(spec_dir, 'config.json'), '.'),
]

binaries = []
hiddenimports = []

# Collect PySide6 data
tmp_ret = collect_all('PySide6')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# Collect pyfiglet data
tmp_ret = collect_all('pyfiglet')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

a = Analysis(
    ['saturn-gui.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas'],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='saturn_gui_win',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)