# 多智能体云平台智能客服系统 (Multi-Agent Cloud Platform Customer Service System) 🚀

![Framework](https://img.shields.io/badge/Framework-LangGraph-blue?style=flat-square)
![Backend](https://img.shields.io/badge/Backend-FastAPI-green?style=flat-square)
![VectorDB](https://img.shields.io/badge/VectorDB-Milvus-orange?style=flat-square)
![GraphDB](https://img.shields.io/badge/GraphDB-Neo4j-blueviolet?style=flat-square)
![LLM](https://img.shields.io/badge/LLM-DeepSeek%20%2F%20Qwen-red?style=flat-square)

本项目是一个基于 **LangGraph**、**FastAPI** 和 **Vue 3** 构建的**企业级多智能体云平台智能客服与 FinOps 降本诊断系统**。系统采用大模型驱动与强状态图约束的设计思想，深度融合了基于 **Neo4j 知识图谱的精确 Cypher 检索** 与 **Milvus 向量知识库的模糊关联**。在底层中，我们构建了精细的**双轨制内存系统（短时 Redis + 长时 Milvus）**与 **MCP 角色级沙箱安全工具链**，为复杂云平台下的资产管理、费用核对及高价值降本诊断提供安全、稳健、丝滑的生产级工程实现。

---

## 目录
1. [🌟 核心技术亮点与架构演变](#-核心技术亮点与架构演变)
2. [📂 项目目录结构导航](#-项目目录结构导航)
3. [🛠️ 核心架构与业务流深度剖析](#-核心架构与业务流深度剖析)
4. [📊 数据库设计与高保真时序遥测](#-数据库设计与高保真时序遥测)
5. [🚀 快速启动与本地化/Docker部署指南](#-快速启动与本地化docker部署指南)
6. [🎯 从何开始：具体的阶段式研发路径](#-从何开始具体的阶段式研发路径)

---

## 🌟 核心技术亮点与架构演变

### 1. 生产级双轨制记忆系统 (Dual-Track Memory & Background Extraction)
系统构建了统一的记忆网关 `MemoryManager`，完美隔离并协同了“短期会话缓存”与“长期偏好认知”：
*   **短期工作记忆 (Thread-Level Session Cache)**：利用基于 **Redis** 带 TTL（过期淘汰）的会话物理隔离机制。在单次长会话中，智能体可以极其快速地追踪并存储对话状态，保障了高并发场景下的数据高内聚与隐私隔离。
*   **长期偏好认知 (Long-Term Cognitive Memory)**：
    *   **非阻塞异步提取**：当交互每满 5 轮或用户安全结束当前 Session 时，系统会在后台非阻塞式唤起专门的 `PreferenceExtractor` 智能体。它通过 LLM 大模型对原始对话链进行深度特征审计，剔除无用冗余，自动提炼出用户的“技术栈偏好”、“预算敏感度”及“云架构诉求”等硬核事实与偏好。
    *   **动态语义召回与注入**：将这些事实进行 Embeddings 向量化后持久化写入 **Milvus 长期偏好库**。当该用户发起任意新会话提问时，系统会基于 `user_id` 自动秒级召回关联背景，拼装为 `memory_context` 注入 LLM 上下文，实现跨时空的个性化云上咨询。

### 2. 双驱检索与语义缓存 (Dual-Retrieval Paths & L1 Semantic Cache)
打破常规向量检索召回的模糊性限制，系统设计了极具生产力的双轨检索架构：
*   **语义与检索解耦 (Dual-Retrieval)**：针对产品咨询，系统同时驱动了 **Neo4j 精确 Cypher 图谱查询** 与 **Milvus 向量模糊 Chunk 匹配**。对于规格配额、地域限制等结构化硬限制，直接走图谱精准召回，杜绝大模型产生的参数幻觉。
*   **高精度 L1 级语义拦截器 (Semantic Cache)**：在请求进入 LangGraph 图编排之前，先通过 Milvus 进行余弦距离（Cosine Similarity）比对。
    *   **极致严苛阈值 (Cosine Distance <= 0.08)**：若检索距离小于该严苛阈值，判定为**强语义命中**，直接提取缓存答案极速吐出，无需构建复杂的图或调用 LLM。这不仅极大降低了 Token 成本开销，更带来了毫秒级超高响应速度。

### 3. 基于 MCP (Model Context Protocol) 的角色级沙箱安全工具链 (MCP IDOR Security)
在涉及底层数据库敏感资源查询（如账单流水、监控详情）时，系统彻底杜绝了模型越权风险：
*   **安全鉴权劫持 (UserIdInjector)**：智能体在决定调用工具（例如 `query_user_instances` 查询云实例）时，即使大模型因受到恶意 Prompt 注入攻击或自身幻觉伪造出越权的 `user_id`，多智能体总线底座的 `UserIdInjector` 拦截器都会强行介入。
*   **强制参数覆写**：拦截器从当前经安全认证的可信 Session 中劫持并覆写 `user_id`，强制代入正确的标识符，彻底消除了**平行越权（IDOR）**与**垂直越权**的致命安全漏洞。

### 4. 状态接力协作网络 (State Handoff & Loop)
借助 **LangGraph**，系统摒弃了单一 Agent 承载海量 Prompt 的臃肿设计，构建了**多垂直智能体图扑网络**：
*   **中控分发 (Orchestrator)**：仅专注于语义意图审计与分流。
*   **无缝状态接力 (Handoff)**：例如，在诊断优化云资源时，`Orchestrator` 将提问分流给负责资产提取的 `billing_agent`，并由其运行资产和指标查询；随后利用状态条件边机制（发现 `is_finops_workflow=True`），在无需用户干预下，**以极高鲁棒性自动接力状态**给 `finops_agent` 进行遥测监控诊断与 FinOps 调优，最终将精美的成本降本报告渲染下发。

---

## 📂 项目目录结构导航

```text
cloud_agent/                # 项目根目录
├── agent/                  # 【核心】多智能体算法与推理引擎目录
│   ├── agents/             # 子智能体定义节点（Orchestrator、Billing、FinOps、Product 等）
│   ├── config/             # Pydantic-Settings 全局配置与 MCP 配置管理
│   ├── core/               # 核心底层算法层
│   │   ├── memory/         # 长/短期内存管理器 (Redis/Milvus)、用户偏好提取器
│   │   ├── workflow/       # LangGraph 状态图定义 (state.py) 与拓扑图构建 (graph_manager.py)
│   │   └── cache/          # L1 级高性能语义缓存管理器 (cache.py)
│   ├── database/           # 数据流初始化工具与高保真时序数据生成器
│   │   ├── generate_large_dataset.py  # 高保真 30 天时序遥测模拟发生器
│   │   └── init_large_mock_data.sql   # 自动生成的 2000+ 行大规模仿真 SQL
│   ├── mcp_servers/        # 基于 FastMCP 的数据服务总线（安全隔离访问底层 MySQL）
│   │   └── cloud_platform_server.py   # MCP Server 核心实现
│   ├── tools/              # 异构外部知识引擎（Neo4j 图谱工具、Milvus 向量知识库工具）
│   ├── main.py             # 智能体命令行交互 (CLI) 与单次测试入口
│   └── requirements.txt    # 核心算法端运行依赖
├── app/                    # FastAPI 高性能 ASGI 后端 Web 服务
│   ├── app_main.py         # 接口启动入口（生命周期内预热智能体与语义缓存）
│   ├── router/             # RESTful API 路由与 SSE 流式流通道
│   ├── service/            # 核心业务服务（chat_service.py 将 LangGraph 流包装为标准 SSE 字符流）
│   └── infra/              # 基础设施服务（含 Milvus L1 级语义缓存实现）
├── front/                  # 前端现代交互应用
│   └── cloud_agent/        # 标准 Vite + TS + Vue 3 生产级工程
└── mock_data/              # 异构知识文档原始材料（Markdown & JSON）
```

---

## 🛠️ 核心架构与业务流深度剖析

### 1. 全局数据与控制流流向图
下面是系统基于真实代码实现所绘制的**全局系统技术与控制流图**，展示了从前端请求到语义拦截、图图协作及安全防护的完整数据链条：

```mermaid
graph TD
    %% 前端交互层
    Vue[Vue 3 前端控制台 App.vue] <-->|HTTP & SSE 流式打字机| FastAPI[FastAPI 后端路由 app_main.py]

    %% FastAPI 语义拦截
    subgraph FastAPI_Middleware ["FastAPI 中台拦截服务层"]
        FastAPI <-->|1. 语义匹配 Cosine <= 0.08| MilvusL1[Milvus L1 智能语义缓存]
        FastAPI <-->|2. 未命中则调用| LangGraphMgr[LangGraph 智能图管理器]
    end

    %% 智能体编排网络 (LangGraph)
    subgraph LangGraph_Network ["Multi-Agent Systems (LangGraph Core)"]
        Orchestrator["总调度节点 Orchestrator<br/>(orchestrator.py)"]
        
        %% 四大基础业务 Node
        ProductAgent["产品咨询智能体<br/>(product_agent.py)"]
        BillingAgent["账单与实例查询智能体<br/>(billing_agent.py)"]
        PromotionAgent["优惠推广智能体<br/>(promotion_agent.py)"]
        RecommendAgent["产品推荐智能体<br/>(recommendation_agent.py)"]
        
        %% FinOps 智能体
        FinOpsAgent["FinOps 成本优化智能体<br/>(finops_agent.py)"]
        
        %% 意图路由分流
        Orchestrator -->|意图 = 产品咨询| ProductAgent
        Orchestrator -->|意图 = 资产/订单| BillingAgent
        Orchestrator -->|意图 = 返佣/裂变| PromotionAgent
        Orchestrator -->|意图 = 架构规格推荐| RecommendAgent
        
        %% 状态接力机制 (State Handoff)
        BillingAgent -.->|State Handoff 状态接力<br/>is_finops_workflow == True| FinOpsAgent
    end

    %% 智能图管理器与 Orchestrator 核心调度连接
    LangGraphMgr <--> Orchestrator

    %% 记忆流与历史检索
    Orchestrator <-->|短期会话缓存 TTL| RedisMemory["Redis 内存记忆"]
    Orchestrator <-->|长时间偏好提取召回| MilvusMemory["Milvus 向量偏好记忆库"]

    %% 检索与安全工具通道
    ProductAgent -->|结构化 Cypher 查询| Neo4jSearch["Neo4j 知识图谱检索"]
    ProductAgent -->|模糊 Chunk 向量匹配| MilvusSearch["Milvus 向量知识库检索"]
    
    %% MCP 安全拦截
    BillingAgent & FinOpsAgent -->|安全工具调用拦截| SecurityIDOR["UserIdInjector 安全防御层"]
    SecurityIDOR -->|强行覆写并注入受信任 user_id| MCPClient["FastMCP 平台服务客户端"]

    %% 数据与记忆层 (Data & Memory Layers)
    subgraph Data_Memory_Layers ["Data & Memory Layers (数据与记忆网格)"]
        Neo4j[(Neo4j 知识图谱)]
        MilvusKB[(Milvus 向量知识库)]
        Redis[(Redis 缓存 DB)]
        MilvusMem[(Milvus 向量记忆库)]
        MySQL[(云平台 MySQL 订单/监控数据库)]
    end

    %% 物理连接关系
    Neo4jSearch --> Neo4j
    MilvusSearch --> MilvusKB
    RedisMemory --> Redis
    MilvusMemory --> MilvusMem
    MCPClient -->|MySQL 读写 / 生图接口| MySQL

    %% 样式美化系统
    classDef vue fill:#41B883,stroke:#35495E,stroke-width:2px,color:#fff;
    classDef fastapi fill:#009688,stroke:#004D40,stroke-width:2px,color:#fff;
    classDef cache fill:#FF9800,stroke:#F57C00,stroke-width:2px,color:#fff;
    classDef agent fill:#2196F3,stroke:#0D47A1,stroke-width:2px,color:#fff;
    classDef finops fill:#E91E63,stroke:#880E4F,stroke-width:2px,color:#fff;
    classDef db fill:#607D8B,stroke:#263238,stroke-width:2px,color:#fff;
    classDef safety fill:#9C27B0,stroke:#4A148C,stroke-width:2px,color:#fff;

    class Vue vue;
    class FastAPI fastapi;
    class MilvusL1 cache;
    class Orchestrator,ProductAgent,BillingAgent,PromotionAgent,RecommendAgent agent;
    class FinOpsAgent finops;
    class Neo4j,MilvusKB,Redis,MilvusMem,MySQL db;
    class SecurityIDOR safety;
```

### 2. 多垂直智能体协作与交回
以下展示了总调度器（Orchestrator）与子业务智能体之间，利用 LangGraph 动态跳转条件边的接力关系：

```mermaid
stateDiagram-v2
    [*] --> Orchestrator
    Orchestrator --> Billing : 意图 = 账单/订单/退款
    Orchestrator --> FinOps : 意图 = 实例遥测分析/降本优化建议
    Orchestrator --> [*] : 简单闲聊/通用产品知识库解答
    
    Billing --> Orchestrator : 协同交回控制权(返回空路由字符)
    FinOps --> Orchestrator : 协同交回控制权(返回空路由字符)
```

---

## 📊 数据库设计与高保真时序遥测

### 1. 高保真仿真数据设计背景
在真实的 FinOps 降本诊断中，缺乏有规律的时序指标，就无法检验智能体对**容量瓶颈与资源浪费**的判别精确度。为此，本项目在 `agent/database` 中设计了一个基于高保真数学发生器的 [generate_large_dataset.py](file:///d:/AI/deep_research/cloud_agent/agent/database/generate_large_dataset.py)，可以模拟长达 **30 天**的云资源硬件性能遥测指标。

### 2. 遥测指标的数学模型与仿真场景
数据发生器运用了正弦波动方程、高斯白噪声和偏置区间函数，精准构造了三种典型的工作负荷场景：
*   **闲置状态实例 (Idle Load)**：
    *   *数学物理模型*：
        $$\text{CPU\_utilization} = \text{clip}(\mathcal{N}(3.0, 1.0), 0.5, 8.0)$$
    *   *特征与诊断*：CPU 利用率长期低位徘徊于 1.5% - 4.5% 区间。智能体诊断结论将为：**资源极度浪费，应“退订”或降配为极低规格以削减开支。**
*   **正常昼夜交替负荷 (Normal Diurnal Load)**：
    *   *数学物理模型*：正弦波动叠加随机扰动：
        $$\text{CPU\_utilization} = 30.0 + 15.0 \times \sin\left(\frac{2\pi \times t}{24}\right) + \mathcal{N}(0, 5.0)$$
    *   *特征与诊断*：符合企业白天工作高潮、深夜降温的典型物理规律。智能体诊断结论将为：**资源使用健康，建议维持现状，或转化为按量计费/配置弹性伸缩。**
*   **高负荷节点实例 (Heavy Compute Load)**：
    *   *数学物理模型*：
        $$\text{CPU\_utilization} = \text{clip}(\mathcal{N}(85.0, 4.0), 70.0, 100.0)$$
    *   *特征与诊断*：模拟企业级高负荷核心计算实例，硬件利用率常年高烧（80% - 95%）。智能体诊断结论将为：**存在显著宕机风险与资源瓶颈，FinOps 建议进行“规格升级”以规避安全隐患。**

---

## 🚀 快速启动与本地化/Docker部署指南

针对 Windows 操作系统，为了给您提供高灵活度的开发体验，我们同时编写了 **Docker Compose 一键部署** 与 **轻量化无 Docker 本地混合部署** 两种环境搭建方案：

### 🛠️ 方案 A：Docker Compose 一键启动（强烈推荐、最省心）
在项目根目录下，直接打开 PowerShell 运行：

```powershell
# 1. 后台一键拉起 MySQL、Redis、Neo4j、Milvus 所有服务
docker-compose up -d

# 2. 校验容器状态，确保所有基础设施健康运行
docker-compose ps
```
*各组件端口映射及凭证说明：*
*   **MySQL** (`3306`)：已内置创建好 `mydb` 数据库。账户为 `root` / 密码 `RootPass123!`，普通账户密码 `UserPass123!`。
*   **Redis** (`6379`)：配置认证密码为 `Yoxxxxxx`。**超级管理员用户名请务必指定为 `default`**。
*   **Neo4j** (`7687`/`7474`)：图数据库初始连接密码已设定为 `neo4j` / `12345678`。
*   **Milvus** (`19530`)：开源高并发向量检索引擎，就绪可用。

---

### 🛠️ 方案 B：本地免 Docker 混合搭建（免除容器环境依赖）
若您的主机无法运行 Docker Desktop，可直接在 Windows 上使用原生工具链：

1.  **MySQL 部署**：
    *   访问 [MySQL Installer](https://dev.mysql.com/downloads/installer/) 安装原生 8.0 社区版，或者直接借助 **小皮面板 (PhpStudy)** 一键挂载启动 MySQL 进程。
2.  **Redis 原生运行**：
    *   下载 Windows 原生免安装绿色版 [Redis-Windows](https://github.com/tporadowski/redis/releases) 或者是企业级开发首选替代软体 **Memurai**。双击运行 `redis-server.exe`，配置文件中指定连接密码为 `Yoxxxxxx`，占用 `6379` 端口。
3.  **Neo4j 部署**：
    *   前往 [Neo4j Desktop 官网](https://neo4j.com/download/) 下载安装 Windows Desktop 控制中心。新建一个 Local DBMS，管理员密码设置为 `12345678` 启动即可。
4.  **Milvus 免安装极速运行 (`milvus-lite`)**：
    *   在您的 Windows Python 虚拟环境中直接运行：
        ```bash
        pip install milvus
        ```
    *   并在主程序或测试脚本的前端追加如下初始化声明，即可在本地 19530 端口自动唤醒并运行轻量级向量检索实例：
        ```python
        from milvus import default_server
        default_server.start() # 零 Docker、零外部挂载依赖！
        ```

---

### 📂 初始化大仿真数据集（MySQL SQL 导入）
为提供高对比度的测试支持，我们提前构建了包含 50+ 个仿真用户、200+ 张采购订单以及 2220 条时序遥测指标的大规模 SQL 测试库 [init_large_mock_data.sql](file:///d:/AI/deep_research/cloud_agent/agent/database/init_large_mock_data.sql)：

```powershell
# 1. 连接本地 MySQL 服务端
mysql -u root -p -h 127.0.0.1

# 2. 手动创建带有完整中文字符集支持的数据库
CREATE DATABASE IF NOT EXISTS mydb DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_general_ci;
use mydb;

# 3. 导入 DDL 表结构与全部仿真数据集（请指定您的文件绝对物理路径）
source d:/AI/deep_research/cloud_agent/agent/database/init_large_mock_data.sql;

# 4. 验证数据记录完整度（看到 instance_telemetry 显示 2220 行即代表成功）
select count(*) from instance_telemetry;
```

---

### 🔑 环境变量与鉴权配置 (`.env`)
在运行智能体之前，请复制并配置 `agent/.env` 配置文件。以下为标准的本地运行默认配置示例：

```env
# ==========================================================
# 多智能体云客服系统环境配置 (.env)
# ==========================================================

# 1. 大语言模型密钥配置 (以 DeepSeek 密钥为例，支持并兼容阿里云百炼/OpenAI等主流大语言模型)
DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
MODEL=deepseek-chat
BASE_URL=https://api.deepseek.com/v1
DASHSCOPE_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxx"
TAVILY_API_KEY="tvly-xxxxxxxxxxxxxxxxxxxxxxxx"

# 2. 短期缓存配置 (Redis 连接，请务必指定超级管理员用户名为 default)
REDIS_URL=redis://default:Yoxxxxxx@localhost:6379
REDIS_TTL=1800

# 3. 关系型数据库配置 (用于 MCP MySQL 数据总线安全连接)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=UserPass123!
MYSQL_DATABASE=mydb

# 4. 向量库配置 (用于 L1 语义缓存及长期偏好召回)
MILVUS_HOST=localhost
MILVUS_PORT=19530
MILVUS_COLLECTION=mult_agent_memory2

# 5. 图数据库配置 (用于云产品拓扑精确检索)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=12345678

# 6. 系统调试日志级别
LOG_LEVEL=INFO
```

---

### 🖥️ 运行 FastAPI 后端服务
1.  激活并配置 Python 虚拟环境，并安装核心库依赖：
    ```bash
    cd agent
    pip install -r requirements.txt
    ```
2.  启动高性能 ASGI FastAPI 代理中控服务：
    ```bash
    cd ../app
    python app_main.py
    ```
    *后端成功挂载至 `http://127.0.0.1:5000`，自动与底层的 LangGraph 推理大脑、Redis 会话库、Milvus 缓存库无缝联调。*

### 🎨 启动 Vue 3 极美客服端前端
1.  切换进入前端源码目录：
    ```bash
    cd ../front/cloud_agent
    ```
2.  极速拉取并安装前端依赖包：
    ```bash
    npm install
    ```
3.  唤醒 Vite 高清开发热服务器：
    ```bash
    npm run dev
    ```
4.  根据终端抛出的地址（如 `http://localhost:5173`）在浏览器中打开，即可进入科技感十足、带丝滑流式 SSE 渲染、多场景卡片动态展示的**企业级多智能体客服终端**，即可向智能体发起多轮云平台资产深度诊断与规格调优问询！

---

## 🎯 从何开始：具体的阶段式研发路径

为了帮助您快速吃透并具备开发改造该系统的能力，强烈建议您遵循以下**四个渐进式研发阶段**进行探索：

*   **第一阶段：筑基 (配置与源注入)**：配置各源，并将高保真测试数据成功源导入 MySQL，确保环境中的 Redis、Milvus、Neo4j 各项服务可用就绪。
*   **第二阶段：破冰 (命令行 CLI 直击大脑内核)**：
    *   在不联调 Web 和前端的情况下，直接进入 `agent/` 目录运行 `python main.py` 启动终端聊天，验证智能体内核。
    *   测试问答：*“什么是VPC”*（验证 Neo4j 图检索）、*“查询我的云实例”*（验证 MCP 工具链调用）。
    *   研读源码：[state.py](file:///d:/AI/deep_research/cloud_agent/agent/core/workflow/state.py)、[graph_manager.py](file:///d:/AI/deep_research/cloud_agent/agent/core/workflow/graph_manager.py) 与 [orchestrator.py](file:///d:/AI/deep_research/cloud_agent/agent/agents/orchestrator.py)，吃透全局状态管理、节点路由及意图解析的核心机制。
*   **第三阶段：解密 (深入外部连接安全与异构存储)**：
    *   研读 MCP 代理服务器代码 [cloud_platform_server.py](file:///d:/AI/deep_research/cloud_agent/agent/mcp_servers/cloud_platform_server.py)，看它如何构建工具和注入 `UserIdInjector` 拦截越权漏洞的。
    *   研读内存管理器 [memory_manager.py](file:///d:/AI/deep_research/cloud_agent/agent/core/memory/memory_manager.py)，体会 Redis 活跃会话历史与 Milvus 后台异步提取偏好并在下次提问中自动融合召回的工程闭环。
*   **第四阶段：登堂入室 (全链路前后端 SSE 联调优化)**：
    *   打开后端服务 `app_main.py` 及核心聊天服务层 [chat_service.py](file:///d:/AI/deep_research/cloud_agent/app/service/chat_service.py)，深入体会大模型多智能体思考漫长阶段，后端是如何利用 Python 异步 Generator 和流式多线程，把思考块实时流式推送至浏览器的。
    *   研读前端 [App.vue](file:///d:/AI/deep_research/cloud_agent/front/cloud_agent/src/App.vue)，学习前端在 `fetch` 通道中利用 reader 对 chunk 流数据包进行解码、高亮及卡片分流渲染的技术精髓。

---

## 💡 总结与架构演进建议

本套架构完全贴合了现代 **AI 工程师 (AI Engineer)** 从大模型纯 Prompt 到状态约束与复合 AI 系统（Compound AI System）的工业级工程落地规范。
*   **水平功能扩展**：当您需要添加新的垂直智能体（例如 *安全支持智能体*、*网络排错智能体*）时，您只需在 `agent/agents/` 新增节点代码，并在 `graph_manager.py` 的拓扑状态机中简单配置新的节点并加入与 `Orchestrator` 的路由分支即可。
*   **极致检索准确性**：如遇到特定专业词汇匹配偏离，可优先在 [init_large_mock_data.sql](file:///d:/AI/deep_research/cloud_agent/agent/database/init_large_mock_data.sql) 对应的 Neo4j 产品图谱结构化属性中进行图扩充，或将优质云产品文档持续灌入 `mock_data` 中，系统会通过自动流实现持续的非结构化向量覆盖。
