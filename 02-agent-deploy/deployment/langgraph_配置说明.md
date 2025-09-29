# LangGraph 配置文件说明

## langgraph.json 配置详解

这个配置文件定义了 LangGraph 应用的部署参数和依赖关系。

### 配置项说明

```json
{
    "dockerfile_lines": [],  // Dockerfile 自定义行，用于构建 Docker 镜像时的额外配置
    "graphs": {
      "task_maistro": "./task_maistro.py:graph"  // 图定义：将 task_maistro.py 文件中的 graph 对象注册为 "task_maistro" 图
    },
    "python_version": "3.11",  // Python 版本要求
    "dependencies": [
      "."  // 依赖项：当前目录（包含 requirements.txt）
    ]
}
```

### 关键配置解释

1. **graphs**: 定义了可用的图（工作流）
   - `task_maistro`: 任务管理助手的图定义
   - 路径格式：`文件路径:对象名`

2. **python_version**: 指定运行环境所需的 Python 版本

3. **dependencies**: 指定依赖项来源
   - `"."` 表示当前目录，会查找 requirements.txt 文件

4. **dockerfile_lines**: 用于自定义 Docker 构建过程
   - 当前为空数组，表示使用默认构建方式

### 使用场景

这个配置文件主要用于：
- LangGraph Studio 部署
- Docker 容器化部署
- 云服务部署

### 注意事项

- 确保 `task_maistro.py` 文件中导出了名为 `graph` 的对象
- Python 版本必须与配置中的版本匹配
- 依赖项会在部署时自动安装
