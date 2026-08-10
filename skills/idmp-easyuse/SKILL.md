---
name: idmp-easyuse
description: IDMP总控编排技能 - 核心枢纽技能。根据用户需求（无论是无文件输入的场景Demo生成，还是带有文件/明确业务数据的具体接入），实现"一键式"自动化编排。静默调度 idmp-sample-data-generator、MCP 可视化工具链和 idmp-analysis-creator 完成全流程（行业调研 -> 数据生成 -> 告警分析 -> 面板创建）。
metadata:
   author: Wang Zhe
   version: 0.4.1
   owner_team: solution-center
---

# IDMP EasyUse 技能

作为 IDMP 项目的总控枢纽，静默调度四个子技能，实现从行业调研到数据建模、告警分析、可视化面板的一键式全流程自动化编排。

## 输入要求

| 类别 | 触发条件 | 典型输入 |
|------|---------|---------|
| **类别 1：场景 Demo 生成** | 仅自然语言描述，无数据文件 | "帮我生成一套智慧工厂能耗监控的演示数据和看板" |
| **类别 2：业务数据接入** | 提供了数据结构文件和/或明确业务需求 | CSV 数据、Excel/SQL/Markdown 结构定义、指定面板和告警规则 |
| IDMP 登录信息 | 两种类别均需 | URL（如 `http://127.0.0.1:6042`）、用户名、密码 |

---

## 常见陷阱（Gotchas）

> 以下规则是 Agent 在没有明确提示时最容易出错的地方，执行前必须阅读。

**步骤顺序不可调换**
- 必须严格按第一步→第二步→第三步→第四步→第五步→第六步→第七步顺序执行，不得并行或跳步。

**调研文档是唯一设计基准**
- 类别 1 执行第二步生成 `outputs/industry_research.md` 后，后续所有子技能必须以此文档为准，严禁自行修改层级结构、告警阈值或面板需求。

**调研报告属性名规范 (Attribute Referencing)**
- 在 `outputs/industry_research.md` 的第二节，采集指标建议采用 `中文名 (English_Name)` 格式。
- 在第三节（关键指标）和第四节（告警规则）中编写公式或条件时，**必须统一使用 `${attributes['中文标题']}` 的格式**（如：`${attributes['温度']} > 50`）。
- 该中文标题必须与第二节中的名称完全一致，严禁直接使用英文标识符。

**跨设备计算禁止**
- 调研报告第三节（关键指标）、第四节（告警规则）、第五节（面板需求）中，不得生成任何跨设备计算的指标、告警或面板。

**静默执行**
- 六个步骤之间必须无缝衔接，全部完成后统一输出最终报告。除不可恢复的错误外，不得在中间请求用户确认。

**面板和分析数量下限（类别 1）**
- 面板总数和分析任务总数各不少于 5 个，且必须分布在不同设备或层级节点上，不得集中在单一节点。

**MCP 工具优先级（⚠️ 必须遵守）**
- **第四步（关键指标）、第五步（告警规则）、第六步（过程事件）**：
  - ✅ **优先使用 `add_analysis`**（自然语言描述方式）。该工具能自动推断触发类型、聚合函数和输出属性格式，避免 `create_analysis` 中 `output`、`trigger` 字段结构复杂、难以正确填写的问题。
  - ⚠️ 仅当 `add_analysis` 生成结果不符合调研文档要求时，才降级使用 `create_analysis` / `create_alarm_rule` 精确控制参数。
- **第七步（可视化面板）**：
  - ✅ **优先使用 `add_panel`**（自然语言描述方式）。该工具能自动解析属性名并填充完整的 PanelAttribute 对象（含 `attributeExpression`、`expression`、`formula`、`window` 等字段）。
  - ❌ **禁止直接使用 `create_panel` 的 `ya_attributes`/`xa_attributes` 参数**：其 schema 仅标注为 `array of object`，未声明必要子字段，模型无法正确推断——直接传入会导致属性列为 `null`，面板报错 `The column name of the data referred attribute null in the panel is empty`。
  - ⚠️ 仅在 `add_panel` 无法匹配属性（如 L1 根节点无直接属性）时，才使用 `create_panel`，并从已有正常面板的 `yaAttributes` 结构中复制完整字段后修改。

**状态驱动与内容压缩 (State-Driven & Compression)**
- 全流程必须维护并更新项目根目录下的 `outputs/state.json`。
- **状态内容**：必须包含场景名、项目路径、登录凭据、调研元数据（指标/告警列表）、资产树结构（含 Node ID）、已完成步骤。
- **动态寻址**：所有文件读写均应基于 `state.json` 中的 `project_root` 进行相对或绝对路径计算。
- **上下文压缩**：步骤间传递信息时，优先引用 `state.json` 中的字段，而非重复粘贴大量冗余文本，以保持 Token 高效利用。

---

## 执行流程

## Telemetry (MUST)

> 调用 `skill-telemetry`，传入 `name=idmp-easyuse version=0.4.1 author=Wang Zhe`。
> 失败不阻塞，但必须尝试。详见 `skill-telemetry`。

<!-- 注意：frontmatter 中 metadata.version 的值即为 telemetry 上报的版本号，请保持一致。 -->

### 第一步：初始化项目与状态机

**1.1 输入与输出**

- **类别 1**：用户未提供任何数据结构文件（xlsx/文本文档）或 CSV 数据文件，仅有自然语言描述。
- **类别 2**：用户提供了上述任意文件，或明确指定了面板展示要求和告警规则。

**1.2 确定场景名称与项目目录**

1. **环境检查**：
   - 首先运行 `python3 --version` 检查环境中是否已安装 Python。
   - 若**未安装**，必须明确告知用户并询问是否允许自动安装（如 `sudo apt update && sudo apt install python3 -y`）。
   - 若用户**拒绝安装**，必须立即停止当前任务并友好告知原因。
2. **场景名称确定**：
   - 优先使用用户在输入中明确提到的场景关键词（如“智慧工厂”、“中央空调”等）。
   - 若用户描述模糊，从描述中提取核心资产或业务目标，转化为简短的英文标识符（下划线连接，如 `smart_factory`）。
3. **项目目录初始化**：
   - 使用本技能目录下的 `scripts/prepare_project_dir.py` 脚本自动创建项目目录。
   - **执行路径说明**：由于客户启动 OpenCode 的工作目录不确定，**必须**先定位本 `SKILL.md` 所在的绝对路径，并以此为基准运行脚本。
   - **必须运行以下命令**（传入确定的场景名称）：
     ```bash
     python3 <skill_dir>/scripts/prepare_project_dir.py <scenario_name>
     ```
   - 确认目录名后，所有子技能的文件操作均在此目录下进行，严格遵循：
     - 中间脚本 → `scripts/` 子目录
     - 输出文件 → `outputs/` 子目录
4. **初始化 `state.json`**：
   - 在 `outputs/` 下创建 `state.json`。
   - 同步登录信息：
     - 读取用户提供的凭据。
     - 更新 `state.json` 中的 `tsdb-login` 和 `idmp-login` 中的信息。
   - **样例结构**：
     ```json
     {
       "scenario": "smart_factory",
       "root": "/absolute/path/to/demo/smart_factory_20260331",
       "category": 1,
       "tsdb-login": { "url": "http://localhost:6041", "user": "root", "pass": "taosdata" },
       "idmp-login": { "url": "http://localhost:6042", "user": "admin", "pass": "password", "api_key": "api_xxx.yyy" },
       "steps": ["init"]
     }
     ```
5. **MCP 服务器检查与创建**：
   - 从 `state.json` 中的 `idmp-login.url` 提取 `IDMP_HOST`，检查是否存在 URL 为 `http://<IDMP_HOST>:6042/api/v1/mcp/stream` 的 MCP 服务器。
   - 若不存在，必须尝试根据 `references/idmp_mcp_config.md` 中的配置信息创建该 MCP 服务器。
   - 调用 `scripts/prepare_mcp_config_content.py --state outputs/state.json` 完成 API Key 的创建与获取，将输出的 API Key 写入 `state.json` 的 `idmp-login.api_key` 字段，并替换到 MCP 配置中。若 `state.json` 中已存在 `idmp-login.api_key`，则直接使用，跳过创建步骤。
   - 若创建失败，必须立即询问用户是否继续任务；若用户选择继续，则在明确告知 MCP 服务不可用的前提下进入后续步骤，否则停止当前流程。

---

### 第二步：行业场景深度调研（仅类别 1）

**触发条件**：类别 1 时执行；类别 2 直接跳至第三步。

对用户描述的行业/场景进行系统化深度建模，生成 `outputs/industry_research.md`。该文档必须严格遵循调研文档编写规范 `references/research_specification.md`，覆盖以下维度：

| 维度 | 内容要求 |
|------|---------|
| **一、层级结构** | 完整拓扑树（L1 -> L2 -> L3 -> L4），列出所有节点并提供层级映射说明 |
| **二、采集数据规范** | 覆盖所有设备类型；定义物理量名称、**中文标题**、频次、单位及典型数值范围 |
| **三、各层级关键指标** | **每一层级均需**配置计算指标；公式统一采用 `${attributes['中文标题']}` 格式；**禁止跨设备计算**；**必须参考 `references/idmp_analysis_abilities.md` 中的触发类型和计算能力进行设计** |
| **四、告警规则** | **每一层级均需**配置告警逻辑；条件统一采用 `${attributes['中文标题']}` 格式；**禁止跨设备告警**；**必须参考 `references/idmp_analysis_abilities.md` 中的触发类型和计算能力进行设计** |
| **五、关键事件** | 通过分析的"生成事件"能力，捕获并记录业务中重要的事件；**无需每个层级都配置，选择关键节点即可**；**必须参考 `references/idmp_analysis_abilities.md` 中的触发类型和计算能力进行设计** |
| **六、可视化面板需求** | **每一层级均需**配置多样化面板；**必须参考 `references/idmp_panel_types.md` 中的面板类型进行设计**；**禁止跨设备面板** |
| **七、调研摘要** | 汇总统计全量指标、告警、事件及面板数量，确保 Demo 复杂性达标 |

调研完成后生成的 `outputs/industry_research.md` 将作为后续所有步骤的统一设计基准（参见 Gotchas）。

---

### 第三步：数据与资产建模

调用 `idmp-sample-data-generator` 技能，传递以下内容：

| 传递内容 | 类别 1 | 类别 2 |
|---------|-------|-------|
| 项目根目录路径 | ✅ 必传 | ✅ 必传 |
| `outputs/industry_research.md` 的完整路径 | ✅ 必传 | — |
| 用户提供的数据结构文件和 CSV 文件 | — | ✅ 必传 |

---

### 第四步：关键指标配置

**注意：本步骤必须使用 MCP (Model Context Protocol) 实现。**

传递以下内容（供 MCP 工具使用）：

| 传递内容 | 类别 1 | 类别 2 |
|---------|-------|-------|
| 项目根目录路径 | ✅ 必传 | ✅ 必传 |
| `outputs/industry_research.md` 路径 | ✅ 必传 | — |
| MCP 调用命令 | ✅ 必传 根据 `outputs/industry_research.md` 中的各层级关键指标，在<完整拓扑的根节点>的资产目录下生成各层级指标。指标从叶子节点开始，逐层生成，直到根节点（L1）。 | ✅ 必传 根据用户提供的指标，生成各层级指标。|

**工具选择（必须遵守）**：
- ✅ **优先调用 `add_analysis`**，传入 `element_id`（目标节点）、`root_element_id`（L1 根节点）和中文自然语言 `description`。
- 描述需包含：指标名称、触发频率、聚合函数、属性名称（与调研文档一致的中文名）。
- 示例：`"每1分钟对1号气象站的风速做滑动最大值计算，输出属性名为'气象站1分钟最高风速'"`
- ⚠️ `add_analysis` 失败或结果不符时，才降级使用 `create_analysis` 精确构造 `trigger`/`output` 参数。

**> 执行完毕后，检查关键指标是否按照要求创建成功，如果不成功，列出未成功的指标和失败原因。然后必须调用 `update_state.py` 将 `"indicators"` 追加到 `state.json` 中。**

---

### 第五步：告警规则配置  (MCP 模式实现)

**注意：本步骤必须使用 MCP (Model Context Protocol) 实现。**

传递以下内容（供 MCP 工具使用）：

| 传递内容 | 类别 1 | 类别 2 |
|---------|-------|-------|
| 项目根目录路径 | ✅ 必传 | ✅ 必传 |
| `outputs/industry_research.md` 路径 | ✅ 必传 | — |
| MCP 调用命令 | ✅ 必传 根据 `outputs/industry_research.md` 中的各层级告警规则，在<完整拓扑的根节点>的资产目录下生成各层级告警规则。告警规则从叶子节点开始，逐层生成，直到根节点（L1）。 | ✅ 必传 根据用户提供的告警规则，生成各层级告警规则。|

**工具选择（必须遵守）**：
- ✅ **优先调用 `add_analysis`**，传入 `element_id`、`root_element_id` 和中文自然语言 `description`。
- 描述需包含：告警名称、触发条件（含属性名和阈值）、持续时长、恢复条件、告警级别（Critical/Major/Warning/Minor）。
- 示例：`"当变桨电池电压低于360V持续1分钟时触发Major告警，命名为'变桨电池欠压告警'，恢复条件为电压大于等于360V"`
- ⚠️ `add_analysis` 失败或结果不符时，才降级使用 `create_alarm_rule` 精确构造参数。

**> 执行完毕后，检查告警规则是否按照要求创建成功，如果不成功，列出未成功的告警规则和失败原因。然后必须调用 `update_state.py` 将 `"alarms"` 追加到 `state.json` 中。**

---

### 第六步：过程事件配置  (MCP 模式实现)

**注意：本步骤必须使用 MCP (Model Context Protocol) 实现。**

传递以下内容（供 MCP 工具使用）：

| 传递内容 | 类别 1 | 类别 2 |
|---------|-------|-------|
| 项目根目录路径 | ✅ 必传 | ✅ 必传 |
| `outputs/industry_research.md` 路径 | ✅ 必传 | — |
| MCP 调用命令 | ✅ 必传 根据 `outputs/industry_research.md` 中的各层级关键事件，在<完整拓扑的根节点>的资产目录下生成各层级关键事件。关键事件从叶子节点开始，逐层生成，直到根节点（L1）。 | ✅ 必传 根据用户提供的关键事件，生成各层级关键事件。|

**工具选择（必须遵守）**：
- ✅ **优先调用 `add_analysis`**，传入 `element_id`、`root_element_id` 和中文自然语言 `description`。
- 描述需包含：事件名称、开始触发条件、持续时长、结束条件、事件级别、需在事件窗口内捕获的统计量。
- 示例：`"当有功功率低于10kW且风速大于5m/s持续5分钟时，记录一次Critical级别的'机组非计划停机事件'，统计事件窗口内的平均风速，结束条件为有功功率大于等于10kW或风速小于等于5m/s"`
- ⚠️ `add_analysis` 失败或结果不符时，才降级使用 `create_analysis`（trigger_type=Event）精确构造参数。

**> 执行完毕后，检查关键事件是否按照要求创建成功，如果不成功，列出未成功的关键事件和失败原因。然后必须调用 `update_state.py` 将 `"events"` 追加到 `state.json` 中。**

---

### 第七步：可视化面板配置 (MCP 模式实现)

**注意：本步骤必须使用 MCP (Model Context Protocol) 实现。**

传递以下内容（供 MCP 工具使用）：

| 传递内容 | 类别 1 | 类别 2 |
|---------|-------|-------|
| 项目根目录路径 | ✅ 必传 | ✅ 必传 |
| `outputs/industry_research.md` 路径 | ✅ 必传 | — |
| MCP 调用命令 | ✅ 必传 根据 `outputs/industry_research.md` 中的可视化面板需求，在<完整拓扑的根节点>的资产目录下生成各层级面板。面板从叶子节点开始，逐层生成，直到根节点（L1）。 | ✅ 必传 根据用户提供的可视化面板需求，生成各层级面板。|

**工具选择（必须遵守）**：
- ✅ **优先调用 `add_panel`**，传入 `element_id`（目标节点）和中文自然语言 `description`。
- 描述需包含：图表类型（折线/散点/柱状/状态时间轴等）、所需属性名称（与调研文档一致的中文名）、时间范围和业务含义。
- 示例：`"折线图，展示过去7天1号气象站的风速和1分钟最高风速随时间变化"`
- ⚠️ **已知行为**：`add_panel` 没有独立的 `name` 参数，面板名称（`name`/`fileName`）会被设置为完整的 `description` 字符串，这是该工具的固有机制，属于预期行为，无需额外处理。若要精确控制面板名称，须改用 `create_panel`（参见下方降级说明）。
- ❌ **禁止直接使用 `create_panel` 的 `ya_attributes`/`xa_attributes` 参数**：其 schema 仅标注为 `array of object`，未声明必要子字段（`attributeExpression`、`expression`、`formula`、`window` 等），直接传入会导致属性列为 `null`，面板报错 `The column name of the data referred attribute null in the panel is empty`。
- ⚠️ 仅当 `add_panel` 因节点无直接属性而失败（如 L1 根节点），或业务要求精确面板名称时，才使用以下两步流程：① 先用 `add_panel` 生成草稿，从返回的 `draft_result.yaAttributes` 获取完整属性结构；② 立即删除草稿，再用 `create_panel` 指定 `name` + 复用步骤①的属性对象重建。

**> 执行完毕后，检查面板是否按照要求创建成功，如果不成功，列出未成功的面板和失败原因。然后必须调用 `update_state.py` 将 `"panels"` 追加到 `state.json` 中。**

---

### 第八步：生成报告

将以下内容汇总生成 `outputs/final_report.md` 并保存至项目 `outputs/` 目录，同时在终端向用户展示摘要：

| 章节 | 字段 |
|------|------|
| 项目基本信息 | 场景名称、项目目录路径、执行时间（YYYY-MM-DD HH:MM:SS） |
| 行业调研概览（类别 1） | 层级数、设备类型数、关键指标数、面板需求数、告警规则数 |
| 数据建模结果 | 数据库名、超级表列表、子表（设备）总数 |
| 面板创建结果 | 面板总数、各节点面板分布 |
| 告警分析结果 | 分析规则总数、各节点分布 |
| 生成文件清单 | `outputs/industry_research.md`（类别 1）、`outputs/final_report.md` |


---

## 编排完整性检查清单

全流程执行完毕后，逐条确认以下项目，有遗漏立即补充执行：

- [ ] **类别 1 调研完成**：`outputs/industry_research.md` 已生成且包含五个完整维度
- [ ] **项目目录唯一**：项目根目录名称含时间戳，未覆盖已有目录
- [ ] **流程执行完整**：`idmp-sample-data-generator`、`MCP 可视化面板配置` 均已按序完成
- [ ] **上下文传递完整**：每个子技能调用时均传递了项目目录路径和前置步骤关键信息
- [ ] **数量达标（类别 1）**：面板总数 ≥ 5 个，分析任务总数 ≥ 5 个，且均分布在多个节点
- [ ] **报告已生成**：`outputs/final_report.md` 已保存

