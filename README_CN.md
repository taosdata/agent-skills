# TaosData Agent Skills Marketplace

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

先添加 TaosData marketplace：

```bash
claude plugin marketplace add taosdata/agent-skills
```

再安装 `idmp-plugin`：

```bash
claude plugin install idmp-plugin@taosdata
```

`idmp-plugin` 已经打包了配套 skills。只要你在用 Claude Code，就不需要再额外装一遍 standalone skills。

## 第 6 步：给其他 Agent 安装 standalone skills

如果你用的不是 Claude Code，而是其他支持 skills 机制的 Agent，再从 GitHub 安装 standalone skills：

```bash
npx --yes skills add taosdata/agent-skills -g -y
```

## 仓库结构

```text
.
├── .claude-plugin/
│   └── marketplace.json
└── plugins/
    └── idmp-plugin/
        ├── .claude-plugin/
        │   └── plugin.json
        └── skills/
```

本仓库负责维护：

- Claude Code marketplace metadata
- Claude Code plugin metadata
- `plugins/idmp-plugin/skills/`：随 plugin 一起分发的 packaged skills
