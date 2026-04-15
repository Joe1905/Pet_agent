import os
import subprocess

from string_manager import StringManager


def compile_resources():
    qrc_file = "images/resource.qrc"  # 你的.qrc文件路径
    py_file = "resource_rc.py"
    strings =StringManager()

    if not os.path.exists(qrc_file):
        print(strings.get("loadQrc.error_str1"),qrc_file)
        return

    try:
        # 使用pyrcc6编译资源文件（关键修改）
        subprocess.run(
            [
                "pyside6-rcc",
                qrc_file,
                "-o",
                py_file
            ],
            check=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        # print(strings.get("loadQrc.success_str"),py_file)
    except subprocess.CalledProcessError as e:
        pass

        # print(strings.get("loadQrc.error_str2"), e.returncode)
        # print(strings.get("loadQrc.error_str3"), e.stderr if e.stderr else strings.get("loadQrc.error_str4"))
    except Exception as e:
        # print(strings.get("loadQrc.error_str5"), f"{e}")
        pass
def compile_favor(ui_name:str):
    subprocess.run(
        [
            "pyside6-uic",
            f"{ui_name}.ui",
            "-o",
            f"{ui_name}_ui.py"
        ],
        check=True,
        text=True,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
# 在程序启动时调用编译函数
# compile_resources()
compile_favor("message")