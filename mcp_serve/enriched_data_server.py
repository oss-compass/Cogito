# enriched_data_server.py

import os
import json
import httpx
from typing import Optional
from mcp.server import FastMCP
from dotenv import load_dotenv

# --- 配置 ---
# Gitee Compass API 的基础 URL
# BASE_URL = "https://compass.gitee.com/"
BASE_URL = "https://oss-compass.isrc.ac.cn"

# --- 初始化 ---

# 加载 .env 文件 (确保 .env 文件在项目根目录)
script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

# 初始化 FastMCP 服务器为 SSE 模式
# 新服务名: compass_enriched_data_tools
# 新端口: 8001
app = FastMCP(
    'compass_enriched_data_tools',
    host='0.0.0.0',
    port=8001
)

# --- 内部辅助函数 ---

async def _post_request_to_compass(
    endpoint: str,
    label: str,
    begin_date: str,
    end_date: str,
    direction: str = "desc",
    page: int = 1,
    size: int = 10,
) -> str:
    """一个通用的辅助函数，用于调用 Gitee Compass 的 enriched data API"""
    full_url = os.path.join(BASE_URL, endpoint)
    token = os.getenv("GITEE_ACCESS_TOKEN")

    if not token:
        return json.dumps({"status": 401, "error": "Access token not found in .env file."})

    payload = {
        "access_token": token,
        "label": label,
        "direction": direction,
        "begin_date": begin_date,
        "end_date": end_date,
        "page": page,
        "size": size,
    }
    headers = {"Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url=full_url, headers=headers, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.text
        except httpx.HTTPStatusError as e:
            return json.dumps({"status": e.response.status_code, "error": "HTTP Error", "details": e.response.text})
        except httpx.RequestError as e:
            return json.dumps({"status": 500, "error": "Request Failed", "details": str(e)})

# --- MCP 工具定义 ---

@app.tool()
async def get_fork_enriched_data(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取 GitHub/Gitee 仓库的 fork enriched(丰富)数据。提供了关于谁、在何时 fork 了仓库的详细信息。
    Args:
        label: 要查询的仓库地址, 例如 'https://github.com/oss-compass/compass-web-service'。
        begin_date: 查询起始日期, 格式为 'YYYY-MM-DD'。
        end_date: 查询结束日期, 格式为 'YYYY-MM-DD'。
        page: 分页页码, 默认为 1。
        size: 每页数量, 默认为 10。
    Returns:
        包含 fork enriched 数据的 JSON 字符串。
    """
    return await _post_request_to_compass("api/v2/fork/search", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_pull_event_enriched_data(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取 GitHub/Gitee 的 pull request event enriched(丰富)数据。包含 PR 被合并、关闭、评论等事件的详细信息。
    Args:
        label: 要查询的仓库地址。
        begin_date: 查询起始日期。
        end_date: 查询结束日期。
        page: 分页页码。
        size: 每页数量。
    Returns:
        包含 pull request event enriched 数据的 JSON 字符串。
    """
    # 注意: 根据您的文档，原始路径为 'pull_envet', 这里已修正为 'pull_event'
    return await _post_request_to_compass("api/v2/pull_event/search", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_git_commit_enriched_data(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取 GitHub/Gitee 的 git commit enriched(丰富)数据。提供每次代码提交的详细信息，包括作者、提交者、代码增删行数等。
    Args:
        label: 要查询的仓库地址。
        begin_date: 查询起始日期。
        end_date: 查询结束日期。
        page: 分页页码。
        size: 每页数量。
    Returns:
        包含 git commit enriched 数据的 JSON 字符串。
    """
    return await _post_request_to_compass("api/v2/git/search", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_issue_enriched_data(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取 GitHub/Gitee 的 issue enriched(丰富)数据。提供关于 issue 创建、状态变更、分配人等的详细信息。
    Args:
        label: 要查询的仓库地址。
        begin_date: 查询起始日期。
        end_date: 查询结束日期。
        page: 分页页码。
        size: 每页数量。
    Returns:
        包含 issue enriched 数据的 JSON 字符串。
    """
    return await _post_request_to_compass("api/v2/issue/search", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_pull_request_enriched_data(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取 GitHub/Gitee 的 pull request enriched(丰富)数据。提供 PR 的详细元数据，包括创建者、合并者、状态、标签等。
    Args:
        label: 要查询的仓库地址。
        begin_date: 查询起始日期。
        end_date: 查询结束日期。
        page: 分页页码。
        size: 每页数量。
    Returns:
        包含 pull request enriched 数据的 JSON 字符串。
    """
    return await _post_request_to_compass("api/v2/metadata/pullRequests", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_repo_enriched_data(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取 GitHub/Gitee 的 repository enriched(丰富)数据。提供仓库的综合信息，如 star 数、fork 数、订阅数、版本发布历史等。
    Args:
        label: 要查询的仓库地址。
        begin_date: 查询起始日期。
        end_date: 查询结束日期。
        page: 分页页码。
        size: 每页数量。
    Returns:
        包含 repository enriched 数据的 JSON 字符串。
    """
    return await _post_request_to_compass("api/v2/repo/search", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_stargazer_enriched_data(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取 GitHub/Gitee 的 stargazer (点赞者) enriched(丰富)数据。提供关于谁、在何时 star 了仓库的详细信息。
    Args:
        label: 要查询的仓库地址。
        begin_date: 查询起始日期。
        end_date: 查询结束日期。
        page: 分页页码。
        size: 每页数量。
    Returns:
        包含 stargazer enriched 数据的 JSON 字符串。
    """
    return await _post_request_to_compass("api/v2/stargazer/search", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_watch_enriched_data(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取 GitHub/Gitee 的 watch (关注者) enriched(丰富)数据。提供关于谁、在何时 watch 了仓库的详细信息。
    Args:
        label: 要查询的仓库地址。
        begin_date: 查询起始日期。
        end_date: 查询结束日期。
        page: 分页页码。
        size: 每页数量。
    Returns:
        包含 watch enriched 数据的 JSON 字符串。
    """
    return await _post_request_to_compass("api/v2/watch/search", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_releases_enriched_data(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取 GitHub/Gitee 的 releases (版本发布) enriched(丰富)数据。提供仓库所有版本发布的详细列表。
    Args:
        label: 要查询的仓库地址。
        begin_date: 查询起始日期。
        end_date: 查询结束日期。
        page: 分页页码。
        size: 每页数量。
    Returns:
        包含 releases enriched 数据的 JSON 字符串。
    """
    return await _post_request_to_compass("api/v2/releases/search", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_github_event_data(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取原始的 GitHub Event 数据。这包括了推送(PushEvent)、创建(CreateEvent)等多种类型的事件。
    Args:
        label: 要查询的仓库地址。
        begin_date: 查询起始日期。
        end_date: 查询结束日期。
        page: 分页页码。
        size: 每页数量。
    Returns:
        包含 GitHub event 数据的 JSON 字符串。
    """
    return await _post_request_to_compass("api/v2/event/search", label, begin_date, end_date, page=page, size=size)
    
@app.tool()
async def get_github_repo_event_data(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取 GitHub 仓库级别的 Event 聚合数据。提供了按时间段聚合的贡献统计，如推送贡献、PR贡献、Issue贡献等。
    Args:
        label: 要查询的仓库地址。
        begin_date: 查询起始日期。
        end_date: 查询结束日期。
        page: 分页页码。
        size: 每页数量。
    Returns:
        包含 GitHub repo event 数据的 JSON 字符串。
    """
    return await _post_request_to_compass("api/v2/repo_event/search", label, begin_date, end_date, page=page, size=size)


if __name__ == "__main__":
    app.run(transport='sse')