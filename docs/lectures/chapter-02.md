# 第二章：状态管理与内存系统（讲义）

## 6. 状态模式设计（实操）
- 学习目标：
  - 设计类型化、可验证的复杂状态模式
  - 在多模式场景中保持可维护与可扩展
- 关键要点：
  - 状态 Schema 与 Pydantic/TypedDict 等选型
  - 多模式与校验、错误处理策略
  - 复杂数据结构与边界条件
- 实操：`01-agent-build/2-StateAndMemory/01-state-schema.ipynb`，`03-multiple-schemas.ipynb`
- 练习：为不同对话阶段定义不同状态 Schema 并切换

## 7. 状态缩减器与消息管理（实操）
- 学习目标：
  - 通过缩减器实现消息过滤/修剪与内存优化
  - 支持长对话的稳定运行
- 要点：
  - Reducer 设计；消息窗口与策略
  - Token/轮次/角色维度的过滤
- 实操：`01-agent-build/2-StateAndMemory/02-state-reducers.ipynb`，`04-trim-filter-messages.ipynb`
- 练习：实现“系统消息保留、工具调用保留、用户消息按 token 修剪”策略

## 8. 外部存储与持久化（实操）
- 学习目标：
  - 选择并配置外部存储（SQLite/PostgreSQL）
  - 实现会话摘要与高效持久化
- 要点：
  - Checkpointer 与外部 DB 的读写
  - 摘要生成与增量更新策略
- 实操：`01-agent-build/2-StateAndMemory/05-chatbot-external-memory.ipynb`，`06-chatbot-summarization.ipynb`
- 练习：对长对话定期生成摘要并替换早期消息

