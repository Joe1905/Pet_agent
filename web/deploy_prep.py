
import os
import shutil
from pathlib import Path

# 定义路径
project_root = Path(__file__).parent.parent
web_dir = project_root / "web"
assets_dir = web_dir / "assets"
config_dir = web_dir / "config"
src_images_dir = project_root / "src" / "ui" / "images"
src_config_dir = project_root / "src" / "config"
src_root = project_root / "src"

# 创建 assets 目录
if not assets_dir.exists():
    assets_dir.mkdir()
    print(f"Created directory: {assets_dir}")

# 复制 config 目录
if src_config_dir.exists():
    if config_dir.exists():
        shutil.rmtree(config_dir)
    shutil.copytree(src_config_dir, config_dir)
    print(f"Copied config directory to {config_dir}")
else:
    print(f"Warning: Source config directory not found: {src_config_dir}")

# 复制文件
# 策略修改：复制 src/ui/images 下的所有 png 和 gif 文件到 assets
# 这样可以确保 liubai.png, qirui.png 等都在
if src_images_dir.exists():
    for file in src_images_dir.glob("*"):
        if file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif']:
            shutil.copy(file, assets_dir / file.name)
            print(f"Copied {file.name} to assets")

# 单独复制 ico
if (src_root / "chat.ico").exists():
    shutil.copy(src_root / "chat.ico", assets_dir / "favicon.ico")
    print("Copied chat.ico to favicon.ico")

# 创建 requirements.txt
requirements = """
fastapi
uvicorn
python-multipart
requests
lunar_python
"""

with open(web_dir / "requirements.txt", "w") as f:
    f.write(requirements.strip())
    print(f"Created requirements.txt at {web_dir}")

print("Deployment preparation complete.")
