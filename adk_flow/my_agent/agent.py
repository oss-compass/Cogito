# Part of agent.py
import os
from typing import AsyncGenerator
from google.adk.agents import LoopAgent, LlmAgent, SequentialAgent, BaseAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext

# --- 引入本地模块 ---
from .prompt_manager import prompts
from .tools import (
    custom_model_wrapper,
    duckduckgo_search_tool,
    compass_toolset,
    exit_loop,
    COMPLETION_PHRASE
)

# --- 常量 ---
APP_NAME = "compass_report_agent_structured"
STATE_CURRENT_DOC = "current_document"
STATE_CRITICISM = "criticism"

# --- 1. 准备模板 ---
health_report_template = prompts.load("templates/health_report.md")

# --- 2. Agent 定义 ---

# Agent 0: 状态初始化器 (State Initializer)
# 职责: 预先初始化关键状态变量，防止后续 Agent 因读取空变量而崩溃
class StateInitializer(BaseAgent):
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 初始化 criticism 为默认值
        initial_criticism = "等待审查..."
        ctx.session.state[STATE_CRITICISM] = initial_criticism
        
        # 发送事件以更新状态（让 ADK 知道状态已变更）
        yield Event(
            author=self.name, 
            actions=EventActions(state_delta={STATE_CRITICISM: initial_criticism})
        )

state_initializer = StateInitializer(name="StateInitializer")

# Agent 1: 研究与起草 (Research & Draft)
initial_writer_agent = LlmAgent(
    name="ResearchAndDraftAgent",
    model=custom_model_wrapper,
    tools=[duckduckgo_search_tool, compass_toolset],
    instruction=prompts.load("research_draft.txt", template=health_report_template),
    description="Handles intent detection, research, and drafts the initial report based on OSS-Compass data.",
    output_key=STATE_CURRENT_DOC
)

# Agent 2a: 审查员 (Critic)
critic_agent_in_loop = LlmAgent(
    name="ReportCriticAgent",
    model=custom_model_wrapper,
    include_contents='none',
    instruction=prompts.load("critic.txt", completion_phrase=COMPLETION_PHRASE),
    description="Critiques the report for adherence to OSS-Compass values, data integrity, and template structure.",
    output_key=STATE_CRITICISM
)

# Agent 2b: 修改者 (Refiner)
refiner_agent_in_loop = LlmAgent(
    name="ReportRefinerAgent",
    model=custom_model_wrapper,
    include_contents='none',
    instruction=prompts.load("refiner.txt", completion_phrase=COMPLETION_PHRASE),
    description="Refines the report based on criticism or exits the loop.",
    tools=[exit_loop, duckduckgo_search_tool, compass_toolset],
    output_key=STATE_CURRENT_DOC
)

# Agent 2: 循环控制器
refinement_loop = LoopAgent(
    name="RefinementLoop",
    sub_agents=[
        critic_agent_in_loop,
        refiner_agent_in_loop,
    ],
    max_iterations=4
)

# Agent 3: 最终输出
final_output_agent = LlmAgent(
    name="FinalOutputAgent",
    model=custom_model_wrapper,
    include_contents='none',
    instruction=prompts.load("final_output.txt"),
    description="Outputs the final report."
)

# --- 3. 整体流程 ---
root_agent = SequentialAgent(
    name="OSS_Compass_Agent",
    sub_agents=[
        state_initializer,    # Step 0: 初始化状态 (新增)
        initial_writer_agent, # Step 1: Research & Draft
        refinement_loop,      # Step 2: Critique & Refine Loop
        final_output_agent    # Step 3: Final Display
    ],
    description="Standardized OSS-Compass evaluation workflow."
)