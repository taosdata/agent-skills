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
    rows_per_batch: 1000

jobs:
  insert-data:
    steps:
      - uses: tdengine/create-super-table
      - uses: tdengine/create-child-table
      - uses: tdengine/insert
```

## Example 2: Smart Meters (Full Featured)

Classic smart meter scenario with 10,000 devices, each reporting every 5 minutes.

```yaml
# taosgen-config-tdengine-meters.yaml
tdengine:
  dsn: "taos+ws://root:taosdata@localhost:6041/tsbench"
  drop_if_exists: false
  props: "precision 'ms' vgroups 4"
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
      type: int
      min: 1
      max: 10
    - name: location
      type: binary(24)
      values:
        - "California.Campbell"
        - "Texas.Austin"
        - "NewYork.NewYorkCity"
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
    - name: voltage
      type: int
      expr: "220 + 10 * math.sin(_i / 10)"
    - name: phase
      type: float
      min: 0.0
      max: 360.0
  generation:
    interlace: 0
    rows_per_table: 10000
    rows_per_batch: 10000

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
  dsn: "taos+ws://root:taosdata@localhost:6041/tsbench"
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
  columns:
    - name: ts
      type: timestamp
    - name: current
      type: float
    - name: voltage
      type: int
    - name: phase
      type: float
  tags:
    - name: groupid
      type: int
    - name: location
      type: binary(24)
  generation:
    rows_per_table: 10000
    rows_per_batch: 10000

jobs:
  insert-data:
    steps:
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
  user: ""
  password: ""
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
      type: binary(32)
      values:
        - "factory1"
        - "factory2"
        - "factory3"
  columns:
    - name: ts
      type: timestamp
      start: now + 10s
      precision: ms
      step: 1
    - name: temperature
      type: float
      min: 20.0
      max: 80.0
    - name: humidity
      type: float
      min: 30.0
      max: 90.0
  generation:
    interlace: 100
    rows_per_table: 10000
    rows_per_batch: 1000

jobs:
  publish:
    steps:
      - name: "Publish sensor data"
        uses: mqtt/publish
        with:
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
      type: binary(16)
      values:
        - "dc1"
        - "dc2"
    - name: rack
      type: binary(8)
      values:
        - "r1"
        - "r2"
        - "r3"
        - "r4"
  columns:
    - name: ts
      type: timestamp
      start: now + 10s
      precision: ms
      step: 1
    - name: cpu_usage
      type: float
      min: 0.0
      max: 100.0
    - name: memory_usage
      type: float
      min: 0.0
      max: 100.0
    - name: disk_io
      type: int
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
  dsn: "taos+ws://root:taosdata@localhost:6041/tsbench"
  drop_if_exists: false
  props: "precision 'ms' vgroups 20"
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
      type: int
      min: 1
      max: 100
  columns:
    - name: ts
      type: timestamp
      start: now + 10s
      precision: ms
      step: 1
    - name: value
      type: double
      min: 0.0
      max: 1000000.0
  generation:
    interlace: 1000
    rows_per_table: 100000
    rows_per_batch: 30000
    tables_reuse_data: true

jobs:
  write:
    steps:
      - uses: tdengine/create-super-table
      - uses: tdengine/create-child-table
        with:
          batch:
            size: 5000
            concurrency: 20
      - uses: tdengine/insert
        with:
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
      type: timestamp
      start: now + 10s
      precision: ms
      step: 1
    # Sine wave with noise (simulating AC voltage)
    - name: ac_voltage
      type: float
      expr: "220 * math.sin(_i / 50) + math.random(-10, 10)"
    # Step function (simulating state changes)
    - name: state
      type: int
      expr: "math.floor(_i / 1000) % 4"
    # Decaying exponential (simulating battery drain)
    - name: battery
      type: float
      expr: "100 * math.exp(-_i / 10000) + math.random(-1, 1)"
    # Periodic spike (simulating peak hours)
    - name: load
      type: float
      expr: "((math.sin(_i / 100) + 1) / 2 + ((math.floor(_i / 1440) % 2 == 0) and 0.5 or 0)) * 100"
  generation:
    rows_per_table: 10000
    rows_per_batch: 10000

jobs:
  write:
    steps:
      - uses: tdengine/create-super-table
      - uses: tdengine/create-child-table
      - uses: tdengine/insert
```

## Example 8: Multi-Stage Pipeline (DAG)

For complex scenarios requiring explicit dependencies.

```yaml
# taosgen-config-pipeline.yaml
tdengine:
  dsn: "taos+ws://root:taosdata@localhost:6041/test"

schema:
  name: "stage_data"
  tbname:
    count: 1000
  generation:
    rows_per_table: 10000
    rows_per_batch: 10000

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

  # Stage 3: Incremental Load
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
5. **Simple First**: Use single job with multiple steps; only use DAG (needs) when truly necessary
6. **DSN Format**: Use direct string like `taos+ws://root:taosdata@localhost:6041/tsbench`
7. **Props Format**: Use single quotes for precision value: `precision 'ms'`
