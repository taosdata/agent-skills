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

## Safety

- **Password handling**: Never hardcode passwords in generated configs. Use `${ENV_VAR:-default}` format.
- **Drop database warning**: If `drop_if_exists: true`, show warning and ask for confirmation.
- **Destructive operations**: Always confirm before suggesting commands that may delete data.

## References

- `references/CONFIG.md` - Detailed config generation guide
- `references/RUN.md` - Detailed run assistance guide
- `references/EXAMPLES.md` - Configuration examples library
