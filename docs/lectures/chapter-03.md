# 第三章：人机交互系统（讲义）

## 9. 流式处理与中断（实操）
- 学习目标：
  - 在流式场景中支持可控中断与恢复
  - 提升实时响应与并发能力
- 要点：
  - 流式输出与消息增量
  - 中断点与恢复语义
  - 并发分支与回合控制
- 实操：`01-agent-build/3-HumanInTheLoop/01-streaming-interruption.ipynb`
- 练习：为流式生成添加“人工中断-编辑-继续”流程

## 10. 断点与调试机制（实操）
- 学习目标：引入 Human-in-the-Loop 调试与断点
- 要点：静态/动态断点；审批与继续；调试 UI
- 实操：`01-agent-build/3-HumanInTheLoop/02-breakpoints.ipynb`，`04-dynamic-breakpoints.ipynb`
- 练习：为关键节点设置动态断点并记录人工决策

## 11. 状态编辑与反馈（实操）
- 学习目标：人工反馈介入并编辑状态，校正行为
- 要点：状态回滚、偏差修正、体验设计
- 实操：`01-agent-build/3-HumanInTheLoop/03-edit-state-human-feedback.ipynb`
- 练习：引入简单的“人工打分→影响下轮推理”机制

## 12. 时间旅行调试（实操）
- 学习目标：从历史快照回溯，复盘错误与性能
- 要点：快照管理、状态对比、调试会话管理
- 实操：`01-agent-build/3-HumanInTheLoop/05-time-travel.ipynb`
- 练习：对一次失败流程进行“时间旅行”并修复

