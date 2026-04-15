
import os
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import uvicorn
import json
import asyncio
import requests
import base64
import shutil
import re
import configparser

# 获取当前文件所在目录
current_dir = Path(__file__).parent

# --- 配置 ---
# 修改为中间层 FastAPI 的地址
MIDDLEWARE_API_URL = os.getenv("MIDDLEWARE_API_URL", "http://101.43.33.48:34223/chat")

app = FastAPI()

# --- CORS 配置 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 静态文件服务 ---
# 允许访问 web 目录下的静态文件（如图片、css）
app.mount("/static", StaticFiles(directory=str(current_dir)), name="static")

# --- 配置读取 ---
def get_config_parser(filename):
    config = configparser.ConfigParser()
    path = current_dir / "config" / filename
    if path.exists():
        config.read(path, encoding='utf-8')
    return config, path

def get_pet_head_url():
    try:
        setting_config, _ = get_config_parser("setting_config.ini")
        current_index = setting_config.get("General_Set", "current_index", fallback="1")
        
        pet_config, _ = get_config_parser("pet_config_private.ini")
        section = f"Pet{current_index}"
        if pet_config.has_section(section):
            pet_head_raw = pet_config.get(section, "pet_head", fallback=":/head/liubai.png")
            if pet_head_raw.startswith(":/head/"):
                filename = pet_head_raw.split("/")[-1]
                return f"/static/assets/{filename}"
            
        return "/static/assets/liubai.png"
    except Exception as e:
        print(f"Error reading config: {e}")
        return "/static/assets/liubai.png"

@app.get("/api/config")
async def get_config():
    return {
        "pet_head": get_pet_head_url()
    }

# --- Favor 接口 ---
@app.get("/api/favor/list")
async def get_favor_list():
    try:
        pet_config, _ = get_config_parser("pet_config_private.ini")
        setting_config, _ = get_config_parser("setting_config.ini")
        current_index = setting_config.get("General_Set", "current_index", fallback="1")
        
        pets = []
        for section in pet_config.sections():
            if section.startswith("Pet"):
                index = pet_config.get(section, "index")
                pet_head_raw = pet_config.get(section, "pet_head", fallback=":/head/liubai.png")
                head_url = "/static/assets/liubai.png"
                if pet_head_raw.startswith(":/head/"):
                    filename = pet_head_raw.split("/")[-1]
                    head_url = f"/static/assets/{filename}"
                
                # 获取好感度
                # 格式：Talk_Times 节下的 pet_{index}
                favor = 0
                if setting_config.has_section("Talk_Times"):
                    favor = setting_config.getint("Talk_Times", f"pet_{index}", fallback=0)
                
                pets.append({
                    "index": int(index),
                    "head": head_url,
                    "favor": favor # 新增好感度字段
                })
        
        # 按 index 排序
        pets.sort(key=lambda x: x["index"])
        
        return {
            "current_index": int(current_index),
            "pets": pets
        }
    except Exception as e:
        return {"error": str(e)}

class SelectPetRequest(BaseModel):
    index: int

@app.post("/api/favor/select")
async def select_pet(request: SelectPetRequest):
    try:
        setting_config, path = get_config_parser("setting_config.ini")
        if not setting_config.has_section("General_Set"):
            setting_config.add_section("General_Set")
        
        setting_config.set("General_Set", "current_index", str(request.index))
        
        with open(path, 'w', encoding='utf-8') as f:
            setting_config.write(f)
            
        return {"status": "success", "new_head": get_pet_head_url()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/favor/reset")
async def reset_settings():
    try:
        # 重置逻辑：
        # 1. 将 current_index 重置为 1
        # 2. 清空 Memory
        # 3. 重置好感度 Talk_Times
        
        setting_config, path = get_config_parser("setting_config.ini")
        
        if not setting_config.has_section("General_Set"):
            setting_config.add_section("General_Set")
        setting_config.set("General_Set", "current_index", "1")
        
        if not setting_config.has_section("Memory"):
            setting_config.add_section("Memory")
        setting_config.set("Memory", "current_memory", "")
        
        # 重置好感度
        if setting_config.has_section("Talk_Times"):
            setting_config.remove_section("Talk_Times")
            setting_config.add_section("Talk_Times")
        
        with open(path, 'w', encoding='utf-8') as f:
            setting_config.write(f)
            
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Memory 接口 ---
@app.get("/api/memory")
async def get_memory():
    try:
        setting_config, _ = get_config_parser("setting_config.ini")
        memory = setting_config.get("Memory", "current_memory", fallback="")
        return {"memory": memory}
    except Exception as e:
        return {"error": str(e)}

class MemoryRequest(BaseModel):
    memory: str

@app.post("/api/memory")
async def save_memory(request: MemoryRequest):
    try:
        setting_config, path = get_config_parser("setting_config.ini")
        if not setting_config.has_section("Memory"):
            setting_config.add_section("Memory")
        
        setting_config.set("Memory", "current_memory", request.memory)
        
        with open(path, 'w', encoding='utf-8') as f:
            setting_config.write(f)
            
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 处理 /favicon.ico 请求
@app.get("/favicon.ico")
async def favicon():
    return File(str(current_dir / "assets" / "favicon.ico"))

class ChatRequest(BaseModel):
    question: str
    image: Optional[str] = None # Base64 编码的图片

async def stream_generator(question: str, image_base64: Optional[str] = None):
    """
    生成器函数，用于流式返回数据给前端
    """
    
    # 读取当前角色和记忆
    try:
        setting_config, _ = get_config_parser("setting_config.ini")
        current_index = setting_config.get("General_Set", "current_index", fallback="1")
        character_key = f"New_Character_{current_index}"
        
        memory = setting_config.get("Memory", "current_memory", fallback="")
        model_memory = f"#历史记忆#\n{memory}\n" if memory else ""
    except:
        character_key = "New_Character_1"
        model_memory = ""
    
    payload = {
        "question": question,
        "character": character_key,
        "memory": model_memory
    }
    
    if image_base64:
        if not image_base64.startswith("data:image"):
            image_url = f"data:image/jpeg;base64,{image_base64}"
        else:
            image_url = image_base64
        payload["image"] = image_url

    # 日志：打印输入 Payload
    print(f"\n[LLM Input] Payload: {json.dumps({k: v for k, v in payload.items() if k != 'image'}, ensure_ascii=False)}")
    if "image" in payload:
        print(f"[LLM Input] Image data length: {len(payload['image'])}")

    try:
        with requests.post(MIDDLEWARE_API_URL, json=payload, stream=True) as response:
            if response.status_code != 200:
                error_msg = f"Server Error: {response.text}"
                print(f"[LLM Error] {error_msg}")
                yield f"data: {json.dumps({'error': error_msg})}\n\n"
                return

            # 缓冲区，用于处理被切断的标签
            buffer = ""
            
            print("[LLM Output Stream Start]")
            
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    # 日志：打印原始 chunk
                    print(chunk, end="", flush=True)
                    
                    buffer += chunk
                    
                    # 简化逻辑：累积数据，直到遇到完整标签或流结束
                    
                    # 1. 移除 <think>...</think>
                    while "<think>" in buffer and "</think>" in buffer:
                        start = buffer.find("<think>")
                        end = buffer.find("</think>") + len("</think>")
                        # 发送 <think> 之前的内容
                        if start > 0:
                            yield f"data: {json.dumps({'content': buffer[:start]})}\n\n"
                        # 丢弃 <think>...</think>
                        buffer = buffer[end:]
                    
                    # 2. 如果只有 <think> 没有 </think>，说明还在思考中，保留 buffer 不发送
                    if "<think>" in buffer:
                        # 发送 <think> 之前的内容（如果有）
                        start = buffer.find("<think>")
                        if start > 0:
                            yield f"data: {json.dumps({'content': buffer[:start]})}\n\n"
                            buffer = buffer[start:]
                        continue # 继续累积数据
                        
                    # 3. 提取 <final answer>...</final answer>
                    # 关键修改：检测到 </final answer> 时，停止发送并移除标签
                    while "<final answer>" in buffer:
                        start = buffer.find("<final answer>") + len("<final answer>")
                        
                        # 检查是否有闭合标签
                        if "</final answer>" in buffer:
                            end = buffer.find("</final answer>")
                            # 提取内容（不包含标签）
                            content = buffer[start:end]
                            yield f"data: {json.dumps({'content': content})}\n\n"
                            
                            # 丢弃已处理部分（包括闭合标签）
                            buffer = buffer[end + len("</final answer>"):]
                        else:
                            # 没有闭合标签，检查是否有闭合标签的前缀
                            # 如果 buffer 结尾可能是 </final answer> 的一部分，则保留这部分不发送
                            # 否则发送内容
                            
                            content_to_send = buffer[start:]
                            
                            # 检查结尾是否可能是闭合标签的前缀
                            possible_tag = False
                            for i in range(1, len("</final answer>") + 1):
                                if content_to_send.endswith("</final answer>"[:i]):
                                    possible_tag = True
                                    # 发送除了潜在标签前缀之外的内容
                                    safe_content = content_to_send[:-i]
                                    if safe_content:
                                        yield f"data: {json.dumps({'content': safe_content})}\n\n"
                                    # 更新 buffer，只保留 <final answer> + 潜在前缀
                                    # 这样下次循环可以继续匹配
                                    buffer = buffer[:start] + content_to_send[-i:]
                                    break
                            
                            if not possible_tag:
                                # 安全，直接发送
                                yield f"data: {json.dumps({'content': content_to_send})}\n\n"
                                # 更新 buffer，只保留 <final answer> 标签本身，以便下次继续定位
                                buffer = buffer[:start]
                            
                            break # 跳出 while，等待更多数据

                    # 4. 如果既不在 think 也不在 final answer
                    # 检查 buffer 结尾是否可能是标签的一部分
                    if buffer.endswith("<") or \
                       (buffer.endswith("t") and "<" in buffer) or \
                       (buffer.endswith("th") and "<" in buffer) or \
                       (buffer.endswith("thi") and "<" in buffer) or \
                       (buffer.endswith("thin") and "<" in buffer) or \
                       (buffer.endswith("think") and "<" in buffer) or \
                       (buffer.endswith("f") and "<" in buffer) or \
                       (buffer.endswith("fi") and "<" in buffer) or \
                       (buffer.endswith("fin") and "<" in buffer) or \
                       (buffer.endswith("fina") and "<" in buffer) or \
                       (buffer.endswith("final") and "<" in buffer):
                        pass # 等待更多数据
                    else:
                        # 如果 buffer 里没有 <think> 也没有 <final answer>，直接发送
                        if "<" not in buffer:
                             yield f"data: {json.dumps({'content': buffer})}\n\n"
                             buffer = ""
                        else:
                             # 有 < 但不是我们关心的标签，可能是普通文本包含 <
                             pass
                    
                    await asyncio.sleep(0)
            
            print("\n[LLM Output Stream End]")
            
            # 循环结束后，如果缓冲区还有内容，做最后一次清理和发送
            if buffer:
                # 如果还在 think 中，说明 think 没闭合，丢弃
                if "<think>" in buffer:
                    pass 
                # 如果在 final answer 中，发送剩余部分（不包含标签）
                elif "<final answer>" in buffer:
                    start = buffer.find("<final answer>") + len("<final answer>")
                    content = buffer[start:]
                    # 如果残留了闭合标签的一部分，去掉它
                    # 这里简单处理，假设最后残留的是 </final answer> 的前缀
                    # 但实际上流结束了，说明标签没闭合，直接发送内容即可
                    yield f"data: {json.dumps({'content': content})}\n\n"
                # 其他内容直接发送
                else:
                    yield f"data: {json.dumps({'content': buffer})}\n\n"
                    
    except Exception as e:
        print(f"\n[LLM Exception] {str(e)}")
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    return StreamingResponse(
        stream_generator(request.question, request.image),
        media_type="text/event-stream"
    )

@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    """
    接收上传的图片，保存到 web/uploads 目录，并返回访问 URL
    """
    upload_dir = current_dir / "uploads"
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 返回图片的 Base64 编码，方便前端直接用于聊天
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        
    return {
        "filename": file.filename,
        "url": f"/static/uploads/{file.filename}",
        "base64": f"data:image/jpeg;base64,{encoded_string}"
    }

if __name__ == "__main__":
    print("启动 Web 后端服务器在 http://0.0.0.0:8020")
    uvicorn.run(app, host="0.0.0.0", port=8020)
