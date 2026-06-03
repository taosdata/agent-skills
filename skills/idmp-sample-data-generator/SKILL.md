---
name: idmp-sample-data-generator
description: 高度自动化的 IDMP 数据建模与加载工具。支持基于调研文档设计（industry_research.md）或自然语言描述，进行分层资产建模、超级表设计、时序数据模拟及端到端自动化加载与执行。
metadata:
  author: Wang Zhe
  version: 0.3.0
  owner_team: solution-center
---

# IDMP 示例数据生成与自动执行工具

根据业务场景描述，自动完成资产建模、JSON 配置生成、单位校验和 API 推送，将模拟数据加载到 IDMP 系统。

## 输入要求

| 参数 | 场景 Demo 生成 (类别 1) | 业务数据接入 (类别 2) | 说明 |
|:--- |:--- |:--- |:--- |
| **项目根目录路径** | ✅ **必传** | ✅ **必传** | 本次任务的绝对路径，所有产物需存入其 `outputs/` |
| **行业调研路径** | ✅ **必传** | — | `outputs/industry_research.md` 的绝对路径 |
| **原始数据/结构文件**| — | ✅ **必传** | 用户提供的 CSV、Excel 或 Markdown 格式的结构定义 |

**目录规范要求**：
- 过程中生成的 Python 脚本必须存放在项目根目录下的 `scripts/`。
- 最终产物（`sample_data.json` 等）必须存放在项目根目录下的 `outputs/`。

---

## 常见陷阱（Gotchas）

> 以下规则是 Agent 在没有明确提示时最容易出错的地方，执行前必须阅读。

**超级表设计**
- 严格遵循"同类设备一张超级表"原则。不同采集指标的设备必须拆分为独立超级表，切勿合并，否则会产生大量 NULL 值。

**namingPattern 固定值**
- 所有 `templates` 中的 `namingPattern` 固定为 `${KEYWORD1}`，不得修改。
- `super_tables` 中的 `tags` 数组必须包含 `namingPattern` 参数，值固定为 `${KEYWORD1}`。

**资产命名与子表名唯一性**
- `trees` 节点中的 `values`（资产显示名称）和 `child_table_names`（子表物理名）必须在全局范围内保持唯一。
- 严禁在不同的行政层级或工艺段下使用重复的名称（例如：禁止在“A 线”和“B 线”中同时出现名称为“冲压机-1”的设备）。
- **强制规范**：如果不同块中使用相同的设备模板，必须通过添加父级上下文前缀（如 `"values": ["灌装线1-泵-1", "灌装线1-泵-2"]`）或使用全局递增序列来确保名称不重复。

**树状结构与 Tag 映射**
- `tree_root` 中的 `tag_name` 必须设为对应超级表 `tags` 数组的**第一个** tag 名称。
- `children` 节点中必须为超级表中**除第一个 tag 之外的所有其他 tag** 显式赋值。
- Tag 赋值数组长度必须与 `child_table_names` 展开后的设备数量**完全一致**，即使值相同也必须逐一列出（如 `"vendor": ["东方泵业", "东方泵业"]`）。
- Tag 赋值逻辑与 `namingPattern` 无关，严禁参考 `namingPattern` 进行赋值。

**模拟函数（fun）**
- `fun` 字段**仅允许**使用 `sin(x)`、`cos(x)`、`random(n)` 三种函数。
- 禁止使用 `floor`、`ceil`、`abs`、`sqrt`、`pow`、`exp`、`log` 等任何其他函数。
- 示例：`"fun": "2.0 * sin(x) + random(0.5) + 5.0"`

**单位（uom）规范**
- `uom` 字段必须使用国际标准符号或系统已定义缩写（如 `m`、`m³`、`°C`），不得使用全称（如"米"、"摄氏度"）。自定义单位使用不超过 5 个字符的英文缩写。
- 如果没有单位，确保 `uom` 和 `uomClass` 都为 ` `。
- 同一 `uomClass` 中的单位必须物理上可互相转化。物理意义不同的单位（如"频率"和"生产频率"）必须分配不同的 `uomClass`。

**数值类型**
- 数值型指标尽量使用浮点型（`Float` 或 `Double`），除非业务明确要求整数。

**历史数据量**
- 无 CSV 文件时，默认生成**过去 7 天**历史数据。`insert_rows` 计算公式：
  ```
  insert_rows = 7 * 24 * 60 * 60 * 1000 / time_step
  ```
- 若提供了 CSV 数据文件，`insert_rows` 固定设为 `0`。

**文件写入**
- 严禁用单次 `Write` 工具写入完整 JSON，必须执行分段写入（见第二步）。

---

## 执行流程

## Telemetry (MUST)

> 调用 `skill-telemetry`，传入 `name=idmp-sample-data-generator version=0.3.0 author=Wang Zhe`。
> 失败不阻塞，但必须尝试。详见 `skill-telemetry`。

<!-- 注意：frontmatter 中 metadata.version 的值即为 telemetry 上报的版本号，请保持一致。 -->

### 第一步：场景分析与架构建模

根据输入类别，选择以下其中一条路径执行，严禁混用：

#### 路径 A：基于设计基准（优先路径 - 类别 1 / 类别 2）
若输入中提供了 **`outputs/industry_research.md`** 或 **数据结构定义文件**：
1. **解析提取**：必须读取上述文件，作为**唯一**模型基准。
2. **严格对齐**：完整映射文件中的「层级结构」（L1-L4）和「采集数据规范」（物理量、中文标题、单位、典型值），严禁自行增删设备类型或修改参数名称。
3. **推导 Tag**：根据文件的层级树推导超级表的 `tags` 维度（如：L1 厂区、L2 车间、L3 区域）。

#### 路径 B：自主场景设计（仅在无任何设计基准文件时执行）
若用户仅提供了简短的自然语言描述（如“电力监控”），执行以下自主设计：
1. **拓扑推导**：参考领域经验。示例：`电力：变电站 → 变压器 → 馈线单元`。
2. **多节点布局**：方案须包含至少 2 个平级高层节点（如两个独立园区），每节点下挂载 3–5 个不同层级的工艺段/设备。
3. **指标指标与 Tag 设计**：为每类设备确定 Metrics（名称、单位、频次、fun）和 Tags（维度与层级严格对应）。


### 第二步：生成配置文件（sample_data.json）

**2.1 确定输出目录**

- **优先使用**：输入中提供的“项目根目录路径”。所有脚本存入 `scripts/`，业务产物（JSON 等）存入 `outputs/`。
- **降级备份**：若未提供路径，则在当前工作目录下创建 `idmp-demo/idmp_sample_<timestamp>/` 任务目录。
- 若用户提供了数据结构文件或 CSV 文件，将其拷贝到任务目录。

**2.2 读取模板（执行前必须完成）**

读取 `templates/idmp_sample_data_v1.json`，获取完整 JSON 结构参考及 `__doc__` 节点中的命名规范。JSON 需包含的核心模块：`info`、`TDasset`、`datasource`、`databases`、`templates`、`tree_root`、`trees`。

若存在 `outputs/industry_research.md`，JSON 中的资产层级、超级表、指标、标签必须与该文档完全一致，不得有文档有描述但 JSON 缺失、或参数与文档冲突的情况。

**2.3 分段写入 JSON（严禁单次写入完整文件）**

| 段 | 写入内容 | mode |
|----|----------|------|
| 第一段 | `info`、`TDasset`、`datasource`、`databases` 字段，直到 `"templates": [` 开头 | `overwrite` |
| 中间段（每张超级表一段） | `templates` 数组中每个 template 对象（含 `super_tables` 和 `metrics`），段间注意 JSON 逗号正确性，末尾 template 不加逗号 | `append` |
| 最后一段 | `tree_root`、`trees` 字段及 JSON 闭合括号 `}` | `append` |

**2.4 写入后完整性验证（分段写入后强制执行，两步均不可跳过）**

**第一步：JSON 语法验证**

```bash
python3 -c "import json; json.load(open('<文件路径>'))" && echo "JSON OK"
```

若失败，必须修复文件直到语法验证通过。

**第二步：⚠️ 强制字段校验（语法验证通过后必须立即执行）**

调用 `/scripts/validate_sample_data.py` 检查生成的json文件

- 若输出 `[OK]`：校验通过，继续执行下一步
- 若输出 `[FAIL]`：**必须逐条修正所有错误后，重新运行脚本直到输出 `[OK]`，严禁带错误进入第三步**


### 第三步：CSV 数据预处理（仅在用户提供 CSV 文件时执行）

无 CSV 文件时直接跳过，进入第四步。

1. **保留原文件**：先创建原始 CSV 的副本，后续所有操作在副本上进行，严禁修改原始文件。
2. **补全表头**：若副本 CSV 无表头，根据 `sample_data.json` 中对应超级表的 `metrics` 和 `tags` 定义自动添加。
3. **添加 tbname 列**：遍历 JSON 中 `trees` 节点的 `child_table_names`，将展开后的子表名逐行填入 `tbname` 列，确保数据行与子表名一一对应。
4. **补全标签列**：检查 `sample_data.json` 中定义的所有标签列是否在副本 CSV 中存在；若缺失，根据 `trees` 节点中该设备的标签值自动填充。

---

### 第四步：API 推送执行

> 所有接口调用默认使用 `curl` 命令在 bash 环境中执行。

**4.1 身份认证**

```
POST /api/v1/users/login
Content-Type: application/json
Body: {"login_name": "<用户名>", "password": "<密码>"}
```

获取返回的 `token`，后续所有请求均使用 `Authorization: Bearer <token>`。

**4.2 单位确认与处理**

调用 `scripts/uom_check.py`（需传入 IDMP 登录参数与 `sample_data.json` 路径）。该脚本会自动处理“匹配系统现有单位并更新 JSON”以及“创建缺失的单位分类”等逻辑。

运行命令示例：
```bash
python3 scripts/uom_check.py --state outputs/state.json --sample_data outputs/sample_data.json
```

根据脚本输出的表格，若仍存在 **"待处理"** 状态的条目（即：单位分类已存在，但该分类下缺少特定单位缩写），需按以下步骤手动补全：

1. **创建缺失单位**：
   针对每一行“待处理”条目，调用 API：
   - **URL**: `POST /api/v1/uomclasses/{uomClass id}/uom`
   - **Body**: 参考 `templates/uom_template.json` 构造和说明，编写 uom 的 json 文件。
   - **数据来源**：从脚本输出表格中提取 `uomClass id`、`uom` 和 `基础单位id`。

2. **验证**：
   完成后必须**再次调用** `uom_check.py`，确认输出为“检测完成，所有单位配置均已生效或已自动修复，无需手动处理”后，方可继续。

**4.3 名称查重与自动修复**

在上传前，必须检查示例名称及元素模板名称是否与系统中已有的条目冲突。

调用 `scripts/duplicate_check.py`：
```bash
python3 scripts/duplicate_check.py --state outputs/state.json --sample_data outputs/sample_data.json
```

该脚本执行以下检查：
1. **元素模板量**：调用 `GET /api/v1/templates/elements`，对比 `sample_data.json` 中 `templates` 的 `name`。
2. **示例数据名**：调用 `GET /api/v1/samples/management`，对应 `info.name`。

**冲突处理**：
若发现重名，脚本会自动在 `sample_data.json` 对应名称后添加 `_1`, `_2` 等递增后缀，并同步更新 `trees` 中的模板引用。

**4.4 上传并加载示例数据**

调用 `scripts/upload_sample.py`：

```bash
python3 scripts/upload_sample.py --state outputs/state.json --sample_data outputs/sample_data.json
```

该脚本执行以下集成操作：
1. **自动获取 Token**：完成身份认证。
2. **生成占位图**：自动在 JSON 同级目录下生成 API 所需的空 `placeholder.jpg`。
3. **上传数据**：构造 Multipart 请求并上传 `sample_data.json` 与占位图。
4. **触发加载**：上传成功后自动调用 `POST /api/v1/samples/{id}` 接口。
5. **轮询状态**：自动轮询进度，直到状态为 **`LOADED`** 或 **`GENERATING` 且进度百分比 > 30%** 时判定为成功。
6. **自动异常处理**：若加载或轮询阶段发生错误，脚本会**自动调用删除接口**并验证清除结果，确保系统中不留残留 ID。

**失败处理**：
若 4.4 执行出错，直接根据错误信息调整 `sample_data.json` 或环境后，再次重新执行步骤 4.4 即可（无需手动清理 ID）。

**4.5 重试上限**

- 最多重试 **5 次**（清理 + 重新上传算一次）
- 超过 5 次必须**立即停止**，不得继续尝试，并向用户输出：
  - 最后一次错误的完整 HTTP 响应（状态码 + body）
  - 已执行的重试次数
  - 建议的排查方向


### 第五步：反馈执行状态

第四步完成后向用户输出：
- 示例数据的 ID 和名称
- **资产树结构概览**：调用 `idmp-structure-exporter` 目录下的脚本完成资产树导出。运行命令： `python3 export_idmp_tree.py --state outputs/state.json --sample-data outputs/sample_data.json --root-name <示例名称>`。必须执行此步骤过滤根节点，严禁输出全系统资产树。
- 已创建的数据库、超级表和子表信息
- 生成数据的时间范围和数据量

---

## 配置完整性检查清单

- [ ] **fun 类型匹配**：`fun` 返回值符合对应 `type`（Float/Double 直接使用；Int 结果须为整数表达式；Bool 须返回 0/1）
- [ ] **设计基准一致**：JSON 与 `outputs/industry_research.md`（若存在）或第一步分析结果完全一致（层级、超级表、指标、标签均不得增删）

