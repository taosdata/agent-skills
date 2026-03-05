#!/usr/bin/env python3
"""
Validate generated configs against official documentation examples.
"""

from generator import (
    generate_smart_meters_tdengine,
    generate_smart_meters_mqtt,
    generate_smart_meters_kafka,
    generate_mqtt_realtime,
    generate_tdengine_with_checkpoint,
    generate_yaml
)


def validate_tdengine():
    """Validate TDengine config matches official example."""
    print('=== TDengine 智能电表示例验证 ===')

    config = generate_smart_meters_tdengine(
        host='127.0.0.1',
        port=6041,
        database='tsbench',
        table_count=10000,
        rows_per_table=10000
    )

    # 验证顶层结构
    assert 'tdengine' in config, "Missing tdengine section"
    assert 'schema' in config, "Missing schema section"
    assert 'jobs' in config, "Missing jobs section"

    # 验证 TDengine 配置
    td = config['tdengine']
    assert td['dsn'] == 'taos+ws://root:taosdata@127.0.0.1:6041/tsbench'
    assert td['drop_if_exists'] == False
    assert "precision 'ms'" in td['props'], "Props must have single quotes around precision"
    assert 'pool' in td
    assert td['pool']['enabled'] == True

    # 验证 Schema 配置
    schema = config['schema']
    assert schema['name'] == 'meters'
    assert schema['tbname']['prefix'] == 'd'
    assert schema['tbname']['count'] == 10000
    assert schema['tbname']['from'] == 0

    # 验证列定义
    columns = {c['name']: c for c in schema['columns']}
    assert 'ts' in columns
    assert columns['ts']['type'] == 'timestamp'
    assert columns['ts']['start'] == 'now'
    assert columns['ts']['precision'] == 'ms'

    assert 'current' in columns
    assert columns['current']['type'] == 'float'
    assert 'min' in columns['current'] and 'max' in columns['current']

    assert 'voltage' in columns
    assert columns['voltage']['type'] == 'int'
    assert 'expr' in columns['voltage']

    # 验证 generation
    gen = schema['generation']
    assert gen['rows_per_table'] == 10000
    assert gen['rows_per_batch'] == 10000

    # 验证 jobs
    jobs = config['jobs']
    assert 'insert' in jobs
    steps = jobs['insert']['steps']
    assert len(steps) == 3
    assert steps[0]['uses'] == 'tdengine/create-super-table'
    assert steps[1]['uses'] == 'tdengine/create-child-table'
    assert steps[2]['uses'] == 'tdengine/insert'

    print('  ✓ DSN 格式正确')
    print('  ✓ Props 包含单引号精度值')
    print('  ✓ Schema 结构完整')
    print('  ✓ 列定义包含 timestamp(float,min,max) + expr')
    print('  ✓ Jobs 步骤正确')
    print('  TDengine 验证通过\n')


def validate_mqtt():
    """Validate MQTT config matches official example."""
    print('=== MQTT 发布示例验证 ===')

    config = generate_smart_meters_mqtt(
        uri='tcp://localhost:1883',
        table_count=10000,
        rows_per_table=100
    )

    # 验证 MQTT 配置
    mqtt = config['mqtt']
    assert mqtt['uri'] == 'tcp://localhost:1883'
    assert mqtt['client_id'] == 'taosgen'
    assert mqtt['keep_alive'] == 5
    assert mqtt['clean_session'] == True

    # 验证 generation.concurrency (MQTT 示例中有此参数)
    gen = config['schema']['generation']
    assert 'concurrency' in gen, "MQTT example should have generation.concurrency"
    assert gen['concurrency'] == 8

    # 验证 action
    steps = config['jobs']['publish']['steps']
    assert steps[0]['uses'] == 'mqtt/publish'
    with_params = steps[0].get('with', {})
    assert 'topic' in with_params
    assert 'qos' in with_params

    print('  ✓ MQTT URI 格式正确')
    print('  ✓ 包含 generation.concurrency')
    print('  ✓ mqtt/publish action 配置正确')
    print('  MQTT 验证通过\n')


def validate_kafka():
    """Validate Kafka config matches official example."""
    print('=== Kafka 生产示例验证 ===')

    config = generate_smart_meters_kafka(
        bootstrap_servers='localhost:9092',
        topic='factory-electric-meter',
        table_count=10000,
        rows_per_table=100
    )

    # 验证 Kafka 配置
    kafka = config['kafka']
    assert kafka['bootstrap_servers'] == 'localhost:9092'
    assert kafka['topic'] == 'factory-electric-meter'
    assert kafka['client_id'] == 'taosgen'

    # 验证 generation.concurrency
    gen = config['schema']['generation']
    assert 'concurrency' in gen, "Kafka example should have generation.concurrency"

    # 验证 action
    steps = config['jobs']['produce']['steps']
    assert steps[0]['uses'] == 'kafka/produce'
    with_params = steps[0].get('with', {})
    assert 'acks' in with_params

    print('  ✓ Kafka bootstrap_servers 正确')
    print('  ✓ Topic 配置正确')
    print('  ✓ 包含 generation.concurrency')
    print('  ✓ kafka/produce action 配置正确')
    print('  Kafka 验证通过\n')


def validate_mqtt_realtime():
    """Validate MQTT realtime simulation with time_interval."""
    print('=== MQTT 实时数据模拟验证 ===')

    config = generate_mqtt_realtime(uri='tcp://localhost:1883', table_count=28)

    # 验证 rows_per_table = -1 (无限数据)
    gen = config['schema']['generation']
    assert gen['rows_per_table'] == -1, "Realtime mode should have rows_per_table=-1"

    # 验证 time_interval 配置
    steps = config['jobs']['publish']['steps']
    with_params = steps[0].get('with', {})
    assert 'time_interval' in with_params, "MQTT publish should support time_interval"

    ti = with_params['time_interval']
    assert ti['enabled'] == True
    assert ti['interval_strategy'] == 'literal'

    print('  ✓ rows_per_table = -1 (无限数据)')
    print('  ✓ time_interval.enabled = True')
    print('  ✓ interval_strategy = literal')
    print('  实时模拟验证通过\n')


def validate_checkpoint():
    """Validate checkpoint configuration."""
    print('=== Checkpoint 断点续传验证 ===')

    config = generate_tdengine_with_checkpoint(
        host='127.0.0.1',
        database='tsbench',
        table_count=100000,
        rows_per_table=100
    )

    steps = config['jobs']['insert-data']['steps']

    # 验证 create-database 支持 checkpoint
    assert steps[0]['uses'] == 'tdengine/create-database'
    assert 'checkpoint' in steps[0].get('with', {})

    # 验证 insert 支持 checkpoint
    assert steps[3]['uses'] == 'tdengine/insert'
    assert 'checkpoint' in steps[3].get('with', {})

    print('  ✓ tdengine/create-database 支持 checkpoint')
    print('  ✓ tdengine/insert 支持 checkpoint')
    print('  Checkpoint 验证通过\n')


def validate_no_env_vars():
    """Validate no environment variable syntax in output."""
    print('=== 安全验证: 无环境变量语法 ===')

    config = generate_smart_meters_tdengine()
    yaml_out = generate_yaml(config, 'tdengine', 'meters')

    # 检查没有 ${...} 语法
    assert '${' not in yaml_out, "YAML should not contain shell env var syntax"
    assert '${' not in yaml_out, "YAML should not contain any env var syntax"

    print('  ✓ 无 ${...} 环境变量语法')
    print('  安全验证通过\n')


if __name__ == '__main__':
    print('开始验证生成的配置与官方文档示例的一致性...\n')

    validate_tdengine()
    validate_mqtt()
    validate_kafka()
    validate_mqtt_realtime()
    validate_checkpoint()
    validate_no_env_vars()

    print('=== 所有验证通过 ===')
    print('生成的配置完全符合官方文档示例的约束条件')
