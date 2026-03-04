# taosgen Config Generation Reference

This reference provides detailed guidance for generating taosgen YAML configurations.

## Configuration Structure

```yaml
# Global settings
tdengine:
  dsn: "taos+ws://root:taosdata@localhost:6041/tsbench"
  drop_if_exists: false
  props: "precision 'ms' vgroups 4"
  pool:
    enabled: true
    max_size: 100
    min_size: 2
    timeout: 1000

mqtt:
  uri: "tcp://localhost:1883"
  user: ""
  password: ""
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
      type: int
      min: 1
      max: 10
  columns:
    - name: ts
      type: timestamp
      start: now + 10s
      precision: ms
      step: 1
    - name: current
      type: float
      min: 0.0
      max: 100.0
  generation:
    interlace: 0
    rows_per_table: 10000
    rows_per_batch: 10000
    tables_reuse_data: true

# Jobs (single job with steps for sequential execution)
jobs:
  insert-data:
    steps:
      - uses: tdengine/create-super-table
      - uses: tdengine/create-child-table
        with:
          batch:
            size: 1000
            concurrency: 10
      - uses: tdengine/insert
        with:
          concurrency: 8
```

## Data Types

### Supported Types

| Category | Types |
|----------|-------|
| Integer | `timestamp`, `bool`, `tinyint`, `tinyint unsigned`, `smallint`, `smallint unsigned`, `int`, `int unsigned`, `bigint`, `bigint unsigned` |
| Float | `float`, `double`, `decimal` |
| String | `nchar`, `varchar(n)`, `binary(n)` |

**Not supported**: `json`, `geometry`, `varbinary`, `blob`

**Note**: For string types with length, use `binary(24)` or `varchar(50)` format (length in parentheses).

## Data Generation Types

Data generation type is inferred from the presence of specific keys. Do NOT use `gen_type:` prefix.

### random (inferred from min/max or values)

```yaml
- name: current
  type: float
  min: 0.0
  max: 100.0

# OR with values list:
- name: location
  type: binary(24)
  values:
    - "California.Campbell"
    - "Texas.Austin"
    - "NewYork.NewYorkCity"
```

### order (inferred from min/max on integer/timestamp types)

```yaml
- name: id
  type: int
  min: 1
  max: 1000000

# Timestamp with step:
- name: ts
  type: timestamp
  start: now + 10s
  precision: ms
  step: 1
```

### expression (inferred from expr key)

```yaml
- name: voltage
  type: float
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

## Generation Control

```yaml
schema:
  generation:
    interlace: 0           # 0 = disable, >0 = interlace rows count
    rows_per_table: 10000  # Rows per table
    rows_per_batch: 10000  # Rows per batch request
    tables_reuse_data: true
```

**Note on num_cached_batches**: This parameter is automatically calculated. If manually specified, it cannot exceed the number of batches needed (rows_per_table / rows_per_batch).

## Actions

Actions are specified in `jobs.<job_name>.steps`. For sequential execution, use a single job with multiple steps.

### Simple Sequential Job Structure

```yaml
jobs:
  insert-data:
    steps:
      - uses: tdengine/create-super-table
      - uses: tdengine/create-child-table
        with:
          batch:
            size: 1000
            concurrency: 10
      - uses: tdengine/insert
        with:
          concurrency: 8
```

### tdengine/create-super-table

Creates a super table (STable). Uses global schema configuration.

```yaml
- uses: tdengine/create-super-table
```

### tdengine/create-child-table

Creates child tables.

```yaml
- uses: tdengine/create-child-table
  with:
    batch:
      size: 1000
      concurrency: 10
```

### tdengine/insert

Inserts data into tables.

```yaml
- uses: tdengine/insert
  with:
    concurrency: 8
    format: stmt  # or "sql"
    auto_create_table: false
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
    concurrency: 8
    topic: "factory/{table}/{location}"  # Dynamic topic with placeholders
    qos: 1  # 0, 1, or 2
    retain: false
    tbname_key: "table"
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

## Connection Configuration

### TDengine

```yaml
tdengine:
  dsn: "taos+ws://root:taosdata@localhost:6041/tsbench"
  drop_if_exists: false
  props: "precision 'ms' vgroups 4"  # Note: precision value in single quotes
  pool:
    enabled: true
    max_size: 100
    min_size: 2
    timeout: 1000
```

**Important**: Use direct string for DSN, not environment variable syntax.

### MQTT

```yaml
mqtt:
  uri: "tcp://localhost:1883"
  user: ""
  password: ""
  client_id: "taosgen"
  keep_alive: 5
  clean_session: true
  max_buffered_messages: 10000
```

### Kafka

```yaml
kafka:
  bootstrap_servers: "localhost:9092"
  client_id: "taosgen"
  topic: "test-topic"
  rdkafka_options:
    security.protocol: "plaintext"
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
3. **Concurrency**: Adjust based on CPU cores (typically 4-16)
4. **Interlace**: Use `interlace: 100` for more realistic multi-table scenarios
5. **Simple jobs**: For sequential execution, use single job with multiple steps instead of DAG dependencies
6. **String types**: Always specify length in parentheses, e.g., `binary(24)`, `varchar(50)`
7. **Data generation**: Omit `gen_type`, let system infer from presence of `min/max`, `expr`, or `values`
8. **DSN format**: Use direct string, not environment variable reference
9. **Props format**: Use single quotes around precision value, e.g., `precision 'ms'`
