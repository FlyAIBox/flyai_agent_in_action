# 第五章：长期记忆系统（讲义）

## 理论基础：长期记忆在 Agent 中的作用

### 为什么需要长期记忆？

传统的 Agent 系统存在"健忘症"问题：

1. **上下文窗口限制**：LLM 只能处理有限长度的对话历史
2. **会话隔离**：不同会话之间无法共享学习经验
3. **知识累积缺失**：无法长期积累和利用历史交互数据
4. **个性化不足**：无法根据用户历史行为提供个性化服务

### 长期记忆系统的架构设计

#### 记忆层次结构

```
工作记忆 (Working Memory)     ← 当前对话上下文
     ↓
短期记忆 (Short-term Memory)  ← 近期会话摘要
     ↓
长期记忆 (Long-term Memory)   ← 持久化知识库
```

#### 记忆类型分类

1. **语义记忆**：事实性知识和概念
2. **情节记忆**：具体事件和经历
3. **程序记忆**：技能和操作流程
4. **元记忆**：关于记忆本身的知识

### 向量数据库与检索技术

#### 嵌入空间的数学原理

**余弦相似度**：
```
similarity(A, B) = (A · B) / (||A|| * ||B||)
```

**检索流程**：
```
查询 → 嵌入编码 → 向量搜索 → 相似度排序 → 结果返回
```

## 16. 记忆存储架构（实操）
- 学习目标：
  - 设计长期记忆与向量检索集成
  - 构建更新与淘汰机制
- 要点：
  - 存储层抽象；嵌入与索引
  - 检索召回与排序；写入策略
- 实操：`01-agent-build/5-LongTermMemroy/01-memory_store.ipynb`
- 练习：比较不同嵌入模型的检索效果

### 记忆存储架构设计

#### 1. 分层存储系统

**存储层抽象**：
```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import numpy as np

class MemoryStore(ABC):
    @abstractmethod
    async def store(self, memory_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """存储记忆"""
        pass
    
    @abstractmethod
    async def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """检索相关记忆"""
        pass
    
    @abstractmethod
    async def update(self, memory_id: str, content: str, metadata: Dict[str, Any]) -> None:
        """更新记忆"""
        pass
    
    @abstractmethod
    async def delete(self, memory_id: str) -> None:
        """删除记忆"""
        pass
```

**向量存储实现**：
```python
import chromadb
from sentence_transformers import SentenceTransformer

class VectorMemoryStore(MemoryStore):
    def __init__(self, collection_name: str = "agent_memory"):
        self.client = chromadb.PersistentClient()
        self.collection = self.client.get_or_create_collection(collection_name)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    async def store(self, memory_id: str, content: str, metadata: Dict[str, Any]) -> None:
        embedding = self.encoder.encode([content])[0].tolist()
        
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata]
        )
    
    async def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = self.encoder.encode([query])[0].tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        return [
            {
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "similarity": 1 - results["distances"][0][i]  # Convert distance to similarity
            }
            for i in range(len(results["ids"][0]))
        ]
```

#### 2. 记忆管理策略

**记忆重要性评估**：
```python
from datetime import datetime, timedelta
import math

class MemoryImportanceCalculator:
    def __init__(self, decay_factor: float = 0.01):
        self.decay_factor = decay_factor
    
    def calculate_importance(self, 
                           access_count: int,
                           creation_time: datetime,
                           last_access_time: datetime,
                           user_rating: float = 0.5) -> float:
        """计算记忆重要性分数"""
        
        # 时间衰减
        time_decay = math.exp(-self.decay_factor * 
                             (datetime.now() - last_access_time).days)
        
        # 访问频率
        frequency_score = math.log(1 + access_count)
        
        # 用户评分
        rating_score = user_rating
        
        # 综合重要性
        importance = (frequency_score * 0.4 + 
                     time_decay * 0.3 + 
                     rating_score * 0.3)
        
        return min(1.0, importance)
```

**记忆淘汰机制**：
```python
class MemoryEvictionPolicy:
    def __init__(self, max_memories: int = 10000):
        self.max_memories = max_memories
        
    async def should_evict(self, memory_store: MemoryStore) -> bool:
        """判断是否需要淘汰记忆"""
        current_count = await memory_store.count()
        return current_count >= self.max_memories
    
    async def select_eviction_candidates(self, 
                                       memory_store: MemoryStore,
                                       evict_count: int) -> List[str]:
        """选择要淘汰的记忆ID"""
        # 获取所有记忆的重要性分数
        memories = await memory_store.list_all()
        
        # 按重要性排序，选择分数最低的记忆
        sorted_memories = sorted(memories, 
                               key=lambda x: x['importance_score'])
        
        return [mem['id'] for mem in sorted_memories[:evict_count]]
```

### 检索优化策略

#### 1. 多策略检索

```python
class HybridRetriever:
    def __init__(self, vector_store: VectorMemoryStore):
        self.vector_store = vector_store
        
    async def hybrid_retrieve(self, 
                            query: str, 
                            top_k: int = 5,
                            semantic_weight: float = 0.7) -> List[Dict[str, Any]]:
        """混合检索：语义 + 关键词 + 时间"""
        
        # 1. 语义检索
        semantic_results = await self.vector_store.retrieve(query, top_k * 2)
        
        # 2. 关键词检索
        keyword_results = await self._keyword_search(query, top_k * 2)
        
        # 3. 时间相关性检索
        temporal_results = await self._temporal_search(query, top_k * 2)
        
        # 4. 融合排序
        fused_results = self._fuse_results(
            semantic_results, keyword_results, temporal_results,
            semantic_weight
        )
        
        return fused_results[:top_k]
    
    def _fuse_results(self, *result_lists, semantic_weight: float) -> List[Dict[str, Any]]:
        """结果融合算法"""
        result_scores = {}
        
        for i, results in enumerate(result_lists):
            weight = semantic_weight if i == 0 else (1 - semantic_weight) / (len(result_lists) - 1)
            
            for j, result in enumerate(results):
                memory_id = result['id']
                # RRF (Reciprocal Rank Fusion) scoring
                score = weight / (j + 1)
                
                if memory_id in result_scores:
                    result_scores[memory_id]['score'] += score
                else:
                    result_scores[memory_id] = {
                        'score': score,
                        'result': result
                    }
        
        # 按分数排序
        sorted_results = sorted(result_scores.values(), 
                              key=lambda x: x['score'], reverse=True)
        
        return [item['result'] for item in sorted_results]
```

#### 2. 自适应检索

```python
class AdaptiveRetriever:
    def __init__(self, memory_store: MemoryStore):
        self.memory_store = memory_store
        self.user_feedback_history = []
        
    async def adaptive_retrieve(self, 
                              query: str, 
                              user_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """基于用户行为的自适应检索"""
        
        # 分析查询意图
        query_intent = await self._analyze_query_intent(query)
        
        # 根据用户上下文调整检索策略
        retrieval_params = self._adapt_retrieval_params(
            query_intent, user_context
        )
        
        # 执行检索
        results = await self.memory_store.retrieve(
            query, 
            top_k=retrieval_params['top_k']
        )
        
        # 后处理：重排序
        reranked_results = self._rerank_by_user_preference(
            results, user_context
        )
        
        return reranked_results
```

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

## 19. 记忆型智能体（Memory Agent）（实操）
- 学习目标：将记忆接入对话，实现上下文感知
- 要点：召回→重写→回答；个性化与持续学习
- 实操：`01-agent-build/5-LongTermMemroy/04-memory_agent.ipynb`
- 练习：为每轮对话生成“学习卡片”并入库

