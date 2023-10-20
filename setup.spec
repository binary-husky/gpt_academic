# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.building.api import PYZ, EXE, COLLECT
from PyInstaller.building.build_main import Analysis
from PyInstaller.utils.hooks import collect_all


datas, binaries, hiddenimports = [], [], []
for pkg in ["docs.waifu_plugin", "gradio", "gradio_client", "request_llm", "themes", "tqdm", "requests", "regex",
            "packaging", "filelock", "numpy", "safetensors", "yaml"]:
    tmp_ret = collect_all(pkg)
    datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


datas += [("docs/logo.ico", "docs"), ("docs/logo.png", "docs")]
hiddenimports += ['tiktoken_ext.openai_public', 'tiktoken_ext']


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='chatgpt-academic',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[r'docs\logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='chatgpt-academic',
)
