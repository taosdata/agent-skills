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



errors = []

def err(path, msg):
    errors.append(f"  [FAIL] {path}: {msg}")



def validate(data: dict, filepath: str):
    # ── 顶层必填字段 ──────────────────────────────────────────────
    for top_key in ('info', 'TDasset', 'datasource', 'databases', 'templates', 'trees'):
        if top_key not in data:
            err('root', f"缺少顶层字段: {top_key}")
    if 'tree_root' in data:
        err('root', "禁止存在 tree_root 字段，根节点信息必须在 trees 中定义")

    # ── info ──────────────────────────────────────────────────────
    info = data.get('info', {})
    for k in ('id', 'name', 'description', 'file'):
        if not info.get(k):
            err('info', f"缺少或为空: {k}")
    if info.get('file') and Path(filepath).name != info['file']:
        err('info.file', f"值 '{info['file']}' 与实际文件名 '{Path(filepath).name}' 不一致")

    # ── tree_root 已废弃，禁止出现（上方已检测，此处无需重复）────────

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

            # non_stop_mode 值校验：必须为 JSON 布尔值（默认为 true）
            if 'non_stop_mode' in stb and not isinstance(stb['non_stop_mode'], bool):
                err(spath, f"non_stop_mode 必须为布尔值 true 或 false（默认为 true），当前值: {stb['non_stop_mode']!r}")

            # insert_rows 值校验：按公式 7*24*3600*1000/time_step 计算，必须 > 0
            if 'insert_rows' in stb:
                ir = stb['insert_rows']
                if not isinstance(ir, int) or ir <= 0:
                    err(spath, f"insert_rows 必须为正整数（按 7*24*3600*1000/time_step 计算），当前值: {ir}")

            # metrics
            metrics = stb.get('metrics', [])
            if not metrics:
                err(spath, "缺少 metrics 或 metrics 为空")
            for mi, m in enumerate(metrics):
                mpath = f"{spath}.metrics[{mi}] ({m.get('name', '?')})"
                for field in ('name', 'title', 'description', 'type', 'tdType'):
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
                if 'fun' not in m:
                    err(mpath, "缺少必填字段: fun")
                elif m.get('fun') == "":
                    err(mpath, "fun 不能为空字符串，必须填写模拟函数表达式（如 '4*sin(x)+random(2)+4'）")
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

    # ── tree_root 已废弃，跳过一致性校验 ───────────────────────────

    # ── trees ─────────────────────────────────────────────────────
    trees = data.get('trees')
    if not isinstance(trees, dict):
        err('trees', "trees 必须为对象(dict)，不能是数组(list)")
        trees = {}

    # 校验 trees 根节点
    if isinstance(trees, dict):
        if 'value' not in trees:
            err('trees', "根节点缺少必填字段: value")
        if 'values' in trees:
            err('trees', "根节点只允许 value，禁止出现 values")
        if 'visible' not in trees:
            err('trees', "根节点缺少必填字段: visible")
        if 'children' not in trees:
            err('trees', "根节点缺少必填字段: children")
        if trees.get('visible') != 'true':
            err('trees', f"根节点 visible 必须为字符串 'true'，当前值: {trees.get('visible')!r}")
        if 'children' in trees and not isinstance(trees['children'], list):
            err('trees', "根节点 children 必须为数组")

    templates_map = {t['name']: t for t in templates if 'name' in t}

    all_values = set()
    all_ctns = set()

    def collect_all_children(node, path):
        if not isinstance(node, dict):
            err(path, "节点必须为对象")
            return

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
        if not isinstance(children, list):
            return

        for ci, child in enumerate(children):
            cpath = f"{path}.children[{ci}]"
            if not isinstance(child, dict):
                err(cpath, "节点必须为对象")
                continue

            tmpl_name = child.get('template')
            tmpl = templates_map.get(tmpl_name)
            is_leaf = bool(tmpl and tmpl.get('leaf', False))

            if is_leaf:
                for field in ('template', 'child_table_names', 'values'):
                    if field not in child:
                        err(cpath, f"叶子节点缺少必填字段: {field}")

                ctn = child.get('child_table_names')
                if 'child_table_names' in child and not isinstance(ctn, list):
                    err(cpath, "叶子节点的 child_table_names 必须是显式数组，禁止使用范围语法")
                elif isinstance(ctn, list):
                    for name in ctn:
                        if re.search(r'[\u4e00-\u9fff]', str(name)):
                            err(cpath, f"child_table_names 中含中文: '{name}'，必须使用纯英文及数字")

                # 检查 tag 显式赋值
                stbs = tmpl.get('super_tables', [])
                for stb in stbs:
                    tags = stb.get('tags', [])
                    for tag in tags:
                        tag_name = tag.get('name')
                        if tag_name and tag_name not in child:
                            err(cpath, f"缺少对超级表 '{stb.get('name')}' 中 tag '{tag_name}' 的显式赋值")
                        elif tag_name and isinstance(child.get(tag_name), list):
                            if isinstance(ctn, list) and len(child[tag_name]) != len(ctn):
                                err(cpath,
                                    f"tag '{tag_name}' 赋值数组长度 {len(child[tag_name])} "
                                    f"与 child_table_names 长度 {len(ctn)} 不一致")
            else:
                for field in ('template', 'values', 'children'):
                    if field not in child:
                        err(cpath, f"中间层节点缺少必填字段: {field}")
                if 'children' in child and not isinstance(child.get('children'), list):
                    err(cpath, "中间层节点 children 必须为数组")

            collect_all_children(child, cpath)

    if isinstance(trees, dict):
        collect_all_children(trees, 'trees')

    # ── Tag 值不含"." ─────────────────────────────────────────────
    def check_tag_values(node, path):
        if not isinstance(node, dict):
            return
        for key, val in node.items():
            if key in ('children', 'template', 'child_table_names', 'values', 'device_id', 'value'):
                continue
            if isinstance(val, list):
                for v in val:
                    if isinstance(v, str) and '.' in v:
                        err(f"{path}.{key}", f"Tag 值 '{v}' 含'.'，必须拆分为多个 Tag")
            elif isinstance(val, str) and '.' in val:
                err(f"{path}.{key}", f"Tag 值 '{val}' 含'.'，必须拆分为多个 Tag")
        children = node.get('children', [])
        if isinstance(children, list):
            for ci, child in enumerate(children):
                check_tag_values(child, f"{path}.children[{ci}]")

    if isinstance(trees, dict):
        check_tag_values(trees, 'trees')


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
