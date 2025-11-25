# Cogito

## 📂 模块导航

| 模块 | 目录 | 说明 |
|------|------|------|
| 🔧 MCP 工具箱 | `mcp_serve/` | 提供底层数据支持，包含指标模型、数据清洗及绘图服务。 |
| 🤖 智能体工作流 | `adk_flow/` | 基于 ADK 构建的多智能体协作系统（起草、审查、修改）。 |

## 🚀 快速开始

本项目推荐使用 uv 进行依赖管理。

**全局前置要求**
 - Python 3.10
 - uv
 - Gitee Access Token (用于数据获取)
 - LLM API Key (用于智能体推理)

**一键初始化**

```bash
# 1. 克隆项目
git clone https://github.com/ryan6073/Cogito.git
cd Cogito

# 2. 初始化环境
uv venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 3. 安装所有依赖
uv pip install -r ./mcp_serve/requirements.txt
uv pip install google-adk
uv pip install python-dotenv
```

启动流程请按照以下顺序启动系统：先启动 MCP 数据服务。再启动 ADK 智能体。

License: MIT | Powered by Google ADK & FastMCP