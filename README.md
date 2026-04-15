# Local Pet

一个可爱的桌面宠物助手应用，基于 PySide6 构建的 AI 聊天机器人。

## 功能特点

- 🐾 桌面宠物形象，交互式界面
- 💬 AI 智能对话功能
- 🔐 登录系统
- 💾 记忆与偏好设置
- 🎨 可自定义的宠物外观

## 技术栈

- **桌面应用**: Python 3 + PySide6 (Qt for Python)
- **AI 对话**: 连接远程 vLLM 部署的大模型
- **后端服务**: Python（部署在服务器上，提供 RAG + Milvus 向量数据库支持）
- **Web 前端**: 原生 HTML/CSS/JS

## 项目结构

```
local_pet/
├── src/                    # 桌面应用源代码
│   ├── main.py            # 应用入口
│   ├── ai_agent.py        # AI Agent
│   ├── link_model.py      # 模型连接（连接远程 vLLM）
│   ├── file_load.py       # 文件加载
│   ├── window_tool.py     # 窗口工具
│   ├── config/            # 配置文件（远程服务器地址）
│   └── ui/               # UI 模块
├── backend/               # 后端服务（部署在服务器上）
│   └── rag-milvus-project/  # RAG + Milvus 向量数据库
├── web/                   # Web 前端
└── README.md
```

## 运行方式

### 桌面应用

```bash
cd src
python main.py
```

### Web 服务

```bash
cd web
python server.py
```

## 构建打包

```bash
cd src
python package.bat
```

## 配置

配置文件位于 `src/config/` 目录，主要配置项包括：
- **远程服务器地址**: `setting.ini` 中配置连接远程 vLLM 服务的地址
- 宠物外观设置
- 用户偏好

> 注意：桌面应用通过网络连接服务器上的 vLLM 大模型和后端服务，请确保网络互通。

## 许可证

MIT License
