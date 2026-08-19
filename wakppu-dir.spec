# 폴더형(onedir) 빌드 설정.
#
#   pyinstaller wakppu-dir.spec --noconfirm --clean
#
# 한 파일(onefile)로 묶으면 실행할 때마다 스스로 압축을 풀어 임시 폴더에서
# 실행하는데, 이 동작이 악성코드 패커와 똑같이 생겨서 백신이 자주 오탐한다.
# 폴더형은 그 자기추출 단계가 없어 오탐이 훨씬 적다. 대신 파일이 여러 개다.

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
    exclude_binaries=True,
    name="WakppuBall",
    debug=False,
    strip=False,
    upx=False,
    console=False,
    icon="wakppu.ico",
    version="version_info.txt",
)

coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="왁뿌볼")
