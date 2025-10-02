# LangGraph 配置文件生成指南

## 概述

目前 LangGraph CLI **没有提供直接生成 `langgraph.json` 的命令**，需要手动创建和配置。本指南提供了多种创建和配置 `langgraph.json` 的方法。

## 方法一：使用项目模板

### 1. 创建新项目模板
```bash
# 创建基础 Python 项目
langgraph new my-project --template new-langgraph-project-python

# 创建 React Agent 项目
langgraph new my-react-agent --template react-agent-python

# 创建记忆代理项目
langgraph new my-memory-agent --template memory-agent-python

# 创建检索代理项目
langgraph new my-rag-agent --template retrieval-agent-python

# 创建数据丰富代理项目
langgraph new my-data-agent --template data-enrichment-agent-python
```

### 2. 复制模板配置
创建后，可以复制模板中的 `langgraph.json` 并根据需要修改。

## 方法二：手动创建配置文件

### 基础模板
```json
{
  "$schema": "https://langgra.ph/schema.json",
  "dependencies": ["."],
  "graphs": {
    "your_graph_name": "./your_file.py:graph_variable"
  },
  "env": ".env",
  "python_version": "3.12"
}
```

### 完整配置模板
```json
{
  "$schema": "https://langgra.ph/schema.json",
  "dependencies": [
    ".",
    "./custom_module.py",
    "langchain_openai",
    "langchain_community"
  ],
  "graphs": {
    "research_assistant": "./research_assistant.py:graph",
    "chat_agent": "./chat_agent.py:agent_graph"
  },
  "env": ".env",
  "python_version": "3.12",
  "dockerfile_lines": [
    "RUN apt-get update && apt-get install -y curl",
    "COPY custom_scripts/ /app/scripts/"
  ],
  "pip_config_file": "./pip.conf"
}
```

## 方法三：使用脚本自动生成

### Python 脚本生成器
```python
#!/usr/bin/env python3
"""
LangGraph 配置文件生成器
自动分析项目结构并生成 langgraph.json
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

def find_python_files(directory: str) -> List[str]:
    """查找目录下的 Python 文件"""
    python_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py') and not file.startswith('__'):
                python_files.append(os.path.join(root, file))
    return python_files

def find_graph_objects(python_file: str) -> List[str]:
    """查找 Python 文件中的 graph 对象"""
    graphs = []
    try:
        with open(python_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # 简单的正则匹配查找 graph 变量
            import re
            patterns = [
                r'graph\s*=\s*\w+\.compile\(\)',
                r'(\w+)\s*=\s*\w+\.compile\(\)',
                r'def\s+(\w+).*:\s*\n.*\.compile\(\)'
            ]
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                graphs.extend(matches)
    except Exception as e:
        print(f"Error reading {python_file}: {e}")
    return graphs

def generate_langgraph_config(project_dir: str, output_file: str = "langgraph.json"):
    """生成 langgraph.json 配置文件"""
    
    # 基础配置
    config = {
        "$schema": "https://langgra.ph/schema.json",
        "dependencies": ["."],
        "graphs": {},
        "env": ".env",
        "python_version": "3.12"
    }
    
    # 查找 Python 文件
    python_files = find_python_files(project_dir)
    
    # 分析每个文件中的 graph 对象
    for py_file in python_files:
        relative_path = os.path.relpath(py_file, project_dir)
        graphs = find_graph_objects(py_file)
        
        for graph_name in graphs:
            if graph_name == 'graph':
                config["graphs"][os.path.splitext(os.path.basename(py_file))[0]] = f"./{relative_path}:{graph_name}"
            else:
                config["graphs"][graph_name] = f"./{relative_path}:{graph_name}"
    
    # 检查是否有 requirements.txt
    if os.path.exists(os.path.join(project_dir, "requirements.txt")):
        config["dependencies"].append(".")
    
    # 检查是否有自定义模块
    custom_modules = []
    for py_file in python_files:
        if not py_file.endswith(('__init__.py', 'test_', 'conftest.py')):
            relative_path = os.path.relpath(py_file, project_dir)
            if relative_path != "main.py" and relative_path != "app.py":
                custom_modules.append(f"./{relative_path}")
    
    if custom_modules:
        config["dependencies"].extend(custom_modules)
    
    # 写入配置文件
    output_path = os.path.join(project_dir, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 已生成 {output_path}")
    print(f"📋 配置内容:")
    print(json.dumps(config, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="生成 LangGraph 配置文件")
    parser.add_argument("project_dir", help="项目目录路径")
    parser.add_argument("-o", "--output", default="langgraph.json", help="输出文件名")
    
    args = parser.parse_args()
    generate_langgraph_config(args.project_dir, args.output)
```

### 使用方法
```bash
# 保存为 generate_langgraph_config.py
python generate_langgraph_config.py /path/to/your/project

# 或者指定输出文件名
python generate_langgraph_config.py /path/to/your/project -o my_langgraph.json
```

## 方法四：基于现有项目快速配置

### 针对深度研究助手项目
```bash
# 进入项目目录
cd /path/to/your/project

# 创建基础配置
cat > langgraph.json << 'EOF'
{
  "$schema": "https://langgra.ph/schema.json",
  "dependencies": [
    ".",
    "./baike_loader.py",
    "./configuration.py"
  ],
  "graphs": {
    "research_assistant": "./research_assistant.py:graph"
  },
  "env": ".env",
  "python_version": "3.12"
}
EOF
```

## 配置项详解

### 必需字段
- `dependencies`: 依赖项列表
- `graphs`: 图定义映射

### 可选字段
- `$schema`: JSON Schema 验证
- `env`: 环境变量文件路径
- `python_version`: Python 版本 (3.11, 3.12, 3.13)
- `dockerfile_lines`: Docker 自定义配置
- `pip_config_file`: pip 配置文件路径
- `image_distro`: 基础镜像发行版

## 最佳实践

1. **依赖管理**: 优先使用 `requirements.txt`，然后添加本地模块
2. **图命名**: 使用描述性的图名称
3. **版本固定**: 指定具体的 Python 版本
4. **环境变量**: 使用 `.env` 文件管理敏感信息
5. **模块化**: 将不同功能分离到不同文件

## 验证配置

```bash
# 验证 JSON 语法
python -m json.tool langgraph.json

# 使用 LangGraph CLI 验证
langgraph build -c langgraph.json --tag test-image
```

## 总结

虽然 LangGraph CLI 没有直接生成 `langgraph.json` 的命令，但通过以上方法可以快速创建和配置符合项目需求的配置文件。建议使用项目模板作为起点，然后根据具体需求进行调整。
