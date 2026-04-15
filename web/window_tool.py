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

    def execute_action(self, action: str, args: list):
        actions = {
            "get_current_address": self.get_current_address,
            "get_today_weather": self.get_today_weather,
            "get_future_weather": self.get_future_weather,
            "get_current_time": self.get_current_time,
            "get_holiday_json": self.get_holiday_json
        }
        if action in actions:
            # 部分方法不需要参数，部分需要
            # 这里做一个简单的适配
            try:
                if action == "get_current_address" or action == "get_current_time":
                    return actions[action]()
                elif args:
                    return actions[action](*args)
                else:
                    return actions[action]()
            except TypeError as e:
                return f"参数错误: {e}"
        else:
            return f"Web端不支持此操作: {action}"

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

    def get_today_weather(self, city):
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
            if data["status"] == "1" and len(data["lives"]) > 0:
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

    def get_future_weather(self, city):
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

    def get_holiday_json(self, name: str) -> str:
        print(f"调用获取节日{name}工具")
        try:
            # 注意：这里假设 config 目录在 web 目录下，或者需要调整路径
            # 原代码是 os.path.join(base_dir, "config", "holiday.json")
            # 如果 web 目录结构不同，可能需要调整
            # 假设 web 目录下也有 config/holiday.json，或者指向上级目录
            
            # 尝试在当前目录找 config
            base_dir = os.path.dirname(os.path.abspath(__file__))
            full_path = os.path.join(base_dir, "config", "holiday.json")
            
            if not os.path.exists(full_path):
                 # 如果找不到，尝试去 src/config 找（如果是本地运行）
                 # 但为了独立性，最好是部署时把 config 目录也复制过来
                 # 这里先不做跨目录查找，保持独立性
                 pass

            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            return f"节日资源文件未找到: {full_path}"
        except Exception as e:
            return f"读取节日文件出错: {e}"
            
        for key in data:
            if data[key]["name"] == name:
                date = data[key]["date"]
                return f"{name}的公历日期为：{date}"
        return "未寻找到该节日"
