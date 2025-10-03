"""
配置管理模块

这个模块定义了任务管理助手的配置参数和配置加载逻辑。
支持从环境变量和运行配置中读取参数，环境变量优先级更高。

主要功能：
1. 定义所有可配置的参数
2. 提供配置加载和解析方法
3. 支持多环境配置管理
4. 确保配置的一致性和类型安全
"""

import os
from dataclasses import dataclass, field, fields
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig
from typing_extensions import Annotated
from dataclasses import dataclass

@dataclass(kw_only=True)
class Configuration:
    """
    聊天机器人的可配置字段
    
    这个配置类定义了任务管理助手的所有可配置参数，
    包括用户ID、待办事项分类和助手角色等。
    """
    user_id: str = "default-user"  # 用户唯一标识符
    todo_category: str = "general"  # 待办事项分类
    task_maistro_role: str = "你是一个有用的任务管理助手。你帮助用户创建、组织和管理待办事项列表。"

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """
        从 RunnableConfig 创建 Configuration 实例
        
        这个方法从运行配置中提取配置参数，支持从环境变量和
        配置对象中读取值，环境变量优先级更高。
        
        Args:
            config: 可选的运行配置对象
        
        Returns:
            Configuration: 配置实例
        """
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )
        values: dict[str, Any] = {
            f.name: os.environ.get(f.name.upper(), configurable.get(f.name))
            for f in fields(cls)
            if f.init
        }
        return cls(**{k: v for k, v in values.items() if v})