# 百度百科文档加载器使用说明

## 概述

`BaiduBaikeLoader` 是一个专门为 LangChain 框架设计的百度百科内容加载器，能够智能地从百度百科获取权威的中文知识内容。这个加载器特别适用于构建中文知识库、问答系统以及研究助手工具。

## 主要特性

### 🎯 智能内容提取
- **优先提取摘要**：自动识别并提取百度百科条目的摘要部分，通常包含最重要的信息
- **回退到正文**：如果摘要不存在，则提取正文段落内容
- **双重解析模式**：支持 BeautifulSoup 精确解析和正则表达式备用方案

### 🔄 容错机制
- **直接访问优先**：首先尝试直接访问条目页面（如：`https://baike.baidu.com/item/人工智能`）
- **搜索回退**：如果直接访问失败，自动回退到搜索页面并选择相关条目
- **异常处理**：单个链接失败不影响其他链接的处理

### ⚙️ 灵活配置
- **内容长度限制**：支持设置最大字符数，避免单次加载过多内容
- **文档数量控制**：可设置最大加载的条目页面数量
- **超时设置**：可自定义 HTTP 请求超时时间
- **自定义请求头**：支持添加自定义 HTTP 请求头

## 安装依赖

```bash
# 必需依赖
pip install requests langchain-core

# 可选依赖（推荐，用于更好的内容解析）
pip install beautifulsoup4
```

## 基础用法

### 简单使用

```python
from baike_loader import BaiduBaikeLoader

# 创建加载器实例
loader = BaiduBaikeLoader("人工智能")

# 获取文档
documents = list(loader.lazy_load())

# 查看结果
for doc in documents:
    print(f"来源: {doc.metadata['source']}")
    print(f"内容: {doc.page_content[:200]}...")
    print("-" * 50)
```

### 高级配置

```python
# 创建高级配置的加载器
loader = BaiduBaikeLoader(
    query="机器学习",           # 搜索查询词
    load_max_docs=3,          # 最多加载3个文档
    doc_content_chars_max=5000,  # 每个文档最多5000字符
    timeout=15,               # 请求超时15秒
    headers={                 # 自定义请求头
        "User-Agent": "MyBot/1.0"
    }
)

# 懒加载方式获取文档
for doc in loader.lazy_load():
    print(f"标题: {doc.metadata.get('title', '未知')}")
    print(f"来源: {doc.metadata['source']}")
    print(f"内容长度: {len(doc.page_content)} 字符")
    print(f"内容预览: {doc.page_content[:100]}...")
    print("=" * 60)
```

## 在 LangChain 中使用

### 与向量数据库结合

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from baike_loader import BaiduBaikeLoader

# 创建嵌入模型
embeddings = OpenAIEmbeddings()

# 加载百度百科内容
loader = BaiduBaikeLoader("深度学习", load_max_docs=5)
documents = list(loader.lazy_load())

# 创建向量数据库
vectorstore = Chroma.from_documents(
    documents=documents,
    embedding=embeddings
)

# 进行相似性搜索
results = vectorstore.similarity_search("什么是神经网络？", k=3)
for result in results:
    print(result.page_content[:200])
```

### 与检索器结合

```python
from langchain.retrievers import VectorStoreRetriever
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI

# 创建检索器
retriever = VectorStoreRetriever(vectorstore=vectorstore)

# 创建问答链
qa_chain = RetrievalQA.from_chain_type(
    llm=OpenAI(),
    chain_type="stuff",
    retriever=retriever
)

# 进行问答
question = "深度学习的应用领域有哪些？"
answer = qa_chain.run(question)
print(f"问题: {question}")
print(f"答案: {answer}")
```

## 参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `query` | str | 必需 | 搜索查询词或实体名称 |
| `load_max_docs` | int | 2 | 最大加载的条目页面数量 |
| `doc_content_chars_max` | Optional[int] | None | 文档内容最大字符数限制 |
| `timeout` | int | 12 | HTTP 请求超时时间（秒） |
| `headers` | Optional[dict] | None | 自定义 HTTP 请求头 |

## 使用场景

### 1. 知识库构建
```python
# 批量构建特定领域的知识库
topics = ["人工智能", "机器学习", "深度学习", "自然语言处理"]
all_documents = []

for topic in topics:
    loader = BaiduBaikeLoader(topic, load_max_docs=3)
    documents = list(loader.lazy_load())
    all_documents.extend(documents)

# 创建知识库
vectorstore = Chroma.from_documents(all_documents, embeddings)
```

### 2. 实时问答系统
```python
# 动态获取最新信息
def get_latest_info(query: str):
    loader = BaiduBaikeLoader(query, load_max_docs=2, doc_content_chars_max=3000)
    documents = list(loader.lazy_load())
    return documents

# 在问答系统中使用
user_question = "什么是ChatGPT？"
relevant_docs = get_latest_info(user_question)
# 将文档传递给LLM进行回答
```

### 3. 研究助手工具
```python
# 为研究助手提供权威信息源
def research_topic(topic: str, max_docs: int = 5):
    loader = BaiduBaikeLoader(
        query=topic,
        load_max_docs=max_docs,
        doc_content_chars_max=8000
    )
    return list(loader.lazy_load())

# 使用示例
research_data = research_topic("量子计算", max_docs=3)
for doc in research_data:
    print(f"来源: {doc.metadata['source']}")
    print(f"内容摘要: {doc.page_content[:300]}...")
```

## 注意事项

### 1. 网络请求
- 确保网络连接正常，能够访问百度百科
- 建议设置合理的超时时间，避免长时间等待
- 大量请求时注意控制频率，避免对服务器造成压力

### 2. 内容质量
- 百度百科内容质量参差不齐，建议对获取的内容进行验证
- 某些条目可能包含过时信息，需要结合其他信息源
- 建议设置字符数限制，避免加载过长的内容

### 3. 依赖管理
- BeautifulSoup 为可选依赖，但强烈推荐安装以获得更好的解析效果
- 需要 LangChain Core 0.3.x 版本（与项目依赖版本保持一致）

### 4. 错误处理
```python
try:
    loader = BaiduBaikeLoader("不存在的条目")
    documents = list(loader.lazy_load())
    if not documents:
        print("未找到相关内容")
except Exception as e:
    print(f"加载失败: {e}")
```

## 常见问题

### Q: 为什么有时候获取不到内容？
A: 可能的原因包括：
- 网络连接问题
- 查询词在百度百科中不存在
- 请求被服务器拒绝（可以尝试添加更多请求头）
- 页面结构发生变化（需要更新选择器）

### Q: 如何提高内容提取的准确性？
A: 建议：
- 安装 BeautifulSoup 依赖
- 使用更具体的查询词
- 设置合理的字符数限制
- 检查返回的元数据中的 source 字段

### Q: 可以用于商业项目吗？
A: 请遵守百度百科的使用条款和 robots.txt 规则，建议：
- 控制请求频率
- 不要用于大规模爬取
- 尊重网站的服务条款

## 更新日志

- **v1.0.0**: 初始版本，支持基础的百度百科内容加载功能
- 支持直接访问和搜索回退两种模式
- 支持内容长度限制和文档数量控制
- 适配 LangChain Core 0.3.x 版本
