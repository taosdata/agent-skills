---
name: idmp-structure-exporter
description: 将 IDMP 系统的元素层级结构导出为标准化的递归嵌套 JSON 文件。输出文件应包含每个元素的 id、name、template_id。当用户需要分析 IDMP 的资产结构、同步资产树或为其它技能准备 IDMP 拓扑信息时触发。
metadata:
  author: Wang Zhe
  version: 0.3.0
  owner_team: solution-center
---

# IDMP 资产树导出工具

将 IDMP 系统的元素层级结构导出为标准化的递归嵌套 JSON 文件，供其他技能（如 `idmp-sample-data-generator`、分析技能）进行程序化读取，解决多技能协作中对资产树认知不统一的问题。

## 输入要求

| 参数 | 是否必需 | 说明 |
|:--- |:--- |:--- |
| **`state.json` 路径** | 推荐 | 包含 `idmp-login` 字段的状态文件，由 `idmp-easyuse` 初始化生成 |
| **输出路径** | ✅ 必传 | 导出 JSON 的目标路径，默认文件名 `idmp_tree_structure.json` |
| **`--root-name`** | 二选一 | 按名称过滤，仅导出指定根节点及其子树 |
| **`--sample-data`** | 二选一 | 指定 `sample_data.json`，自动从中提取 `info.name` 作为根节点过滤条件 |
| **`--update`** | 可选 | 更新模式：从已有输出文件中提取根节点名称并重新拉取最新结构 |
| IDMP 登录信息 | 降级备用 | 若无 `state.json`，从 `login_info.txt` 或用户输入获取 host、user、password |

---

## 常见陷阱（Gotchas）

> 以下规则是 Agent 在没有明确提示时最容易出错的地方，执行前必须阅读。

**严禁导出全系统资产树**
- 由其他技能调用时，必须通过 `--root-name` 或 `--sample-data` 参数限定导出范围。
- 仅当用户明确要求"导出全部资产"时，才可省略过滤参数。

**脚本路径必须动态定位**
- 本技能的脚本相对位置固定为本 `SKILL.md` 同级的 `scripts/export_idmp_tree.py`。
- 执行前必须先定位本 `SKILL.md` 的绝对路径，并以此推导 `SKILL_DIR`，严禁硬编码绝对路径。

**`state.json` 优先于直接登录参数**
- 只要存在 `state.json`，必须通过 `--state` 参数传入，而不是手动传递 `--host`/`--user`/`--password`。

**输出文件不得覆盖已有有效结果**
- 若输出路径已存在文件，默认应追加时间戳以示区分，或在 `--update` 模式下原地更新。

---

## 执行流程

## Telemetry (MUST)

> 调用 `skill-telemetry`，传入 `name=idmp-structure-exporter version=0.3.0 author=Wang Zhe`。
> 失败不阻塞，但必须尝试。详见 `skill-telemetry`。

<!-- 注意：frontmatter 中 metadata.version 的值即为 telemetry 上报的版本号，请保持一致。 -->

---

### 第一步：环境检查与登录信息确认

**1.1 定位技能脚本目录**

本技能脚本相对位置固定（`<skill_dir>/scripts/export_idmp_tree.py`），但安装路径因环境而异。执行前必须先定位本 `SKILL.md` 的绝对路径，再以此推导 `SKILL_DIR`：

```bash
# 找到本 SKILL.md 的位置，其所在目录即为 SKILL_DIR
SKILL_DIR="$(dirname "$(realpath "<本SKILL.md的绝对路径>")")" 
ls "$SKILL_DIR/scripts/export_idmp_tree.py"
```

若文件不存在，立即停止并告知用户。

**1.2 确定登录凭据来源**

按以下优先级获取 IDMP 登录信息：

| 优先级 | 来源 | 说明 |
|:--- |:--- |:--- |
| 1（最高） | `state.json` 中的 `idmp-login` 字段 | 由 `idmp-easyuse` 初始化时生成 |
| 2 | 用户指定的登录信息 | 包含 host、user、password |
| 3（最低） | 直接向用户询问 | 仅在上述两种来源均不可用时执行 |

**1.3 确定输出路径**

- 若调用方（如 `idmp-sample-data-generator`）已明确传入输出路径，直接使用。
- 否则，在当前项目的 `outputs/` 目录下生成，文件名默认为 `idmp_tree.json`。

---

### 第二步：执行资产树导出

根据输入参数，选择以下其中一条路径执行，严禁混用：

#### 路径 A：基于 sample_data.json 过滤（优先路径 - 由其他技能调用时）

适用于 `idmp-sample-data-generator` 完成数据加载后需要同步资产树的场景：

```bash
python3 "$SKILL_DIR/scripts/export_idmp_tree.py" \
  --state <STATE_JSON_PATH> \
  --sample-data <SAMPLE_DATA_JSON_PATH> \
  --output <OUTPUT_PATH>
```

#### 路径 B：按根节点名称过滤

适用于用户明确指定资产名称的场景：

```bash
python3 "$SKILL_DIR/scripts/export_idmp_tree.py" \
  --state <STATE_JSON_PATH> \
  --root-name "<ROOT_ELEMENT_NAME>" \
  --output <OUTPUT_PATH>
```

#### 路径 C：更新已有结构文件

适用于资产树已导出过、需要刷新最新状态的场景：

```bash
python3 "$SKILL_DIR/scripts/export_idmp_tree.py" \
  --state <STATE_JSON_PATH> \
  --update \
  --output <OUTPUT_PATH>
```

#### 路径 D：导出全系统资产树（仅用户明确要求时）

```bash
python3 "$SKILL_DIR/scripts/export_idmp_tree.py" \
  --state <STATE_JSON_PATH> \
  --output <OUTPUT_PATH>
```

---

### 第三步：验证与交付

**3.1 JSON 格式验证**

脚本执行完毕后，立即验证输出文件的语法正确性：

```bash
python3 -c "import json; data = json.load(open('<OUTPUT_PATH>')); print('节点总数：', sum(1 for _ in __import__('itertools').chain([data])))" && echo "JSON OK"
```

**3.2 结果交付**

向用户或调用方返回：

| 交付项 | 说明 |
|:--- |:--- |
| 输出文件绝对路径 | 供后续技能直接引用 |


---

## 执行完整性检查清单

- [ ] **脚本路径已确认**：`export_idmp_tree.py` 存在于技能脚本目录
- [ ] **登录凭据已就绪**：优先从 `state.json` 读取，其次 `login_info.txt`，最后询问用户
- [ ] **过滤参数已指定**：除用户明确要求全量导出外，必须传入 `--root-name`、`--sample-data` 或 `--update` 之一
- [ ] **输出文件已验证**：JSON 语法正确，根节点字段完整
- [ ] **结果已交付**：已将文件路径和资产树概览返回给用户或调用方
```

## 注意事项

1. **登录信息**：如果 `login_info.txt` 不存在或不可读，请优先提示用户提供连接信息。
2. **大型资产树**：脚本已处理分页逻辑，但对于极端庞大的资产树（数万个节点），请注意内存占用并告知进度。
3. **文件命名**：默认输出文件名为 `idmp_tree.json`。

