# Docker Compose 配置说明

## docker-compose-example.yml 详解

这个 Docker Compose 配置文件定义了一个完整的 LangGraph 应用部署环境，包括数据库、缓存和应用服务。

### 服务架构

```yaml
volumes:
    langgraph-data:  # 数据持久化卷
        driver: local

services:
    # Redis 缓存服务
    langgraph-redis:
        image: redis:6  # Redis 6 版本
        healthcheck:  # 健康检查配置
            test: redis-cli ping  # 检查命令
            interval: 5s  # 检查间隔
            timeout: 1s  # 超时时间
            retries: 5  # 重试次数
        ports:
            - "6379:6379"  # 端口映射：主机端口:容器端口

    # PostgreSQL 数据库服务
    langgraph-postgres:
        image: postgres:16  # PostgreSQL 16 版本
        ports:
            - "5432:5432"  # 数据库端口
        environment:  # 环境变量
            POSTGRES_DB: postgres  # 数据库名
            POSTGRES_USER: postgres  # 用户名
            POSTGRES_PASSWORD: postgres  # 密码
        volumes:
            - langgraph-data:/var/lib/postgresql/data  # 数据持久化
        healthcheck:  # 健康检查
            test: pg_isready -U postgres  # 检查命令
            start_period: 10s  # 启动等待时间
            timeout: 1s  # 超时时间
            retries: 5  # 重试次数
            interval: 5s  # 检查间隔

    # LangGraph API 服务
    langgraph-api:
        image: "my-image"  # 自定义镜像（需要先构建）
        ports:
            - "8123:8000"  # API 端口映射
        depends_on:  # 服务依赖
            langgraph-redis:
                condition: service_healthy  # 等待 Redis 健康
            langgraph-postgres:
                condition: service_healthy  # 等待 PostgreSQL 健康
        environment:  # 环境变量
            REDIS_URI: redis://langgraph-redis:6379  # Redis 连接地址
            OPENAI_API_KEY: "your_openai_api_key"  # OpenAI API 密钥
            LANGSMITH_API_KEY: "your_langsmith_api_key"  # LangSmith API 密钥
            POSTGRES_URI: postgres://postgres:postgres@langgraph-postgres:5432/postgres?sslmode=disable  # 数据库连接地址
```

### 服务说明

#### 1. Redis 服务 (langgraph-redis)
- **用途**: 提供缓存和会话存储
- **版本**: Redis 6
- **端口**: 6379
- **健康检查**: 每5秒检查一次连接状态

#### 2. PostgreSQL 服务 (langgraph-postgres)
- **用途**: 存储应用数据和持久化信息
- **版本**: PostgreSQL 16
- **端口**: 5432
- **数据持久化**: 使用 Docker 卷确保数据不丢失
- **健康检查**: 检查数据库是否就绪

#### 3. LangGraph API 服务 (langgraph-api)
- **用途**: 运行任务管理助手应用
- **端口**: 8123 (外部访问) -> 8000 (容器内部)
- **依赖**: 等待数据库和缓存服务启动完成
- **环境变量**: 配置各种 API 密钥和连接地址

### 部署步骤

1. **构建应用镜像**:
   ```bash
   docker build -t my-image .
   ```

2. **配置环境变量**:
   - 替换 `your_openai_api_key` 为实际的 OpenAI API 密钥
   - 替换 `your_langsmith_api_key` 为实际的 LangSmith API 密钥

3. **启动服务**:
   ```bash
   docker-compose up -d
   ```

4. **访问应用**:
   - API 地址: http://localhost:8123
   - 数据库: localhost:5432
   - Redis: localhost:6379

### 注意事项

- 确保所有 API 密钥已正确配置
- 数据会持久化在 `langgraph-data` 卷中
- 服务启动顺序由 `depends_on` 控制
- 健康检查确保服务完全就绪后才启动依赖服务
