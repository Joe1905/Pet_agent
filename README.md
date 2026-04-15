# Local Pet

一个可爱的桌面宠物助手应用，基于 PySide6 构建的 AI 聊天机器人。

## 功能特点

- 🐾 桌面宠物形象，交互式界面
- 💬 AI 智能对话功能
- 🔐 登录系统
- 💾 记忆与偏好设置
- 🎨 可自定义的宠物外观

## 技术栈

- **后端**: Python 3
- **UI 框架**: PySide6 (Qt for Python)
- **AI**: OpenAI API / 本地模型支持
- **向量数据库**: Milvus (RAG 支持)

## 项目结构

```
local_pet/
├── src/                    # 主源代码
│   ├── main.py            # 应用入口
│   ├── ai_agent.py        # AI Agent
│   ├── link_model.py      # 模型连接
│   ├── file_load.py       # 文件加载
│   ├── window_tool.py     # 窗口工具
│   ├── config/            # 配置文件
│   └── ui/               # UI 模块
├── backend/               # 后端服务
│   └── rag-milvus-project/
├── web/                   # Web 前端
├── use_api.bat           # API 调用脚本
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

配置文件位于 `src/config/` 目录，请根据需要配置：
- AI 模型 API 密钥
- 宠物外观设置
- 用户偏好

## 许可证

MIT License
