# taosgen Configuration Examples

This reference provides ready-to-use taosgen configuration examples for common scenarios.

## Example 1: Minimal TDengine Test

Simplest configuration for quick testing.

```yaml
# taosgen-config-tdengine-minimal.yaml
schema:
  name: "meters"
  tbname:
    count: 100
  generation:
    rows_per_table: 1000

jobs:
  write:
    name: "Write Test Data"
    steps:
      - uses: tdengine/create-database
      - uses: tdengine/create-super-table
      - uses: tdengine/create-child-table
      - uses: tdengine/insert
```

## Example 2: Smart Meters (Full Featured)

Classic smart meter scenario with 10,000 devices, each reporting every 5 minutes.

```yaml
# taosgen-config-tdengine-meters.yaml
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
    count: 10000
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
      values: ["California.Campbell", "Texas.Austin", "NewYork.NewYorkCity"]
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
    rows_per_table: 10000
    rows_per_batch: 10000
    num_cached_batches: 10000

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
            size: 1000
            concurrency: 10

  insert-data:
    name: "Insert Data"
    needs: [create-tables]
    steps:
      - name: "Write data to meters"
        uses: tdengine/insert
        with:
          database: "tsbench"
          format: stmt
          concurrency: 8
          time_interval:
            enabled: true
            interval_strategy: fixed
            fixed_interval:
              base_interval: 300000
```

## Example 3: CSV Data Import

Import data from existing CSV files.

```yaml
# taosgen-config-csv-import.yaml
tdengine:
  dsn: "${TAOSGEN_DSN:-taos+ws://root:taosdata@localhost:6041/tsbench}"
  drop_if_exists: false

schema:
  name: "meters"
  from_csv:
    tags:
      file_path: "./ctb-tags.csv"
      has_header: true
      tbname_index: 2
    columns:
      file_path: "./ctb-data.csv"
      has_header: true
      tbname_index: 0
      timestamp_index: 1
      timestamp_precision: "ms"
      timestamp_offset:
        offset_type: relative
        value: "+10s"
  tags:
    - name: groupid
      type: INT
    - name: location
      type: VARCHAR(24)
  columns:
    - name: ts
      type: TIMESTAMP
    - name: current
      type: FLOAT
    - name: voltage
      type: INT
    - name: phase
      type: FLOAT
  generation:
    rows_per_table: 10000
    rows_per_batch: 10000

jobs:
  import-data:
    name: "Import from CSV"
    steps:
      - uses: tdengine/create-database
      - uses: tdengine/create-super-table
      - uses: tdengine/create-child-table
      - uses: tdengine/insert
```

**ctb-tags.csv**:
```csv
groupid,location,tbname
1,California.Campbell,d1
2,Texas.Austin,d2
3,NewYork.NewYorkCity,d3
```

**ctb-data.csv**:
```csv
tbname,ts,current,voltage,phase
d1,1700000010000,5.23,221.5,146.2
d3,1700000010000,8.76,219.8,148.7
d2,1700000010000,12.45,223.1,147.3
```

## Example 4: MQTT Publishing

Publish generated data to MQTT broker.

```yaml
# taosgen-config-mqtt-publish.yaml
mqtt:
  uri: "tcp://localhost:1883"
  user: "${MQTT_USER:-}"
  password: "${MQTT_PASS:-}"
  client_id: "taosgen"
  keep_alive: 5
  clean_session: true
  max_buffered_messages: 10000

schema:
  name: "sensors"
  tbname:
    prefix: "device"
    count: 10000
  tags:
    - name: location
      type: VARCHAR(32)
      gen_type: random
      values: ["factory1", "factory2", "factory3"]
  columns:
    - name: ts
      type: TIMESTAMP
      gen_type: order
      min: 1700000000000
    - name: temperature
      type: FLOAT
      gen_type: random
      min: 20.0
      max: 80.0
    - name: humidity
      type: FLOAT
      gen_type: random
      min: 30.0
      max: 90.0
  generation:
    interlace: 100
    rows_per_table: 10000
    rows_per_batch: 1000

jobs:
  publish:
    name: "Publish to MQTT"
    steps:
      - name: "Publish sensor data"
        uses: mqtt/publish
        with:
          format: json
          concurrency: 8
          topic: "factory/{table}/{location}"
          qos: 1
          retain: false
          tbname_key: "device_id"
          records_per_message: 1
          time_interval:
            enabled: true
            interval_strategy: fixed
            fixed_interval:
              base_interval: 60000
```

## Example 5: Kafka Producing

Produce data to Kafka with JSON serialization.

```yaml
# taosgen-config-kafka-produce.yaml
kafka:
  bootstrap_servers: "localhost:9092"
  client_id: "taosgen"
  topic: "factory-metrics"
  rdkafka_options:
    security.protocol: "plaintext"

schema:
  name: "metrics"
  tbname:
    prefix: "host"
    count: 1000
  tags:
    - name: datacenter
      type: VARCHAR(16)
      gen_type: random
      values: ["dc1", "dc2"]
    - name: rack
      type: VARCHAR(8)
      gen_type: random
      values: ["r1", "r2", "r3", "r4"]
  columns:
    - name: ts
      type: TIMESTAMP
      gen_type: order
      min: 1700000000000
    - name: cpu_usage
      type: FLOAT
      gen_type: random
      min: 0.0
      max: 100.0
    - name: memory_usage
      type: FLOAT
      gen_type: random
      min: 0.0
      max: 100.0
    - name: disk_io
      type: INT
      gen_type: random
      min: 0
      max: 10000
  generation:
    interlace: 0
    rows_per_table: 100000
    rows_per_batch: 5000

jobs:
  produce:
    name: "Produce to Kafka"
    steps:
      - name: "Send metrics to Kafka"
        uses: kafka/produce
        with:
          concurrency: 8
          key_pattern: "{table}"
          key_serializer: "string-utf8"
          value_serializer: "json"
          acks: "1"
          compression: "snappy"
          tbname_key: "host"
          records_per_message: 10
```

## Example 6: High Concurrency Test

Optimized for maximum write throughput.

```yaml
# taosgen-config-high-concurrency.yaml
tdengine:
  dsn: "${TAOSGEN_DSN:-taos+ws://root:taosdata@localhost:6041/tsbench}"
  drop_if_exists: false
  props: "precision ms vgroups 20"
  pool:
    enabled: true
    max_size: 200
    min_size: 10
    timeout: 5000

schema:
  name: "highload"
  tbname:
    prefix: "t"
    count: 100000
  tags:
    - name: gid
      type: INT
      gen_type: random
      min: 1
      max: 100
  columns:
    - name: ts
      type: TIMESTAMP
      gen_type: order
      min: 1700000000000
    - name: value
      type: DOUBLE
      gen_type: random
      min: 0.0
      max: 1000000.0
  generation:
    interlace: 1000
    rows_per_table: 100000
    rows_per_batch: 30000
    num_cached_batches: 50000
    tables_reuse_data: true

jobs:
  init:
    name: "Initialize"
    steps:
      - uses: tdengine/create-database
      - uses: tdengine/create-super-table
      - uses: tdengine/create-child-table
        with:
          batch:
            size: 5000
            concurrency: 20

  write:
    name: "High Concurrency Write"
    needs: [init]
    steps:
      - uses: tdengine/insert
        with:
          format: stmt
          concurrency: 32
          auto_create_table: false
          failure_handling:
            max_retries: 5
            retry_interval_ms: 1000
            on_failure: skip
          checkpoint:
            enabled: true
            interval_sec: 30
```

## Example 7: Lua Expression Complex Data

Using Lua expressions for realistic data simulation.

```yaml
# taosgen-config-lua-expr.yaml
schema:
  name: "complex"
  tbname:
    prefix: "device"
    count: 1000
  columns:
    - name: ts
      type: TIMESTAMP
      gen_type: order
      min: 1700000000000
    # Sine wave with noise (simulating AC voltage)
    - name: ac_voltage
      type: FLOAT
      gen_type: expression
      expr: "220 * math.sin(_i / 50) + math.random(-10, 10)"
    # Step function (simulating state changes)
    - name: state
      type: INT
      gen_type: expression
      expr: "math.floor(_i / 1000) % 4"
    # Decaying exponential (simulating battery drain)
    - name: battery
      type: FLOAT
      gen_type: expression
      expr: "100 * math.exp(-_i / 10000) + math.random(-1, 1)"
    # Periodic spike (simulating peak hours)
    - name: load
      type: FLOAT
      gen_type: expression
      expr: "((math.sin(_i / 100) + 1) / 2 + ((math.floor(_i / 1440) % 2 == 0) and 0.5 or 0)) * 100"
  generation:
    rows_per_table: 10000

jobs:
  write:
    steps:
      - uses: tdengine/create-database
      - uses: tdengine/create-super-table
      - uses: tdengine/create-child-table
      - uses: tdengine/insert
```

## Example 8: Multi-Stage Pipeline

DAG with multiple dependent jobs.

```yaml
# taosgen-config-pipeline.yaml
tdengine:
  dsn: "${TAOSGEN_DSN:-taos+ws://root:taosdata@localhost:6041/test}"

schema:
  name: "stage_data"
  tbname:
    count: 1000
  generation:
    rows_per_table: 10000

jobs:
  # Stage 1: Setup
  create-db:
    name: "Create DB"
    needs: []
    steps:
      - uses: tdengine/create-database

  create-tables:
    name: "Create Tables"
    needs: [create-db]
    steps:
      - uses: tdengine/create-super-table
      - uses: tdengine/create-child-table

  # Stage 2: Initial Load
  initial-load:
    name: "Initial Data Load"
    needs: [create-tables]
    steps:
      - uses: tdengine/insert
        with:
          time_interval:
            enabled: true
            interval_strategy: fixed
            fixed_interval:
              base_interval: 1000

  # Stage 3: Validation (placeholder for future action)
  # validate:
  #   name: "Validate Data"
  #   needs: [initial-load]
  #   steps:
  #     - uses: tdengine/validate

  # Stage 4: Incremental Load
  incremental-load:
    name: "Incremental Load"
    needs: [initial-load]
    steps:
      - uses: tdengine/insert
        with:
          schema:
            generation:
              rows_per_table: 5000
```

## Usage Tips

1. **Start Small**: Use Example 1 (Minimal) to validate your setup
2. **Scale Gradually**: Start with small `count` and `rows_per_table`, then increase
3. **Monitor Resources**: Watch CPU, memory, and network during high concurrency tests
4. **Use Checkpoints**: Enable checkpoint for long-running tests to allow resume
5. **Environment Variables**: Always use `${VAR:-default}` for sensitive information
