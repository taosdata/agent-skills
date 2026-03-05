# taosgen Config Generation Reference

This reference provides detailed guidance for generating taosgen YAML configurations.

> **IMPORTANT**: To avoid generating invalid parameters, use the code-based approach defined in `scripts/generator.py` and validate against `scripts/schema.json`.

## Rigorous Generation Method

### Using Python Script

```python
from scripts.generator import (
    generate_smart_meters_tdengine,
    generate_smart_meters_mqtt,
    generate_smart_meters_kafka,
    generate_yaml,
    save_config,
    validate_config
)

# Generate config
config = generate_smart_meters_tdengine(
    host="localhost",
    port=6041,
    database="tsbench",
    table_count=1000,
    rows_per_table=10
)

# Validate
errors = validate_config(config, "tdengine")
if errors:
    print("Validation errors:", errors)
else:
    # Save
    path = save_config(config, "tdengine", "smart-meters")
    print(f"OutputPath: {path}")
```

### Using JSON Schema Validation

```python
import json
import yaml
from jsonschema import validate

# Load schema
with open('scripts/schema.json') as f:
    schema = json.load(f)

# Validate
config = yaml.safe_load(open('config.yaml'))
validate(instance=config, schema=schema)
```

## Configuration Structure

### TDengine Config (Valid Parameters ONLY)

```yaml
tdengine:
  dsn: "taos+ws://root:taosdata@localhost:6041/tsbench"  # REQUIRED
  drop_if_exists: false                                    # optional, default: false
  props: "precision 'ms' vgroups 4"                       # optional, note: 'ms' in single quotes
  pool:                                                    # optional
    enabled: true
    max_size: 100
    min_size: 2
    timeout: 1000
```

**Note**: The `props` field format: `precision 'ms' vgroups 4` - the precision value must be in single quotes.

### MQTT Config (Valid Parameters ONLY)

These are the ONLY valid parameters for MQTT (from official docs):

```yaml
mqtt:
  uri: "tcp://localhost:1883"      # REQUIRED - Broker URI
  user: ""                          # optional - Username
  password: ""                      # optional - Password
  client_id: "taosgen"              # optional - Client ID prefix, default: taosgen
  keep_alive: 5                     # optional - Keep alive in seconds, default: 5
  clean_session: true               # optional - Clean session flag, default: true
  max_buffered_messages: 10000      # optional - Max buffered messages, default: 10000
```

**INVALID parameters** (will cause taosgen to fail):
- ❌ `broker` - not supported, use `uri`
- ❌ `username` - not supported, use `user`
- ❌ `port` - include in `uri` (e.g., `tcp://localhost:1883`)
- ❌ `qos` - belongs in `mqtt/publish` action `with` section
- ❌ `retain` - belongs in `mqtt/publish` action `with` section
- ❌ `timeout` - not supported

### Kafka Config (Valid Parameters ONLY)

```yaml
kafka:
  bootstrap_servers: "localhost:9092"  # REQUIRED
  client_id: "taosgen"                  # optional, default: taosgen
  topic: "test-topic"                   # REQUIRED
  rdkafka_options:                      # optional
    security.protocol: "plaintext"      # options: plaintext, ssl, sasl_plaintext, sasl_ssl
    sasl.mechanism: "PLAIN"             # options: PLAIN, SCRAM-SHA-256, SCRAM-SHA-512, GSSAPI
    sasl.username: "user"
    sasl.password: "pass"
```

## Schema Definition

### tbname (Table Name Generation)

```yaml
schema:
  tbname:
    prefix: "d"        # default: "d"
    count: 10000       # default: 10000
    from: 0            # default: 0 (starting index)
```

### tags and columns

```yaml
schema:
  tags:     # Label columns (tag columns in TDengine)
    - name: groupid
      type: int
      min: 1
      max: 10
    - name: location
      type: binary(24)
      values:
        - "California"
        - "Texas"

  columns:  # Data columns
    - name: ts
      type: timestamp
      start: now
      precision: ms
      step: 1
    - name: current
      type: float
      min: 0.0
      max: 100.0
    - name: voltage
      type: int
      expr: "220 + 10 * math.sin(_i / 10)"
```

### Supported Data Types

| Category | Types |
|----------|-------|
| Integer | `timestamp`, `bool`, `tinyint`, `tinyint unsigned`, `smallint`, `smallint unsigned`, `int`, `int unsigned`, `bigint`, `bigint unsigned` |
| Float | `float`, `double`, `decimal` |
| String | `nchar`, `varchar(n)`, `binary(n)` |

**NOT supported**: `json`, `geometry`, `varbinary`, `decimal`, `blob`

### Data Generation (Inferred - NO gen_type field)

The generation type is **automatically inferred** from the presence of keys:

**1. Random with min/max** (for numeric types):
```yaml
- name: current
  type: float
  min: 0.0      # presence triggers random mode
  max: 100.0
```

**2. Random from values** (for string types):
```yaml
- name: location
  type: binary(24)
  values:       # presence triggers random mode with values
    - "California"
    - "Texas"
```

**3. Expression** (Lua script):
```yaml
- name: voltage
  type: float
  expr: "220 + 10 * math.sin(_i / 10)"  # presence triggers expression mode
```

**4. Order/Sequential** (for integers and timestamps):
```yaml
- name: id
  type: int
  min: 1        # for order, both min and max should be specified
  max: 1000000

- name: ts
  type: timestamp
  start: now    # presence triggers timestamp order mode
  precision: ms
  step: 1
```

**Built-in Lua variables**:
- `_i`: Call index, starting from 0
- `_table`: Table name
- `_last`: Last returned value (numeric types only, initial 0.0)

## Generation Control

```yaml
schema:
  generation:
    interlace: 0              # Control interlace rows, default: 0 (disabled)
    rows_per_table: 10000     # Rows per table, default: 10000
    rows_per_batch: 10000     # Rows per batch request, default: 10000
    num_cached_batches: 0     # Cached batches, default: 0 (disabled)
    tables_reuse_data: true   # Reuse data across tables, default: true
```

**Note on num_cached_batches**: If specified, cannot exceed `rows_per_table / rows_per_batch`.

## Jobs and Steps

### Simple Sequential Job (Recommended)

```yaml
jobs:
  insert:
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

### Valid Actions

| Action | Description |
|--------|-------------|
| `tdengine/create-database` | Create TDengine database |
| `tdengine/create-super-table` | Create super table (uses global schema) |
| `tdengine/create-child-table` | Create child tables |
| `tdengine/insert` | Insert data |
| `mqtt/publish` | Publish to MQTT |
| `kafka/produce` | Produce to Kafka |

### Action Parameters

#### tdengine/create-child-table

```yaml
- uses: tdengine/create-child-table
  with:
    batch:
      size: 1000        # Tables per batch
      concurrency: 10   # Concurrent batches
```

#### tdengine/insert

```yaml
- uses: tdengine/insert
  with:
    concurrency: 8
    format: stmt           # or "sql"
    auto_create_table: false
    failure_handling:
      max_retries: 3
      retry_interval_ms: 1000
      on_failure: skip     # or "exit"
    time_interval:
      enabled: true
      interval_strategy: fixed   # or "first_to_first", "last_to_first", "literal"
      fixed_interval:
        base_interval: 300000    # milliseconds
      wait_strategy: sleep       # or "busy_wait"
    checkpoint:
      enabled: true
      interval_sec: 60
```

#### mqtt/publish

```yaml
- uses: mqtt/publish
  with:
    concurrency: 8
    topic: "factory/{table}/{location}"  # Supports {table} and {column} placeholders
    qos: 1                        # 0, 1, or 2
    retain: false
    tbname_key: "table"
    records_per_message: 1
    # Also supports: failure_handling, time_interval
```

#### kafka/produce

```yaml
- uses: kafka/produce
  with:
    concurrency: 8
    key_pattern: "{table}"
    key_serializer: "string-utf8"   # or int8, int16, int32, int64, uint8, etc.
    value_serializer: "json"        # or "influx"
    acks: "1"                       # "0", "1", or "all"
    compression: "none"             # "gzip", "snappy", "lz4", "zstd"
    tbname_key: "table"
    records_per_message: 1
    # Also supports: failure_handling, time_interval
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
      tbname_index: 0
      timestamp_index: 1
      timestamp_precision: "ms"
      timestamp_offset:
        offset_type: relative  # or "absolute"
        value: "+10s"
      repeat_read: false
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

## Common Mistakes to Avoid

1. ❌ **Using `gen_type` field** - Generation type is inferred from presence of keys
2. ❌ **Using `len` for string types** - Use `type: binary(24)` format
3. ❌ **Using `broker` in MQTT** - Use `uri`
4. ❌ **Using `username` in MQTT** - Use `user`
5. ❌ **Putting `qos` in mqtt config** - Belongs in `mqtt/publish` action
6. ❌ **Using `per_table_rows`** - Use `rows_per_table`
7. ❌ **Using `per_batch_rows`** - Use `rows_per_batch`
8. ❌ **Missing quotes in props** - Use `precision 'ms'` not `precision ms`

## References

- `scripts/generator.py` - Python generator with strict parameter validation
- `scripts/schema.json` - JSON Schema for configuration validation
- Official docs: `/opt/source/TDengine/docs/zh/14-reference/02-tools/11-taosgen.md`
