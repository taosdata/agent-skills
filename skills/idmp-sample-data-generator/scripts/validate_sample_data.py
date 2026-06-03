#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validate_sample_data.py
校验 sample_data.json 是否符合 idmp_sample_data_v1.json __doc__ 中的所有强制规则。
用法：python3 validate_sample_data.py <sample_data.json路径>
"""

import json
import re
import sys
from pathlib import Path

ALLOWED_FUN_FUNCS = re.compile(r'\b(?!sin|cos|random)\b[a-zA-Z_][a-zA-Z0-9_]*\s*\(')
ALLOWED_FUN_PATTERN = re.compile(r'^[\d\s\+\-\*\/\.\(\)xX]*(?:(?:sin|cos|random)\s*\([^)]*\)[\d\s\+\-\*\/\.]*)*$')

errors = []

def err(path, msg):
    errors.append(f"  [FAIL] {path}: {msg}")

def check_fun(fun_str, path):
    # 提取所有函数调用名
    func_calls = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', fun_str)
    forbidden = [f for f in func_calls if f not in ('sin', 'cos', 'random')]
    if forbidden:
        err(path, f"fun 中使用了禁止的函数: {forbidden}，仅允许 sin(x)、cos(x)、random(n)")

def validate(data: dict, filepath: str):
    # ── 顶层必填字段 ──────────────────────────────────────────────
    for top_key in ('info', 'TDasset', 'datasource', 'databases', 'templates', 'tree_root', 'trees'):
        if top_key not in data:
            err('root', f"缺少顶层字段: {top_key}")

    # ── info ──────────────────────────────────────────────────────
    info = data.get('info', {})
    for k in ('id', 'name', 'description', 'file'):
        if not info.get(k):
            err('info', f"缺少或为空: {k}")
    if info.get('file') and Path(filepath).name != info['file']:
        err('info.file', f"值 '{info['file']}' 与实际文件名 '{Path(filepath).name}' 不一致")

    # ── tree_root ─────────────────────────────────────────────────
    tree_root = data.get('tree_root', {})
    if not tree_root.get('tag_name'):
        err('tree_root', "缺少 tag_name")

    # ── templates ─────────────────────────────────────────────────
    templates = data.get('templates', [])
    leaf_templates = {}   # name -> first tag name

    for ti, tmpl in enumerate(templates):
        tpath = f"templates[{ti}] ({tmpl.get('name', '?')})"

        if 'name' not in tmpl:
            err(tpath, "缺少 name")
        if 'leaf' not in tmpl:
            err(tpath, "缺少 leaf")
        if tmpl.get('namingPattern') != '${KEYWORD1}':
            err(tpath, f"namingPattern 必须为 '${{KEYWORD1}}'，当前值: {tmpl.get('namingPattern')!r}")

        if not tmpl.get('leaf', False):
            # 非叶子节点，无需检查 super_tables
            continue

        # 叶子节点：检查 super_tables
        super_tables = tmpl.get('super_tables', [])
        if not super_tables:
            err(tpath, "leaf=true 的模板缺少 super_tables")

        for si, stb in enumerate(super_tables):
            spath = f"{tpath}.super_tables[{si}] ({stb.get('name', '?')})"

            # 必填字段
            for field in ('db', 'name', 'time_step', 'non_stop_mode',
                          'beyond_current_time', 'insert_rows',
                          'batch_insert_num', 'insert_interval'):
                if field not in stb:
                    err(spath, f"缺少必填字段: {field}")

            # insert_rows 值校验
            if 'insert_rows' in stb and 'time_step' in stb:
                ts = stb['time_step']
                ir = stb['insert_rows']
                expected = 7 * 24 * 60 * 60 * 1000 // ts
                if ir == 0:
                    pass  # CSV 模式，允许为 0
                elif abs(ir - expected) > 1:
                    err(spath, f"insert_rows={ir} 与 7天公式计算值 {expected} (time_step={ts}) 不符，"
                               "CSV模式下才能设为0")

            # metrics
            metrics = stb.get('metrics', [])
            if not metrics:
                err(spath, "缺少 metrics 或 metrics 为空")
            for mi, m in enumerate(metrics):
                mpath = f"{spath}.metrics[{mi}] ({m.get('name', '?')})"
                for field in ('name', 'title', 'description', 'type', 'tdType', 'fun'):
                    if not m.get(field) and m.get(field) != 0:
                        err(mpath, f"缺少必填字段: {field}")
                if m.get('type') in ('Float', 'Double', 'Int', 'Bigint'):
                    for field in ('uomClass', 'uom'):
                        if not m.get(field):
                            err(mpath, f"数值型指标缺少: {field}")
                
                # uom 和 uomClass 一致性检查 (必须同时为空或同时非空)
                uom_val = str(m.get('uom') or "").strip()
                uom_class_val = str(m.get('uomClass') or "").strip()
                if bool(uom_val) != bool(uom_class_val):
                    err(mpath, f"uom('{uom_val}') 与 uomClass('{uom_class_val}') 不一致：必须同时为空或同时有值")
                if 'fun' in m:
                    check_fun(m['fun'], f"{mpath}.fun")
                if m.get('tdType') != 'metric':
                    err(mpath, f"metrics 中 tdType 应为 'metric'，当前: {m.get('tdType')!r}")

            # tags
            tags = stb.get('tags', [])
            if not tags:
                err(spath, "缺少 tags 或 tags 为空")

            first_tag_name = None
            for tgi, tag in enumerate(tags):
                tgpath = f"{spath}.tags[{tgi}] ({tag.get('name', '?')})"
                for field in ('name', 'title', 'description', 'type', 'tdType'):
                    if not tag.get(field):
                        err(tgpath, f"缺少必填字段: {field}")
                if tag.get('tdType') != 'tag':
                    err(tgpath, f"tags 中 tdType 应为 'tag'，当前: {tag.get('tdType')!r}")
                if first_tag_name is None:
                    first_tag_name = tag.get('name')

            # 记录叶子模板的第一个 tag，供 tree_root 校验
            tmpl_name = tmpl.get('name')
            if tmpl_name and first_tag_name:
                leaf_templates[tmpl_name] = first_tag_name

    # ── tree_root 与第一个 leaf 模板的 tag 一致性 ─────────────────
    if leaf_templates:
        tree_root_tag = tree_root.get('tag_name')
        all_first_tags = list(leaf_templates.values())
        if tree_root_tag not in all_first_tags:
            err('tree_root.tag_name',
                f"值 '{tree_root_tag}' 不在任何叶子模板的第一个tag中: {all_first_tags}")

    # ── trees ─────────────────────────────────────────────────────
    trees = data.get('trees', [])
    templates_map = {t['name']: t for t in templates if 'name' in t}

    all_values = set()
    all_ctns = set()

    def collect_all_children(node, path):
        # 记录并校验 values 和 child_table_names 的全局唯一性
        node_vals = node.get('values')
        if node_vals:
            v_list = node_vals if isinstance(node_vals, list) else [node_vals]
            for v in v_list:
                if v in all_values:
                    err(path, f"资产名称(values) '{v}' 重复，全局资产名必须唯一")
                all_values.add(v)

        node_ctns = node.get('child_table_names')
        if node_ctns and isinstance(node_ctns, list):
            for c in node_ctns:
                if c in all_ctns:
                    err(path, f"子表名(child_table_names) '{c}' 重复，全局子表名必须唯一")
                all_ctns.add(c)

        children = node.get('children', [])
        for ci, child in enumerate(children):
            cpath = f"{path}.children[{ci}]"
            tmpl_name = child.get('template')
            tmpl = templates_map.get(tmpl_name)
            is_leaf = tmpl and tmpl.get('leaf', False)

            # 仅对叶子节点生效的校验
            if is_leaf and tmpl:
                ctn = child.get('child_table_names', child.get('values', []))
                # 1. child_table_names 必须是显式列表而不是范围
                if not isinstance(ctn, list):
                    err(cpath, "叶子节点的 child_table_names 必须是显式数组，禁止使用范围语法")
                else:
                    for name in ctn:
                        if re.search(r'[\u4e00-\u9fff]', str(name)):
                            err(cpath, f"child_table_names 中含中文: '{name}'，必须使用纯英文及数字")

                # 2. 检查 tag 显式赋值
                stbs = tmpl.get('super_tables', [])
                for stb in stbs:
                    tags = stb.get('tags', [])
                    # 除第一个 tag 外，其余 tag 必须在 child 中显式赋值
                    for tag in tags[1:]:
                        tag_name = tag.get('name')
                        if tag_name and tag_name not in child:
                            err(cpath, f"缺少对超级表 '{stb.get('name')}' 中 tag '{tag_name}' 的显式赋值")
                        elif tag_name and isinstance(child.get(tag_name), list):
                            if isinstance(ctn, list) and len(child[tag_name]) != len(ctn):
                                err(cpath,
                                    f"tag '{tag_name}' 赋值数组长度 {len(child[tag_name])} "
                                    f"与 child_table_names 长度 {len(ctn)} 不一致")

            collect_all_children(child, cpath)

    for ti, tree in enumerate(trees):
        collect_all_children(tree, f"trees[{ti}]")

    # ── Tag 值不含"." ─────────────────────────────────────────────
    def check_tag_values(node, path):
        for key, val in node.items():
            if key in ('children', 'template', 'child_table_names', 'values', 'device_id'):
                continue
            if isinstance(val, list):
                for v in val:
                    if isinstance(v, str) and '.' in v:
                        err(f"{path}.{key}", f"Tag 值 '{v}' 含'.'，必须拆分为多个 Tag")
            elif isinstance(val, str) and '.' in val:
                err(f"{path}.{key}", f"Tag 值 '{val}' 含'.'，必须拆分为多个 Tag")
        for ci, child in enumerate(node.get('children', [])):
            check_tag_values(child, f"{path}.children[{ci}]")

    for ti, tree in enumerate(trees):
        check_tag_values(tree, f"trees[{ti}]")


def main():
    if len(sys.argv) < 2:
        print("用法: python3 validate_sample_data.py <sample_data.json路径>")
        sys.exit(1)

    filepath = sys.argv[1]
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 解析失败: {e}")
        sys.exit(2)
    except FileNotFoundError:
        print(f"[ERROR] 文件不存在: {filepath}")
        sys.exit(2)

    validate(data, filepath)

    if errors:
        print(f"\n{'='*60}")
        print(f"校验失败，共发现 {len(errors)} 个问题：")
        print('='*60)
        for e in errors:
            print(e)
        print('='*60)
        print("\n请修正以上问题后重新执行校验。")
        sys.exit(1)
    else:
        print(f"\n[OK] {filepath} 校验通过，所有强制字段完整。")
        sys.exit(0)


if __name__ == '__main__':
    main()
