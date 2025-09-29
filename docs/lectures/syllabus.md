# 课程章节大纲（对齐仓库代码）

> 本大纲基于仓库现有 Notebook 和示例目录整理，确保“内容–代码”一一对应，便于教学与实操落地。

| 序号 | 课程标题 | 实操 | 主要内容 | 对应代码 |
| ---- | -------- | ---- | -------- | -------- |
| 第一章：Agent 基础入门 |||||
| 1 | 3 分钟了解 Agent 与 LangGraph | 否 | 什么是 Agent；LangGraph 设计理念；Chat Models；生态；快速上手；社区资源 | 01-agent-build/0-Introduce/basics.ipynb |
| 1.1 | Agent 开发环境搭建 | 是 | Python 环境；依赖与版本；API 密钥；LangGraph Studio；Jupyter；常见问题 | README.md，ubuntu_quick_install.sh，requirements.txt，01-agent-build/1-Base/06-deployment.ipynb，01-agent-build/1-Base/studio/ |
| 2 | Agent 记忆系统基础 | 是 | Checkpointer 原理；SQLite 内存；持久化；会话记忆；检索优化；内存清理 | 01-agent-build/1-Base/01-agent-memory.ipynb |
| 3 | 链式调用与路由 | 是 | 链式调用；路由器；条件分支；错误处理；性能优化；调试技巧 | 01-agent-build/1-Base/02-chain.ipynb，01-agent-build/1-Base/03-router.ipynb |
| 4 | 基础 Agent 开发 | 是 | Agent vs Chain；工具调用；ReAct；错误处理；聊天机器人；性能监控 | 01-agent-build/1-Base/04-agent.ipynb |
| 5 | 简单图构建实战 | 是 | StateGraph 概念；节点/边/状态；条件路由；编译执行；三节点图；可视化调试 | 01-agent-build/1-Base/05-simple-graph.ipynb |
| 5.1 | 案例：LangGraph Studio 部署 | 是 | Studio 配置；可视化调试；实时监控；性能分析；部署优化；常见问题 | 01-agent-build/1-Base/06-deployment.ipynb，01-agent-build/1-Base/studio/ |
| 第二章：状态管理与内存系统 |||||
| 6 | 状态模式设计 | 是 | 复杂状态；类型化状态；多模式管理；验证与错误；自定义模式；复杂结构 | 01-agent-build/2-StateAndMemory/01-state-schema.ipynb，01-agent-build/2-StateAndMemory/03-multiple-schemas.ipynb |
| 7 | 状态归约器与消息管理 | 是 | 归约器原理；消息过滤修剪；内存优化；长对话；自定义归约器；策略实现 | 01-agent-build/2-StateAndMemory/02-state-reducers.ipynb，01-agent-build/2-StateAndMemory/04-trim-filter-messages.ipynb |
| 8 | 外部存储与持久化 | 是 | Checkpointer；SQLite vs PostgreSQL；对话摘要；持久化策略；配置；性能测试 | 01-agent-build/2-StateAndMemory/05-chatbot-external-memory.ipynb，01-agent-build/2-StateAndMemory/06-chatbot-summarization.ipynb |
| 第三章：人机交互系统 |||||
| 9 | 流式处理与中断 | 是 | 流式中断；实时数据流；中断机制；并发；实现；优化 | 01-agent-build/3-HumanInTheLoop/01-streaming-interruption.ipynb |
| 10 | 断点与调试机制 | 是 | HIL 原理；断点机制；动态断点；审批流程；静态断点；交互界面 | 01-agent-build/3-HumanInTheLoop/02-breakpoints.ipynb，01-agent-build/3-HumanInTheLoop/04-dynamic-breakpoints.ipynb |
| 11 | 状态编辑与反馈 | 是 | 状态编辑；人工反馈；回滚；体验设计；反馈收集；状态同步 | 01-agent-build/3-HumanInTheLoop/03-edit-state-human-feedback.ipynb |
| 12 | 时间旅行调试 | 是 | 时间旅行；状态快照；历史回溯；会话管理；状态对比；工具优化 | 01-agent-build/3-HumanInTheLoop/05-time-travel.ipynb |
| 第四章：高级 Agent 开发 |||||
| 13 | 并行执行与性能优化 | 是 | 并行节点；异步执行；瓶颈识别；资源调度；实现；基准测试 | 01-agent-build/4-BuildYourAssiant/01-parallelization.ipynb |
| 14 | Map-Reduce 模式 | 是 | 模式设计；分片；聚合；容错；实现；大数据测试 | 01-agent-build/4-BuildYourAssiant/02-map-reduce.ipynb |
| 15 | 子图设计与模块化 | 是 | 子图架构；模块化；复用；通信；编排；测试 | 01-agent-build/4-BuildYourAssiant/03-sub-graph.ipynb |
| 15.1 | 案例：研究助手系统 | 是 | 案例分析；多智能体；信息整合；报告生成；实战；集成测试 | 01-agent-build/4-BuildYourAssiant/04-research-assistant/ |
| 第五章：长期记忆系统 |||||
| 16 | 记忆存储架构 | 是 | 长期记忆；向量库集成；检索；更新；实现；优化 | 01-agent-build/5-LongTermMemroy/01-memory_store.ipynb |
| 17 | 记忆模式与用户画像 | 是 | 模式设计；用户画像；个性化；隐私保护；系统；验证 | 01-agent-build/5-LongTermMemroy/02-memoryschema_profile.ipynb |
| 18 | 记忆集合与分类 | 是 | 集合设计；分类管理；标签；检索优化；集合操作；评估 | 01-agent-build/5-LongTermMemroy/03-memoryschema_collection.ipynb |
| 19 | 记忆 Agent 整合 | 是 | 架构；上下文感知；个性化交互；学习能力；上下文管理；评估 | 01-agent-build/5-LongTermMemroy/04-memory_agent.ipynb |
| 第六章：生产部署与运维 |||||
| 20 | Agent 创建与配置 | 是 | 实例创建；参数管理；环境变量；初始化；配置文件；测试 | 02-agent-deploy/01-creating.ipynb |
| 21 | 连接管理与通信 | 是 | 连接机制；通信协议；连接池；会话管理；稳定性；优化 | 02-agent-deploy/02-connecting.ipynb |
| 22 | 并发处理与防重复 | 是 | 并发机制；防重复；消息队列；控制策略；稳定性；压力测试 | 02-agent-deploy/03-double-texting.ipynb |
| 23 | Assistant API 开发 | 是 | API 设计；REST 实现；文档；测试；版本；性能 | 02-agent-deploy/04-assistant.ipynb |
| 23.1 | 案例：容器化部署 | 是 | Docker 配置；微服务；环境管理；编排；镜像构建；生产验证 | 02-agent-deploy/deployment/ |
| 第七章：Agent 评估与监控 |||||
| 24 | Agent 评估体系构建 | 否 | 重要性；指标体系；自动化/人工；数据准备；框架；流程自动化 | 03-agent-evaluation/langfuse/大模型评估体系与Langfuse实战指南.md |
| 25 | OpenAI SDK 集成 | 是 | SDK 集成；结构化输出；API 优化；错误处理；成本控制；监控 | 03-agent-evaluation/langfuse/01_01_integration_openai_sdk.ipynb，01_02_integration_openai_structured_output.ipynb |
| 26 | LangChain & LangGraph 集成 | 是 | LangChain 追踪；LangGraph 监控；多智能体追踪；指标；集成优化；数据分析 | 03-agent-evaluation/langfuse/01_03_integration_langchain.ipynb，01_04_integration_langgraph.ipynb |
| 27 | 提示词管理与性能基准 | 是 | 提示词版本；函数调用优化；基准测试；A/B 测试；优化策略；对比分析 | 03-agent-evaluation/langfuse/02_prompt_management_openai_functions.ipynb，02_prompt_management_performance_benchmark.ipynb |
| 27.1 | 案例：质量评估与优化 | 是 | 方法论；LangChain 评估；结果分析；持续优化；自动化；方案实施 | 03-agent-evaluation/langfuse/03_evaluation_with_langchain.ipynb |
| 27.2 | 案例：安全监控系统 | 是 | LangGraph Agent 示例；LLM 安全监控；异常检测；策略配置；系统搭建；评估 | 03-agent-evaluation/langfuse/04_example_langgraph_agents.ipynb，04_example_llm_security_monitoring.ipynb |

提示：更详细的教学安排、学习目标、考核方式和实验步骤见章节讲义（docs/lectures）。

