# -*- coding: utf-8 -*-
"""
工具调用路由器 - 简化版智能代理系统
====================================

本模块演示了如何使用 LangGraph 构建一个简化的工具调用路由器系统。
与 agent.py 相比，这个版本更加简洁，专注于展示工具调用的基本流程。

主要特点：
1. 单一工具（乘法计算）
2. 简化的图结构（工具执行后直接结束）
3. 清晰的条件路由逻辑
4. 适合初学者理解工具调用的核心概念

技术栈：
- LangChain: 大语言模型集成框架
- LangGraph: 状态图构建和编排框架
- OpenAI GPT-4: 大语言模型
"""

# 导入必要的模块
from langchain_openai import ChatOpenAI  # OpenAI聊天模型接口
from langgraph.graph import MessagesState  # 消息状态类型
from langgraph.graph import StateGraph, START, END  # 图构建核心组件
from langgraph.prebuilt import ToolNode, tools_condition  # 预构建的工具相关组件

# ==================== 工具定义 ====================

def multiply(a: int, b: int) -> int:
    """
    乘法计算工具
    
    功能：计算两个整数的乘积
    用途：处理用户提出的乘法运算需求
    
    Args:
        a (int): 被乘数
        b (int): 乘数
        
    Returns:
        int: 两个数的乘积
        
    Example:
        >>> multiply(7, 8)
        56
    """
    return a * b

# ==================== 大语言模型配置 ====================

# 初始化OpenAI GPT-4模型
# 使用GPT-4 Omni模型，具备强大的工具调用能力
llm = ChatOpenAI(model="gpt-4o")

# 将乘法工具绑定到大语言模型
# 绑定后，模型能够理解并调用乘法计算工具
llm_with_tools = llm.bind_tools([multiply])

# ==================== 图节点定义 ====================

def tool_calling_llm(state: MessagesState):
    """
    工具调用大语言模型节点
    
    功能：处理用户消息，决定是否需要调用工具
    输入：包含用户消息的状态对象
    输出：包含AI响应或工具调用的新状态
    
    Args:
        state (MessagesState): 包含消息历史的状态对象
        
    Returns:
        dict: 包含新消息的状态更新
        
    工作流程：
    1. 接收用户消息
    2. 调用大语言模型分析用户意图
    3. 模型决定是否需要调用乘法工具
    4. 返回包含响应或工具调用的状态更新
    
    注意：此节点不包含系统消息，模型将基于用户消息直接响应
    """
    # 直接调用大语言模型处理用户消息
    # 模型会根据消息内容决定是否调用乘法工具
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# ==================== 状态图构建 ====================

# 创建状态图构建器
# MessagesState 专门用于处理消息序列的状态管理
builder = StateGraph(MessagesState)

# 添加节点到图中
builder.add_node("tool_calling_llm", tool_calling_llm)  # 大语言模型节点
builder.add_node("tools", ToolNode([multiply]))  # 工具执行节点

# 添加边（连接）到图中
builder.add_edge(START, "tool_calling_llm")  # 从开始节点连接到模型节点

# 添加条件边：根据模型节点的输出决定下一步
builder.add_conditional_edges(
    "tool_calling_llm",
    # 条件判断逻辑：
    # - 如果模型的最新消息包含工具调用 -> 路由到工具节点
    # - 如果模型的最新消息不包含工具调用 -> 路由到结束节点
    tools_condition,  # 预构建的工具条件判断函数
)

# 工具执行完成后，直接结束流程
# 注意：与 agent.py 不同，这里工具执行后不返回模型节点
builder.add_edge("tools", END)

# ==================== 图编译和执行 ====================

# 编译状态图，生成可执行的图对象
# 编译后的图可以接收初始状态并执行完整的工具调用流程
graph = builder.compile()

# 使用示例：
# 1. 创建初始状态：{"messages": [HumanMessage(content="请计算 6 乘以 9")]}
# 2. 调用图：result = graph.invoke(initial_state)
# 3. 获取结果：result["messages"][-1].content
# 
# 执行流程：
# START -> tool_calling_llm -> (条件判断) -> tools -> END
#                    |                    |
#                    |                    v
#                    |               (如果不需要工具)
#                    v                    |
#                   END <-----------------|