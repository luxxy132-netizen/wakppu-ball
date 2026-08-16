"""왁뿌볼 — 데스크탑 스트레스 해소 위젯.

배경이 뚫린 작은 창에 3D 왁뿌볼만 떠 있다.
공을 끌면 창이 움직이고, 그냥 누르면 왁스가 부서졌다가 다시 흡착된다.
크기·디자인·질감은 우측 상단 ⋯ 버튼.

실행:
    .venv\\Scripts\\pythonw.exe wakppu\\widget.py

기본은 DWM 방식이다. 클릭이 정상 동작한다.
빈 배경을 클릭해도 뒤 창으로 통과하지는 않는다(창 영역 안이므로).

투명 처리를 아예 끄려면(진단용):
    .venv\\Scripts\\pythonw.exe wakppu\\widget.py --opaque

클릭 통과가 꼭 필요하면 예전 색상키 방식을 쓸 수 있지만,
그러면 공을 눌러도 반응하지 않는다(WebView2 구조상 불가피):
    .venv\\Scripts\\pythonw.exe wakppu\\widget.py --chroma

무슨 일이 있었는지는 wakppu\\wakppu.log 에 남는다.
"""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import webview

# exe 로 묶으면 자원은 임시 폴더에 풀리고(_MEIPASS) 그 폴더는 종료 때 사라진다.
# 로그처럼 남겨야 하는 파일은 exe 옆에 써야 한다.
if getattr(sys, "frozen", False):
    HERE = Path(sys._MEIPASS)                 # index.html · vendor · sfx · 아이콘
    BASE = Path(sys.executable).resolve().parent
else:
    HERE = BASE = Path(__file__).resolve().parent

PAGE = HERE / "index.html"
ICON = HERE / "wakppu.ico"
LOG = BASE / "wakppu.log"

# 이 색으로 칠해진 픽셀이 통째로 뚫린다. 장난감에 우연히 나올 일 없는 값으로 고른다.
CHROMA = (1, 2, 3)
# 투명화를 끈 진단 모드에서 쓰는 배경 (크로마 색은 거의 검정이라 눈에 나쁘다)
OPAQUE_BG = "#201E28"
START_SIZE = 150

SHORTCUT_NAME = "왁뿌볼"
# 바로가기를 한 번 만들었는지 기억하는 곳. exe 옆이 아니라 여기 둬야
# exe 를 읽기 전용 폴더에 둬도 되고, 사용자가 바로가기를 지웠을 때 되살아나지 않는다.
STATE_DIR = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "wakppu"


def log(msg: str) -> None:
    stamp = time.strftime("%H:%M:%S")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"[{stamp}] {msg}\n")


def _launch_target() -> tuple[str, str, str]:
    """바로가기가 가리켜야 할 (실행파일, 인자, 작업폴더)."""
    if getattr(sys, "frozen", False):
        exe = str(Path(sys.executable).resolve())
        return exe, "", str(Path(exe).parent)

    # 소스로 돌릴 때는 콘솔이 안 뜨는 pythonw 를 쓴다
    pyw = Path(sys.executable).with_name("pythonw.exe")
    py = str(pyw if pyw.exists() else Path(sys.executable))
    return py, f'"{Path(__file__).resolve()}"', str(BASE)


def create_shortcut() -> str:
    """바탕화면에 바로가기를 만들고 그 경로를 돌려준다.

    바탕화면 경로는 OneDrive 로 옮겨져 있을 수 있어 직접 조립하지 않고
    Windows 에게 물어본다. 그래서 PowerShell 을 거친다.
    """
    target, args, workdir = _launch_target()
    icon = target if getattr(sys, "frozen", False) else str(ICON)

    script = f"""
$ws = New-Object -ComObject WScript.Shell
$path = Join-Path ([Environment]::GetFolderPath('Desktop')) '{SHORTCUT_NAME}.lnk'
$sc = $ws.CreateShortcut($path)
$sc.TargetPath = '{target}'
$sc.Arguments = '{args}'
$sc.WorkingDirectory = '{workdir}'
$sc.Description = '왁뿌볼 - 누르면 왁스가 갈라지는 데스크탑 ASMR 위젯'
$sc.WindowStyle = 7
$sc.IconLocation = '{icon},0'
$sc.Save()
Write-Output $path
"""
    # 한글이 깨지지 않도록 BOM 붙인 UTF-8 파일로 넘긴다
    tmp = Path(tempfile.gettempdir()) / "wakppu_shortcut.ps1"
    tmp.write_text(script, encoding="utf-8-sig")
    try:
        out = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(tmp)],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            timeout=30,
        )
        if out.returncode != 0:
            raise RuntimeError((out.stderr or "").strip()[:300])
        return (out.stdout or "").strip()
    finally:
        tmp.unlink(missing_ok=True)


def ensure_shortcut() -> None:
    """처음 실행할 때 한 번만 바로가기를 만든다.

    exe 는 설치 과정이 없는 단일 파일이라 그냥 두면 바로가기가 생기지 않는다.
    지운 바로가기가 매번 되살아나면 곤란하므로 표식을 남겨 두 번은 만들지 않는다.
    """
    marker = STATE_DIR / "shortcut_created"
    if marker.exists():
        return
    try:
        path = create_shortcut()
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        marker.write_text(path, encoding="utf-8")
        log(f"바로가기 생성: {path}")
    except Exception as exc:
        log(f"바로가기 생성 실패: {exc!r}")


class Api:
    """HTML 쪽에서 window.pywebview.api 로 부르는 창 제어."""

    def __init__(self) -> None:
        self.window: webview.Window | None = None

    def pos(self) -> list[int]:
        return [self.window.x, self.window.y]

    def move(self, x: float, y: float) -> None:
        self.window.move(int(x), int(y))

    def resize(self, w: float, h: float) -> None:
        self.window.resize(int(w), int(h))

    def log(self, msg: str) -> None:
        """페이지가 어디까지 진행됐는지 남긴다. 창이 멎으면 이 기록이 유일한 단서다."""
        log(f"[page] {msg}")

    def make_shortcut(self) -> str:
        """⋯ 메뉴의 '바탕화면에 바로가기' 버튼."""
        try:
            path = create_shortcut()
            STATE_DIR.mkdir(parents=True, exist_ok=True)
            (STATE_DIR / "shortcut_created").write_text(path, encoding="utf-8")
            log(f"바로가기 생성(수동): {path}")
            return "바탕화면에 만들었습니다"
        except Exception as exc:
            log(f"바로가기 생성 실패(수동): {exc!r}")
            return "실패했습니다 (wakppu.log 확인)"

    def close(self) -> None:
        for w in webview.windows:
            w.destroy()


def _wait_for_form(window: webview.Window):
    """폼이 만들어질 때까지 최대 5초 기다린다."""
    from webview.platforms.winforms import BrowserView

    for _ in range(100):
        form = BrowserView.instances.get(window.uid)
        if form is not None and form.IsHandleCreated:
            return form
        time.sleep(0.05)
    return BrowserView.instances.get(window.uid)


def punch_dwm(window: webview.Window) -> None:
    """DWM 에게 창 전체를 유리판으로 넘겨 순수 검정을 투명으로 만든다.

    색상 키(TransparencyKey) 방식은 창을 레이어드 윈도우로 바꾸는데,
    WebView2 는 부모와 별개인 자식 창에 그려지므로 Windows 가 클릭 통과를
    판정할 때 보는 부모 표면은 전부 키 색이다. 그래서 공 위를 눌러도
    클릭이 뒤로 빠져나가 위젯이 통째로 먹통이 된다.
    이 방식은 레이어드 윈도우를 쓰지 않아 클릭이 정상 동작한다.
    """
    import ctypes

    form = _wait_for_form(window)
    if form is None:
        log("DWM 실패 - 폼을 못 찾음")
        return

    class Margins(ctypes.Structure):
        _fields_ = [("cxLeftWidth", ctypes.c_int), ("cxRightWidth", ctypes.c_int),
                    ("cyTopHeight", ctypes.c_int), ("cyBottomHeight", ctypes.c_int)]

    try:
        from System import Action
        from System.Drawing import Color
    except Exception as exc:
        log(f"DWM 실패 - 모듈: {exc!r}")
        return

    def apply() -> None:
        try:
            form.BackColor = Color.Black          # 순수 검정만 DWM 이 투명으로 처리한다
            hwnd = int(str(form.Handle.ToInt64()))
            rc = ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(
                hwnd, ctypes.byref(Margins(-1, -1, -1, -1)))
            log(f"DWM 적용 (hr={rc}, 0 이면 성공)")
        except Exception as exc:
            log(f"DWM 실패 - UI 스레드: {exc!r}")

    try:
        form.BeginInvoke(Action(apply))
    except Exception as exc:
        log(f"DWM 실패 - BeginInvoke: {exc!r}")


def punch_background(window: webview.Window) -> None:
    """창 배경을 실제로 뚫는다.

    pywebview 는 WebView2 컨트롤만 투명하게 만들고 그 뒤 WinForms 폼은
    기본 회색으로 남겨 둬서, 페이지가 투명해도 회색 판이 그대로 보인다.
    폼 배경을 크로마 색으로 칠하고 같은 색을 TransparencyKey 로 지정하면
    그 픽셀이 화면에서 사라지고 클릭도 뒤로 통과한다.
    """
    try:
        # winforms 모듈이 System.Drawing 참조를 먼저 걸어 두므로 이 순서를 지킨다
        from webview.platforms.winforms import BrowserView
        from System import Action
        from System.Drawing import Color
    except Exception as exc:
        log(f"투명화 불가 - 모듈을 못 불러옴: {exc!r}")
        return

    form = _wait_for_form(window)
    if form is None:
        log(f"투명화 불가 - 폼을 못 찾음 (uid={window.uid}, 있는 키={list(BrowserView.instances)})")
        return

    key = Color.FromArgb(255, *CHROMA)

    def apply() -> None:
        try:
            form.AllowTransparency = True
            form.BackColor = key
            form.TransparencyKey = key
            log(f"색상키 적용됨 (BackColor={form.BackColor}, Key={form.TransparencyKey})")
        except Exception as exc:
            log(f"색상키 실패 - UI 스레드에서: {exc!r}")

    try:
        form.BeginInvoke(Action(apply))
    except Exception as exc:
        log(f"색상키 실패 - BeginInvoke: {exc!r}")


def main() -> None:
    opaque = "--opaque" in sys.argv
    chroma = "--chroma" in sys.argv     # 예전 색상키 방식. 투명하지만 클릭이 전부 통과한다.
    mode = "opaque" if opaque else ("색상키" if chroma else "dwm")
    log(f"시작 (모드={mode})")

    api = Api()
    api.window = webview.create_window(
        "왁뿌볼",
        # 경로를 그대로 넘기면 pywebview 가 내장 HTTP 서버로 서빙하는데,
        # 그 서버가 오디오 프리로드 같은 동시 요청을 잘 못 버텨 창이 멎었다.
        # file:// 로 직접 열면 그런 중간 단계가 없다.
        url=PAGE.as_uri(),
        js_api=api,
        width=START_SIZE,
        height=START_SIZE,
        frameless=True,
        easy_drag=False,        # 드래그는 공에서 직접 처리한다
        on_top=False,
        transparent=not opaque,
        background_color=OPAQUE_BG if opaque else
                         ("#%02X%02X%02X" % CHROMA if chroma else "#000000"),
        resizable=False,        # 테두리가 없어 잡을 곳이 없다. 크기는 ⋯ 메뉴에서.
        shadow=False,
    )

    def on_start(window: webview.Window) -> None:
        if not opaque:
            (punch_background if chroma else punch_dwm)(window)
        ensure_shortcut()

    icon = str(ICON) if ICON.exists() else None
    webview.start(on_start, api.window, icon=icon)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # exe 는 콘솔이 없어 오류가 그냥 사라진다. 반드시 로그로 남긴다.
        import traceback

        log("치명적 오류\n" + traceback.format_exc())
        raise
