# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

spec_dir = os.getcwd()

datas = [
    (os.path.join(spec_dir, 'saturn-background.png'), '.'),
    (os.path.join(spec_dir, 'saturn_title.png'), '.'),
    (os.path.join(spec_dir, 'logo.png'), '.'),
    (os.path.join(spec_dir, 'logo.ico'), '.'),
    (os.path.join(spec_dir, 'config.json'), '.'),
]

binaries = []
hiddenimports = [
    # Only include essential PySide6 modules
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    # Shader download module
    'shader_download_classes',
]

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
    excludes=[
        # Web/Browser modules (huge!)
        'PySide6.QtWebEngine',
        'PySide6.QtWebEngineCore',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebChannel',
        'PySide6.QtPdf',
        'PySide6.QtPdfWidgets',
        
        # 3D/Graphics modules (not needed)
        'PySide6.Qt3DCore',
        'PySide6.Qt3DRender',
        'PySide6.Qt3DInput',
        'PySide6.Qt3DAnimation',
        'PySide6.Qt3DExtras',
        'PySide6.QtQuick',
        'PySide6.QtQuick3D',
        'PySide6.QtQuickControls2',
        'PySide6.QtQuickWidgets',
        'PySide6.QtQml',
        
        # Multimedia (not used)
        'PySide6.QtMultimedia',
        'PySide6.QtMultimediaWidgets',
        
        # Other unused PySide6 modules
        'PySide6.QtCharts',
        'PySide6.QtDataVisualization',
        'PySide6.QtNetworkAuth',
        'PySide6.QtPositioning',
        'PySide6.QtRemoteObjects',
        'PySide6.QtSensors',
        'PySide6.QtSerialPort',
        'PySide6.QtSql',
        'PySide6.QtTest',
        'PySide6.QtTextToSpeech',
        'PySide6.QtBluetooth',
        'PySide6.QtNfc',
        'PySide6.QtSvg',
        'PySide6.QtSvgWidgets',
        'PySide6.QtDesigner',
        'PySide6.QtHelp',
        'PySide6.QtUiTools',
        'PySide6.QtXml',
        
        # Other heavy libraries
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL.ImageQt',
    ],
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
    name='saturn_gui_linux',
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
    icon='logo.png',
)
