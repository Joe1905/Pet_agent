@echo off
REM ================================
REM Conda 环境下打包 PySide6 项目
REM 入口文件: main.py
REM 图标文件: chat.ico
REM 排除: logs 文件夹
REM ================================

call conda activate local_pet

cd /d %~dp0

python -m nuitka ^
  --standalone ^
  --enable-plugin=pyside6 ^
  --windows-console-mode=force ^
  --lto=yes ^
  --output-dir=build ^
  --include-data-dir=./config=config ^
  --include-data-dir=./ui=ui ^
  --include-data-dir=./pet_image=pet_image ^
  main.py
echo 打包完成！按任意键退出...
pause
