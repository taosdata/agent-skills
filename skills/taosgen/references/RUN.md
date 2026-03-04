# taosgen Run Assistance Reference

This reference provides detailed guidance for running taosgen with generated configurations.

## Prerequisites Check

Before running taosgen, verify:

1. **taosgen installed**:
   ```bash
   which taosgen
   taosgen --version
   ```

2. **Target service accessible**:
   - For TDengine: Check if server is running and accessible
   - For MQTT: Verify broker is accepting connections
   - For Kafka: Verify brokers are available

3. **Configuration valid**: YAML syntax is correct

## Command Line Parameters

### Basic Usage

```bash
taosgen -h <host> -c <config-file>
```

### Full Parameter List

| Parameter | Short | Description | Default |
|-----------|-------|-------------|---------|
| --host | -h | Server hostname or IP | localhost |
| --port | -P | Server port | 6030 |
| --user | -u | Username | root |
| --password | -p | Password | taosdata |
| --config-file | -c | YAML config file path | - |
| --help | -? | Show help | - |
| --version | -V | Show version | - |

### Parameter Precedence

Command line parameters override configuration file settings.

Priority: CLI args > Config file > Default values

## Environment Variables

Recommended environment variables for security:

```bash
# TDengine
export TAOSGEN_DSN="taos+ws://root:taosdata@localhost:6041/tsbench"
export TAOS_PASSWORD="taosdata"

# MQTT
export MQTT_USER="mqtt_user"
export MQTT_PASS="mqtt_password"

# Kafka SASL
export KAFKA_SASL_USER="kafka_user"
export KAFKA_SASL_PASS="kafka_password"
```

## Running with Different Scenarios

### Scenario 1: Local Development Test

```bash
# Small scale test
taosgen -h localhost -c ./taosgen-config-tdengine-minimal.yaml
```

### Scenario 2: Remote Server

```bash
# Override host and credentials
taosgen -h 192.168.1.100 -P 6041 -u root -p "$TAOS_PASSWORD" -c ./config.yaml
```

### Scenario 3: Dry Run (Validate Config)

If taosgen supports dry-run mode:
```bash
taosgen --dry-run -c ./config.yaml
```

Otherwise, use minimal data scale for validation.

## Performance Tuning Tips

### 1. Connection Pool

Ensure `tdengine.pool.enabled: true` in config for high concurrency.

### 2. CPU Affinity

For best performance, consider binding taosgen to specific CPU cores:
```bash
taskset -c 0-7 taosgen -c ./config.yaml
```

### 3. Network Optimization

- Use WebSocket over TCP for better compatibility
- Ensure sufficient network bandwidth
- Consider co-locating taosgen with target service

### 4. Monitoring

Watch these metrics during run:
- CPU usage (taosgen and target service)
- Memory usage
- Network I/O
- Disk I/O (for TDengine)

## Troubleshooting

### Error: Connection Refused

**Cause**: Target service not running or not accessible
**Solution**:
```bash
# Check TDengine
systemctl status taosd

# Check MQTT
netstat -tlnp | grep 1883

# Check Kafka
netstat -tlnp | grep 9092
```

### Error: Authentication Failed

**Cause**: Wrong username or password
**Solution**:
- Verify credentials
- Check if using environment variables correctly

### Error: Config Validation Failed

**Cause**: YAML syntax error or invalid parameters
**Solution**:
```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Check for common issues:
# - Tab characters (use spaces only)
# - Missing required fields
# - Invalid data types
```

### Error: Out of Memory

**Cause**: Data generation too fast, buffer overflow
**Solution**:
- Reduce `num_cached_batches`
- Reduce `concurrency`
- Reduce `rows_per_batch`

### Slow Performance

**Solutions**:
1. Increase `concurrency` (but not beyond CPU cores)
2. Increase `rows_per_batch`
3. Enable connection pool
4. Use `stmt` format instead of `sql`
5. Check network latency

## Checkpoint and Resume

For long-running tests, enable checkpoint:

```yaml
jobs:
  insert-data:
    steps:
      - uses: tdengine/insert
        with:
          checkpoint:
            enabled: true
            interval_sec: 60
```

This allows resuming from interruption.

## Sample Run Output

Expected console output:

```
[INFO] Starting taosgen v0.3.0
[INFO] Loading config: /path/to/config.yaml
[INFO] Job: create-db - Started
[INFO] Job: create-db - Completed (0.5s)
[INFO] Job: create-stables - Started
[INFO] Job: create-stables - Completed (0.2s)
[INFO] Job: create-tables - Started
[INFO] Job: create-tables - Completed (5.3s)
[INFO] Job: insert-data - Started
[INFO] Progress: 10000/100000000 rows (0.01%)
...
```

## Post-Run Verification

After running, verify results:

### For TDengine

```sql
-- Check database
create database tsbench;
use tsbench;

-- Check tables
show stables;
show tables;

-- Check data count
select count(*) from meters;
```

### For MQTT

Use MQTT client to subscribe and verify messages:
```bash
mosquitto_sub -h localhost -t "factory/#" -v
```

### For Kafka

Use kafka-console-consumer to verify:
```bash
kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test-topic --from-beginning
```
