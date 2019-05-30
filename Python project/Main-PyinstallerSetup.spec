# -*- mode: python -*-
# To generate a new Spec file run the following command: pyi-makespec --onefile --console --icon='MsIcon.ico' Main.py
# To convert this project into an exe file run the following command in directory: pyinstaller Main-PyinstallerSetup.spec
# and then add the required files on binaries.
# Don't forget to change the project directory.

import sys
sys.setrecursionlimit(5000)

block_cipher = None


a = Analysis(['Main.py'],
             pathex=['E:\\ImmersionMUS\\Data Request\\Backups\\Lectura Ms'],
             binaries=[('SerialConfigWindowHighDPI.ui', '.'), ('MainFunctionsHighDPI.ui', '.'), 
	     ('MsIcon.ico', '.')],
             datas=[],
             hiddenimports=[],
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
          name='Main',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True, icon='MsIcon.ico' )
