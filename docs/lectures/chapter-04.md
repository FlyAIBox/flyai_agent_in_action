# 第四章：高级 Agent 开发（讲义）

## 理论基础：复杂 Agent 系统架构

### 从简单到复杂：Agent 系统的演进

**演进路径**：
```
单节点 Agent → 链式 Agent → 并行 Agent → 多智能体系统
```

### 高级 Agent 系统的核心挑战

1. **性能瓶颈**：单线程执行限制了系统吞吐量
2. **资源利用**：CPU、内存、网络资源的合理分配
3. **复杂性管理**：随着节点增加，系统复杂度指数级增长
4. **故障处理**：部分节点失败时的恢复策略

### 并行计算在 Agent 中的应用

#### 数据并行 vs 任务并行

**数据并行**：
```
大数据集 → 分片 → 并行处理 → 结果聚合
```

**任务并行**：
```
复杂任务 → 子任务分解 → 并行执行 → 结果合并
```

#### 并行模式设计

1. **扇出-扇入模式**（Fan-out/Fan-in）
2. **管道模式**（Pipeline）
3. **Map-Reduce 模式**
4. **Actor 模式**

## 13. 并行执行与性能优化（实操）
- 学习目标：
  - 设计并行节点与异步执行
  - 定位瓶颈并做基准测试
- 要点：
  - 扇出/扇入；并行度与资源调度
  - 监控与剖析，端到端延迟优化
- 实操：`01-agent-build/4-BuildYourAssiant/01-parallelization.ipynb`
- 练习：对 3 个检索子任务并行，并比较总时延

### 并行执行架构设计

#### 1. 扇出-扇入模式实现

**基础扇出**：
```python
from langgraph.graph import StateGraph, END
import asyncio

def create_parallel_graph():
    graph = StateGraph(state_schema)
    
    # 扇出节点：分发任务
    graph.add_node("fanout", fanout_node)
    
    # 并行处理节点
    graph.add_node("process_a", process_a_node)
    graph.add_node("process_b", process_b_node)
    graph.add_node("process_c", process_c_node)
    
    # 扇入节点：聚合结果
    graph.add_node("fanin", fanin_node)
    
    # 定义边
    graph.add_edge("fanout", ["process_a", "process_b", "process_c"])
    graph.add_edge(["process_a", "process_b", "process_c"], "fanin")
    
    return graph
```

**异步并行处理**：
```python
async def parallel_process_node(state):
    tasks = []
    
    # 创建并行任务
    for item in state["items"]:
        task = asyncio.create_task(process_item(item))
        tasks.append(task)
    
    # 等待所有任务完成
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # 处理异常
    successful_results = []
    for result in results:
        if not isinstance(result, Exception):
            successful_results.append(result)
    
    return {"results": successful_results}
```

#### 2. 资源调度与限制

**并发控制**：
```python
import asyncio
from typing import List, Callable

class ResourceManager:
    def __init__(self, max_concurrent: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_tasks = []
    
    async def schedule_task(self, coro: Callable):
        async with self.semaphore:
            return await coro()
    
    async def batch_process(self, tasks: List[Callable], batch_size: int = 10):
        results = []
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[self.schedule_task(task) for task in batch],
                return_exceptions=True
            )
            results.extend(batch_results)
        return results
```

### 性能监控与优化

#### 1. 性能指标收集

```python
import time
import psutil
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class PerformanceMetrics:
    execution_time: float
    memory_usage: float
    cpu_usage: float
    throughput: float
    error_rate: float

class PerformanceMonitor:
    def __init__(self):
        self.metrics = []
        self.start_time = None
        
    def start_monitoring(self):
        self.start_time = time.time()
        
    def collect_metrics(self, processed_items: int, errors: int = 0) -> PerformanceMetrics:
        end_time = time.time()
        execution_time = end_time - self.start_time
        
        return PerformanceMetrics(
            execution_time=execution_time,
            memory_usage=psutil.virtual_memory().percent,
            cpu_usage=psutil.cpu_percent(),
            throughput=processed_items / execution_time if execution_time > 0 else 0,
            error_rate=errors / processed_items if processed_items > 0 else 0
        )
```

#### 2. 瓶颈识别与优化

**延迟分析**：
```python
import functools
import logging

def measure_latency(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = await func(*args, **kwargs)
            latency = time.time() - start
            logging.info(f"{func.__name__} latency: {latency:.3f}s")
            return result
        except Exception as e:
            latency = time.time() - start
            logging.error(f"{func.__name__} failed after {latency:.3f}s: {e}")
            raise
    return wrapper
```

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

