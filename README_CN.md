# TAOS Data Agent Skills Marketplace

本仓库提供可复用的 **TDengine IDMP** skills，供 AI Agent 配合 `idmp-cli` 使用。

## 前置条件

安装这些 skills 之前，请先准备好：

- Node.js **16+**
- `npm` / `npx`
- 可访问的 TDengine IDMP 环境地址
- 用户名密码，或预先签发好的 API key

## 第 1 步：安装 `idmp-cli`

```bash
npm install -g @tdengine/idmp-cli
idmp-cli --version
```

## 第 2 步：配置 IDMP 地址并直接登录

用一条命令创建默认 profile 并持久化 session：

```bash
printf '%s\n' "$IDMP_PASSWORD" | idmp-cli config init --profile default --server http://your-idmp:6042 --username admin@example.com --password-stdin
# 或
printf '%s\n' "$IDMP_API_KEY" | idmp-cli config init --profile default --server http://your-idmp:6042 --api-key-stdin
idmp-cli config show
idmp-cli auth check
```

## 第 3 步：按需新增并切换地址

如果你有多个环境，建议分别保存成 profile：

```bash
idmp-cli config init --profile staging --server http://staging-idmp:6042 --username admin@example.com
idmp-cli profile use staging
idmp-cli config show
```

## 第 4 步：后续按需重新登录

如果 profile 已经保存好，只需要刷新 session，可以继续使用 `auth login`：

```bash
printf '%s\n' "$IDMP_PASSWORD" | idmp-cli auth login --username admin@example.com --password-stdin
printf '%s\n' "$IDMP_API_KEY" | idmp-cli auth login --api-key-stdin
idmp-cli auth check
```

## 第 5 步：给 Claude Code 安装 plugin

先添加 TAOS Data marketplace：

```bash
claude plugin marketplace add taosdata/agent-skills
```

再安装 `idmp-plugin`：

```bash
claude plugin install idmp-plugin@taosdata
```

`idmp-plugin` 已经打包了配套 skills。只要你在用 Claude Code，就不需要再额外安装或拷贝这些 packaged skills。

## 第 6 步：给 OpenAI Codex 安装 plugin

使用支持 `codex plugin` 的 Codex 版本（已用 Codex CLI 0.156.1 验证）。
仓库发布到 GitHub 后，添加 GitHub marketplace：

```bash
codex plugin marketplace add taosdata/agent-skills
codex plugin add idmp-plugin@taosdata
codex plugin list
```

验证尚未推送的本地 checkout 时，才使用 `codex plugin marketplace add .`。

新建 Codex 会话以加载随包 skills。可以用以下提示词做只读冒烟验证：
“使用 idmp-plugin:idmp-shared 和 idmp-plugin:idmp-element 检查 IDMP 连接，并列出可访问的根元素。”
Codex 的执行环境需要能运行 `idmp-cli` 并访问配置的 IDMP 服务。
安装 plugin 不会自动安装 `idmp-cli` 或完成 IDMP 登录。

Claude Code 和 Codex 共用同一套 packaged skills，无需另行复制。

插件采用官方推荐的 [Agent Plugins 可移植格式](https://developers.openai.com/plugins/build/plugins#plugin-structure)：
根目录 `plugin.json` 声明 schema 和插件身份，OpenAI 展示信息位于
`extensions.com.openai.interface`，skills 从 `skills/` 自动发现。

通过 OpenAI 的 Claude plugin 提交页面时，应上传 `plugins/idmp-plugin/` 目录的归档，
不要上传整个仓库。归档根目录必须直接包含 `.claude-plugin/plugin.json` 和
`skills/<skill-name>/SKILL.md`；整个仓库根目录只用于
`codex plugin marketplace add taosdata/agent-skills` marketplace 安装。

本地打包可执行 `make codex` 或 `make claude`，生成的 ZIP 文件位于 `dist/`。

## 第 7 步：给其他 Agent 复用 packaged skills

本仓库不再单独发布顶层 standalone `skills/` 包。如果你用的是其他支持文件目录式 skills 的 Agent，可以直接复制 plugin 随包提供的 skills：

```bash
mkdir -p /path/to/other-agent/skills
cp -R plugins/idmp-plugin/skills/* /path/to/other-agent/skills/
```

如果目标 Agent 没有独立的 skills 目录机制，就把对应的 `SKILL.md` 及同级 `references/` 目录手工导入到该 Agent 的可复用 prompt / instruction 系统中。

## 仓库结构

```text
.
├── .agents/plugins/
│   └── marketplace.json
├── .claude-plugin/
│   └── marketplace.json
└── plugins/
    └── idmp-plugin/
        ├── .claude-plugin/
        │   └── plugin.json
        ├── plugin.json
        └── skills/
```

本仓库负责维护：

- Claude Code marketplace metadata
- Claude Code plugin metadata
- Codex marketplace 和 plugin metadata
- `plugins/idmp-plugin/skills/`：随 plugin 一起分发的 packaged skills
