# -*- coding: utf-8 -*-
# compass_model_data_tools.py

import os
import json
import httpx
from typing import Optional
from mcp.server import FastMCP
from dotenv import load_dotenv

# --- 配置 ---
# Gitee Compass API 的基础 URL
# 注意：请根据您的实际情况确认此 URL 是否正确
BASE_URL = "https://compass.gitee.com/"

# --- 初始化 ---

# 加载 .env 文件
script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

# 初始化 FastMCP 服务器为 SSE 模式
app = FastMCP(
    'compass_model_data_tools',
    host='0.0.0.0',
    port=8000
)

# --- 内部辅助函数 ---

async def _fetch_metric_model(
    endpoint: str,
    label: str,
    begin_date: str,
    end_date: str,
    direction: str = "desc",
    page: int = 1,
    size: int = 10,
) -> str:
    """一个通用的辅助函数，用于调用 Gitee Compass 的指标模型 API"""
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
async def get_contributor_milestone_persona(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取项目贡献者里程画像。此画像根据贡献者的长期参与度将其分为临时、常规和核心贡献者。
    Args:
        label: 要查询的仓库地址, 例如 'https://github.com/oss-compass/compass-web-service'。
        begin_date: 查询起始日期, 格式为 'YYYY-MM-DD'。
        end_date: 查询结束日期, 格式为 'YYYY-MM-DD'。
        page: 分页页码, 默认为 1。
        size: 每页数量, 默认为 10。
    Returns:
        包含贡献者里程画像数据的 JSON 字符串。
    """
    return await _fetch_metric_model("api/v2/metricModel/contributorMilestonePersona", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_contributor_role_persona(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取项目贡献者角色画像。此画像区分了组织贡献者和个人贡献者。
    Args:
        label: 要查询的仓库地址, 例如 'https://github.com/oss-compass/compass-web-service'。
        begin_date: 查询起始日期, 格式为 'YYYY-MM-DD'。
        end_date: 查询结束日期, 格式为 'YYYY-MM-DD'。
        page: 分页页码, 默认为 1。
        size: 每页数量, 默认为 10。
    Returns:
        包含贡献者角色画像数据的 JSON 字符串。
    """
    return await _fetch_metric_model("api/v2/metricModel/contributorRolePersona", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_contributor_domain_persona(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取项目贡献者领域画像。此画像根据贡献领域（如代码、Issue、文档等）对贡献者进行分类。
    Args:
        label: 要查询的仓库地址, 例如 'https://github.com/oss-compass/compass-web-service'。
        begin_date: 查询起始日期, 格式为 'YYYY-MM-DD'。
        end_date: 查询结束日期, 格式为 'YYYY-MM-DD'。
        page: 分页页码, 默认为 1。
        size: 每页数量, 默认为 10。
    Returns:
        包含贡献者领域画像数据的 JSON 字符串。
    """
    return await _fetch_metric_model("api/v2/metricModel/contributorDomainPersona", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_organizations_activity(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取项目中的组织活跃度。分析来自不同组织（公司、机构）的贡献情况。
    Args:
        label: 要查询的仓库地址, 例如 'https://github.com/oss-compass/compass-web-service'。
        begin_date: 查询起始日期, 格式为 'YYYY-MM-DD'。
        end_date: 查询结束日期, 格式为 'YYYY-MM-DD'。
        page: 分页页码, 默认为 1。
        size: 每页数量, 默认为 10。
    Returns:
        包含组织活跃度数据的 JSON 字符串。
    """
    return await _fetch_metric_model("api/v2/metricModel/organizationsActivity", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_project_activity(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取项目的整体活跃度指标。包括贡献者数量、提交频率、PR/Issue评论活动等。
    Args:
        label: 要查询的仓库地址, 例如 'https://github.com/oss-compass/compass-web-service'。
        begin_date: 查询起始日期, 格式为 'YYYY-MM-DD'。
        end_date: 查询结束日期, 格式为 'YYYY-MM-DD'。
        page: 分页页码, 默认为 1。
        size: 每页数量, 默认为 10。
    Returns:
        包含项目活跃度评分和相关指标的 JSON 字符串。
    """
    return await _fetch_metric_model("api/v2/metricModel/activity", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_community_service_and_support(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取项目的社区服务与支撑指标。分析 Issue 和 PR 的响应时间、处理效率等。
    Args:
        label: 要查询的仓库地址, 例如 'https://github.com/oss-compass/compass-web-service'。
        begin_date: 查询起始日期, 格式为 'YYYY-MM-DD'。
        end_date: 查询结束日期, 格式为 'YYYY-MM-DD'。
        page: 分页页码, 默认为 1。
        size: 每页数量, 默认为 10。
    Returns:
        包含社区服务与支撑指标的 JSON 字符串。
    """
    return await _fetch_metric_model("api/v2/metricModel/communityServiceAndSupport", label, begin_date, end_date, page=page, size=size)

@app.tool()
async def get_collaboration_development_index(label: str, begin_date: str, end_date: str, page: int = 1, size: int = 10) -> str:
    """
    获取项目的协作开发指数。衡量代码审查、合并率、PR与Issue的关联度等协作效率。
    Args:
        label: 要查询的仓库地址, 例如 'https://github.com/oss-compass/compass-web-service'。
        begin_date: 查询起始日期, 格式为 'YYYY-MM-DD'。
        end_date: 查询结束日期, 格式为 'YYYY-MM-DD'。
        page: 分页页码, 默认为 1。
        size: 每页数量, 默认为 10。
    Returns:
        包含协作开发指数的 JSON 字符串。
    """
    return await _fetch_metric_model("api/v2/metricModel/collaborationDevelopmentIndex", label, begin_date, end_date, page=page, size=size)


if __name__ == "__main__":
    app.run(transport='sse')