# -*- coding: utf-8 -*-
"""
从 sample_data.json 中提取数据库名和子表名，按模板分组输出到 Markdown 文档。

用法:
    python extract_tables.py --sample-data <sample_data.json 路径> [--output <输出路径>]

输出文件默认保存在 sample_data.json 同目录下，命名为 table_summary.md。
"""

import argparse
import json
import sys
from collections import OrderedDict
from pathlib import Path


def extract_databases(data: dict) -> list[str]:
    """提取 databases[].name"""
    databases = data.get("databases", [])
    return [db["name"] for db in databases if "name" in db]


def build_template_supertable_map(data: dict) -> dict:
    """从 templates[].super_tables[].name 构建模板名到超级表名列表的映射。"""
    mapping = {}
    for tpl in data.get("templates", []):
        tpl_name = tpl.get("name", "")
        st_names = [st["name"] for st in tpl.get("super_tables", []) if "name" in st]
        if tpl_name:
            mapping[tpl_name] = st_names
    return mapping


def walk_trees(nodes: list, result: OrderedDict, st_map: dict) -> None:
    """
    递归遍历 trees 节点，找到所有含 child_table_names 的叶子节点，
    按 template 名称分组收集子表信息（含超级表名）。
    """
    for node in nodes:
        template = node.get("template", "")
        child_table_names = node.get("child_table_names", [])
        values = node.get("values", [])

        if child_table_names:
            if template not in result:
                result[template] = []
            # 查找该模板对应的超级表名
            super_table_names = st_map.get(template, [])
            super_table_str = ", ".join(super_table_names) if super_table_names else ""
            # 将子表名、设备名、超级表名配对
            for i, table_name in enumerate(child_table_names):
                device_name = values[i] if i < len(values) else ""
                result[template].append({
                    "table_name": table_name,
                    "device_name": device_name,
                    "super_table": super_table_str,
                })

        # 递归处理子节点
        children = node.get("children", [])
        if children:
            walk_trees(children, result, st_map)


def generate_markdown(db_names: list[str], table_groups: OrderedDict) -> str:
    """生成 Markdown 格式的输出内容。"""
    lines = []
    lines.append("# 数据库与子表清单\n")

    # 数据库名
    lines.append("## 数据库\n")
    for name in db_names:
        lines.append(f"- `{name}`")
    lines.append("")

    # 子表按模板分组
    lines.append("## 子表清单\n")
    total_tables = sum(len(tables) for tables in table_groups.values())
    lines.append(f"共 **{len(table_groups)}** 个模板，**{total_tables}** 张子表。\n")

    for idx, (template, tables) in enumerate(table_groups.items(), 1):
        # 获取该分组的超级表名（取第一条记录的值即可，同组一致）
        super_table = tables[0].get("super_table", "") if tables else ""
        header = f"### {idx}. {template}"
        if super_table:
            header += f"（超级表：`{super_table}`）"
        lines.append(header + "\n")
        lines.append("| 子表名 | 设备名称 | 超级表 |")
        lines.append("|--------|---------|--------|")
        for t in tables:
            lines.append(f"| `{t['table_name']}` | {t['device_name']} | `{t.get('super_table', '')}` |")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="从 sample_data.json 提取数据库名和子表名，输出到 Markdown 文档"
    )
    parser.add_argument(
        "--sample-data",
        required=True,
        help="sample_data.json 的路径",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="输出 Markdown 文件路径（默认与 sample_data.json 同目录下 table_summary.md）",
    )
    args = parser.parse_args()

    sample_data_path = Path(args.sample_data)
    if not sample_data_path.exists():
        print(f"[错误] 文件不存在: {sample_data_path}", file=sys.stderr)
        sys.exit(1)

    # 确定输出路径
    if args.output:
        output_path = Path(args.output)
        # 如果传入的是目录（已存在的目录或以 / 结尾），自动拼接默认文件名
        if output_path.is_dir() or str(args.output).endswith(('/', '\\')):
            output_path = output_path / "table_summary.md"
    else:
        output_path = sample_data_path.parent / "table_summary.md"

    # 读取 JSON
    with open(sample_data_path, encoding="utf-8") as f:
        data = json.load(f)

    # 提取数据库名
    db_names = extract_databases(data)
    if not db_names:
        print("[警告] 未找到数据库名（databases.name）", file=sys.stderr)

    # 遍历 trees 提取子表
    # 构建模板名 -> 超级表名映射
    st_map = build_template_supertable_map(data)

    table_groups = OrderedDict()
    trees = data.get("trees", [])
    walk_trees(trees, table_groups, st_map)

    if not table_groups:
        print("[警告] 未找到任何子表（child_table_names）", file=sys.stderr)

    # 生成并写入 Markdown
    md_content = generate_markdown(db_names, table_groups)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[完成] 已输出到: {output_path}")
    print(f"  数据库: {', '.join(db_names)}")
    print(f"  模板数: {len(table_groups)}")
    print(f"  子表数: {sum(len(t) for t in table_groups.values())}")


if __name__ == "__main__":
    main()
