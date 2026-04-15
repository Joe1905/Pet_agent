
import tempfile
import shutil
import sys
import os
import codecs
import configparser

from string_manager import StringManager


class ResourceExtractor:
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    temp_dir = None
    string_manager = StringManager()
    setting_config = None
    pet_config = None

    @staticmethod
    def get_resource_path(relative_path):
        """获取资源的绝对路径（兼容开发和单文件模式）"""
        # print("base_path", ResourceExtractor.base_path)
        return os.path.join(ResourceExtractor.base_path, relative_path)

    @staticmethod
    def extract_to_temp(resource_relative_paths):
        """将资源提取到临时目录（隐藏资源用）"""
        ResourceExtractor.temp_dir = tempfile.mkdtemp()
        for rel_path in resource_relative_paths:
            src_path = ResourceExtractor.get_resource_path(rel_path)
            dest_path = os.path.join(ResourceExtractor.temp_dir, rel_path)
            # 确保目标目录存在
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            if os.path.isfile(src_path):
                shutil.copy2(src_path, dest_path)
            elif os.path.isdir(src_path):
                shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
        return ResourceExtractor.temp_dir

    @staticmethod
    def cleanup_temp():
        """清理临时目录（可选，程序退出时调用）"""
        if ResourceExtractor.temp_dir and os.path.exists(ResourceExtractor.temp_dir):
            shutil.rmtree(ResourceExtractor.temp_dir, ignore_errors=True)

    @staticmethod
    def get_gguf_model_path():

        if getattr(sys, 'frozen', False):
            # 单文件模式：sys.executable 指向 exe 文件路径
            temp_res_dir = os.path.dirname(sys.executable)
        else:
            # 开发模式：返回当前脚本所在目录（用于测试）
            temp_res_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(
            temp_res_dir,
            "modelSource",
            "Qwen1.5-7B-Chat-GGUF",
            "qwen1_5-7b-chat-q4_0.gguf"
        )
        strings = StringManager()
        # print(strings.get("file_load.log_title"), model_path)
        return model_path

    @staticmethod
    def get_small_model_path():

        if getattr(sys, 'frozen', False):
            # 单文件模式：sys.executable 指向 exe 文件路径
            temp_res_dir = os.path.dirname(sys.executable)
        else:
            # 开发模式：返回当前脚本所在目录（用于测试）
            temp_res_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(
            temp_res_dir,
            "modelSource",
            "m3e-small"
        )
        strings = StringManager()
        # print(strings.get("file_load.log_title"), model_path)
        return model_path

    @staticmethod
    def to_load_config():
        config = configparser.ConfigParser()
        config_path = ResourceExtractor.get_resource_path("config\setting.ini")
        try:
            with codecs.open(config_path, 'r', 'utf-8') as f:
                config.read_file(f)
            # print(ResourceExtractor.string_manager.get("main.load_success"))
            return config
        except Exception as e:
            # print(ResourceExtractor.string_manager.get("main.load_fail") + f":{str(e)}")
            sys.exit(1)

    @staticmethod
    def get_setting_config():
        if ResourceExtractor.setting_config is None:
            ResourceExtractor.setting_config =ResourceExtractor.to_load_config()

        return ResourceExtractor.setting_config

    @staticmethod
    def set_setting_config(obj, sign):
        CONFIG_MAPPINGS = [
            ("Memory", "current_memory", "Memory", "current_memory"),
            ("Memory", "current_file", "Memory", "current_file"),
            ("Talk_Times", "pet_1", "Talk_Times", "pet_1"),
            ("Talk_Times", "pet_2", "Talk_Times", "pet_2"),
            ("Talk_Times", "talk_day_1", "Talk_Times", "talk_day_1"),
            ("Talk_Times", "talk_day_2", "Talk_Times", "talk_day_2"),
            ("Talk_Times", "talk_times_1", "Talk_Times", "talk_times_1"),
            ("Talk_Times", "talk_times_2", "Talk_Times", "talk_times_2"),
            ("General_Set", "current_index", "General_Set", "current_index"),
            ("Nick_Name", "nickname1", "Nick_Name", "nickname1"),
            ("Nick_Name", "nickname2", "Nick_Name", "nickname2"),
            ("Url", "server_url", "Url", "server_url"),
        ]
        try:
            config = ResourceExtractor.get_setting_config()
            config_path = ResourceExtractor.get_resource_path("config\setting.ini")

            # 遍历所有配置项，统一更新
            for target_section, target_key, obj_section, obj_key in CONFIG_MAPPINGS:
                # 从obj中安全提取值（避免KeyError）
                section_data = obj.get(obj_section, {})
                value = section_data.get(obj_key)
                if value is not None:
                    # 确保目标节存在（configparser要求先有节才能设键）
                    if not config.has_section(target_section):
                        config.add_section(target_section)
                    # 设置值（转为字符串，满足configparser要求）
                    config.set(target_section, target_key, str(value))

            with codecs.open(config_path, 'w', 'utf-8') as f:
                config.write(f)
            ResourceExtractor.setting_config = ResourceExtractor.to_load_config()
            if sign is not None:
                sign.emit(True)
        except Exception as e:
            # print("保存失败")
            if sign is not None:
                sign.emit(False)

    @staticmethod
    def reset_setting_config(sign):
        config = ResourceExtractor.get_setting_config()

        config_path = ResourceExtractor.get_resource_path("config\setting.ini")
        try:
            string_manager = StringManager()
            config["Memory"]["current_memory"] = ""
            config["Memory"]["current_file"] = "0"
            config["Talk_Times"]["pet_1"] = "0"
            config["Talk_Times"]["pet_2"] = "0"
            config["Talk_Times"]["talk_day_1"] = "0"
            config["Talk_Times"]["talk_times_1"] = "0"
            config["Talk_Times"]["talk_day_2"] = "0"
            config["Talk_Times"]["talk_times_2"] = "0"
            config["General_Set"]["current_index"] = "1"
            config["Nick_Name"]["nickname1"] = string_manager.get("default_name.nickname1")
            config["Nick_Name"]["nickname2"] = string_manager.get("default_name.nickname2")
            config["Url"]["server_url"] = ""
            with codecs.open(config_path, 'w', 'utf-8') as f:
                config.write(f)
            if sign is not None:
                sign.emit(True)
        except Exception as e:
            # print("保存失败")
            if sign is not None:
                sign.emit(False)

    @staticmethod
    def text_is_equal( text1, text2):
        def normalize_text(text):
            """标准化文本：去除首尾空白 + 统一换行符为\n"""
            return text.strip().replace('\r\n', '\n')
        return normalize_text(text1) == normalize_text(text2)

    @staticmethod
    def get_pet_config(temp_res_dir = None):
        if ResourceExtractor.pet_config is not None:
            return ResourceExtractor.pet_config
        if temp_res_dir is None:
            temp_res_dir = ResourceExtractor.extract_to_temp([
                "pet_image",
                "config"
            ])
        string_manager = StringManager()
        # 从临时目录加载配置和动图
        config_path = os.path.join(temp_res_dir, "config/pet_config_private.ini")

        # 读取配置文件
        config = configparser.ConfigParser()
        try:
            with codecs.open(config_path, 'r', 'utf-8') as f:
                config.read_file(f)
            # print(string_manager.get("main.load_success"))
            ResourceExtractor.pet_config = config
            return config
        except Exception as e:
            # print(string_manager.get("main.load_fail") + f":{str(e)}")
            return None