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
        ("sfx/soap1.mp3", "sfx"),
        ("sfx/soap2.mp3", "sfx"),
        ("sfx/soap3.mp3", "sfx"),
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
    # GitHub 릴리스는 자산 파일명에서 한글을 지워 default.exe 로 만들어 버린다.
    # 파일명은 ASCII 로 두고, 속성창·작업관리자에 뜨는 이름은 version_info 로 한글이 되게 한다.
    name="WakppuBall",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,          # 검은 콘솔 창 없이 위젯만 뜬다
    icon="wakppu.ico",
    version="version_info.txt",
)
