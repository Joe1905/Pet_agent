@echo off
REM ================================
REM Conda 环境下打包 PySide6 项目
REM 项目路径: D:\PyCharmProjects\local_pet
REM 入口文件: src\main.py
REM 图标文件: src\chat.ico
REM 排除: logs 文件夹
REM ================================


call conda activate local_pet

cd /d D:\PyCharmProjects\local_pet\src

python -m nuitka ^
  --standalone ^
  --enable-plugin=pyside6 ^
  --windows-console-mode=attach ^
  --lto=yes ^
  --output-dir=build ^
  --include-data-dir=./config=config ^
  --include-data-dir=./ui=ui ^
  --include-data-dir=./pet_image=pet_image ^
  main.py
echo 打包完成！按任意键退出...
pause
