#!/usr/bin/env python3
"""
Taosgen Configuration Generator

A rigorous, code-based approach to generating taosgen YAML configurations.
This script defines strict parameter boundaries based on official documentation
and generates valid configurations that pass taosgen's validation.

Reference:
- Official docs: /opt/source/TDengine/docs/zh/14-reference/02-tools/11-taosgen.md
- Examples: /opt/source/tsgen/conf/
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union, Any
import yaml
from datetime import datetime


# ============================================================================
# DATA CLASSES - Strict parameter definitions based on official documentation
# ============================================================================

@dataclass
class TDengineConfig:
    """TDengine connection configuration.

    Valid parameters (from official docs):
    - dsn: Connection string, e.g., "taos+ws://root:taosdata@localhost:6041/tsbench"
    - drop_if_exists: Whether to drop existing database (bool)
    - props: Database properties, e.g., "precision 'ms' vgroups 4"
    - pool: Connection pool settings
    """
    dsn: str = "taos+ws://root:taosdata@localhost:6041/tsbench"
    drop_if_exists: bool = False
    props: str = "precision 'ms' vgroups 4"
    pool: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.pool is None:
            self.pool = {
                "enabled": True,
                "max_size": 100,
                "min_size": 2,
                "timeout": 1000
            }

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "dsn": self.dsn,
            "drop_if_exists": self.drop_if_exists,
            "props": self.props,
        }
        if self.pool:
            result["pool"] = self.pool
        return result


@dataclass
class MqttConfig:
    """MQTT broker configuration.

    Valid parameters (from official docs):
    - uri: Broker URI, default "tcp://localhost:1883"
    - user: Username (optional)
    - password: Password (optional)
    - client_id: Client ID prefix, default "taosgen"
    - keep_alive: Keep alive in seconds, default 5
    - clean_session: Whether to clean session, default true
    - max_buffered_messages: Max buffered messages, default 10000
    """
    uri: str = "tcp://localhost:1883"
    user: str = ""
    password: str = ""
    client_id: str = "taosgen"
    keep_alive: int = 5
    clean_session: bool = True
    max_buffered_messages: int = 10000

    def to_dict(self) -> Dict[str, Any]:
        result = {"uri": self.uri}
        if self.user:
            result["user"] = self.user
        if self.password:
            result["password"] = self.password
        result["client_id"] = self.client_id
        result["keep_alive"] = self.keep_alive
        result["clean_session"] = self.clean_session
        result["max_buffered_messages"] = self.max_buffered_messages
        return result


@dataclass
class KafkaConfig:
    """Kafka broker configuration.

    Valid parameters (from official docs):
    - bootstrap_servers: Kafka cluster addresses, e.g., "host1:9092,host2:9092"
    - client_id: Client ID prefix, default "taosgen"
    - topic: Topic name
    - rdkafka_options: Additional librdkafka options
    """
    bootstrap_servers: str = "localhost:9092"
    client_id: str = "taosgen"
    topic: str = "test-topic"
    rdkafka_options: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "bootstrap_servers": self.bootstrap_servers,
            "client_id": self.client_id,
        }
        if self.topic:
            result["topic"] = self.topic
        if self.rdkafka_options:
            result["rdkafka_options"] = self.rdkafka_options
        return result


@dataclass
class ColumnConfig:
    """Column definition for schema.

    Data types (from official docs):
    - Integer: timestamp, bool, tinyint, smallint, int, bigint (and unsigned variants)
    - Float: float, double, decimal
    - String: nchar, varchar(n), binary(n)

    Data generation (inferred from presence of keys):
    - random: min/max or values
    - order: min/max for integers
    - expression: expr field with Lua expression
    """
    name: str
    type: str  # e.g., "int", "float", "binary(24)", "timestamp"
    count: int = 1  # Number of columns to generate with this name as prefix (e.g., count=3 -> col1, col2, col3)
    min: Optional[Union[int, float]] = None
    max: Optional[Union[int, float]] = None
    values: Optional[List[str]] = None
    expr: Optional[str] = None
    start: Optional[str] = None  # For timestamp: "now", "now + 10s", or "1700000000000"
    precision: Optional[str] = None  # For timestamp: "ms", "us", "ns"
    step: Optional[Union[int, str]] = None  # For timestamp: step size, e.g., 1 or "300s"

    def to_dict(self) -> Dict[str, Any]:
        result = {"name": self.name, "type": self.type}

        # Only include count if > 1 (default is 1)
        if self.count > 1:
            result["count"] = self.count

        # Data generation based on presence of keys (not gen_type)
        if self.expr:
            result["expr"] = self.expr
        elif self.values:
            result["values"] = self.values
        elif self.min is not None and self.max is not None:
            result["min"] = self.min
            result["max"] = self.max

        # Timestamp-specific fields
        if self.start:
            result["start"] = self.start
        if self.precision:
            result["precision"] = self.precision
        if self.step is not None:
            result["step"] = self.step

        return result


@dataclass
class TbnameConfig:
    """Table name generation configuration."""
    prefix: str = "d"
    count: int = 10000
    from_val: int = 0  # Renamed from 'from' to avoid Python keyword

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prefix": self.prefix,
            "count": self.count,
            "from": self.from_val
        }


@dataclass
class GenerationConfig:
    """Data generation control.

    Valid parameters (from official docs):
    - interlace: Interlace rows count, default 0
    - concurrency: Data generation threads (for MQTT/Kafka), default uses insert threads
    - rows_per_table: Rows per table, default 10000 (-1 for unlimited)
    - rows_per_batch: Rows per batch, default 10000
    - num_cached_batches: Cached batches, default 10000 (0 = disabled)
    - tables_reuse_data: Reuse data across tables, default true
    """
    interlace: int = 0
    concurrency: Optional[int] = None  # Data generation threads, MQTT/Kafka use
    rows_per_table: int = 10000  # -1 for unlimited
    rows_per_batch: int = 10000
    num_cached_batches: int = 0  # 0 = disabled
    tables_reuse_data: bool = True

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "interlace": self.interlace,
            "rows_per_table": self.rows_per_table,
            "rows_per_batch": self.rows_per_batch,
        }
        if self.concurrency is not None:
            result["concurrency"] = self.concurrency
        if self.num_cached_batches != 0:
            result["num_cached_batches"] = self.num_cached_batches
        if not self.tables_reuse_data:
            result["tables_reuse_data"] = self.tables_reuse_data
        return result


@dataclass
class SchemaConfig:
    """Schema definition for data generation."""
    name: str = "meters"
    tbname: Optional[TbnameConfig] = None
    tags: List[ColumnConfig] = field(default_factory=list)
    columns: List[ColumnConfig] = field(default_factory=list)
    generation: Optional[GenerationConfig] = None

    def __post_init__(self):
        if self.tbname is None:
            self.tbname = TbnameConfig()
        if self.generation is None:
            self.generation = GenerationConfig()

    def to_dict(self) -> Dict[str, Any]:
        result = {"name": self.name}
        if self.tbname:
            result["tbname"] = self.tbname.to_dict()
        if self.tags:
            result["tags"] = [t.to_dict() for t in self.tags]
        if self.columns:
            result["columns"] = [c.to_dict() for c in self.columns]
        if self.generation:
            result["generation"] = self.generation.to_dict()
        return result


@dataclass
class StepConfig:
    """Job step configuration.

    Valid actions (from official docs):
    - tdengine/create-database
    - tdengine/create-super-table
    - tdengine/create-child-table
    - tdengine/insert
    - mqtt/publish
    - kafka/produce
    """
    uses: str
    name: Optional[str] = None
    with_params: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"uses": self.uses}
        if self.name:
            result["name"] = self.name
        if self.with_params:
            result["with"] = self.with_params
        return result


@dataclass
class JobConfig:
    """Job configuration."""
    steps: List[StepConfig] = field(default_factory=list)
    name: Optional[str] = None
    needs: Optional[List[str]] = None

    def to_dict(self) -> Dict[str, Any]:
        result = {"steps": [s.to_dict() for s in self.steps]}
        if self.name:
            result["name"] = self.name
        if self.needs:
            result["needs"] = self.needs
        return result


@dataclass
class TaosgenConfig:
    """Complete taosgen configuration."""
    target: str  # "tdengine", "mqtt", "kafka"
    scenario: str
    schema: SchemaConfig = field(default_factory=SchemaConfig)
    tdengine: Optional[TDengineConfig] = None
    mqtt: Optional[MqttConfig] = None
    kafka: Optional[KafkaConfig] = None
    jobs: Dict[str, JobConfig] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        result = {}

        # Add connection config based on target
        if self.target == "tdengine" and self.tdengine:
            result["tdengine"] = self.tdengine.to_dict()
        elif self.target == "mqtt" and self.mqtt:
            result["mqtt"] = self.mqtt.to_dict()
        elif self.target == "kafka" and self.kafka:
            result["kafka"] = self.kafka.to_dict()

        # Schema
        result["schema"] = self.schema.to_dict()

        # Jobs
        if self.jobs:
            result["jobs"] = {k: v.to_dict() for k, v in self.jobs.items()}

        return result


# ============================================================================
# GENERATOR FUNCTIONS - Pre-defined scenario templates
# ============================================================================

def generate_smart_meters_tdengine(
    host: str = "localhost",
    port: int = 6041,
    database: str = "tsbench",
    table_count: int = 10000,
    rows_per_table: int = 10000
) -> Dict[str, Any]:
    """Generate TDengine config for smart meters scenario."""

    config = TaosgenConfig(
        target="tdengine",
        scenario="smart-meters",
        tdengine=TDengineConfig(
            dsn=f"taos+ws://root:taosdata@{host}:{port}/{database}",
            drop_if_exists=False,
            props="precision 'ms' vgroups 4"
        ),
        schema=SchemaConfig(
            name="meters",
            tbname=TbnameConfig(prefix="d", count=table_count, from_val=0),
            tags=[
                ColumnConfig(name="groupid", type="int", min=1, max=10),
                ColumnConfig(
                    name="location",
                    type="binary(24)",
                    values=[
                        "California.Campbell",
                        "California.SanFrancisco",
                        "California.SanJose",
                        "Texas.Austin",
                        "Texas.Dallas",
                        "NewYork.NewYorkCity"
                    ]
                )
            ],
            columns=[
                ColumnConfig(name="ts", type="timestamp", start="now", precision="ms", step=1),
                ColumnConfig(name="current", type="float", min=0.0, max=100.0),
                ColumnConfig(name="voltage", type="int", expr="220 + 10 * math.sin(_i / 10)"),
                ColumnConfig(name="phase", type="float", min=0.0, max=360.0)
            ],
            generation=GenerationConfig(
                interlace=0,
                rows_per_table=rows_per_table,
                rows_per_batch=10000,
                num_cached_batches=0
            )
        ),
        jobs={
            "insert": JobConfig(
                steps=[
                    StepConfig(uses="tdengine/create-super-table"),
                    StepConfig(
                        uses="tdengine/create-child-table",
                        with_params={"batch": {"size": 1000, "concurrency": 10}}
                    ),
                    StepConfig(
                        uses="tdengine/insert",
                        with_params={"concurrency": 8}
                    )
                ]
            )
        }
    )

    return config.to_dict()


def generate_smart_meters_mqtt(
    uri: str = "tcp://localhost:1883",
    user: str = "",
    password: str = "",
    table_count: int = 10000,
    rows_per_table: int = 10000
) -> Dict[str, Any]:
    """Generate MQTT config for smart meters scenario."""

    config = TaosgenConfig(
        target="mqtt",
        scenario="smart-meters",
        mqtt=MqttConfig(
            uri=uri,
            user=user,
            password=password,
            client_id="taosgen",
            keep_alive=5,
            clean_session=True,
            max_buffered_messages=10000
        ),
        schema=SchemaConfig(
            name="meters",
            tbname=TbnameConfig(prefix="d", count=table_count, from_val=0),
            tags=[
                ColumnConfig(name="groupid", type="int", min=1, max=10),
                ColumnConfig(
                    name="location",
                    type="varchar(20)",
                    values=["Chicago", "Houston", "Phoenix", "Dallas", "Austin"]
                )
            ],
            columns=[
                ColumnConfig(name="ts", type="timestamp", start="1700000000000", precision="ms", step="300s"),
                ColumnConfig(name="current", type="float", min=0, max=100),
                ColumnConfig(name="voltage", type="int", expr="220 * math.sqrt(2) * math.sin(_i)"),
                ColumnConfig(name="phase", type="float", min=0, max=360)
            ],
            generation=GenerationConfig(
                interlace=1,
                concurrency=8,  # Data generation threads for MQTT
                rows_per_table=rows_per_table,
                rows_per_batch=10000,
                num_cached_batches=0
            )
        ),
        jobs={
            "publish": JobConfig(
                steps=[
                    StepConfig(
                        uses="mqtt/publish",
                        with_params={
                            "concurrency": 8,
                            "topic": "factory/{table}/{location}",
                            "qos": 1
                            # time_interval can be added here if needed:
                            # "time_interval": {
                            #     "enabled": True,
                            #     "interval_strategy": "literal"
                            # }
                        }
                    )
                ]
            )
        }
    )

    return config.to_dict()


def generate_smart_meters_kafka(
    bootstrap_servers: str = "localhost:9092",
    topic: str = "factory-electric-meter",
    table_count: int = 10000,
    rows_per_table: int = 10000
) -> Dict[str, Any]:
    """Generate Kafka config for smart meters scenario."""

    config = TaosgenConfig(
        target="kafka",
        scenario="smart-meters",
        kafka=KafkaConfig(
            bootstrap_servers=bootstrap_servers,
            client_id="taosgen",
            topic=topic
        ),
        schema=SchemaConfig(
            name="meters",
            tbname=TbnameConfig(prefix="d", count=table_count, from_val=0),
            tags=[
                ColumnConfig(name="groupid", type="int", min=1, max=10),
                ColumnConfig(
                    name="location",
                    type="varchar(20)",
                    values=["Chicago", "Houston", "Phoenix", "Dallas", "Austin"]
                )
            ],
            columns=[
                ColumnConfig(name="ts", type="timestamp", start="1700000000000", precision="ms", step="300s"),
                ColumnConfig(name="current", type="float", min=0, max=100),
                ColumnConfig(name="voltage", type="int", expr="220 * math.sqrt(2) * math.sin(_i)"),
                ColumnConfig(name="phase", type="float", min=0, max=360)
            ],
            generation=GenerationConfig(
                interlace=1,
                concurrency=8,  # Data generation threads for Kafka
                rows_per_table=rows_per_table,
                rows_per_batch=10000,
                num_cached_batches=0
            )
        ),
        jobs={
            "produce": JobConfig(
                steps=[
                    StepConfig(
                        uses="kafka/produce",
                        with_params={
                            "concurrency": 8,
                            "acks": "1"
                        }
                    )
                ]
            )
        }
    )

    return config.to_dict()


def generate_mqtt_realtime(
    uri: str = "tcp://localhost:1883",
    table_count: int = 100
) -> Dict[str, Any]:
    """Generate MQTT config with real-time simulation using time_interval."""
    config = TaosgenConfig(
        target="mqtt",
        scenario="realtime",
        mqtt=MqttConfig(uri=uri),
        schema=SchemaConfig(
            name="meters",
            tbname=TbnameConfig(prefix="ev-", count=table_count, from_val=1),
            columns=[
                ColumnConfig(name="ts", type="timestamp", start="now", precision="ms", step="1s"),
                ColumnConfig(name="voltage", type="float", min=200, max=240)
            ],
            generation=GenerationConfig(
                interlace=1,
                rows_per_table=-1,  # Unlimited rows for continuous streaming
                rows_per_batch=10000,
                num_cached_batches=0
            )
        ),
        jobs={
            "publish": JobConfig(
                steps=[
                    StepConfig(
                        uses="mqtt/publish",
                        with_params={
                            "concurrency": 1,
                            "topic": "ev/{table}",
                            "qos": 0,
                            "time_interval": {
                                "enabled": True,
                                "interval_strategy": "literal"  # Real-time simulation
                            }
                        }
                    )
                ]
            )
        }
    )
    return config.to_dict()


def generate_tdengine_with_checkpoint(
    host: str = "localhost",
    port: int = 6041,
    database: str = "tsbench",
    table_count: int = 100000,
    rows_per_table: int = 100
) -> Dict[str, Any]:
    """Generate TDengine config with checkpoint enabled for resume capability."""
    config = TaosgenConfig(
        target="tdengine",
        scenario="with-checkpoint",
        tdengine=TDengineConfig(
            dsn=f"taos+ws://root:taosdata@{host}:{port}/{database}",
            drop_if_exists=True,
            props="precision 'ms' vgroups 4"
        ),
        schema=SchemaConfig(
            name="meters",
            tbname=TbnameConfig(prefix="d", count=table_count, from_val=0),
            tags=[
                ColumnConfig(name="groupid", type="int", min=1, max=10),
                ColumnConfig(
                    name="location",
                    type="binary(24)",
                    values=["New York", "Los Angeles", "Chicago"]
                )
            ],
            columns=[
                ColumnConfig(name="ts", type="timestamp", start="1700000000000", precision="ms", step=1),
                ColumnConfig(name="current", type="float", min=0, max=100),
                ColumnConfig(name="voltage", type="int", expr="_i * math.pi % 180"),
                ColumnConfig(name="phase", type="float", min=0, max=360)
            ],
            generation=GenerationConfig(
                interlace=1,
                rows_per_table=rows_per_table,
                rows_per_batch=10000,
                num_cached_batches=0
            )
        ),
        jobs={
            "insert-data": JobConfig(
                steps=[
                    # tdengine/create-database supports checkpoint
                    StepConfig(
                        uses="tdengine/create-database",
                        with_params={
                            "checkpoint": {
                                "enabled": True,
                                "interval_sec": 10
                            }
                        }
                    ),
                    StepConfig(uses="tdengine/create-super-table"),
                    StepConfig(
                        uses="tdengine/create-child-table",
                        with_params={"batch": {"size": 1000, "concurrency": 10}}
                    ),
                    StepConfig(
                        uses="tdengine/insert",
                        with_params={
                            "concurrency": 8,
                            "checkpoint": {
                                "enabled": True,
                                "interval_sec": 10
                            }
                        }
                    )
                ]
            )
        }
    )
    return config.to_dict()


def generate_minimal_tdengine(table_count: int = 100, rows_per_table: int = 1000) -> Dict[str, Any]:
    """Generate minimal TDengine config for testing."""

    return {
        "schema": {
            "name": "meters",
            "tbname": {"count": table_count},
            "generation": {
                "rows_per_table": rows_per_table,
                "rows_per_batch": min(rows_per_table, 1000)
            }
        },
        "jobs": {
            "insert": {
                "steps": [
                    {"uses": "tdengine/create-super-table"},
                    {"uses": "tdengine/create-child-table"},
                    {"uses": "tdengine/insert"}
                ]
            }
        }
    }


# ============================================================================
# OUTPUT FUNCTIONS
# ============================================================================

def generate_yaml(config: Dict[str, Any], target: str, scenario: str) -> str:
    """Generate YAML with header comment."""
    header = f"""# Generated by taosgen-config skill
# Version: 0.1.0
# Target: {target}
# Scenario: {scenario}
# Generated at: {datetime.now().strftime("%Y-%m-%d")}

"""
    yaml_content = yaml.dump(config, default_flow_style=False, allow_unicode=True, sort_keys=False)
    return header + yaml_content


def save_config(config: Dict[str, Any], target: str, scenario: str, output_path: Optional[str] = None) -> str:
    """Save configuration to file."""
    if output_path is None:
        output_path = f"taosgen-config-{target}-{scenario}.yaml"

    yaml_content = generate_yaml(config, target, scenario)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)

    return output_path


# ============================================================================
# VALIDATION
# ============================================================================

VALID_TARGETS = ["tdengine", "mqtt", "kafka"]
VALID_ACTIONS = [
    "tdengine/create-database",
    "tdengine/create-super-table",
    "tdengine/create-child-table",
    "tdengine/insert",
    "mqtt/publish",
    "kafka/produce"
]
VALID_DATA_TYPES = [
    "timestamp", "bool", "tinyint", "tinyint unsigned", "smallint", "smallint unsigned",
    "int", "int unsigned", "bigint", "bigint unsigned",
    "float", "double", "decimal",
    "nchar", "varchar", "binary"
]


def validate_config(config: Dict[str, Any], target: str) -> List[str]:
    """Validate configuration and return list of errors."""
    errors = []

    # Validate target
    if target not in VALID_TARGETS:
        errors.append(f"Invalid target: {target}. Must be one of: {VALID_TARGETS}")

    # Check required sections
    if "schema" not in config:
        errors.append("Missing required section: schema")
    else:
        schema = config["schema"]
        if "name" not in schema:
            errors.append("Missing required field: schema.name")

    # Validate connection config exists for target
    if target == "tdengine" and "tdengine" not in config:
        errors.append("Missing required section: tdengine for TDengine target")
    elif target == "mqtt" and "mqtt" not in config:
        errors.append("Missing required section: mqtt for MQTT target")
    elif target == "kafka" and "kafka" not in config:
        errors.append("Missing required section: kafka for Kafka target")

    # Validate jobs
    if "jobs" in config:
        for job_name, job in config["jobs"].items():
            if "steps" not in job:
                errors.append(f"Job '{job_name}' missing required field: steps")
            else:
                for i, step in enumerate(job["steps"]):
                    if "uses" not in step:
                        errors.append(f"Job '{job_name}', step {i} missing required field: uses")
                    elif step["uses"] not in VALID_ACTIONS:
                        errors.append(f"Job '{job_name}', step {i}: Invalid action '{step['uses']}'. "
                                    f"Must be one of: {VALID_ACTIONS}")

    return errors


if __name__ == "__main__":
    # Example usage
    print("Generating sample configurations...\n")

    # TDengine smart meters
    config = generate_smart_meters_tdengine(table_count=1000, rows_per_table=10)
    yaml_output = generate_yaml(config, "tdengine", "smart-meters")
    print("=== TDEngine Smart Meters Config ===")
    print(yaml_output)

    # Validate
    errors = validate_config(config, "tdengine")
    if errors:
        print("Validation errors:", errors)
    else:
        print("Validation: PASSED\n")

    # MQTT smart meters
    config = generate_smart_meters_mqtt(table_count=1000, rows_per_table=10)
    yaml_output = generate_yaml(config, "mqtt", "smart-meters")
    print("=== MQTT Smart Meters Config ===")
    print(yaml_output)

    errors = validate_config(config, "mqtt")
    if errors:
        print("Validation errors:", errors)
    else:
        print("Validation: PASSED\n")
