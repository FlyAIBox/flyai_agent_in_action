"""
任务管理助手 (Task mAIstro) - LangGraph 智能代理系统

这个模块实现了一个基于 LangGraph 的智能任务管理助手，具备以下核心功能：

1. 长期记忆管理：
   - 用户档案存储：保存用户的基本信息、兴趣爱好等
   - 待办事项管理：创建、更新、跟踪用户的任务列表
   - 个性化指令：学习用户偏好，提供定制化服务

2. 智能对话处理：
   - 自然语言理解：解析用户意图和需求
   - 上下文感知：基于历史对话提供个性化响应
   - 自动记忆更新：智能识别并保存重要信息

3. 工作流架构：
   - 主节点 (task_mAIstro)：处理用户输入和生成响应
   - 更新节点：分别处理档案、待办事项和指令的更新
   - 路由机制：根据用户意图智能选择处理流程

4. 技术特性：
   - 使用 Trustcall 进行结构化数据提取
   - 支持并行工具调用提高效率
   - 基于 Pydantic 的数据验证
   - 可配置的用户隔离和分类管理
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from trustcall import create_extractor

from typing import Literal, Optional, TypedDict

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import merge_message_runs
from langchain_core.messages import SystemMessage, HumanMessage

from langchain_openai import ChatOpenAI

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore

import configuration

## 工具类定义

# 用于监控 Trustcall 工具调用的间谍类
class Spy:
    """
    监控工具调用过程的间谍类
    
    这个类用于追踪和记录在 Trustcall 执行过程中调用的工具，
    帮助开发者了解哪些工具被调用以及调用的详细信息。
    """
    def __init__(self):
        self.called_tools = []  # 存储被调用的工具列表

    def __call__(self, run):
        """
        监控运行过程，记录工具调用
        
        Args:
            run: 运行对象，包含工具调用的详细信息
        """
        q = [run]  # 使用队列进行广度优先搜索
        while q:
            r = q.pop()
            if r.child_runs:  # 如果有子运行，继续搜索
                q.extend(r.child_runs)
            if r.run_type == "chat_model":  # 如果是聊天模型运行
                self.called_tools.append(
                    r.outputs["generations"][0][0]["message"]["kwargs"]["tool_calls"]
                )

# 从 Trustcall 工具调用中提取信息（包括补丁和新记忆）
def extract_tool_info(tool_calls, schema_name="Memory"):
    """
    从工具调用中提取信息，包括补丁和新记忆
    
    这个函数用于解析模型返回的工具调用结果，提取出对文档的更新操作
    和新创建的记忆信息，并将其格式化为可读的字符串。
    
    Args:
        tool_calls: 模型返回的工具调用列表
        schema_name: 模式工具的名称（如 "Memory", "ToDo", "Profile"）
    
    Returns:
        str: 格式化后的变更信息字符串
    """
    # 初始化变更列表
    changes = []
    
    # 遍历所有工具调用组
    for call_group in tool_calls:
        for call in call_group:
            if call['name'] == 'PatchDoc':  # 如果是文档补丁操作
                # 检查是否有补丁需要应用
                if call['args']['patches']:
                    changes.append({
                        'type': 'update',  # 更新类型
                        'doc_id': call['args']['json_doc_id'],  # 文档ID
                        'planned_edits': call['args']['planned_edits'],  # 计划编辑
                        'value': call['args']['patches'][0]['value']  # 实际值
                    })
                else:
                    # 处理不需要更改的情况
                    changes.append({
                        'type': 'no_update',  # 无更新类型
                        'doc_id': call['args']['json_doc_id'],  # 文档ID
                        'planned_edits': call['args']['planned_edits']  # 计划编辑
                    })
            elif call['name'] == schema_name:  # 如果是新模式创建
                changes.append({
                    'type': 'new',  # 新建类型
                    'value': call['args']  # 参数值
                })

    # 将结果格式化为单个字符串
    result_parts = []
    for change in changes:
        if change['type'] == 'update':
            result_parts.append(
                f"文档 {change['doc_id']} 已更新:\n"
                f"计划: {change['planned_edits']}\n"
                f"添加内容: {change['value']}"
            )
        elif change['type'] == 'no_update':
            result_parts.append(
                f"文档 {change['doc_id']} 未更改:\n"
                f"{change['planned_edits']}"
            )
        else:
            result_parts.append(
                f"新建 {schema_name}:\n"
                f"内容: {change['value']}"
            )
    
    return "\n\n".join(result_parts)

## 数据模式定义

# 用户档案模式
class Profile(BaseModel):
    """
    用户档案模式
    
    用于存储与用户聊天时的个人信息，包括基本信息和兴趣爱好等。
    这些信息将帮助AI助手更好地理解用户，提供个性化的服务。
    """
    name: Optional[str] = Field(description="用户的姓名", default=None)
    location: Optional[str] = Field(description="用户的居住地", default=None)
    job: Optional[str] = Field(description="用户的职业", default=None)
    connections: list[str] = Field(
        description="用户的个人关系，如家庭成员、朋友或同事",
        default_factory=list
    )
    interests: list[str] = Field(
        description="用户的兴趣爱好", 
        default_factory=list
    )

# 待办事项模式
class ToDo(BaseModel):
    """
    待办事项模式
    
    用于存储和管理用户的任务信息，包括任务描述、完成时间、
    截止日期、解决方案和当前状态等。
    """
    task: str = Field(description="需要完成的任务描述")
    time_to_complete: Optional[int] = Field(description="预计完成任务所需的时间（分钟）")
    deadline: Optional[datetime] = Field(
        description="任务的截止日期（如果适用）",
        default=None
    )
    solutions: list[str] = Field(
        description="具体的、可执行的解决方案列表（如具体想法、服务提供商或完成任务的相关具体选项）",
        min_items=1,
        default_factory=list
    )
    status: Literal["not started", "in progress", "done", "archived"] = Field(
        description="任务的当前状态",
        default="not started"
    )

## 初始化模型和工具

# 更新记忆工具
class UpdateMemory(TypedDict):
    """ 
    决定更新哪种类型的记忆
    
    这个类型定义用于指定要更新的记忆类型，包括用户档案、
    待办事项或指令等不同类型的信息。
    """
    update_type: Literal['user', 'todo', 'instructions']

# 初始化聊天模型
model = ChatOpenAI(model="gpt-4o", temperature=0)

## 创建用于更新用户档案和待办事项列表的 Trustcall 提取器
profile_extractor = create_extractor(
    model,
    tools=[Profile],
    tool_choice="Profile",
)

## 提示词模板

# 聊天机器人指令：用于选择更新内容和调用工具
MODEL_SYSTEM_MESSAGE = """{task_maistro_role} 

你拥有一个长期记忆系统，用于跟踪以下三种信息：
1. 用户档案（关于用户的一般信息）
2. 用户的待办事项列表
3. 更新待办事项列表的通用指令

以下是当前用户档案（如果尚未收集信息，可能为空）：
<user_profile>
{user_profile}
</user_profile>

以下是当前待办事项列表（如果尚未添加任务，可能为空）：
<todo>
{todo}
</todo>

以下是当前用户指定的待办事项列表更新偏好（如果尚未指定偏好，可能为空）：
<instructions>
{instructions}
</instructions>

以下是你处理用户消息的推理指令：

1. 仔细分析下面呈现的用户消息。

2. 决定是否需要更新你的长期记忆：
- 如果提供了关于用户的个人信息，通过调用类型为 `user` 的 UpdateMemory 工具来更新用户档案
- 如果提到了任务，通过调用类型为 `todo` 的 UpdateMemory 工具来更新待办事项列表
- 如果用户指定了如何更新待办事项列表的偏好，通过调用类型为 `instructions` 的 UpdateMemory 工具来更新指令

3. 如果合适，告诉用户你已经更新了记忆：
- 不要告诉用户你更新了用户档案
- 当你更新待办事项列表时，告诉用户
- 不要告诉用户你更新了指令

4. 倾向于更新待办事项列表。无需请求明确许可。

5. 在调用工具保存记忆后，或如果没有调用工具，自然地回应用户。"""

# Trustcall 指令
TRUSTCALL_INSTRUCTION = """反思以下交互过程。

使用提供的工具来保留关于用户的任何必要记忆。

使用并行工具调用来同时处理更新和插入操作。

系统时间: {time}"""

# 更新待办事项列表的指令
CREATE_INSTRUCTIONS = """反思以下交互过程。

基于此交互，更新你关于如何更新待办事项列表项的指令。使用用户的任何反馈来更新他们喜欢如何添加项目等。

你当前的指令是：

<current_instructions>
{current_instructions}
</current_instructions>"""

## 节点定义

def task_mAIstro(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """
    从存储中加载记忆并使用它们来个性化聊天机器人的响应
    
    这是主要的任务管理节点，负责：
    1. 从存储中检索用户的档案、待办事项和指令
    2. 构建包含记忆的系统消息
    3. 调用模型生成个性化响应
    4. 决定是否需要更新记忆
    
    Args:
        state: 消息状态，包含对话历史
        config: 运行配置，包含用户ID等信息
        store: 存储接口，用于读取和写入记忆
    
    Returns:
        dict: 包含模型响应的消息状态
    """
    
    # 从配置中获取用户ID
    configurable = configuration.Configuration.from_runnable_config(config)
    user_id = configurable.user_id
    todo_category = configurable.todo_category
    task_maistro_role = configurable.task_maistro_role

   # 从存储中检索用户档案记忆
    namespace = ("profile", todo_category, user_id)
    memories = store.search(namespace)
    if memories:
        user_profile = memories[0].value
    else:
        user_profile = None

    # 从存储中检索待办事项记忆
    namespace = ("todo", todo_category, user_id)
    memories = store.search(namespace)
    todo = "\n".join(f"{mem.value}" for mem in memories)

    # 检索自定义指令
    namespace = ("instructions", todo_category, user_id)
    memories = store.search(namespace)
    if memories:
        instructions = memories[0].value
    else:
        instructions = ""
    
    # 构建包含记忆的系统消息
    system_msg = MODEL_SYSTEM_MESSAGE.format(task_maistro_role=task_maistro_role, user_profile=user_profile, todo=todo, instructions=instructions)

    # 使用记忆和聊天历史生成响应
    response = model.bind_tools([UpdateMemory], parallel_tool_calls=False).invoke([SystemMessage(content=system_msg)]+state["messages"])

    return {"messages": [response]}

def update_profile(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """
    反思聊天历史并更新记忆集合
    
    这个节点负责更新用户的档案信息，包括：
    1. 从存储中检索现有档案记忆
    2. 使用 Trustcall 提取器分析对话内容
    3. 更新或创建新的档案记忆
    4. 将更新后的记忆保存到存储中
    
    Args:
        state: 消息状态，包含对话历史
        config: 运行配置，包含用户ID等信息
        store: 存储接口，用于读取和写入记忆
    
    Returns:
        dict: 包含工具消息的响应，确认档案已更新
    """
    
    # 从配置中获取用户ID
    configurable = configuration.Configuration.from_runnable_config(config)
    user_id = configurable.user_id
    todo_category = configurable.todo_category

    # 定义记忆的命名空间
    namespace = ("profile", todo_category, user_id)

    # 检索最新的记忆作为上下文
    existing_items = store.search(namespace)

    # 为 Trustcall 提取器格式化现有记忆
    tool_name = "Profile"
    existing_memories = ([(existing_item.key, tool_name, existing_item.value)
                          for existing_item in existing_items]
                          if existing_items
                          else None
                        )

    # 合并聊天历史和指令
    TRUSTCALL_INSTRUCTION_FORMATTED=TRUSTCALL_INSTRUCTION.format(time=datetime.now().isoformat())
    updated_messages=list(merge_message_runs(messages=[SystemMessage(content=TRUSTCALL_INSTRUCTION_FORMATTED)] + state["messages"][:-1]))

    # 调用提取器
    result = profile_extractor.invoke({"messages": updated_messages, 
                                         "existing": existing_memories})

    # 将 Trustcall 的记忆保存到存储中
    for r, rmeta in zip(result["responses"], result["response_metadata"]):
        store.put(namespace,
                  rmeta.get("json_doc_id", str(uuid.uuid4())),
                  r.model_dump(mode="json"),
            )
    tool_calls = state['messages'][-1].tool_calls
    # 返回带有更新确认的工具消息
    return {"messages": [{"role": "tool", "content": "已更新用户档案", "tool_call_id":tool_calls[0]['id']}]}

def update_todos(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """
    反思聊天历史并更新记忆集合
    
    这个节点负责更新用户的待办事项列表，包括：
    1. 从存储中检索现有待办事项记忆
    2. 使用 Trustcall 提取器分析对话内容，识别新的任务
    3. 更新或创建新的待办事项记忆
    4. 将更新后的记忆保存到存储中
    5. 返回详细的更新信息给用户
    
    Args:
        state: 消息状态，包含对话历史
        config: 运行配置，包含用户ID等信息
        store: 存储接口，用于读取和写入记忆
    
    Returns:
        dict: 包含详细更新信息的工具消息
    """
    
    # 从配置中获取用户ID
    configurable = configuration.Configuration.from_runnable_config(config)
    user_id = configurable.user_id
    todo_category = configurable.todo_category

    # 定义记忆的命名空间
    namespace = ("todo", todo_category, user_id)

    # 检索最新的记忆作为上下文
    existing_items = store.search(namespace)

    # 为 Trustcall 提取器格式化现有记忆
    tool_name = "ToDo"
    existing_memories = ([(existing_item.key, tool_name, existing_item.value)
                          for existing_item in existing_items]
                          if existing_items
                          else None
                        )

    # 合并聊天历史和指令
    TRUSTCALL_INSTRUCTION_FORMATTED=TRUSTCALL_INSTRUCTION.format(time=datetime.now().isoformat())
    updated_messages=list(merge_message_runs(messages=[SystemMessage(content=TRUSTCALL_INSTRUCTION_FORMATTED)] + state["messages"][:-1]))

    # 初始化间谍对象，用于监控 Trustcall 的工具调用
    spy = Spy()
    
    # 创建用于更新待办事项列表的 Trustcall 提取器
    todo_extractor = create_extractor(
    model,
    tools=[ToDo],
    tool_choice=tool_name,
    enable_inserts=True  # 启用插入新记录功能
    ).with_listeners(on_end=spy)  # 添加监听器以监控工具调用

    # 调用提取器
    result = todo_extractor.invoke({"messages": updated_messages, 
                                         "existing": existing_memories})

    # 将 Trustcall 的记忆保存到存储中
    for r, rmeta in zip(result["responses"], result["response_metadata"]):
        store.put(namespace,
                  rmeta.get("json_doc_id", str(uuid.uuid4())),
                  r.model_dump(mode="json"),
            )
        
    # 响应 task_mAIstro 中的工具调用，确认更新
    tool_calls = state['messages'][-1].tool_calls

    # 提取 Trustcall 所做的更改，并将其添加到返回给 task_mAIstro 的工具消息中
    todo_update_msg = extract_tool_info(spy.called_tools, tool_name)
    return {"messages": [{"role": "tool", "content": todo_update_msg, "tool_call_id":tool_calls[0]['id']}]}

def update_instructions(state: MessagesState, config: RunnableConfig, store: BaseStore):
    """
    反思聊天历史并更新记忆集合
    
    这个节点负责更新用户的自定义指令，包括：
    1. 从存储中检索现有的用户指令
    2. 基于对话内容生成新的指令
    3. 将更新后的指令保存到存储中
    
    Args:
        state: 消息状态，包含对话历史
        config: 运行配置，包含用户ID等信息
        store: 存储接口，用于读取和写入记忆
    
    Returns:
        dict: 包含更新确认的工具消息
    """
    
    # 从配置中获取用户ID
    configurable = configuration.Configuration.from_runnable_config(config)
    user_id = configurable.user_id
    todo_category = configurable.todo_category
    
    namespace = ("instructions", todo_category, user_id)

    # 获取现有的用户指令
    existing_memory = store.get(namespace, "user_instructions")
        
    # 在系统提示中格式化记忆
    system_msg = CREATE_INSTRUCTIONS.format(current_instructions=existing_memory.value if existing_memory else None)
    new_memory = model.invoke([SystemMessage(content=system_msg)]+state['messages'][:-1] + [HumanMessage(content="请根据对话内容更新指令")])

    # 在存储中覆盖现有记忆
    key = "user_instructions"
    store.put(namespace, key, {"memory": new_memory.content})
    tool_calls = state['messages'][-1].tool_calls
    # 返回带有更新确认的工具消息
    return {"messages": [{"role": "tool", "content": "已更新指令", "tool_call_id":tool_calls[0]['id']}]}

# 条件边
def route_message(state: MessagesState, config: RunnableConfig, store: BaseStore) -> Literal[END, "update_todos", "update_instructions", "update_profile"]:
    """
    基于记忆和聊天历史决定是否更新记忆集合
    
    这是一个路由函数，用于决定下一步应该执行哪个节点：
    - 如果没有工具调用，则结束流程
    - 如果有工具调用，则根据工具类型路由到相应的更新节点
    
    Args:
        state: 消息状态，包含对话历史
        config: 运行配置
        store: 存储接口
    
    Returns:
        str: 下一个要执行的节点名称，或 END 表示结束
    """
    message = state['messages'][-1]
    if len(message.tool_calls) == 0:  # 如果没有工具调用
        return END
    else:
        tool_call = message.tool_calls[0]
        if tool_call['args']['update_type'] == "user":  # 如果是用户档案更新
            return "update_profile"
        elif tool_call['args']['update_type'] == "todo":  # 如果是待办事项更新
            return "update_todos"
        elif tool_call['args']['update_type'] == "instructions":  # 如果是指令更新
            return "update_instructions"
        else:
            raise ValueError(f"未知的更新类型: {tool_call['args']['update_type']}")

# 创建图 + 所有节点
builder = StateGraph(MessagesState, config_schema=configuration.Configuration)

# 定义记忆提取过程的流程
builder.add_node(task_mAIstro)  # 主任务管理节点
builder.add_node(update_todos)  # 更新待办事项节点
builder.add_node(update_profile)  # 更新用户档案节点
builder.add_node(update_instructions)  # 更新指令节点

# 定义流程
builder.add_edge(START, "task_mAIstro")  # 从开始到主节点
builder.add_conditional_edges("task_mAIstro", route_message)  # 从主节点根据条件路由
builder.add_edge("update_todos", "task_mAIstro")  # 从更新待办事项回到主节点
builder.add_edge("update_profile", "task_mAIstro")  # 从更新档案回到主节点
builder.add_edge("update_instructions", "task_mAIstro")  # 从更新指令回到主节点

# 编译图
graph = builder.compile()