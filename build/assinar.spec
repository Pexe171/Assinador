# Especificação do PyInstaller para gerar o executável.
block_cipher = None


a = Analysis(['app/main.py'],
             pathex=[],
             binaries=[],
             datas=[('assets', 'assets')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[])
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='assinar',
          debug=False,
          strip=False,
          upx=True,
          console=True)
