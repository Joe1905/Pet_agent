import requests
import os
import json
from typing import Any


def save_json_to_file(data: Any, out_dir: str, filename: str, ensure_ascii: bool = False, indent: int = 2) -> str:
    """
    将 JSON 可序列化对象保存到 out_dir/filename（原子写入）。
    返回保存的完整路径。
    """
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)
    tmp_path = out_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
    os.replace(tmp_path, out_path)
    return out_path

if __name__ == "__main__":
    r = requests.get("https://api.jiejiariapi.com/v1/holidays/2026")
    data = r.json()
    print(data)
    save_json_to_file(data,"config", "holiday.json")
