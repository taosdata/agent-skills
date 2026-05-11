# TaosData Agent Skills Marketplace

Reusable **TDengine IDMP** skills for AI agents.

Use this repository together with `idmp-cli`.

## Prerequisites

Before installing these skills, make sure you have:

- Node.js **16+**
- `npm` / `npx`
- network access to your TDengine IDMP environment
- either a username/password or a pre-issued API key

## Step 1: Install `idmp-cli`

```bash
npm install -g @tdengine/idmp-cli
idmp-cli --version
```

## Step 2: Configure the IDMP server and log in

Create the default profile and persist a session in one command:

```bash
printf '%s\n' "$IDMP_PASSWORD" | idmp-cli config init --profile default --server http://your-idmp:6042 --username admin@example.com --password-stdin
# or
printf '%s\n' "$IDMP_API_KEY" | idmp-cli config init --profile default --server http://your-idmp:6042 --api-key-stdin
idmp-cli config show
idmp-cli auth check
```

## Step 3: Add and switch another address when needed

If you use multiple environments, save them as separate profiles:

```bash
idmp-cli config init --profile staging --server http://staging-idmp:6042 --username admin@example.com
idmp-cli profile use staging
idmp-cli config show
```

## Step 4: Re-authenticate later when needed

Use `auth login` when the saved profile already exists and you only need a new session:

```bash
printf '%s\n' "$IDMP_PASSWORD" | idmp-cli auth login --username admin@example.com --password-stdin
printf '%s\n' "$IDMP_API_KEY" | idmp-cli auth login --api-key-stdin
idmp-cli auth check
```

## Step 5: Install the plugin for Claude Code

First add the TaosData marketplace:

```bash
claude plugin marketplace add taosdata/agent-skills
```

Then install `idmp-plugin`:

```bash
claude plugin install idmp-plugin@taosdata
```

`idmp-plugin` already bundles the matching skills. If you are using Claude Code, you do not need to install or copy the packaged skills again.

## Step 6: Reuse the packaged skills for other agents

This repository does not publish a separate top-level standalone `skills/` bundle. If another agent supports filesystem-based skills, copy the packaged plugin skills directly:

```bash
mkdir -p /path/to/other-agent/skills
cp -R plugins/idmp-plugin/skills/* /path/to/other-agent/skills/
```

If the target agent does not support a dedicated skills directory, import the relevant `SKILL.md` files and their sibling `references/` directories into that agent's reusable prompt or instruction system manually.

## Repository layout

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

This repository is the source of truth for:

- Claude Code marketplace metadata
- Claude Code plugin metadata
- `plugins/idmp-plugin/skills/` as the packaged skills bundle shipped with the plugin
