# 第一章：Agent 基础入门（讲义）

## 1. 3 分钟了解 Agent 与 LangGraph
- 学习目标：
  - 明确 Agent 与传统程序架构差异
  - 掌握 LangGraph 的“精确性与控制力”设计理念
  - 了解 Chat Models 与生态组件
- 关键要点：
  - Agent 概念、组成与生命周期
  - LangGraph vs LangChain：图式编排与可控执行
  - 第一个 LangGraph 程序骨架与最小示例
- 实操关联：`01-agent-build/0-Introduce/basics.ipynb`
- 课后练习：
  - 用你熟悉的场景（如 FAQ）画出 Agent 执行图
  - 修改示例，添加一个“打印”节点并验证执行顺序

## 1.1 Agent 开发环境搭建（实操）
- 学习目标：
  - 完成 Python/依赖安装与密钥配置
  - 启用 LangGraph Studio 并能在本地调试
- 步骤清单：
  - Python 3.12（或 ≥3.11），conda/pip 环境
  - 安装依赖与可选扩展；配置 OpenAI/Langfuse 密钥
  - 安装并启动 LangGraph Studio；Jupyter 配置
  - 常见问题排查（网络、SSL、代理、权限）
- 参考材料：
  - `README.md`、`ubuntu_quick_install.sh`、`requirements.txt`
  - `01-agent-build/1-Base/06-deployment.ipynb`、`01-agent-build/1-Base/studio/`
- 验收标准：
  - 能运行任一 Notebook 并呼起模型
  - Studio 可查看/调试图的节点与边

## 2. Agent 记忆系统基础（实操）
- 学习目标：
  - 理解 Checkpointer/会话记忆与状态持久化
  - 能在 SQLite 上正确保存/恢复对话状态
- 关键要点：
  - Checkpointer 读写与恢复语义
  - 记忆检索与清理策略
- 实操关联：`01-agent-build/1-Base/01-agent-memory.ipynb`
- 练习：将记忆窗口从 k 条改为基于 token 的修剪

## 3. 链式调用与路由（实操）
- 学习目标：掌握链式/条件分支/路由与错误处理
- 要点：
  - 路由器设计与条件分发
  - 异常捕获与重试策略
- 实操：`01-agent-build/1-Base/02-chain.ipynb`，`03-router.ipynb`
- 练习：为不同意图走不同子链并统计命中率

## 4. 基础 Agent 开发（实操）
- 学习目标：明确 Agent vs Chain 区别与 ReAct 工具调用
- 要点：工具调用协议、错误处理、性能监控
- 实操：`01-agent-build/1-Base/04-agent.ipynb`
- 练习：接入一个检索工具并实现最小 ReAct 回答

## 5. 简单图构建实战（实操）
- 学习目标：能编译/执行/可视化一个 3 节点图
- 要点：StateGraph、节点/边/状态、条件路由
- 实操：`01-agent-build/1-Base/05-simple-graph.ipynb`
- 练习：增加一个“回退”边并在 Studio 中调试

## 5.1 案例：LangGraph Studio 部署（实操）
- 学习目标：部署与调试 Studio，观察运行轨迹
- 要点：可视化调试、实时监控、性能分析
- 实操：`01-agent-build/1-Base/06-deployment.ipynb`，`01-agent-build/1-Base/studio/`
- 练习：导出一次完整运行的可视化图并标注关键路径

