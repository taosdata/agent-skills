# Taosgen Skills 方案 Review

基于官方文档和示例文件的完整对比分析

## 文档来源
- 中文文档: `/opt/source/TDengine/docs/zh/14-reference/02-tools/11-taosgen.md`
- 英文文档: `/opt/source/TDengine/docs/en/14-reference/02-tools/11-taosgen.md`
- 示例配置: `/opt/source/TDengine/docs/examples/taosgen/taosgen_config.yaml`
- 更多示例: `/opt/source/tsgen/conf/`

---

## 一、当前方案符合的部分 ✅

### 1. 顶层结构
- [x] tdengine / mqtt / kafka / schema / jobs 五个主要部分

### 2. TDengine 配置
- [x] dsn, drop_if_exists, props, pool
- [x] pool.enabled, pool.max_size, pool.min_size, pool.timeout

### 3. MQTT 配置
- [x] uri, user, password, client_id, keep_alive, clean_session, max_buffered_messages

### 4. Kafka 配置
- [x] bootstrap_servers, client_id, topic, rdkafka_options

### 5. Schema 配置
- [x] name, tbname (prefix, count, from), tags, columns, generation
- [x] tbname.from 使用整数（不是字符串）

### 6. 列配置
- [x] name, type (支持 binary(n) 和 varchar(n))
- [x] min/max (random), values (random from list), expr (expression)
- [x] timestamp: start, precision, step

### 7. Generation 配置
- [x] interlace, rows_per_table, rows_per_batch, num_cached_batches, tables_reuse_data

### 8. Actions
- [x] tdengine/create-database, tdengine/create-super-table, tdengine/create-child-table, tdengine/insert
- [x] mqtt/publish, kafka/produce

---

## 二、遗漏和不一致 ❌

### 1. schema.generation.concurrency ⚠️ 重要遗漏

**文档原文**:
> concurrency（整数）：表示生成数据的线程数量，默认值为写入线程数量。

**示例** (`mqtt_publish_config`):
```yaml
schema:
  generation:
    interlace: 1
    concurrency: 8    # <-- 遗漏！
    rows_per_table: 10000
    rows_per_batch: 10000
```

**影响**: MQTT/Kafka 场景中常用

### 2. tdengine/create-database 支持 checkpoint ⚠️ 遗漏

**文档原文**:
> - checkpoint：描述写入数据中断/恢复功能相关配置参数

**示例** (`tdengine-gen-checkpoint.yaml`):
```yaml
jobs:
  insert-data:
    steps:
      - uses: tdengine/create-database
        with:
          checkpoint:
            enabled: true
            interval_sec: 10
```

**影响**: 断点续传功能需要在 create-database 时配置

### 3. time_interval 在 mqtt/publish 和 kafka/produce 中的支持 ⚠️ 遗漏

**文档原文**:
> - time_interval：参数说明请参考 [写入 TDengine 数据行动的格式] 中的同名参数。

**示例** (`mqtt-gen-ev-realtime.yaml`):
```yaml
jobs:
  publish-data:
    steps:
      - uses: mqtt/publish
        with:
          concurrency: 1
          topic: ev/{table}
          qos: 0
          time_interval:
            enabled: true
            interval_strategy: literal
```

### 4. step 格式 ⚠️ 不完整

**文档原文**:
> - step（整数）：表示时间戳的步长

**实际示例支持**:
```yaml
# 可以是整数
step: 1

# 也可以是字符串（带单位）
step: 300s    # <-- 支持单位！
step: 1s      # <-- 支持单位！
```

### 5. 列的 count 属性 ⚠️ 遗漏

**文档原文**:
> - count（整数）：表示指定该类型的列连续出现的数量，例如 count：4096 即可生成 4096 个指定类型的列。

**示例**:
```yaml
columns:
  - name: current
    type: float
    count: 4096   # 生成 current1 到 current4096
    min: 0
    max: 100
```

### 6. random distribution ⚠️ 遗漏（但很少用）

**文档原文**:
> - distribution（字符串）：表示随机数的分别模型，目前仅支持均匀分布，后续按需扩充，默认值为 "uniform"。

### 7. 列的 props 属性 ⚠️ 遗漏（但很少用）

**文档原文**:
> - props（字符串）：表示 TDengine 数据库的列支持的属性信息
>   - encode：指定此列两级压缩中的第一级编码算法。
>   - compress：指定此列两级压缩中的第二级加密算法。
>   - level：指定此列两级压缩中的第二级加密算法的压缩率高低。

### 8. rows_per_table = -1 ⚠️ 遗漏

**文档原文**:
> rows_per_table（整数），每个数据表写入的行数，默认值为 10000，-1 表示无限数据。

**示例** (`mqtt-gen-ev-realtime.yaml`):
```yaml
generation:
  rows_per_table: -1   # 无限数据
```

### 9. timestamp start 格式 ⚠️ 不完整

**实际示例支持**:
```yaml
# 可以是字符串
type: timestamp
start: "1700000000000"   # 字符串

# 也可以是关键字
start: now               # 关键字
start: now + 10s         # 关键字 + 偏移
```

---

## 三、关键修复建议

### Priority 1: 必须修复

1. **添加 schema.generation.concurrency**
2. **添加 tdengine/create-database 的 checkpoint 支持**
3. **添加 mqtt/publish 和 kafka/produce 的 time_interval 支持**
4. **支持 rows_per_table = -1**

### Priority 2: 建议添加

5. **支持 step 的字符串格式（带单位）**
6. **支持 timestamp start 为字符串（时间戳值）**
7. **添加列的 count 属性**

### Priority 3: 可选添加

8. **列的 distribution 和 props**（高级特性，很少使用）

---

## 四、完整更新的参数结构

### schema.generation

```yaml
generation:
  interlace: 0              # 整数 >= 0
  concurrency: 8            # 整数，数据生成线程数（MQTT/Kafka常用）
  rows_per_table: 10000     # 整数 >= 1 或 -1（无限）
  rows_per_batch: 10000     # 整数 >= 1
  num_cached_batches: 0     # 整数 >= 0，0=禁用
  tables_reuse_data: true   # 布尔
```

### 列配置

```yaml
columns:
  - name: current
    type: float
    count: 1              # 整数，列重复次数（默认1）
    min: 0.0              # random
    max: 100.0            # random
    # OR
    values: ["a", "b"]    # random from list
    # OR
    expr: "math.sin(_i)"  # expression

  - name: ts
    type: timestamp
    start: now            # "now" / "now + 10s" / "1700000000000"
    precision: ms         # s / ms / us / ns
    step: 1               # 整数 或 "300s" / "1s"
```

### Actions

```yaml
# tdengine/create-database 支持 checkpoint
- uses: tdengine/create-database
  with:
    checkpoint:
      enabled: true
      interval_sec: 60

# mqtt/publish 支持 time_interval
- uses: mqtt/publish
  with:
    concurrency: 8
    topic: "test/{table}"
    qos: 1
    time_interval:
      enabled: true
      interval_strategy: literal  # fixed / first_to_first / last_to_first / literal

# kafka/produce 支持 time_interval
- uses: kafka/produce
  with:
    concurrency: 8
    acks: "1"
    time_interval:
      enabled: true
      interval_strategy: fixed
      fixed_interval:
        base_interval: 1000
```

---

## 五、验证建议

1. **使用官方示例验证**: 确保所有官方示例都能通过 schema 验证
2. **错误提示**: 当生成无效配置时，给出明确的错误信息
3. **未知参数检测**: 使用 `additionalProperties: false` 严格拒绝未知参数
