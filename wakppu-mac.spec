# macOS 빌드 설정. 반드시 맥에서 실행해야 한다 (PyInstaller 는 크로스 컴파일이 안 된다).
#
#   pip install pywebview pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-WebKit pyinstaller
#   pyinstaller wakppu-mac.spec --noconfirm --clean
#
# dist/왁뿌볼.app 이 나온다.

a = Analysis(
    ["widget.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("index.html", "."),
        ("wakppu.icns", "."),
        ("vendor/three.min.js", "vendor"),
        ("sfx/crack1.mp3", "sfx"),
        ("sfx/crack2.mp3", "sfx"),
        ("sfx/crack3.mp3", "sfx"),
        ("sfx/soap1.mp3", "sfx"),
        ("sfx/soap2.mp3", "sfx"),
        ("sfx/soap3.mp3", "sfx"),
    ],
    # 맥에서는 Cocoa(WKWebView) 백엔드를 쓴다. 윈도우용 winforms/pythonnet 은 필요 없다.
    hiddenimports=[
        "webview.platforms.cocoa",
        "objc",
        "Foundation",
        "AppKit",
        "WebKit",
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
    name="왁뿌볼",
    debug=False,
    strip=False,
    upx=False,
    console=False,
    # 애플 실리콘은 서명이 아예 없는 실행 파일을 거부한다.
    # "-" 는 임시(ad-hoc) 서명이라 개발자 계정 없이도 붙일 수 있다.
    codesign_identity="-",
)

coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="왁뿌볼")

app = BUNDLE(
    coll,
    name="왁뿌볼.app",
    icon="wakppu.icns",
    bundle_identifier="com.wakppu.ball",
    info_plist={
        "CFBundleName": "왁뿌볼",
        "CFBundleDisplayName": "왁뿌볼",
        "CFBundleShortVersionString": "1.2.0",
        "CFBundleVersion": "1.2.0",
        "NSHighResolutionCapable": True,
        # 창이 항상 위로 뜨지 않으므로 Dock 아이콘은 남겨 둔다.
        # 놓쳤을 때 Dock 에서 다시 찾을 수 있어야 한다.
        "LSUIElement": False,
    },
)
