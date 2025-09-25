# -*- coding: utf-8 -*-
# img_upload_server.py
import os
import json
import base64
import httpx
import traceback
import io
import re
from mcp.server import FastMCP
from dotenv import load_dotenv

# --- 依赖库 ---
# 运行此服务前, 请确保已安装以下库:
# pip install python-dotenv httpx matplotlib numpy

# --- 配置 ---
HOST = '0.0.0.0'
PORT = 8004

# --- 初始化 ---

# 加载 .env 文件
script_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(script_dir, '.env')
load_dotenv(dotenv_path=dotenv_path)

# 初始化 FastMCP 服务器
app = FastMCP(
    'python_plotting_tool',
    host=HOST,
    port=PORT
)

# --- 辅助函数 ---
def remove_safe_imports(code: str) -> str:
    """
    从代码字符串中移除常见且安全的导入语句，因为这些库已经预先提供。
    """
    patterns = [
        r"^\s*import\s+matplotlib\.pyplot\s+as\s+plt\s*$",
        r"^\s*import\s+numpy\s+as\s+np\s*$",
        r"^\s*import\s+matplotlib\s*$",
    ]
    for pattern in patterns:
        code = re.sub(pattern, "", code, flags=re.MULTILINE)
    return code

# --- MCP 工具定义 ---

@app.tool()
async def generate_plot_from_python(python_code: str) -> str:
    """
    执行一段 Python 绘图代码 (使用 Matplotlib), 生成图片并上传到图床。

    Args:
        python_code: 包含 Matplotlib 绘图逻辑的 Python 代码字符串。

    Returns:
        一个 JSON 字符串，包含成功后的图片 URL 或失败后的错误信息。
    """
    # --- 安全沙箱环境 ---
    # 为了安全，我们只允许代码访问受限的库和函数
    safe_globals = {
        "__builtins__": {
            "print": print, "range": range, "list": list, "dict": dict, "str": str,
            "int": int, "float": float, "len": len, "abs": abs, "min": min, "max": max,
            "sum": sum, "sorted": sorted, "enumerate": enumerate, "zip": zip,
        },
        "plt": None, # Matplotlib.pyplot
        "np": None,  # Numpy
    }

    # 动态导入安全的库
    try:
        import matplotlib
        matplotlib.use('Agg')  # 使用非交互式后端, 避免 GUI 错误
        import matplotlib.pyplot as plt
        import numpy as np
        
        # 解决中文显示问题：设置支持中文的字体
        # 请确保您的服务器/容器已安装此字体 (例如: sudo apt-get install -y fonts-wqy-zenhei)
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
        plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

        safe_globals["plt"] = plt
        safe_globals["np"] = np
    except ImportError as e:
        return json.dumps({"status": 500, "error": "Server Environment Error", "details": f"Required library not found: {e}"})

    image_buffer = io.BytesIO()

    try:
        # --- 代码执行 ---
        # 预处理用户代码: 移除安全导入和不必要的函数调用
        processed_code = remove_safe_imports(python_code)
        # 禁用用户代码中的 show() 和 savefig()
        processed_code = processed_code.replace("plt.show()", "")
        processed_code = re.sub(r"plt\.savefig\s*\(.*\)", "", processed_code)
        
        # 在安全环境中执行用户的绘图逻辑
        exec(processed_code, safe_globals, {})

        # 在代码执行后，由服务显式保存内存中的当前图表
        plt.savefig(image_buffer, format='png', dpi=150, bbox_inches='tight')

        plt.close('all') # 执行后关闭所有图形，释放内存

        image_buffer.seek(0)
        image_data = image_buffer.read()

        if not image_data:
            raise ValueError("The executed Python code did not generate an image. This might be due to a rendering issue (e.g., fonts not found).")

    except Exception:
        error_details = traceback.format_exc()
        plt.close('all') # 确保即使出错也关闭图形
        return json.dumps({"status": 500, "error": "Python Code Execution Error", "details": error_details})
    
    finally:
        image_buffer.close()

    # --- 图片上传 ---
    api_key = os.getenv("IMGBB_API_KEY")
    if not api_key:
        return json.dumps({"status": 401, "error": "Configuration Error", "details": "IMGBB_API_KEY not found in .env file."})

    upload_url = "https://api.imgbb.com/1/upload"
    payload = {"key": api_key, "image": base64.b64encode(image_data).decode('utf-8')}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(upload_url, data=payload, timeout=30.0)
            response.raise_for_status()
            result = response.json()
            if result.get("success"):
                image_url = result["data"]["url"]
                return json.dumps({"status": 200, "url": image_url})
            else:
                error_message = result.get("error", {}).get("message", "Unknown upload error")
                return json.dumps({"status": 500, "error": "Image Upload Failed", "details": error_message})
        except httpx.RequestError as e:
            return json.dumps({"status": 500, "error": "Network Error", "details": f"Failed to connect to image host: {e}"})


if __name__ == "__main__":
    print("MCP server for Python plotting is running...")
    print(f"Listening on http://{HOST}:{PORT}")
    print("Ensure your .env file contains: IMGBB_API_KEY='your_api_key_here'")
    app.run(transport='sse')

