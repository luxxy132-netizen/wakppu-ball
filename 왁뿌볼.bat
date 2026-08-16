@echo off
rem 콘솔 창 없이 위젯만 띄운다.
start "" "%~dp0..\.venv\Scripts\pythonw.exe" "%~dp0widget.py"
