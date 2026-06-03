# IDMP Structure Exporter (资产树展示与同步工具)

## 简介

`idmp-structure-exporter` 是一个专门用于将工业数字管理平台 (IDMP) 系统中复杂的元素层级结构转化为标准化、递归嵌套 JSON 文件的工具。它是 IDMP 自动化编排体系中负责“位置感知”的基础组件，为后续的分析配置、看板创建和 demo 展示提供统一的拓扑基准。

## 核心功能

*   **树形递归同步**：通过 API 自动化检索系统中所有的资产层级，并按 `id` -> `children` 关系生成完整的树结构。
*   **字段标准化**：每个节点固定包含 `id`, `name`, `template_id` 三大核心字段，确保与其他组件的接口兼容。
*   **智能场景过滤**：
    *   **名称过滤**：通过 `--root-name` 仅导出特定业务分支的资产树。
    *   **自动提取**：支持通过 `--sample-data` 从示例模型 JSON 中自动识别最终场景名称，解决自动重命名冲突导致的数据偏差。
*   **上下文共享**：生成的 `idmp_tree.json` 旨在存放在项目根目录下，供 `idmp-analysis-creator` 和 `idmp-panel-creator` 等执行层脚本共同调用，减少 API 访问次数。

## 目录结构

```text
idmp-structure-exporter/
├── README.md           # 本说明文件
├── SKILL.md            # Agent 执行资产导出任务的详细指引
└── scripts/            # 核心执行脚本
    └── export_idmp_tree.py # 递归导出 IDMP 元素拓扑的 Python 脚本
```

## 在 IDMP-EasyUse 体系中的作用

在全自动编排流程中，本技能不仅负责在最后一步为用户输出**资产树结构概览初**，还作为其他技能的前置依赖（Step 4 & 5），帮助分析器和看板器在茫茫多的系统元素中精准锁定当前 Demo 的目标节点 ID。

## 使用注意事项

1.  **节点限制**：脚本默认获取顶层根节点并递归。对于大型资产树环境，建议配合 `--root-name` 进行范围限制。
2.  **安全性**：请确保 `login_info.txt` 及其凭据所在的本地环境安全，严禁在日志中输出明文 Token。
3.  **无属性原则**：本技能仅关注资产拓扑（Where），不负责导出物理指标（What）。如需属性列表，请使用 `list_attributes.py` 工具。
