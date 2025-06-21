# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

def get_qt_plugins_dir():
    import PyQt5
    from pathlib import Path
    return str(Path(PyQt5.__file__).parent / 'Qt5' / 'plugins')

a = Analysis(['graveautoclicker.py'],
             pathex=[],
             binaries=[],
             datas=[
                 ('icon.ico', '.'),
                 (get_qt_plugins_dir() + '\\platforms\\qwindows.dll', 'platforms'),
                 (get_qt_plugins_dir() + '\\styles\\qwindowsvistastyle.dll', 'styles')
             ],
             hiddenimports=['pynput.keyboard._win32', 'pynput.mouse._win32'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='GraveAutoClicker',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='icon.ico')