# taosgen Config Generation Reference

This reference provides detailed guidance for generating taosgen YAML configurations.

## Configuration Structure

```yaml
# Global settings
tdengine:
  dsn: "${TAOSGEN_DSN:-taos+ws://root:taosdata@localhost:6041/tsbench}"
  drop_if_exists: false
  props: "precision ms vgroups 4"
  pool:
    enabled: true
    max_size: 100
    min_size: 2
    timeout: 1000

mqtt:
  uri: "tcp://localhost:1883"
  user: "${MQTT_USER:-}"
  password: "${MQTT_PASS:-}"
  client_id: "taosgen"
  keep_alive: 5
  clean_session: true
  max_buffered_messages: 10000

kafka:
  bootstrap_servers: "localhost:9092"
  client_id: "taosgen"
  topic: "test-topic"
  rdkafka_options:
    security.protocol: "plaintext"

# Schema definition
schema:
  name: "meters"
  tbname:
    prefix: "d"
    count: 10000
    from: 0
  tags:
    - name: groupid
      type: INT
      gen_type: random
      min: 1
      max: 10
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
  generation:
    interlace: 0
    rows_per_table: 10000
    rows_per_batch: 10000
    num_cached_batches: 10000
    tables_reuse_data: true

# Jobs (DAG)
jobs:
  create-db:
    name: "Create Database"
    needs: []
    steps:
      - name: "Create database"
        uses: tdengine/create-database
        with:
          database: "tsbench"

  create-stables:
    name: "Create Super Tables"
    needs: [create-db]
    steps:
      - name: "Create super table"
        uses: tdengine/create-super-table
        with:
          database: "tsbench"
          name: "meters"

  create-tables:
    name: "Create Child Tables"
    needs: [create-stables]
    steps:
      - name: "Create child tables"
        uses: tdengine/create-child-table
        with:
          database: "tsbench"
          batch:
            size: 1000
            concurrency: 10

  insert-data:
    name: "Insert Data"
    needs: [create-tables]
    steps:
      - name: "Write data"
        uses: tdengine/insert
        with:
          database: "tsbench"
          format: stmt
          concurrency: 8
```

## Data Types

### Supported Types

| Category | Types |
|----------|-------|
| Integer | `timestamp`, `bool`, `tinyint`, `tinyint unsigned`, `smallint`, `smallint unsigned`, `int`, `int unsigned`, `bigint`, `bigint unsigned` |
| Float | `float`, `double`, `decimal` |
| String | `nchar`, `varchar` (binary) |

**Not supported**: `json`, `geometry`, `varbinary`, `blob`

## Data Generation Types

### random

```yaml
- name: current
  type: FLOAT
  gen_type: random
  distribution: uniform  # Currently only uniform
  min: 0.0
  max: 100.0
  # OR use values list:
  values: ["value1", "value2", "value3"]
```

### order

```yaml
- name: id
  type: INT
  gen_type: order
  min: 1
  max: 1000000
```

### expression (Lua)

```yaml
- name: voltage
  type: FLOAT
  gen_type: expression
  expr: "220 + 10 * math.sin(_i / 10)"
```

**Built-in variables**:
- `_i`: Call index, starting from 0
- `_table`: Table name
- `_last`: Last returned value (numeric types only, initial 0.0)

**Example complex expression**:
```lua
(math.sin(_i / 7) * math.cos(_i / 13) + 0.5 * (math.random(80, 120) / 100)) *
((_i % 50 < 25) and (1 + 0.3 * math.sin(_i / 3)) or 0.7) +
10 * (math.floor(_i / 100) % 2)
```

## CSV Data Source

```yaml
schema:
  from_csv:
    tags:
      file_path: "./tags.csv"
      has_header: true
      tbname_index: 2
      exclude_indices: "0"  # Exclude column 0
    columns:
      file_path: "./data.csv"
      has_header: true
      repeat_read: false
      tbname_index: 0
      timestamp_index: 1
      timestamp_precision: "ms"
      timestamp_offset:
        offset_type: relative  # or "absolute"
        value: "+10s"  # or timestamp value for absolute
```

## Actions

### tdengine/create-database

Creates a TDengine database.

```yaml
- uses: tdengine/create-database
  with:
    database: "tsbench"
    checkpoint:
      enabled: true
      interval_sec: 60
```

### tdengine/create-super-table

Creates a super table (STable).

```yaml
- uses: tdengine/create-super-table
  with:
    database: "tsbench"
    name: "meters"
    # Can override schema here
```

### tdengine/create-child-table

Creates child tables.

```yaml
- uses: tdengine/create-child-table
  with:
    database: "tsbench"
    batch:
      size: 1000
      concurrency: 10
```

### tdengine/insert

Inserts data into tables.

```yaml
- uses: tdengine/insert
  with:
    database: "tsbench"
    format: stmt  # or "sql"
    auto_create_table: false
    concurrency: 8
    failure_handling:
      max_retries: 3
      retry_interval_ms: 1000
      on_failure: skip  # or "exit"
    time_interval:
      enabled: true
      interval_strategy: fixed  # "first_to_first", "last_to_first", "literal"
      fixed_interval:
        base_interval: 300000  # ms
      dynamic_interval:
        min_interval: -1
        max_interval: -1
      wait_strategy: sleep  # or "busy_wait"
    checkpoint:
      enabled: true
      interval_sec: 60
```

### mqtt/publish

Publishes data to MQTT broker.

```yaml
- uses: mqtt/publish
  with:
    format: json
    concurrency: 8
    topic: "factory/{table}/{location}"  # Dynamic topic with placeholders
    qos: 1  # 0, 1, or 2
    retain: false
    tbname_key: "table"  # JSON field name for table name
    records_per_message: 1
    # Also supports failure_handling and time_interval
```

**Topic placeholders**:
- `{table}`: Table name
- `{column}`: Column value (replace 'column' with actual column name)

### kafka/produce

Produces data to Kafka.

```yaml
- uses: kafka/produce
  with:
    concurrency: 8
    key_pattern: "{table}"  # Dynamic key
    key_serializer: "string-utf8"  # or int8, int16, int32, int64, uint8, uint16, uint32, uint64
    value_serializer: "json"  # or "influx"
    acks: "1"  # "0", "1", or "all"
    compression: "none"  # "gzip", "snappy", "lz4", "zstd"
    tbname_key: "table"
    records_per_message: 1
    # Also supports failure_handling and time_interval
```

## Time Offset Format

For `timestamp_offset` with `offset_type: relative`:

| Unit | Meaning |
|------|---------|
| y | Years |
| m | Months |
| d | Days |
| s | Seconds |

Examples:
- `"+1d3h"`: Add 1 day and 3 hours
- `"-30m"`: Subtract 30 minutes
- `"+1y6m"`: Add 1 year and 6 months

## Best Practices

1. **Use connection pool**: Enable `tdengine.pool.enabled: true` for better performance
2. **Batch size**: Use `rows_per_batch: 10000` for optimal throughput
3. **Concurrency**: Adjust `concurrency` based on CPU cores (typically 4-16)
4. **Interlace**: Use `interlace: 100` for more realistic multi-table scenarios
5. **Time interval**: Enable for simulating real-time data ingestion
