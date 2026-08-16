# 바탕화면에 왁뿌볼 바로가기를 만든다.
# 우클릭 → "PowerShell에서 실행" 하거나, 아래 명령으로 실행하세요.
#   powershell -ExecutionPolicy Bypass -File ".\바로가기 만들기.ps1"

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$app  = Join-Path $here "widget.py"
$ico  = Join-Path $here "wakppu.ico"

# 프로젝트 가상환경의 pythonw 를 우선 쓰고, 없으면 시스템 pythonw 를 찾는다
$py = Join-Path (Split-Path -Parent $here) ".venv\Scripts\pythonw.exe"
if (-not (Test-Path $py)) {
  $cmd = Get-Command pythonw.exe -ErrorAction SilentlyContinue
  if ($null -eq $cmd) { throw "pythonw.exe 를 찾을 수 없습니다. Python 을 설치하거나 경로를 직접 지정하세요." }
  $py = $cmd.Source
}

$link = Join-Path ([Environment]::GetFolderPath('Desktop')) "왁뿌볼.lnk"

$ws = New-Object -ComObject WScript.Shell
$sc = $ws.CreateShortcut($link)
$sc.TargetPath       = $py
$sc.Arguments        = '"' + $app + '"'
$sc.WorkingDirectory = $here
$sc.Description      = "왁뿌볼 - 누르면 왁스가 갈라지는 데스크탑 ASMR 위젯"
$sc.WindowStyle      = 7                      # 최소화 (pythonw 라 창은 어차피 없다)
if (Test-Path $ico) { $sc.IconLocation = "$ico,0" }
$sc.Save()

Write-Host "만들었습니다: $link"
