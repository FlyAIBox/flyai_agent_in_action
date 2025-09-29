# 任务管理助手 (Task mAIstro) - 部署指南

## 项目概述

Task mAIstro 是一个基于 LangGraph 的智能任务管理助手，具备长期记忆、个性化服务和智能对话能力。该系统能够理解用户需求，管理待办事项，并学习用户偏好以提供更好的服务。

## 核心功能

### 1. 智能记忆管理
- **用户档案**：自动收集和更新用户的基本信息、兴趣爱好等
- **待办事项**：智能创建、更新和跟踪任务列表
- **个性化指令**：学习用户偏好，提供定制化服务

### 2. 自然语言处理
- **意图识别**：准确理解用户的真实需求
- **上下文感知**：基于历史对话提供连贯的响应
- **多轮对话**：支持复杂的多轮交互

### 3. 工作流管理
- **状态图**：基于 LangGraph 的可视化工作流
- **条件路由**：根据用户意图智能选择处理路径
- **并行处理**：支持同时处理多个任务

## 技术架构

### 核心组件

1. **主节点 (task_mAIstro)**
   - 处理用户输入
   - 生成个性化响应
   - 决定记忆更新策略

2. **更新节点**
   - `update_profile`：更新用户档案
   - `update_todos`：管理待办事项
   - `update_instructions`：学习用户偏好

3. **路由机制**
   - 智能分析用户意图
   - 选择适当的处理流程
   - 确保响应的一致性

### 技术栈

- **LangGraph**：工作流编排和状态管理
- **LangChain**：LLM 集成和工具调用
- **OpenAI GPT-4**：核心语言模型
- **Trustcall**：结构化数据提取
- **Pydantic**：数据验证和序列化
- **Docker**：容器化部署

## 部署配置

### 环境要求

- Python 3.11+
- Docker & Docker Compose
- OpenAI API 密钥
- LangSmith API 密钥（可选）

### 配置文件说明

1. **langgraph.json**：LangGraph 应用配置
   - 定义图结构和依赖关系
   - 指定 Python 版本和构建参数

2. **docker-compose-example.yml**：容器编排配置
   - Redis：缓存和会话存储
   - PostgreSQL：数据持久化
   - LangGraph API：应用服务

3. **configuration.py**：应用配置管理
   - 用户隔离和分类
   - 环境变量支持
   - 配置验证和类型安全

### 部署步骤

1. **环境准备**
   ```bash
   # 克隆项目
   git clone <repository-url>
   cd flyai_agent_in_action/02-agent-deploy/deployment
   
   # 安装依赖
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   export OPENAI_API_KEY="your_openai_api_key"
   export LANGSMITH_API_KEY="your_langsmith_api_key"
   ```

3. **构建和启动服务**
   ```bash
   # 构建 Docker 镜像
   docker build -t my-image .
   
   # 启动所有服务
   docker-compose up -d
   ```

4. **验证部署**
   - API 服务：http://localhost:8123
   - 数据库：localhost:5432
   - Redis：localhost:6379

## 使用指南

### 基本交互

```python
# 创建配置
config = {
    "configurable": {
        "user_id": "user123",
        "todo_category": "work",
        "task_maistro_role": "你是一个工作助手"
    }
}

# 运行图
result = graph.invoke(
    {"messages": [HumanMessage(content="我需要完成项目报告")]},
    config=config
)
```

### 配置参数

- `user_id`：用户唯一标识符
- `todo_category`：待办事项分类（如 "work", "personal"）
- `task_maistro_role`：助手的角色定义

### 记忆管理

系统会自动：
- 收集用户个人信息
- 识别和创建待办事项
- 学习用户偏好和习惯
- 提供个性化建议

## 开发指南

### 代码结构

```
deployment/
├── task_maistro.py          # 主应用逻辑
├── configuration.py         # 配置管理
├── langgraph.json          # LangGraph 配置
├── docker-compose-example.yml  # 容器编排
├── requirements.txt         # Python 依赖
└── README_中文版.md        # 本文档
```

### 扩展开发

1. **添加新的记忆类型**
   - 定义 Pydantic 模型
   - 创建对应的更新节点
   - 更新路由逻辑

2. **自定义工具**
   - 实现工具函数
   - 注册到模型
   - 更新系统提示

3. **优化性能**
   - 调整模型参数
   - 优化记忆检索
   - 实现缓存机制

## 故障排除

### 常见问题

1. **导入错误**
   - 确保安装了所有依赖包
   - 检查 Python 版本兼容性

2. **API 连接失败**
   - 验证 API 密钥是否正确
   - 检查网络连接

3. **数据库连接问题**
   - 确认 PostgreSQL 服务已启动
   - 检查连接字符串配置

### 日志查看

```bash
# 查看应用日志
docker-compose logs langgraph-api

# 查看数据库日志
docker-compose logs langgraph-postgres

# 查看 Redis 日志
docker-compose logs langgraph-redis
```

## 贡献指南

欢迎贡献代码和建议！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 创建 Issue
- 发送邮件
- 参与讨论

---

**注意**：这是一个教学示例项目，用于演示 LangGraph 和 AI 代理的开发。在生产环境中使用前，请确保进行充分的安全性和性能测试。
