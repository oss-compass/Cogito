import datetime
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from mcp import StdioServerParameters
from google.adk.tools.tool_context import ToolContext
import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("API_KEY")
API_BASE = os.getenv("API_BASE")
MCP_API_URL = os.getenv("MCP_API_URL")
MCP_API_KEY = os.getenv("MCP_API_KEY")

# --- 模型配置 ---
# 降低温度以保证报告格式的严谨性, 增加 Token 以容纳长报告
custom_model_wrapper = LiteLlm(
    model="openai/DeepSeek-R1",
    api_base=API_BASE,
    api_key=API_KEY,
    temperature=0.5, 
    top_p=0.8,
    max_tokens=4000,
    frequency_penalty=1.1,
    extra_body={
        "top_k": 20,
    }
)

# --- MCP 工具集 ---

# 1. 搜索工具 (DuckDuckGo via uvx)
duckduckgo_search_tool = MCPToolset(
    connection_params=StdioConnectionParams(
        server_params = StdioServerParameters(
            command='uvx',
            args=["duckduckgo-mcp-server"],
        ),
    ),
    tool_filter=['search', 'fetch_content']
)

# 2. Compass Gitee 工具集 (Compass Server via SSE)
compass_toolset = MCPToolset(
    connection_params=SseConnectionParams(
        url=MCP_API_URL,
    )
)

# --- 自定义工具 ---

def exit_loop(tool_context: ToolContext):
    """仅当评论指出报告已完美且不需要修改时调用。"""
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {}

# --- 辅助常量 ---
CURRENT_DATE = datetime.date.today().strftime("%Y-%m-%d")
COMPLETION_PHRASE = "报告已符合OSS-Compass标准，无进一步修改建议。"