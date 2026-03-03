# Agentic Skills for TDengine

本仓库用于沉淀/分享可复用的 **Agentic Skills**（面向 Claude Code / Codex / OpenCode 等 AI Agent 的“可执行工作说明书”）。

- 技能源码位于：`skills/`
- 完整教程：`docs/AGENT_SKILLS_TUTORIAL.md`
- 贡献指南：`CONTRIBUTING.md`

## 仓库结构

```
.
├── skills/
│   ├── gen-doc/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── RS.md
│   │       ├── FS.md
│   │       ├── DS.md
│   │       ├── TS.md
│   │       └── TM.md
│   ├── gen-doc-rs/
│   │   └── SKILL.md
│   ├── gen-doc-fs/
│   │   └── SKILL.md
│   ├── gen-doc-ds/
│   │   └── SKILL.md
│   ├── gen-doc-ts/
│   │   └── SKILL.md
│   └── gen-doc-tm/
│       └── SKILL.md
├── docs/
│   └── AGENT_SKILLS_TUTORIAL.md
├── examples/
│   ├── Skills.toml
│   └── warp-demo-gen-doc-input.md
└── CONTRIBUTING.md
```

## Quick Start（推荐使用 cowork 管理/安装）

> `cowork` 是 Skills 管理 CLI（安装/更新/安全审计/冲突检查/Skills.toml 依赖管理等）。

### 1) 安装 cowork

```bash
cargo install cowork
cowork --version
```

### 2) 在你的目标项目中安装本仓库 skills（项目本地安装）

在 **你的项目根目录**（不是本仓库根目录）执行：

```bash
cowork install taosdata/agent-skills --local
```

> `--local` 会把 skills 安装到项目的技能目录（例如 `.claude/skills/`），便于 Warp/Agent 发现与使用。

### 3) 在 Warp 中使用

- 方式 A：Slash Command
  - `/gen-doc`
- 方式 B：自然语言
  - “帮我生成一份 RS/FS/DS/TS/TM，slug=xxx，内容如下 ……”

## 文档

- 完整教程：`docs/AGENT_SKILLS_TUTORIAL.md`
- 贡献指南：`CONTRIBUTING.md`

## License

TBD（如用于公司内部，可先不发布；如需开源建议补充许可证并明确贡献协议）。
