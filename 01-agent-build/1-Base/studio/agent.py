# -*- coding: utf-8 -*-
"""
智能代理系统 - 数学计算工具调用示例
=====================================

本模块演示了如何使用 LangGraph 构建一个能够调用数学计算工具的智能代理系统。
该系统能够理解用户的数学问题，自动选择合适的计算工具，并返回准确的计算结果。

主要功能：
1. 定义数学计算工具（加法、乘法、除法）
2. 构建基于消息状态的有向图
3. 实现智能代理与工具调用的条件路由
4. 提供完整的对话式数学计算服务

技术栈：
- LangChain: 大语言模型集成框架
- LangGraph: 状态图构建和编排框架
- OpenAI GPT-4: 大语言模型
"""

# 导入必要的模块
from langchain_core.messages import SystemMessage  # 系统消息类，用于设置AI助手的行为
from langchain_openai import ChatOpenAI  # OpenAI聊天模型接口

from langgraph.graph import START, StateGraph, MessagesState  # 图构建核心组件
from langgraph.prebuilt import tools_condition, ToolNode  # 预构建的工具相关组件

# ==================== 数学计算工具定义 ====================

def add(a: int, b: int) -> int:
    """
    加法计算工具
    
    功能：计算两个整数的和
    用途：处理用户提出的加法运算需求
    
    Args:
        a (int): 第一个加数
        b (int): 第二个加数
        
    Returns:
        int: 两个数的和
        
    Example:
        >>> add(3, 5)
        8
    """
    return a + b

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
        >>> multiply(4, 6)
        24
    """
    return a * b

def divide(a: int, b: int) -> float:
    """
    除法计算工具
    
    功能：计算两个整数的商
    用途：处理用户提出的除法运算需求
    
    Args:
        a (int): 被除数
        b (int): 除数（不能为0）
        
    Returns:
        float: 两个数的商（浮点数）
        
    Example:
        >>> divide(10, 3)
        3.3333333333333335
    """
    return a / b

# 将所有数学工具组合成工具列表
# 这个列表将被绑定到大语言模型，使其能够调用这些工具
tools = [add, multiply, divide]

# ==================== 大语言模型配置 ====================

# 初始化OpenAI GPT-4模型
# model="gpt-4o" 表示使用GPT-4 Omni模型，具有强大的推理和工具调用能力
llm = ChatOpenAI(model="gpt-4o")

# 将工具绑定到大语言模型
# bind_tools() 方法使模型能够理解并调用指定的工具
llm_with_tools = llm.bind_tools(tools)

# 定义系统消息，设置AI助手的行为和角色
# 系统消息会指导模型如何响应用户的数学计算请求
sys_msg = SystemMessage(
    content="你是一个专业的数学计算助手，专门负责处理各种数学运算问题。"
            "当用户提出数学计算需求时，请仔细分析问题，选择合适的计算工具，"
            "并确保计算结果的准确性。"
)

# ==================== 图节点定义 ====================

def assistant(state: MessagesState):
    """
    智能助手节点
    
    功能：处理用户消息，生成包含工具调用的响应
    输入：包含用户消息的状态对象
    输出：包含AI助手响应的新状态
    
    Args:
        state (MessagesState): 包含消息历史的状态对象
        
    Returns:
        dict: 包含新消息的状态更新
        
    工作流程：
    1. 接收用户消息和系统消息
    2. 调用大语言模型生成响应
    3. 模型可能决定调用工具或直接回复
    4. 返回包含响应的状态更新
    """
    # 将系统消息与用户消息组合，然后调用大语言模型
    # 系统消息确保AI助手按照预定义的角色和规则工作
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# ==================== 状态图构建 ====================

# 创建状态图构建器
# MessagesState 是专门用于处理消息序列的状态类型
builder = StateGraph(MessagesState)

# 添加节点到图中
builder.add_node("assistant", assistant)  # 智能助手节点
builder.add_node("tools", ToolNode(tools))  # 工具执行节点

# 添加边（连接）到图中
builder.add_edge(START, "assistant")  # 从开始节点连接到助手节点

# 添加条件边：根据助手节点的输出决定下一步
builder.add_conditional_edges(
    "assistant",
    # 条件判断逻辑：
    # - 如果助手的最新消息包含工具调用 -> 路由到工具节点
    # - 如果助手的最新消息不包含工具调用 -> 路由到结束节点
    tools_condition,  # 预构建的工具条件判断函数
)

# 工具执行完成后，返回到助手节点进行后续处理
builder.add_edge("tools", "assistant")

# ==================== 图编译和执行 ====================

# 编译状态图，生成可执行的图对象
# 编译后的图可以接收初始状态并执行完整的对话流程
graph = builder.compile()

# 使用示例：
# 1. 创建初始状态：{"messages": [HumanMessage(content="请计算 15 + 27")]}
# 2. 调用图：result = graph.invoke(initial_state)
# 3. 获取结果：result["messages"][-1].content
