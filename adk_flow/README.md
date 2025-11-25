# 🤖 Cogito 智能体工作流 (ADK Flow)

本目录包含基于 **Google ADK** 构建的核心业务逻辑。我们采用 **"起草-审查-修改" (Draft-Critic-Refine)** 的闭环模式，确保生成的评估报告既客观又专业。

-----

## 🧠 设计模式

我们使用了 ADK 的以下原语构建系统：

  * **Sequential Pipeline (序列管道):** 定义了从 `初始化` -\> `起草` -\> `优化循环` -\> `输出` 的线性主流程。
  * **Iterative Refinement (迭代优化):** 在优化阶段，引入 **LoopAgent**，让审查员和修改者反复打磨报告，直到满足标准。

-----

## 👥 智能体角色

| 智能体类名 | 职责 | 工具权限 |
| :--- | :--- | :--- |
| **🕵️ ResearchAndDraftAgent**<br>(起草者) | 意图识别、仓库搜索、初稿撰写 | Google Search, Compass Metrics |
| **⚖️ ReportCriticAgent**<br>(审查员) | 检查数据真实性、价值观、格式规范 | 无 (纯文本分析) |
| **✍️ ReportRefinerAgent**<br>(修改者) | 根据意见修改报告，决定是否结束循环 | Google Search, Compass Metrics, `exit_loop` |
| **📤 FinalOutputAgent**<br>(输出者) | 向用户展示最终定稿 | 无 |

-----

## 📂 目录结构

  * **`my_agent/`**: 智能体源码
      * `agent.py`: 核心编排逻辑。
      * `tools.py`: 工具集配置与 MCP 客户端连接。
      * `prompts/`: **[关键]** 所有的 System Instructions 和 Markdown 模板都在这里，方便非程序员调整 Prompt。

-----

## 🚀 运行智能体

确保 MCP 服务已在后台运行 (端口 9001)，然后启动 Web UI：

```bash
# 在 adk_flow 目录下
adk web --port 9000
```

-----
