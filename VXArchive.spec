# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
import os

datas = [('vxarchive.ico', '.'), ('vxarchive/bin', 'bin')]
binaries = []
hiddenimports = [
    'vxarchive',
    'vxarchive.core',
    'vxarchive.core.archive_engine',
    'vxarchive.core.archive_grep',
    'vxarchive.core.archive_repair',
    'vxarchive.core.batch_processor',
    'vxarchive.core.benchmark',
    'vxarchive.core.bookmarks',
    'vxarchive.core.dedup_analyzer',
    'vxarchive.core.diff_sync',
    'vxarchive.core.hasher',
    'vxarchive.core.health_checker',
    'vxarchive.core.iso_mounter',
    'vxarchive.core.lan_share',
    'vxarchive.core.license_manager',
    'vxarchive.core.metadata_inspector',
    'vxarchive.core.password_memory',
    'vxarchive.core.password_vault',
    'vxarchive.core.sanitizer',
    'vxarchive.core.sfx_builder',
    'vxarchive.core.shell_integration',
    'vxarchive.core.shredder',
    'vxarchive.core.splitter',
    'vxarchive.core.steganography',
    'vxarchive.core.threat_scanner',
    'vxarchive.core.transcoder',
    'vxarchive.core.utils',
    'vxarchive.gui',
    'vxarchive.gui.main_window',
    'vxarchive.gui.tab_page',
    'vxarchive.gui.glass_theme',
    'vxarchive.gui.icons',
    'vxarchive.gui.mica_effect',
    'vxarchive.gui.dialog_vault',
    'vxarchive.gui.dialogs_base',
    'vxarchive.gui.dialogs_pro',
    'PyQt6.QtCore',
    'PyQt6.QtGui',
    'PyQt6.QtWidgets'
]

tmp_ret = collect_all('qrcode')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]


a = Analysis(
    ['vxarchive/main.py'],
    pathex=['.'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VXArchive',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='vxarchive.ico',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VXArchive',
)
