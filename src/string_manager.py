import json
import os


class StringManager:
    _instance = None
    _strings = {}
    string_file = "string_table.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.load_strings()
        return cls._instance

    def load_strings(self, file_path=None):
        """加载字符串资源文件"""
        if file_path is None:
            file_path = self.string_file
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_dir, "config", file_path)

            with open(full_path, 'r', encoding='utf-8') as f:
                self._strings = json.load(f)
        except FileNotFoundError:
            raise Exception(f"字符串资源文件未找到: {file_path}")
        except json.JSONDecodeError:
            raise Exception(f"字符串资源文件格式错误: {file_path}")

    def get(self, key_path, default=None, **format_args):
        """
        获取字符串
        :param key_path: 点分隔的键路径 (例如: "ui.main_window.title")
        :param default: 找不到键时的默认值
        :param format_args: 格式化参数
        :return: 格式化后的字符串
        """
        keys = key_path.split('.')
        current = self._strings

        try:
            for key in keys:
                current = current[key]

            if isinstance(current, str) and format_args:
                return current.format(**format_args)
            return current
        except (KeyError, TypeError):
            return default or f"[Missing: {key_path}]"

    def reload(self, file_path=None):
        """重新加载字符串资源"""
        if file_path is not None:
            self.string_file = file_path
        self.load_strings()
