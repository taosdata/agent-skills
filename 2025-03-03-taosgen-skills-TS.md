# 功能测试报告（Test Spec）- taosgen Skills

# 修订记录

| 编写日期 | 发布日期 | 版本 | 修订人 | 主要修改内容 |
| --- | --- | --- | --- | --- |
| 2025-03-03 | - | 0.1.0 | Agent | 初始版本，定义 taosgen skills 测试用例 |

# 测试目标

验证 taosgen-config 和 taosgen-run skills 的功能正确性、易用性和安全性：

1. 配置生成功能：能够正确生成符合 taosgen 规范的 YAML 配置文件
2. 运行辅助功能：能够正确构建运行命令并检查环境
3. 场景覆盖：支持 TDengine、MQTT、Kafka 三种目标类型
4. 安全合规：敏感信息处理符合安全要求

# 参考文档

1. RS: 2025-03-03-taosgen-skills-RS.md
2. FS: 2025-03-03-taosgen-skills-FS.md
3. taosgen 官方文档
4. Agent Skills 规范

# 测试结论

[待测试完成后填写]

# 测试环境

- OS: Linux (Ubuntu 22.04), macOS (14.x)
- taosgen version: 0.3.0+
- TDengine version: 3.x
- cowork version: latest

# 功能测试

## 配置生成功能

### 测试要点

1. 支持三种目标类型（TDengine/MQTT/Kafka）的配置生成
2. 支持预设模板和自定义 Schema
3. 生成的 YAML 格式正确，可通过 taosgen 验证
4. 敏感信息使用环境变量占位符

### 用例列表

| # | 测试用例 | 测试描述 | 测试结果 |
| --- | --- | --- | --- |
| 1.1 | TDengine 基础配置生成 | 使用默认参数生成 TDengine 写入配置，验证 YAML 结构和必需字段 | [待执行] |
| 1.2 | MQTT 配置生成 | 生成向 MQTT Broker 发布数据的配置，验证 topic 动态占位符 | [待执行] |
| 1.3 | Kafka 配置生成 | 生成向 Kafka 生产数据的配置，验证序列化参数 | [待执行] |
| 1.4 | 自定义 Schema 配置 | 定义自定义 tags 和 columns，验证生成逻辑 | [待执行] |
| 1.5 | CSV 数据源配置 | 配置从 CSV 文件读取数据，验证 file_path 和索引参数 | [待执行] |
| 1.6 | Lua 表达式数据生成 | 使用 expression 类型生成数据，验证 expr 字段 | [待执行] |
| 1.7 | 敏感信息处理 | 检查密码是否使用 ${ENV_VAR} 格式，不硬编码实际值 | [待执行] |
| 1.8 | Jobs DAG 依赖 | 验证 needs 字段正确建立作业依赖关系 | [待执行] |
| 1.9 | 输出路径格式 | 验证输出格式为 `OutputPath: /absolute/path/to/file` | [待执行] |
| 1.10 | 配置头部注释 | 验证生成的 YAML 包含版本、时间戳等注释信息 | [待执行] |

## 运行辅助功能

### 测试要点

1. 正确检测 taosgen 安装状态
2. 正确构建运行命令
3. 支持参数覆盖
4. 提供清晰的运行建议

### 用例列表

| # | 测试用例 | 测试描述 | 测试结果 |
| --- | --- | --- | --- |
| 2.1 | taosgen 安装检查 | 检查已安装 taosgen 时返回版本信息 | [待执行] |
| 2.2 | taosgen 未安装提示 | 检查未安装 taosgen 时给出安装建议 | [待执行] |
| 2.3 | 基础命令生成 | 根据配置文件生成基本运行命令 | [待执行] |
| 2.4 | 参数覆盖 | 支持通过参数覆盖配置文件中的连接信息 | [待执行] |
| 2.5 | 环境变量引用 | 验证命令中保留环境变量占位符 | [待执行] |

## Skill 路由功能

### 测试要点

1. Router skill 正确识别用户意图
2. 正确路由到 config 或 run 子技能
3. 支持通过 slash command 直接调用子技能

### 用例列表

| # | 测试用例 | 测试描述 | 测试结果 |
| --- | --- | --- | --- |
| 3.1 | Router 识别 config 意图 | 用户说"生成 taosgen 配置"时路由到 config skill | [待执行] |
| 3.2 | Router 识别 run 意图 | 用户说"运行 taosgen"时路由到 run skill | [待执行] |
| 3.3 | 直接调用 config | 使用 `/taosgen-config` 直接调用配置生成技能 | [待执行] |
| 3.4 | 直接调用 run | 使用 `/taosgen-run` 直接调用运行辅助技能 | [待执行] |

# 易用性测试

测试用例包括但不局限于：

| # | 测试项目 | 测试描述 | 测试结果 |
| --- | --- | --- | --- |
| 4.1 | 交互流程 | 配置生成过程中每一步的提示是否清晰 | [待执行] |
| 4.2 | 默认值合理 | 提供的默认值是否适用于大多数场景 | [待执行] |
| 4.3 | 错误提示 | 输入无效值时的错误提示是否友好 | [待执行] |
| 4.4 | 配置预览 | 是否能在保存前预览配置摘要 | [待执行] |
| 4.5 | 示例提供 | 是否提供常见场景的示例配置 | [待执行] |

# 长期稳定性测试

不适用（本技能为配置生成工具，无长期运行需求）

# 性能测试

| # | 测试项目 | 测试描述 | 预期结果 | 测试结果 |
| --- | --- | --- | --- | --- |
| 5.1 | 简单配置生成速度 | 生成 <100 行的基础配置 | < 2 秒 | [待执行] |
| 5.2 | 复杂配置生成速度 | 生成 >500 行的复杂配置 | < 5 秒 | [待执行] |
| 5.3 | 配置验证速度 | 验证生成的配置格式 | < 1 秒 | [待执行] |

# 安全测试

| # | 测试项目 | 测试描述 | 测试结果 |
| --- | --- | --- | --- |
| 6.1 | 密码不硬编码 | 检查生成的配置中密码使用占位符 | [待执行] |
| 6.2 | 删除风险提示 | `drop_if_exists: true` 时是否显示警告 | [待执行] |
| 6.3 | 危险命令过滤 | 验证不生成包含危险 shell 命令的配置 | [待执行] |
| 6.4 | 路径安全检查 | 验证使用绝对路径，无路径遍历风险 | [待执行] |

# 兼容性测试

| # | 测试项目 | 测试描述 | 测试结果 |
| --- | --- | --- | --- |
| 7.1 | cowork audit 通过 | 运行 `cowork audit` 检查 skills | [待执行] |
| 7.2 | cowork verify 通过 | 运行 `cowork verify` 检查 skills | [待执行] |
| 7.3 | cowork test 通过 | 运行 `cowork test --check-conflicts` | [待执行] |
| 7.4 | taosgen 配置验证 | 使用 `taosgen --dry-run` 验证配置（如支持） | [待执行] |

# 已知问题和限制

1. **Windows 不支持**：taosgen 本身不支持 Windows，本 skill 也不支持
2. **TDengine 2.x 不支持**：仅支持 TDengine 3.x 版本
3. **实时验证依赖**：taosgen 的完整验证需要在运行时才进行

# 附录：测试数据

## 最小测试配置

```yaml
# test-minimal.yaml
schema:
  name: "test"
  tbname:
    count: 10
  generation:
    rows_per_table: 100

jobs:
  write:
    steps:
      - uses: tdengine/create-database
      - uses: tdengine/create-super-table
      - uses: tdengine/create-child-table
      - uses: tdengine/insert
```

## 完整测试配置

```yaml
# test-full.yaml
tdengine:
  dsn: "${TAOSGEN_DSN:-taos+ws://root:taosdata@localhost:6041/tsbench}"
  drop_if_exists: false
  props: "precision ms vgroups 4"
  pool:
    enabled: true
    max_size: 100
    min_size: 2
    timeout: 1000

schema:
  name: "meters"
  tbname:
    prefix: "d"
    count: 100
    from: 0
  tags:
    - name: groupid
      type: INT
      gen_type: random
      min: 1
      max: 10
    - name: location
      type: VARCHAR(24)
      gen_type: random
      values: ["California.Campbell", "Texas.Austin"]
  columns:
    - name: ts
      type: TIMESTAMP
      gen_type: order
      min: 1700000000000
    - name: current
      type: FLOAT
      gen_type: random
      min: 0.0
      max: 100.0
    - name: voltage
      type: INT
      gen_type: expression
      expr: "220 + 10 * math.sin(_i / 10)"
    - name: phase
      type: FLOAT
      gen_type: random
      min: 0.0
      max: 360.0
  generation:
    interlace: 0
    rows_per_table: 1000
    rows_per_batch: 1000
    num_cached_batches: 1000

jobs:
  create-db:
    name: "Create Database"
    needs: []
    steps:
      - name: "Create tsbench database"
        uses: tdengine/create-database
        with:
          database: "tsbench"

  create-stables:
    name: "Create Super Tables"
    needs: [create-db]
    steps:
      - name: "Create meters super table"
        uses: tdengine/create-super-table
        with:
          database: "tsbench"
          name: "meters"

  create-tables:
    name: "Create Child Tables"
    needs: [create-stables]
    steps:
      - name: "Batch create child tables"
        uses: tdengine/create-child-table
        with:
          database: "tsbench"
          batch:
            size: 100
            concurrency: 4

  insert-data:
    name: "Insert Data"
    needs: [create-tables]
    steps:
      - name: "Write data to meters"
        uses: tdengine/insert
        with:
          database: "tsbench"
          format: stmt
          concurrency: 4
          failure_handling:
            max_retries: 3
            retry_interval_ms: 1000
            on_failure: skip
```
