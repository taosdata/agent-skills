# IDMP EasyUse 技能

`idmp-easyuse` 是工业数字管理平台（IDMP）演示生成项目的总控编排技能，负责把行业调研、数据建模、分析配置、面板配置和博客输出串成一条完整流水线。

## 核心能力

- 根据自然语言场景描述，自动生成完整的 IDMP 演示项目。
- 在类别 1 场景下先生成行业调研文档，再以该文档作为后续唯一设计基准。
- 调度 `idmp-sample-data-generator` 完成资产建模与数据生成。
- 通过 MCP 完成关键指标、告警规则、关键事件和可视化面板配置。
- 生成最终执行报告，并调用 `idmp-blog-generator` 输出宣传博客。

## 目录结构

```text
idmp-easyuse/
├── README.md
├── SKILL.md
├── references/
│   ├── idmp_analysis_abilities.md
│   ├── idmp_mcp_config.md
│   ├── idmp_panel_types.md
│   └── research_specification.md
└── scripts/
    ├── prepare_project_dir.py
    └── get_login_token.py
```

## 运行流程

1.  **环境准备**：检查并安装 Python 环境。
2.  **项目初始化**：运行 `scripts/prepare_project_dir.py` 创建 `idmp-demo/{场景名}_{时间戳}/` 目录。
3.  **行业调研**：生成 `outputs/industry_research.md`，定义资产层级、采集点、指标、告警及面板。
4.  **执行建模**：调用子技能完成 IDMP 资产树构建和模拟数据生成。
5.  **配置任务**：调用 MCP ，在各层级节点自动化配置分析规则和监控面板。
6.  **产出报告**：汇总生成最终执行报告 `outputs/final_report.md`。

## 参考文档

- `references/research_specification.md`：调研文档的结构与写法规范。
- `references/idmp_analysis_abilities.md`：分析能力、触发方式和计算约束。
- `references/idmp_panel_types.md`：可用面板类型与适用场景。
- `references/idmp_mcp_config.md`：MCP 服务配置示例。

## 使用说明

通常通过如下自然语言指令触发：
> "请使用 idmp-easyuse 技能，帮我生成一套 [场景名称] 的演示数据和看板。"

## 维护约定

- **唯一性**：每个项目必须在独立的 `idmp-demo/` 子目录中运行，严禁覆盖历史数据。
- **设计基准**：调研阶段生成的 `industry_research.md` 是后续所有步骤的**唯一事实来源**。
- **回复语言**：根据项目规范，所有输出及注释必须使用**中文**。
