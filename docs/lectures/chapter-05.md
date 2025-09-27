# 第五章：长期记忆系统（讲义）

## 16. 记忆存储架构（实操）
- 学习目标：
  - 设计长期记忆与向量检索集成
  - 构建更新与淘汰机制
- 要点：
  - 存储层抽象；嵌入与索引
  - 检索召回与排序；写入策略
- 实操：`01-agent-build/5-LongTermMemroy/01-memory_store.ipynb`
- 练习：比较不同嵌入模型的检索效果

## 17. 记忆模式与用户画像（实操）
- 学习目标：个性化记忆与画像驱动策略
- 要点：画像 Schema、隐私与最小化原则
- 实操：`01-agent-build/5-LongTermMemroy/02-memoryschema_profile.ipynb`
- 练习：加入“隐私字段脱敏”并验证

## 18. 记忆集合与分类（实操）
- 学习目标：对记忆进行集合化管理与分类检索
- 要点：标签与层级；集合操作与评估
- 实操：`01-agent-build/5-LongTermMemroy/03-memoryschema_collection.ipynb`
- 练习：实现“按主题聚类→召回”的流程

## 19. 记忆 Agent 整合（实操）
- 学习目标：将记忆接入对话，实现上下文感知
- 要点：召回→重写→回答；个性化与持续学习
- 实操：`01-agent-build/5-LongTermMemroy/04-memory_agent.ipynb`
- 练习：为每轮对话生成“学习卡片”并入库

