# IDMP Sample Data Generator (示例数据生成与自动执行工具)

## 简介

`idmp-sample-data-generator` 是工业数字管理平台 (IDMP) 自动化编排工具链中的执行层核心技能。它负责将行业调研的结果（或自然语言描述）转化为 TDengine 时序数据库资产树与仿真数据，并实现端到端的自动化部署。

本工具不仅能生成静态的资产模型，还能模拟真实的工业传感器数据，通过自动化的单位校准、冲突检测与任务轮询，一站式完成从 JSON 配置到系统运行的闭环。

## 核心功能

*   **双模驱动建模**：
    *   **基准优先模式**：自动读取 `industry_research.md`，精准还原调研设定的 4 层拓扑（Site-Shop-Area-Device）及 50+ 采集量规范。
    *   **自主推导模式**：若无文档，基于领域知识自动分析并设计合理的工业层级。
*   **仿真数据生成**：内置 `sin(x)`、`cos(x)`、`random(n)` 等数学函数定义，支持自定义历史偏移量（默认 7 天）与采集步长。
*   **端到端管道流程**：
    *   **自动 UOM 校准**：调用 API 获取系统单位信息，自动修正 JSON 中的单位 ID 或创建缺失的单位。
    *   **重名冲突修复**：自动识别系统中已有的同名示例或模板，并进行后缀递增处理。
    *   **集成上传与加载**：单一脚本操作实现 OAuth2 认证、文件上传（Multipart）、加载触发（Load）及异步状态轮询。
*   **严格质量保障**：集成 `validate_sample_data.py` 和 JSON 语法自动检查。

## 目录结构

```text
idmp-sample-data-generator/
├── README.md           # 本说明文件
├── SKILL.md            # Agent 执行建模与数据生成任务的详细指引
├── scripts/            # 数据生成与 API 推送工具脚本
│   ├── uom_check.py            # 单位一致性检查与自动关联逻辑
│   ├── duplicate_check.py      # 名称冲突预检与自修复逻辑
│   ├── upload_sample.py        # 集成上传、触发加载与状态轮询脚本
│   └── validate_sample_data.py  # JSON Schema 与业务逻辑强制校验
└── templates/          # JSON 模型定义模版
    └── idmp_sample_data_v1.json  # 行业场景数据建模标准模版（Sample Data V1）
```

## 在 EasyUse 流程中的位置

在 `idmp-easyuse` 的全自动编排流程中，本技能位于 **第三步**。它承接第一步生成的设计文档，通过其输出的 `sample_data.json` 为后续的告警分析（Step 4）和看板创建（Step 5）提供底座支撑。

## 注意事项

1.  **超级表设计**：务必遵循“同类设备一张超级表”原则。
2.  **单位规范**：必须使用国际缩写标准，严禁使用中文全称。
3.  **分段写入**：由于 JSON 文件体积较大且层级深，推荐采用分段串行写入 `scripts/` 下的中间文件，而不是一次性全覆盖，以避免 Token 限制导致的失败。
