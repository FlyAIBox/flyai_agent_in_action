# LangGraph 研究助手 - 快速入门指南

## 🚀 5分钟快速上手

### 第一步：环境准备
```bash
# 安装核心依赖
pip install langgraph langchain_openai langchain_community tavily-python wikipedia

# 设置环境变量
export OPENAI_API_KEY="your-openai-key"
export OPENAI_BASE_URL="your-proxy-url"  # 如果使用代理
export TAVILY_API_KEY="your-tavily-key"
```

### 第二步：运行基础示例
```python
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# 1. 初始化模型
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 2. 定义状态
from typing import TypedDict, List
from pydantic import BaseModel, Field

class Analyst(BaseModel):
    name: str = Field(description="分析师姓名")
    role: str = Field(description="分析师角色")
    description: str = Field(description="分析师描述")

class ResearchState(TypedDict):
    topic: str
    analysts: List[Analyst]

# 3. 创建简单工作流
def create_analysts(state: ResearchState):
    # 这里简化了实际实现
    return {"analysts": [Analyst(name="AI专家", role="技术分析师", description="专注于AI技术分析")]}

# 4. 构建图
builder = StateGraph(ResearchState)
builder.add_node("create_analysts", create_analysts)
builder.add_edge(START, "create_analysts")
builder.add_edge("create_analysts", END)

graph = builder.compile(checkpointer=MemorySaver())

# 5. 运行
result = graph.invoke({"topic": "AI Agent的未来发展"})
print(result)
```

## 📚 核心概念理解

### 1. 什么是LangGraph？
LangGraph是一个用于构建多智能体工作流的框架，就像搭积木一样，你可以：
- 定义不同的AI角色（节点）
- 连接它们（边）
- 让它们协作完成任务

### 2. 多智能体系统
想象一个研究团队：
- **分析师1**: 负责技术分析
- **分析师2**: 负责市场分析  
- **分析师3**: 负责用户调研
- **协调员**: 整合所有信息

### 3. 人机协同
人类可以：
- 审查AI生成的分析师团队
- 提供反馈和调整建议
- 确保结果符合预期

## 🛠️ 实际使用场景

### 场景1：技术调研
```python
# 研究主题：区块链技术在企业中的应用
topic = "区块链技术在企业数字化转型中的应用价值"
max_analysts = 3

# 系统会自动生成：
# - 技术分析师：关注技术实现
# - 商业分析师：关注商业价值
# - 实施专家：关注落地挑战
```

### 场景2：市场分析
```python
# 研究主题：AI在医疗行业的市场前景
topic = "人工智能在医疗诊断领域的市场机会与挑战"
max_analysts = 4

# 系统会生成：
# - 医疗专家：了解行业需求
# - 技术专家：评估技术可行性
# - 市场分析师：分析竞争格局
# - 政策专家：关注监管环境
```

## 🔧 常见问题解决

### Q1: 如何调整分析师数量？
```python
# 在运行前设置
max_analysts = 5  # 增加到5个分析师
```

### Q2: 如何自定义分析师角色？
```python
# 通过人类反馈调整
graph.update_state(thread, {
    "human_analyst_feedback": "添加一个来自初创公司的技术专家"
}, as_node="human_feedback")
```

### Q3: 如何控制访谈深度？
```python
# 调整访谈轮次
interview_config = {
    "max_num_turns": 3  # 每轮访谈最多3个问题
}
```

## 📈 进阶技巧

### 1. 优化提示词
```python
# 自定义分析师生成指令
custom_instructions = """
请为以下主题创建分析师团队：{topic}
要求：
1. 每个分析师都有独特的专业背景
2. 确保覆盖技术、商业、用户三个维度
3. 分析师之间要有互补性
"""
```

### 2. 添加自定义数据源
```python
# 除了网络搜索和维基百科，还可以添加：
# - 内部文档库
# - 专业数据库
# - 实时数据源
```

### 3. 自定义报告格式
```python
# 修改报告结构
report_template = """
# {topic} 研究报告

## 执行摘要
{summary}

## 主要发现
{findings}

## 建议
{recommendations}

## 附录
{sources}
"""
```

## 🎯 学习路径建议

### 初学者（第1-2周）
1. 运行基础示例，理解基本概念
2. 尝试不同的研究主题
3. 观察系统如何生成分析师和报告

### 进阶者（第3-4周）
1. 自定义分析师生成逻辑
2. 添加新的数据源
3. 优化报告格式和内容

### 专家（第5-8周）
1. 构建更复杂的工作流
2. 集成更多外部服务
3. 部署到生产环境

## 💡 最佳实践

### 1. 主题选择
- ✅ 具体明确："AI在金融风控中的应用"
- ❌ 过于宽泛："人工智能的发展"

### 2. 分析师配置
- ✅ 3-5个分析师，角色互补
- ❌ 太多分析师，导致信息冗余

### 3. 质量检查
- 定期审查生成的分析师团队
- 检查报告的逻辑性和准确性
- 验证引用来源的可靠性

## 🔗 相关资源

- [LangGraph官方文档](https://langchain-ai.github.io/langgraph/)
- [LangChain Academy](https://academy.langchain.com/)
- [OpenAI API文档](https://platform.openai.com/docs)
- [Tavily搜索API](https://tavily.com/)

## 📞 获取帮助

如果遇到问题，可以：
1. 查看完整文档：`research-assistant-documentation.md`
2. 检查环境变量配置
3. 查看LangSmith追踪日志
4. 参考官方示例代码

---

**开始你的AI Agent学习之旅吧！** 🚀
