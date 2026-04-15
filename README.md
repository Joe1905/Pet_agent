# Local Pet

A cute cross-platform desktop pet assistant application with AI-powered conversation, tool calling, memory system, and web access mode.

---

一个可爱的跨平台桌面宠物助手应用，支持 AI 智能对话、工具调用、记忆系统和 Web 访问模式。

## 功能特点

### 桌面宠物应用
- 🐾 **多角色宠物**：支持切换不同宠物形象（猫娘、忠犬等），每种角色有独特的性格和对话风格
- 💬 **智能对话**：基于大语言模型的自然语言交互，支持流式响应
- 🔧 **工具调用**：宠物可调用多种工具（闹钟、定时器、天气查询、网页打开等）
- 💾 **记忆系统**：自动摘要聊天内容，记住主人的偏好、爱好和重要日期
- 🎨 **界面定制**：支持自定义宠物外观、名称和对话主题
- 📊 **好感度系统**：通过持续互动提升与宠物的亲密度

### Web 服务
- 🌐 **浏览器访问**：可通过浏览器与宠物互动，适合无桌面环境的场景
- 📱 **响应式设计**：适配不同屏幕尺寸

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        客户端 (Client)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐           ┌─────────────────┐            │
│  │   桌面应用 (PySide6) │         │   Web 前端 (HTML/JS) │        │
│  │                   │           │                     │        │
│  │  ┌─────────────┐  │           │   FastAPI Server    │        │
│  │  │ ChatAgent   │  │           │   (web/server.py)   │        │
│  │  │ (单例模式)   │  │           │                     │        │
│  │  └──────┬──────┘  │           └──────────┬──────────┘        │
│  │         │ HTTP     │                     │                   │
│  │         │ 请求     │                     │ HTTP 代理          │
│  └─────────┼─────────┘                     │                   │
│            │                               │                   │
└────────────┼───────────────────────────────┼───────────────────┘
             │                               │
             ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      服务器端 (Server)                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              FastAPI Server (rag_server.py)              │   │
│  │                                                          │   │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐  │   │
│  │  │   Chat API  │   │   RAG 检索   │   │  Tavily     │  │   │
│  │  │   路由      │   │  (Milvus)    │   │  联网搜索   │  │   │
│  │  └──────┬──────┘   └──────┬──────┘   └──────────────┘  │   │
│  │         │                 │                           │   │
│  │         └────────────┬─────┘                           │   │
│  │                      ▼                                 │   │
│  │              ┌──────────────┐                         │   │
│  │              │   LangChain  │                         │   │
│  │              │   Chain     │                         │   │
│  │              └──────┬──────┘                         │   │
│  │                     │                                │   │
│  └─────────────────────┼──────────────────────────────────┘   │
│                        ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   vLLM (Qwen3-30B)                      │   │
│  │                   本地部署的 LLM 服务                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 技术栈

### 客户端
| 组件 | 技术 | 说明 |
|------|------|------|
| UI 框架 | PySide6 | Qt for Python，跨平台桌面 UI |
| HTTP 客户端 | requests | 与远程服务通信 |
| 自动化工具 | PyAutoGUI | 工具调用中的鼠标键盘操作 |
| 系统工具 | ctypes, subprocess | DPI 感知、系统命令执行 |

### 服务器端
| 组件 | 技术 | 说明 |
|------|------|------|
| Web 框架 | FastAPI | 高性能 Python Web 框架 |
| LLM 推理 | vLLM | Qwen3-30B-A3B-GPTQ-Int4 |
| 向量数据库 | Milvus | RAG 检索增强 |
| Embedding | HuggingFace | all-MiniLM-L6-v2 |
| 提示词框架 | LangChain | Chain 组合与检索 |
| 联网搜索 | Tavily | 实时信息检索 |

## 项目结构

```
local_pet/
├── src/                           # 桌面应用主目录
│   ├── main.py                    # 应用入口，桌面宠物主窗口
│   ├── link_model.py              # 模型连接层
│   │   ├── ChatAgent              # 对话代理（单例模式）
│   │   │   ├── 流式对话处理        # ask_stream() 支持 SSE
│   │   │   ├── 工具调用解析        # XML 标签格式
│   │   │   ├── 记忆摘要更新        # update_history_memory()
│   │   │   └── 系统提示词管理      # update_system_prompt()
│   │   └── LocalLLM              # HTTP 客户端
│   ├── window_tool.py             # 工具执行器（单例模式）
│   │   ├── open_app()             # 启动应用程序
│   │   ├── type_text()            # 模拟键盘输入
│   │   ├── click()                # 鼠标点击
│   │   ├── run_shell()            # 执行 Shell 命令
│   │   ├── press_keys()           # 快捷键操作
│   │   ├── open_url()            # 打开网址
│   │   ├── get_current_address() # 获取当前位置
│   │   ├── get_today_weather()  # 查询今日天气
│   │   ├── get_future_weather() # 查询天气预报
│   │   ├── get_current_time()   # 获取当前时间
│   │   └── get_holiday_json()   # 查询农历节日
│   ├── file_load.py               # 资源配置加载器
│   │   └── ResourceExtractor     # 处理打包后的资源路径
│   ├── string_manager.py          # 多语言字符串管理
│   ├── logger.py                  # 日志模块
│   ├── ai_agent.py               # AI Agent（预留）
│   ├── config/                   # 配置文件
│   │   ├── setting.ini           # 主配置
│   │   │   ├── [Url]             # 服务器地址
│   │   │   ├── [SessionID]       # 会话标识
│   │   │   ├── [General_Set]     # 当前宠物索引
│   │   │   ├── [Memory]          # 记忆存储
│   │   │   └── [Nick_Name]       # 宠物昵称
│   │   ├── pet_config_private.ini # 宠物外观配置
│   │   ├── string_table.json     # 对话模板与角色定义
│   │   └── holiday.json          # 节日数据
│   ├── ui/                       # UI 模块
│   │   ├── mainUi.py             # 主窗口 UI
│   │   ├── chat_ui.py           # 聊天界面
│   │   ├── favor.py              # 好感度管理
│   │   ├── login.py              # 登录窗口
│   │   ├── memoryDialog.py       # 记忆编辑
│   │   ├── messageInfo.py        # 消息列表模型
│   │   ├── messageUi.py          # 消息气泡组件
│   │   └── loadingUi.py          # 加载动画覆盖层
│   ├── pet_image/               # 宠物动画资源
│   │   └── model1.gif            # 宠物 GIF 动画
│   └── package.bat              # Nuitka 打包脚本
│
├── backend/                      # 服务器端代码
│   └── rag-milvus-project/
│       ├── rag_server.py         # FastAPI 主服务
│       │   ├── /chat             # 对话接口（支持流式）
│       │   ├── /clear_history    # 清理会话历史
│       │   └── /debug_history    # 调试接口
│       ├── rag_chat.py           # RAG Chain 实现
│       ├── ingest_data.py        # 向量数据导入
│       ├── milvus_demo.db        # SQLite 元数据存储
│       ├── system_prompt.json    # 系统提示词配置
│       └── requirements.txt      # Python 依赖
│
├── web/                          # Web 前端
│   ├── server.py                 # FastAPI 服务
│   │   ├── /api/config          # 获取配置
│   │   ├── /api/favor/list       # 宠物列表与好感度
│   │   ├── /api/favor/select     # 切换宠物
│   │   └── /api/favor/reset      # 重置设置
│   ├── index.html                # 主页面
│   ├── components.js             # 前端组件
│   ├── window_tool.py           # Web 版工具
│   └── config/                   # Web 配置
│
├── README.md
└── .gitignore
```

## 核心模块详解

### ChatAgent 对话流程

```
用户输入
    │
    ▼
┌─────────────────────────────────────┐
│  1. 检查是否包含图片                 │
│     - 提取 <question>image:path</question>
│     - Base64 编码后发送到服务器       │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  2. 发送请求到 vLLM 服务器           │
│     POST /chat                      │
│     - question: 用户问题            │
│     - session_id: 会话标识          │
│     - character: 当前角色 Key       │
│     - memory: 记忆上下文            │
│     - image: Base64 图片数据        │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  3. 解析流式响应                    │
│     - <think> 思考过程              │
│     - <tool> 工具调用指令          │
│     - <observation> 工具返回结果   │
│     - <final answer> 最终回答      │
└─────────────────┬───────────────────┘
                  │
          ┌───────┴───────┐
          ▼               ▼
┌─────────────┐   ┌─────────────┐
│ 需要工具    │   │ 直接回答    │
│ 调用        │   │             │
└──────┬──────┘   └──────┬──────┘
       ▼                 │
┌─────────────┐          │
│ WindowTool  │          │
│ 执行工具    │          │
└──────┬──────┘          │
       ▼                 │
       └────────┬────────┘
                ▼
        显示最终回答
```

### 工具调用协议

宠物使用 XML 标签与后端通信，示例：

```
# 需要设置闹钟时
<tool>to_set_clock_alarm("06:30")</tool>

# 工具执行后返回
<observation>闹钟已设置为 06:30</observation>

# 最终回答
<final answer>已经为您设好闹钟了喵~ 记得准时起床哦！</final answer>
```

### 记忆系统

```
┌─────────────┐     定时触发      ┌─────────────┐
│  聊天记录   │ ──────────────▶   │  LLM 摘要   │
│  (logs/*.txt)│                  │  提取爱好等  │
└─────────────┘                  └──────┬──────┘
                                       │
                                       ▼
                              ┌─────────────┐
                              │ setting.ini │
                              │ [Memory]    │
                              │ current_     │
                              │ memory       │
                              └─────────────┘
```

## 配置说明

### 客户端配置 (src/config/setting.ini)

```ini
[Url]
server_url = http://101.43.33.48:43351  # 远程 vLLM 服务器地址

[SessionID]
id = "user001"                          # 会话唯一标识

[General_Set]
current_index = 2                        # 当前宠物索引 (1=六白, 2=七瑞)

[Nick_Name]
nickname1 = 六白                         # 宠物昵称
nickname2 = 七瑞

[Memory]
current_memory = 主人：喜欢羽毛球；讨厌西红柿  # 记忆摘要
current_file =                          # 当前日志文件索引
```

### 角色配置 (src/config/string_table.json)

| Key | 说明 |
|-----|------|
| `Character_1` | 猫娘角色：傲娇但内心温柔，银白毛发碧蓝瞳孔 |
| `Character_2` | 忠犬角色：敦厚柔软，黑色毛发金色瞳孔 |
| `Extra_Rule` | 通用规则：工具调用格式、思考流程 |
| `New_Character_*` | Web 端简化角色定义 |
| `Summary_Prompt` | 记忆摘要提取的提示词模板 |

## 运行方式

### 环境要求

- Python 3.8+
- Conda 环境（推荐）
- Windows 10/11（桌面应用）
- 网络可达远程服务器

### 桌面应用

```bash
# 激活 Conda 环境
conda activate local_pet

# 进入 src 目录
cd src

# 运行应用
python main.py
```

### Web 服务

```bash
# 进入 web 目录
cd web

# 安装依赖
pip install -r requirements.txt

# 运行服务
python server.py

# 访问 http://localhost:8000
```

### 后端服务（服务器部署）

```bash
cd backend/rag-milvus-project

# 启动 vLLM（需提前部署）
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen3-30B-A3B-GPTQ-Int4 \
    --host localhost --port 8001

# 启动 RAG 服务
python rag_server.py
```

## 构建打包

```bash
cd src

# 运行打包脚本（需在 Conda 环境）
python package.bat

# 打包产物位于 build/main.dist/main.exe
```

打包配置：
- `--standalone`: 独立打包，包含所有依赖
- `--enable-plugin=pyside6`: 启用 PySide6 插件
- `--windows-console-mode=force`: 保留控制台（调试用）
- `--lto=yes`: 链接时优化

## 依赖列表

### 客户端 (src/requirements.txt)
```
PySide6>=6.5.0
requests>=2.28.0
pyautogui>=0.4.14
pygetwindow>=0.0.9
lunar-python>=1.15
chardet>=4.0.0
```

### 后端 (backend/rag-milvus-project/requirements.txt)
```
fastapi>=0.100.0
uvicorn>=0.23.0
langchain>=0.1.0
langchain-community>=0.0.10
langchain-openai>=0.0.2
langchain-huggingface>=0.0.1
langchain-milvus>=0.0.1
pymilvus>=2.3.0
huggingface-hub>=0.19.0
tavily-python>=0.3.0
```

### Web (web/requirements.txt)
```
fastapi>=0.100.0
uvicorn>=0.23.0
```

## 许可证

MIT License
