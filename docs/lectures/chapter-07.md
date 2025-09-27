# 第七章：Agent 评估与监控（讲义）

## 24. Agent 评估体系构建
- 学习目标：构建覆盖研发-上线-运维的评估体系
- 要点：指标体系（正确性/稳定性/成本/时延/安全）
- 资料：`03-agent-evaluation/langfuse/大模型评估体系与Langfuse实战指南.md`
- 练习：为你的 Agent 定义一套“可测量的指标”

## 25. OpenAI SDK 集成（实操）
- 学习目标：集成 OpenAI SDK 与结构化输出
- 要点：函数调用、模式校验、错误与成本控制
- 实操：`01_01_integration_openai_sdk.ipynb`，`01_02_integration_openai_structured_output.ipynb`
- 练习：将一个回答改造为“函数调用 + 模式输出”

## 26. LangChain & LangGraph 集成（实操）
- 学习目标：接入 Langfuse 对 LangChain/LangGraph 的追踪
- 要点：多智能体追踪、性能指标、分布式追踪视图
- 实操：`01_03_integration_langchain.ipynb`，`01_04_integration_langgraph.ipynb`
- 练习：找出端到端瓶颈并优化

## 27. 提示词管理与性能基准（实操）
- 学习目标：提示词版本化、基准测试与 A/B
- 要点：Prompt 模板化、函数调用、对比指标
- 实操：`02_prompt_management_openai_functions.ipynb`，`02_prompt_management_performance_benchmark.ipynb`
- 练习：对两版提示词进行 A/B 并输出报告

## 27.1 案例：质量评估与优化（实操）
- 学习目标：以评估驱动的持续优化闭环
- 实操：`03_evaluation_with_langchain.ipynb`
- 练习：建立“评估集→CI 执行→回归报告”的流程

## 27.2 案例：安全监控系统（实操）
- 学习目标：接入 LLM 安全监控与异常检测
- 实操：`04_example_langgraph_agents.ipynb`，`04_example_llm_security_monitoring.ipynb`
- 练习：触发并捕获 3 类常见风险（越狱、越权、泄露）

