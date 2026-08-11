# IDMP EasyUse 技能

`idmp-easyuse` 是工业数字管理平台（IDMP）演示生成项目的**总控编排技能（核心枢纽）**。它根据用户需求（无文件输入的场景 Demo 生成，或带文件/明确业务数据的具体接入），静默调度 `idmp-sample-data-generator` 与 MCP 可视化工具链，把行业调研、数据建模、告警分析、过程事件、可视化面板串成一条完整流水线，实现"一键式"自动化编排。

> ⚠️ **重要警告：请务必确保不要指定任何已存在的数据库！在执行过程中有删除指定数据库的风险。**

## 输入要求

| 类别 | 触发条件 | 典型输入 |
|------|---------|---------|
| **类别 1：场景 Demo 生成** | 仅自然语言描述，无数据文件 | "帮我生成一套智慧工厂能耗监控的演示数据和看板" |
| **类别 2：业务数据接入** | 提供了数据结构文件和/或明确业务需求 | CSV 数据、Excel/SQL/Markdown 结构定义、指定面板和告警规则 |
| IDMP 登录信息 | 两种类别均需 | URL（如 `http://127.0.0.1:6042`）、用户名、密码 |

## 目录结构

```text
idmp-easyuse/
├── README.md                        # 本说明文档
├── SKILL.md                         # 技能主文件（执行规范）
├── references/
│   ├── idmp_analysis_abilities.md   # 分析能力、触发方式和计算约束
│   ├── idmp_mcp_config.md           # MCP 服务配置示例
│   ├── idmp_panel_types.md          # 可用面板类型与适用场景
│   └── research_specification.md    # 调研文档的结构与写法规范
└── scripts/
    ├── prepare_project_dir.py       # 初始化项目目录
    ├── prepare_mcp_config_content.py # 创建/获取 MCP API Key 并写入配置
    ├── get_login_token.py           # 获取登录 Token
    └── update_state.py              # 更新 outputs/state.json 的 steps 数组
```

## 运行流程

全流程分为八步，**必须严格按顺序执行，不得并行或跳步**：

1. **初始化项目与状态机**：检查 Python 环境；用 `scripts/prepare_project_dir.py` 创建 `idmp-demo/{场景名}_{时间戳}/` 目录；初始化 `outputs/state.json`（场景名、项目路径、登录凭据、已完成步骤）；检查并创建 MCP 服务器。
2. **行业场景深度调研**（仅类别 1）：生成 `outputs/industry_research.md`，定义资产层级、采集点、指标、告警、事件及面板。该文档是后续所有步骤的**唯一设计基准**；类别 2 直接跳过此步。
3. **数据与资产建模**：调用 `idmp-sample-data-generator` 完成资产树构建和模拟数据生成。
   > ⚠️ **数据库安全**：请务必确保不要指定任何已存在的数据库！在执行过程中有删除指定数据库的风险。
4. **关键指标配置**：通过 MCP 在各层级节点配置计算指标（优先 `add_analysis`）。
5. **告警规则配置**：通过 MCP 在各层级节点配置告警规则（优先 `add_analysis`）。
6. **过程事件配置**：通过 MCP 在各层级节点配置关键事件（优先 `add_analysis`）。
7. **可视化面板配置**：通过 MCP 在各层级节点配置面板（优先 `add_panel`）。
8. **生成报告**：汇总生成 `outputs/final_report.md`，并在终端向用户展示摘要。

## 关键约定

- **状态驱动与内容压缩**：全程维护并更新项目下的 `outputs/state.json`，每步结束后用 `scripts/update_state.py` 追加步骤标识；步骤间优先引用 `state.json` 字段而非重复粘贴冗余文本。
- **静默执行**：步骤之间无缝衔接，除不可恢复的错误外，不在中间请求用户确认。
- **调研文档是唯一设计基准**：`industry_research.md` 生成后，严禁自行修改层级结构、告警阈值或面板需求。
- **属性引用规范**：指标、告警、事件公式统一采用 `${attributes['中文标题']}` 格式，且中文标题须与采集数据规范完全一致。
- **禁止跨设备计算**：指标、告警、面板均不得跨设备生成。
- **数量下限（类别 1）**：面板总数与分析任务总数各不少于 5 个，且须分布在不同设备或层级节点上。
- **MCP 工具优先级**：第四至六步优先 `add_analysis`（自然语言描述），第七步优先 `add_panel`；仅在结果不符时才降级使用 `create_analysis` / `create_alarm_rule` / `create_panel`。禁止直接使用 `create_panel` 的 `ya_attributes` / `xa_attributes` 参数。
- **Telemetry**：执行时调用 `skill-telemetry` 上报（name/version/author），失败不阻塞但必须尝试。

## 参考文档

- `references/research_specification.md`：调研文档的结构与写法规范。
- `references/idmp_analysis_abilities.md`：分析能力、触发方式和计算约束。
- `references/idmp_panel_types.md`：可用面板类型与适用场景。
- `references/idmp_mcp_config.md`：MCP 服务配置示例。

## 使用说明

通常通过自然语言指令触发：

> "请使用 idmp-easyuse 技能，帮我生成一套 [场景名称] 的演示数据和看板。"

如需接入已有业务数据（类别 2），可一并提供数据结构文件、CSV 数据或明确的面板/告警需求。

## 维护约定

- **唯一性**：每个项目必须在独立的 `idmp-demo/` 子目录中运行，严禁覆盖历史数据。
- **设计基准**：调研阶段生成的 `industry_research.md` 是后续所有步骤的**唯一事实来源**。
- **回复语言**：根据项目规范，所有输出及注释必须使用**中文**。
