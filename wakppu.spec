# PyInstaller 빌드 설정.
#   pyinstaller wakppu.spec --noconfirm
#
# index.html · three.js · 음원 · 아이콘을 모두 exe 안에 넣어 한 파일로 만든다.
# pywebview 는 Edge WebView2 를 pythonnet(clr) 으로 부르기 때문에
# 관련 모듈을 hiddenimports 로 명시해 줘야 번들에서 빠지지 않는다.

a = Analysis(
    ["widget.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("index.html", "."),
        ("wakppu.ico", "."),
        ("vendor/three.min.js", "vendor"),
        ("sfx/crack1.mp3", "sfx"),
        ("sfx/crack2.mp3", "sfx"),
        ("sfx/crack3.mp3", "sfx"),
    ],
    hiddenimports=[
        "clr",
        "clr_loader",
        "pythonnet",
        "webview.platforms.winforms",
        "webview.platforms.edgechromium",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter", "unittest", "pydoc", "doctest", "test"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="왁뿌볼",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,          # 검은 콘솔 창 없이 위젯만 뜬다
    icon="wakppu.ico",
)
