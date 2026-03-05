---
name: taosgen
description: "Generate taosgen YAML configuration and run performance benchmarks for TDengine/MQTT/Kafka (taosgen, benchmark, config, yaml, performance test, time-series data)"
---

# taosgen (Router)

This skill is the single entrypoint for taosgen configuration generation and running performance benchmarks.

taosgen is a time-series data benchmark tool that supports:
- TDengine database write testing
- MQTT message publishing
- Kafka message producing
- Flexible data generation (random, order, Lua expression, CSV)
- Job orchestration with DAG dependencies

## Input

Ask the user for their intent:
- **Config generation**: "Generate config", "Create YAML", "Setup taosgen"
  - Target type: TDengine / MQTT / Kafka
  - Data scale: number of tables, rows per table
  - Connection info: host, port (sensitive info like password use env vars)
- **Run assistance**: "Run taosgen", "Execute benchmark", "Start test"
  - Config file path
  - Parameter overrides (optional)

If the user did not specify, infer from keywords:
- Config/配置/YAML/setup/generate → route to `taosgen-config`
- Run/运行/execute/start/benchmark → route to `taosgen-run`

If still ambiguous, ask a single clarification question:
> "Do you want to (1) generate a taosgen configuration file, or (2) run taosgen with an existing configuration?"

## Routing

- Config generation → use `taosgen-config` skill
- Run assistance → use `taosgen-run` skill

## Configuration Generation Method (Rigorous Approach)

To avoid generating invalid parameters, use the code-based approach:

### Option 1: Python Script (Recommended)

Use the provided generator script: `scripts/generator.py`

```python
from scripts.generator import (
    generate_smart_meters_tdengine,
    generate_smart_meters_mqtt,
    generate_smart_meters_kafka,
    generate_yaml,
    save_config,
    validate_config
)

# Generate TDengine config
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
    # Generate YAML
    yaml_output = generate_yaml(config, "tdengine", "smart-meters")
    print(yaml_output)

    # Or save to file
    path = save_config(config, "tdengine", "smart-meters", "output.yaml")
    print(f"OutputPath: {path}")
```

### Option 2: JSON Schema Validation

Use `scripts/schema.json` for strict validation:

```python
import json
import yaml
from jsonschema import validate, ValidationError

# Load schema
with open('scripts/schema.json') as f:
    schema = json.load(f)

# Validate config
config = yaml.safe_load(open('config.yaml'))
try:
    validate(instance=config, schema=schema)
    print("Validation: PASSED")
except ValidationError as e:
    print(f"Validation error: {e.message}")
```

## Common Engineering Conventions (MUST)

### Category Detection

Determine category from the git repository root directory or current working directory.

### Filename (for generated configs)

Pattern: `taosgen-config-{target}-{scenario}.yaml`
- target: tdengine / mqtt / kafka
- scenario: brief description (e.g., meters, minimal, test)

Examples:
- `taosgen-config-tdengine-meters.yaml`
- `taosgen-config-mqtt-sensors.yaml`

### Output Location

Use current working directory or project's `configs/` directory if exists.

### Output Format

After generating the configuration file, the agent MUST print:
- `OutputPath: /absolute/path/to/taosgen-config-xxx.yaml`

After suggesting run command, the agent MUST print:
- `Command: taosgen -h <host> -c /absolute/path/to/config.yaml`

## Parameter Reference (Strict Boundaries)

### MQTT Config (ONLY these parameters are supported)

```yaml
mqtt:
  uri: "tcp://localhost:1883"      # Broker URI (REQUIRED)
  user: ""                          # Username (optional)
  password: ""                      # Password (optional)
  client_id: "taosgen"              # Client ID prefix
  keep_alive: 5                     # Keep alive in seconds
  clean_session: true               # Clean session flag
  max_buffered_messages: 10000      # Max buffered messages
```

**INVALID parameters** (will cause errors):
- `broker` - use `uri`
- `username` - use `user`
- `qos` - belongs in action `with` section, not mqtt config
- `retain` - belongs in action `with` section
- `timeout` - not supported

### Kafka Config

```yaml
kafka:
  bootstrap_servers: "localhost:9092"  # REQUIRED
  client_id: "taosgen"                  # optional
  topic: "test-topic"                   # REQUIRED
  rdkafka_options:                      # optional
    security.protocol: "plaintext"
    sasl.mechanism: "PLAIN"
    sasl.username: "user"
    sasl.password: "pass"
```

### TDengine Config

```yaml
tdengine:
  dsn: "taos+ws://root:taosdata@localhost:6041/tsbench"  # REQUIRED
  drop_if_exists: false                                    # optional
  props: "precision 'ms' vgroups 4"                       # optional
  pool:                                                    # optional
    enabled: true
    max_size: 100
    min_size: 2
    timeout: 1000
```

**Note**: `props` value must have single quotes around precision, e.g., `precision 'ms'`

### Generation Control

```yaml
schema:
  generation:
    interlace: 0              # integer >= 0
    rows_per_table: 10000     # integer >= 1
    rows_per_batch: 10000     # integer >= 1
    num_cached_batches: 0     # integer >= 0 (0 = disabled)
    tables_reuse_data: true   # boolean
```

### Column Definition (gen_type is INFERRED)

```yaml
# Random generation (inferred from min/max)
- name: current
  type: float
  min: 0.0
  max: 100.0

# Random from values (inferred from values)
- name: location
  type: binary(24)
  values:
    - "California"
    - "Texas"

# Expression (inferred from expr)
- name: voltage
  type: float
  expr: "220 + 10 * math.sin(_i / 10)"

# Order/timestamp (inferred from step)
- name: ts
  type: timestamp
  start: now
  precision: ms
  step: 1
```

### Valid Actions

- `tdengine/create-database`
- `tdengine/create-super-table`
- `tdengine/create-child-table`
- `tdengine/insert`
- `mqtt/publish`
- `kafka/produce`

## Safety

- **Password handling**: DSN should use default credentials for testing. For production, override password via command line `-p` parameter when running taosgen.
- **Drop database warning**: If `drop_if_exists: true`, show warning and ask for confirmation.
- **Destructive operations**: Always confirm before suggesting commands that may delete data.
- **Parameter strictness**: Only use parameters defined in schema.json. Do not hallucinate unsupported parameters.

## References

- `references/CONFIG.md` - Detailed config generation guide
- `references/RUN.md` - Detailed run assistance guide
- `references/EXAMPLES.md` - Configuration examples library
- `scripts/generator.py` - Python generator with strict parameter validation
- `scripts/schema.json` - JSON Schema for configuration validation
