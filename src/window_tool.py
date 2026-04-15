import subprocess
import pyautogui
import time
import ctypes
import webbrowser
import pygetwindow as gw
import requests
from datetime import datetime
from lunar_python import Solar
import os
import json


class WindowTool:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def open_app(self, arr: list):
        try:
            subprocess.Popen(arr)
            return f"已打开 {arr[0]}"
        except Exception as e:
            return f"打开失败: {e}"

    def type_text(self, arr: list):
        text: str = arr[0]
        delay: float = 0.1 if arr.__len__() < 2 else arr[1]
        time.sleep(1)  # 等待窗口激活
        pyautogui.write(text, interval=delay)
        return "已输入文本"

    def click(self, arr: list):
        x: int = arr[0]
        y: int = arr[1]
        pyautogui.click(x, y)
        return f"已点击位置 ({x}, {y})"

    def run_shell(self, arr: list):
        command = arr[0]
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout or result.stderr
        except Exception as e:
            return f"命令执行失败: {e}"

    def press_keys(self, arr: list):
        pyautogui.hotkey(*arr)
        return f"已执行快捷键: {' + '.join(arr)}"

    def open_url(self, arr: list):
        webbrowser.open(arr[0])
        return f"已打开网址: {' '.join(arr)}"

    def execute_action(self, action: str, args: list):
        actions = {
            "open_app": self.open_app,
            "type_text": self.type_text,
            "click": self.click,
            "run_shell": self.run_shell,
            "press_keys": self.press_keys,
            "open_url": self.open_url,
            "get_current_address": self.get_current_address,
            "get_today_weather":self.get_today_weather,
            "get_future_weather":self.get_future_weather,
            "get_current_time":self.get_current_time,
            "get_holiday_json":self.get_holiday_json
        }
        if action in actions:
            return actions[action](args)
        else:
            return f"未知操作: {action}"

    def get_display_scale(self):
        """获取显示缩放比例"""
        try:
            user32 = ctypes.windll.user32
            dpi = user32.GetDpiForSystem()
            return dpi / 96.0  # 返回缩放比例（如1.0表示100%，1.25表示125%）
        except AttributeError:
            # 兼容旧系统
            hdc = user32.GetDC(0)
            dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX = 88
            user32.ReleaseDC(0, hdc)
            return dpi_x / 96.0

    def get_windows_scaling_factor(self):
        try:
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()  # 让当前进程感知 DPI
            dpi = user32.GetDpiForSystem()  # 获取系统 DPI（默认 96）
            scaling = dpi / 96.0  # 计算缩放比例（100% = 1.0）
            return scaling
        except Exception as e:
            # print("获取缩放比例失败:", e)
            return None

    def to_get_window(self, title):
        window = gw.getWindowsWithTitle(title) # 中文系统标题可能是“时钟”或“Clock”
        if window:
            return window
        else:
            # print(f"未找到{title}窗口")
            return None

    def to_click_page_pos(self, parent_pos: list, item_pos: list, scale: float):
        button_x = parent_pos[0] + item_pos[0] * scale
        button_y = parent_pos[1] + item_pos[1] * scale
        return self.execute_action("click", [button_x, button_y])

    def to_get_lang(self) -> str:
        import locale
        lang, encoding = locale.getdefaultlocale()
        return lang

    def to_set_clock_timer(self, param):
        need_time = int(param)
        result = self.execute_action("open_app",
                                ["explorer.exe", "shell:AppsFolder\\Microsoft.WindowsAlarms_8wekyb3d8bbwe!App"])
        time.sleep(1.5)
        lang = self.to_get_lang()
        title = "时钟" if lang == "zh_CN" else "Clock"
        windows = self.to_get_window(title)  # 中文系统标题可能是“时钟”或“Clock”
        scale = self.get_windows_scaling_factor()
        time_h = need_time // 3600
        time_m = (need_time % 3600) // 60
        time_s = need_time % 60
        if time_h > 99:
            return

        screen_width, screen_height = pyautogui.size()
        # print(f"屏幕宽度：{screen_width}，高度：{screen_height}")

        add_window_size = [338, 398]
        text_pos = [100, 270]
        btn_pos = [100, 360]
        btn_start_x = 67
        btn_distance = 106
        btn_start_y = 88
        if windows:
            win = windows[0]
            if win.width < screen_width or win.height < (screen_height * 0.5):
                result2 = self.execute_action("press_keys", ["win", "up"])
            result3 = self.execute_action("press_keys", ["alt", "2"])
            time.sleep(0.5)
            new_window = self.to_get_window(title)[0]
            button_x = new_window.left + new_window.width - 40 * scale
            button_y = new_window.top + new_window.height - 40 * scale
            result4 = self.execute_action("click", [button_x, button_y])

            add_window_pos = [new_window.left + (new_window.width - add_window_size[0] * scale) // 2,
                              new_window.top + (new_window.height - add_window_size[1] * scale) // 2]
            button_x = add_window_pos[0] + btn_start_x * scale
            button_y = add_window_pos[1] + btn_start_y * scale

            self.execute_action("type_text", [str(time_h)])
            self.execute_action("press_keys", ["tab"])
            self.execute_action("type_text", [str(time_m)])
            self.execute_action("press_keys", ["tab"])
            self.execute_action("type_text", [str(time_s)])
            result5 = self.to_click_page_pos(add_window_pos, text_pos, scale)
            result6 = self.execute_action("type_text", ["AI New Clock"])
            # result5 = self.to_click_page_pos(add_window_pos, btn_pos, scale)

        return f"已成功定时{need_time}秒"

    def to_set_clock_stopwatch(self):
        result = self.execute_action("open_app",
                                ["explorer.exe", "shell:AppsFolder\\Microsoft.WindowsAlarms_8wekyb3d8bbwe!App"])
        time.sleep(1.5)
        lang = self.to_get_lang()
        title = "时钟" if lang == "zh_CN" else "Clock"
        windows = self.to_get_window(title)  # 中文系统标题可能是“时钟”或“Clock”
        scale = self.get_windows_scaling_factor()

        screen_width, screen_height = pyautogui.size()
        # print(f"屏幕宽度：{screen_width}，高度：{screen_height}")

        btn_pos_1 = [1510, 470]
        btn_pos_2 = [1330, 470]
        if windows:
            win = windows[0]
            if win.width < screen_width or win.height < (screen_height * 0.5):
                result2 = self.execute_action("press_keys", ["win", "up"])
            result3 = self.execute_action("press_keys", ["alt", "4"])
            time.sleep(0.5)
            new_window = self.to_get_window(title)[0]
            self.to_click_page_pos([new_window.left, new_window.top], btn_pos_1, scale)
            # self.to_click_page_pos([new_window.left, new_window.top], btn_pos_2, scale)


        return "已成功开启秒表计时"

    def to_set_clock_alarm(self, alarm_time:str):
        result = self.execute_action("open_app",
                                ["explorer.exe", "shell:AppsFolder\\Microsoft.WindowsAlarms_8wekyb3d8bbwe!App"])
        time.sleep(1.5)
        lang = self.to_get_lang()
        title = "时钟" if lang == "zh_CN" else "Clock"
        windows = self.to_get_window(title)  # 中文系统标题可能是“时钟”或“Clock”
        scale = self.get_windows_scaling_factor()

        screen_width, screen_height = pyautogui.size()
        # print(f"屏幕宽度：{screen_width}，高度：{screen_height}")
        time1 = alarm_time.split(":")[0]
        time2 = alarm_time.split(":")[1]

        add_window_size = [323, 594]
        text_pos = [100, 260]
        if windows:
            win = windows[0]
            if win.width < screen_width or win.height < (screen_height * 0.5):
                result2 = self.execute_action("press_keys", ["win", "up"])
            result3 = self.execute_action("press_keys", ["alt", "3"])
            time.sleep(0.5)
            new_window = self.to_get_window(title)[0]
            button_x = new_window.left + new_window.width - 40 * scale
            button_y = new_window.top + new_window.height - 40 * scale
            result4 = self.execute_action("click", [button_x, button_y])

            add_window_pos = [new_window.left + (new_window.width - add_window_size[0] * scale) // 2,
                              new_window.top + (new_window.height - add_window_size[1] * scale) // 2]

            result6 = self.execute_action("type_text", [time1])
            result3 = self.execute_action("press_keys", ["tab"])
            result6 = self.execute_action("type_text", [time2])
            result5 = self.to_click_page_pos(add_window_pos, text_pos, scale)
            result6 = self.execute_action("type_text", ["AI New Clock"])


        return f"已成功{alarm_time}的闹钟"


    def get_current_address(self):
        """通过高德IP定位API获取当前省、市、区（精度更高）"""
        ip_url = "https://restapi.amap.com/v3/ip"
        key_api = "b7f5746adaab004e38dfbc9a41b4f01a"
        try:
            params = {
                "key": key_api,
                # 不填ip参数则自动获取当前设备公网IP
            }
            response = requests.get(ip_url, params=params, timeout=5)
            data = response.json()

            if data["status"] == "1":  # 1表示成功
                province = data.get("province", "")
                city = data.get("city", "")
                district = data.get("district", "")  # 部分IP可能返回区县
                return city
            else:
                return f"定位失败：{data.get('info', '未知错误')}"
        except Exception as e:
            return f"地址获取异常：{str(e)}"

    def get_today_weather(self,city = ""):
        if city is "":
            try: city = self.get_current_address()
            except Exception as e:
                return f"天气获取异常{str(e)}"
        print(f"调用查找{city}天气工具")

        base_url = "https://restapi.amap.com/v3/weather/weatherInfo"
        key_api = "b7f5746adaab004e38dfbc9a41b4f01a"
        """根据城市名获取实时天气"""
        try:
            params = {
                "key": key_api,
                "city": city,
                "extensions": "base",  # base=实时天气，all=预报+实时
                "output": "json"
            }

            response = requests.get(base_url, params=params, timeout=5)
            data = response.json()
            if  data["status"] == "1" and len(data["lives"]) > 0:
                print(f"查询{city}天气成功")
                weather_data = data["lives"][0]
                return (
                    f"城市：{weather_data['city']}\n"
                    f"天气：{weather_data['weather']}\n"
                    f"温度：{weather_data['temperature']}℃\n"
                    f"湿度：{weather_data['humidity']}%\n"
                    f"风向：{weather_data['winddirection']}\n"
                    f"更新时间：{weather_data['reporttime']}"
                )
            return f"获取{city}天气失败"
        except Exception as e:
            return f"天气获取异常：{str(e)}"

    def get_future_weather(self,city=""):
        if city is "":
            try: city = self.get_current_address()
            except Exception as e:
                return f"天气获取异常{str(e)}"
        print(f"调用查找{city}未来天气工具")

        base_url = "https://restapi.amap.com/v3/weather/weatherInfo"
        key_api = "b7f5746adaab004e38dfbc9a41b4f01a"
        """根据城市名获取实时天气"""
        try:
            params = {
                "key": key_api,
                "city": city,
                "extensions": "all",  # base=实时天气，all=预报+实时
                "output": "json"
            }

            def to_get_weather_str(weather_data) -> str:
                return (
                    f"日期：{weather_data['date']}\n"
                    f"天气：{weather_data['dayweather']}\n"
                    f"温度：{weather_data['nighttemp']}℃-{weather_data['daytemp']}℃\n"
                    f"风向：{weather_data['daywind']}\n"
                )

            response = requests.get(base_url, params=params, timeout=5)
            data = response.json()
            if data["status"] == "1" and len(data["forecasts"]) > 0:
                print(f"查询{city}天气预报成功")
                weather_all_data = data["forecasts"][0]
                weather_str = f"城市：{weather_all_data['city']}\n"
                weather_list = weather_all_data["casts"]
                for key in weather_list:
                    weather_str += to_get_weather_str(key)
                weather_str += f"更新时间：{weather_all_data['reporttime']}"
                return weather_str
        except Exception as e:
            return f"天气获取异常：{str(e)}"

    def get_current_time(self) -> str:
        """获取时间"""
        print("调用获取时间工具")
        now = datetime.now()
        time_table = "%Y-%m-%d %H:%M:%S"
        zh_time = self.get_current_lunar_str()
        return f"当前时间：{now.strftime(time_table)},当前农历时间：{zh_time}"

    def get_current_lunar_str(self, year=None, month=None, day=None):
        """
        获取指定日期（默认为当前时间）的完整农历写法
        格式示例：甲辰年冬月廿五
        """
        # 1. 默认为当前时间
        if year is None:
            now = datetime.now()
            year, month, day = now.year, now.month, now.day

        # 2. 转换对象
        solar = Solar.fromYmd(year, month, day)
        lunar = solar.getLunar()

        # 3. 获取基础数据
        ganzhi_year = lunar.getYearInGanZhi()  # 甲辰
        lunar_month = lunar.getMonthInChinese()  # 冬
        lunar_day = lunar.getDayInChinese()  # 廿五

        # 4. 【修正点】判断闰月
        # 不直接调用 lunar.isLeap()，而是通过库自带的字符串输出来判断
        # lunar.toString() 会输出类似 "二〇二四年闰二月初一" 的字符串
        is_leap = "闰" in lunar.toString()

        prefix = "闰" if is_leap else ""

        # 5. 拼接结果
        return f"{ganzhi_year}年{prefix}{lunar_month}月{lunar_day}"

    def get_holiday_json(self, name:str) -> str:
        print(f"调用获取节日{name}工具")
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_dir, "config", "holiday.json")

            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise Exception(f"节日资源文件未找到")
        for key in data:
            if data[key]["name"] == name:
                date = data[key]["date"]
                return f"{name}的公历日期为：{date}"
        return "未寻找到该节日"