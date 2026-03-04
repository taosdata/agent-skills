---
name: taosgen-run
description: "Run taosgen benchmark with configuration file (taosgen, run, execute, benchmark, performance test)"
---

# taosgen-run

Assist running taosgen performance benchmarks with existing configuration files.

## When to Use

Use this skill when you need to:
- Run taosgen with a generated configuration file
- Check environment before running (taosgen installed, target accessible)
- Override certain parameters when running
- Get suggestions for performance tuning

## Input

Ask the user for:

1. **Configuration File Path**:
   - Absolute or relative path to YAML config file
   - If not specified, look for `taosgen-config-*.yaml` in current directory

2. **Parameter Overrides** (optional):
   - Host override (`-h`)
   - Port override (`-P`)
   - User override (`-u`)
   - Connection DSN override

3. **Dry Run** (optional):
   - Whether to validate config only without actual execution

## Output

Provide:
1. Environment check results
2. Suggested command to run
3. Performance tuning suggestions (if applicable)

Print:
```
Command: taosgen -h <host> -c /absolute/path/to/config.yaml
```

## Steps

1. **Environment Check**:
   ```bash
   which taosgen
   taosgen --version
   ```
   - If not installed, provide installation instructions

2. **Configuration Validation**:
   - Check if config file exists
   - Validate YAML syntax
   - Check for required fields

3. **Target Connectivity Check** (for TDengine):
   - Parse DSN from config or use provided overrides
   - Suggest connection test command

4. **Command Building**:
   - Build command with base parameters
   - Apply user overrides
   - Format for readability

5. **Pre-run Warnings**:
   - Check if `drop_if_exists: true` in config
   - Estimate data volume and running time
   - Suggest using smaller scale for first run

6. **Output**:
   - Print ready-to-run command
   - Provide monitoring suggestions
   - Explain how to check results

## Command Examples

### Basic Run

```bash
taosgen -c /path/to/taosgen-config-tdengine-meters.yaml
```

### With Host Override

```bash
taosgen -h 192.168.1.100 -c /path/to/config.yaml
```

### With Full Parameters

```bash
taosgen -h 192.168.1.100 -P 6041 -u root -p "$TAOS_PASSWORD" -c /path/to/config.yaml
```

## Password Handling

DSN is configured directly in the YAML file. For security:
- Default DSN uses default TDengine credentials (root/taosdata)
- Override password via command line `-p` parameter when running:
  ```bash
  taosgen -h localhost -p your_password -c config.yaml
  ```

For MQTT/Kafka credentials, configure directly in YAML:
```yaml
mqtt:
  user: "your_mqtt_user"
  password: "your_mqtt_password"

kafka:
  rdkafka_options:
    sasl.username: "your_kafka_user"
    sasl.password: "your_kafka_password"
```

## Safety

- **Credential Safety**: Never display actual passwords in command output. Passwords should be entered via command line `-p` parameter or configured directly in YAML file.
- **Destructive Operation Warning**: If config has `drop_if_exists: true`, warn user about data loss risk.
- **Resource Warning**: For large-scale tests (tables > 100000, rows > 1000000), warn about resource consumption.
- **Confirmation**: For potentially destructive operations, ask for explicit confirmation.

## Post-Run Verification

Suggest verification commands after run:

### For TDengine

```sql
-- Connect to TDengine
taos -h <host>

-- Use database
use tsbench;

-- Check tables
show stables;
show tables;

-- Check data count
select count(*) from meters;

-- Sample data
select * from meters limit 10;
```

### For MQTT

```bash
# Subscribe to verify messages
mosquitto_sub -h <broker> -t "factory/#" -v
```

### For Kafka

```bash
# Consume messages to verify
kafka-console-consumer.sh --bootstrap-server <broker> --topic <topic> --from-beginning
```

## Troubleshooting Guide

If issues occur, check:

1. **Connection refused**: Target service running? Network accessible?
2. **Authentication failed**: Credentials correct? Environment variables set?
3. **Config validation failed**: YAML syntax correct? Required fields present?
4. **Out of memory**: Reduce `num_cached_batches` and `concurrency`
5. **Slow performance**: Check network latency, increase `rows_per_batch`

## References

- `taosgen/references/RUN.md` - Detailed run guide
- `taosgen/references/EXAMPLES.md` - Example configurations
