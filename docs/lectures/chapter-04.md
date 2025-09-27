# 第四章：高级 Agent 开发（讲义）

## 13. 并行执行与性能优化（实操）
- 学习目标：
  - 设计并行节点与异步执行
  - 定位瓶颈并做基准测试
- 要点：
  - 扇出/扇入；并行度与资源调度
  - 监控与剖析，端到端延迟优化
- 实操：`01-agent-build/4-BuildYourAssiant/01-parallelization.ipynb`
- 练习：对 3 个检索子任务并行，并比较总时延

## 14. Map-Reduce 模式（实操）
- 学习目标：将大任务分片→聚合，增强吞吐
- 要点：分片策略、容错、聚合一致性
- 实操：`01-agent-build/4-BuildYourAssiant/02-map-reduce.ipynb`
- 练习：为聚合阶段添加去重与排序

## 15. 子图设计与模块化（实操）
- 学习目标：拆分子图、复用组件、统一编排
- 要点：子图通信、接口契约、可测试性
- 实操：`01-agent-build/4-BuildYourAssiant/03-sub-graph.ipynb`
- 练习：将通用“搜索→总结”封装为子图并复用

## 15.1 案例：研究助手系统（实操）
- 学习目标：搭建多智能体协作的研究助手
- 要点：信息搜集与整合、报告生成、质控
- 实操：`01-agent-build/4-BuildYourAssiant/04-research-assistant/`
- 练习：扩展一个“引用校验”子能力并度量效果

