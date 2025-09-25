# -*- coding: utf-8 -*-
"""
简单状态图示例 - 条件路由和随机决策
====================================

本模块演示了如何使用 LangGraph 构建一个包含条件路由的简单状态图。
这是一个入门级示例，展示了状态图的核心概念：节点、边、条件路由和状态管理。

主要特点：
1. 自定义状态类型（TypedDict）
2. 条件边和随机决策逻辑
3. 状态传递和更新机制
4. 清晰的图结构：开始 -> 节点1 -> (条件判断) -> 节点2/节点3 -> 结束

学习目标：
- 理解状态图的基本结构
- 掌握条件路由的实现方法
- 学习状态在节点间的传递机制
- 了解图编译和执行流程

技术栈：
- LangGraph: 状态图构建和编排框架
- Python TypedDict: 类型化字典定义
- Python typing: 类型提示系统
"""

# 导入必要的模块
import random  # 随机数生成模块，用于模拟决策逻辑
from typing import Literal  # 字面量类型，用于限制返回值范围
from typing_extensions import TypedDict  # 类型化字典，用于定义状态结构
from langgraph.graph import StateGraph, START, END  # 图构建核心组件

# ==================== 状态定义 ====================

class State(TypedDict):
    """
    状态类型定义
    
    使用 TypedDict 定义图的状态结构，确保类型安全。
    状态对象在图的各个节点间传递，每个节点可以读取和修改状态。
    
    Attributes:
        graph_state (str): 图状态字符串，用于存储和传递信息
                         在示例中用于构建情感表达句子
    """
    graph_state: str  # 图状态字符串，存储当前的处理结果

# ==================== 条件边函数 ====================

def decide_mood(state) -> Literal["node_2", "node_3"]:
    """
    情绪决策条件边函数
    
    功能：根据当前状态决定下一步要访问的节点
    输入：当前状态对象
    输出：下一个节点的名称（"node_2" 或 "node_3"）
    
    Args:
        state (State): 当前状态对象，包含 graph_state 字段
        
    Returns:
        Literal["node_2", "node_3"]: 下一个要访问的节点名称
        
    决策逻辑：
    - 使用随机数生成器模拟50/50的决策
    - 50%概率选择"node_2"（快乐路径）
    - 50%概率选择"node_3"（悲伤路径）
    
    注意：在实际应用中，决策逻辑通常基于状态内容或业务规则，
    这里使用随机数仅用于演示目的。
    """
    # 从状态中获取用户输入（在本例中是图状态字符串）
    # 在实际应用中，这里通常会根据状态内容做出智能决策
    user_input = state['graph_state'] 
    
    # 使用随机数实现50/50的决策分割
    # random.random() 返回 [0.0, 1.0) 范围内的随机浮点数
    if random.random() < 0.5:
        # 50% 的概率返回节点2（快乐路径）
        return "node_2"
    
    # 50% 的概率返回节点3（悲伤路径）
    return "node_3"

# ==================== 图节点定义 ====================

def node_1(state):
    """
    节点1：初始处理节点
    
    功能：处理初始状态，为后续节点准备数据
    输入：当前状态对象
    输出：更新后的状态对象
    
    Args:
        state (State): 当前状态对象
        
    Returns:
        dict: 包含更新后状态的状态更新
        
    处理逻辑：
    1. 打印节点执行信息
    2. 在状态字符串后添加 " I am"
    3. 返回更新后的状态
    """
    print("---Node 1---")  # 打印节点执行标识
    # 在现有状态字符串后添加 " I am"，构建情感表达的基础
    return {"graph_state": state['graph_state'] + " I am"}

def node_2(state):
    """
    节点2：快乐路径节点
    
    功能：处理快乐情感路径，完成情感表达
    输入：当前状态对象
    输出：更新后的状态对象
    
    Args:
        state (State): 当前状态对象
        
    Returns:
        dict: 包含更新后状态的状态更新
        
    处理逻辑：
    1. 打印节点执行信息
    2. 在状态字符串后添加 " happy!"
    3. 完成快乐情感的表达
    """
    print("---Node 2---")  # 打印节点执行标识
    # 在现有状态字符串后添加 " happy!"，完成快乐情感表达
    return {"graph_state": state['graph_state'] + " happy!"}

def node_3(state):
    """
    节点3：悲伤路径节点
    
    功能：处理悲伤情感路径，完成情感表达
    输入：当前状态对象
    输出：更新后的状态对象
    
    Args:
        state (State): 当前状态对象
        
    Returns:
        dict: 包含更新后状态的状态更新
        
    处理逻辑：
    1. 打印节点执行信息
    2. 在状态字符串后添加 " sad!"
    3. 完成悲伤情感的表达
    """
    print("---Node 3---")  # 打印节点执行标识
    # 在现有状态字符串后添加 " sad!"，完成悲伤情感表达
    return {"graph_state": state['graph_state'] + " sad!"}

# ==================== 状态图构建 ====================

# 创建状态图构建器
# 使用自定义的 State 类型作为状态结构
builder = StateGraph(State)

# 添加节点到图中
builder.add_node("node_1", node_1)  # 初始处理节点
builder.add_node("node_2", node_2)  # 快乐路径节点
builder.add_node("node_3", node_3)  # 悲伤路径节点

# 添加边（连接）到图中
builder.add_edge(START, "node_1")  # 从开始节点连接到节点1

# 添加条件边：从节点1根据决策结果路由到节点2或节点3
builder.add_conditional_edges("node_1", decide_mood)

# 添加结束边：节点2和节点3都连接到结束节点
builder.add_edge("node_2", END)  # 快乐路径结束
builder.add_edge("node_3", END)  # 悲伤路径结束

# ==================== 图编译和执行 ====================

# 编译状态图，生成可执行的图对象
# 编译后的图可以接收初始状态并执行完整的处理流程
graph = builder.compile()

# 使用示例：
# 1. 创建初始状态：{"graph_state": "Hello"}
# 2. 调用图：result = graph.invoke(initial_state)
# 3. 获取结果：result["graph_state"]
# 
# 可能的执行结果：
# - "Hello I am happy!" (50% 概率)
# - "Hello I am sad!" (50% 概率)
#
# 执行流程：
# START -> node_1 -> (随机决策) -> node_2 -> END
#                    |              |
#                    |              v
#                    |           node_3 -> END
#                    v
#                 (50% 概率)