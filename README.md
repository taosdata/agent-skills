# TAOS Data Agent Skills Marketplace

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

First add the TAOS Data marketplace:

```bash
claude plugin marketplace add taosdata/agent-skills
```

Then install `idmp-plugin`:

```bash
claude plugin install idmp-plugin@taosdata
```

`idmp-plugin` already bundles the matching skills. If you are using Claude Code, you do not need to install or copy the packaged skills again.

## Step 6: Install the plugin for OpenAI Codex

Use a Codex version that supports `codex plugin` (validated with Codex CLI 0.156.1).
After the repository is published, add the GitHub marketplace:

```bash
codex plugin marketplace add taosdata/agent-skills
codex plugin add idmp-plugin@taosdata
codex plugin list
```

When validating an unpushed local checkout, use `codex plugin marketplace add .` instead.

Start a new Codex thread to load the packaged skills. For a read-only smoke test, ask:
"Use idmp-plugin:idmp-shared and idmp-plugin:idmp-element to check my IDMP connection and list the available root elements."
Codex must be able to run `idmp-cli` and access the configured IDMP server.
Plugin installation does not install `idmp-cli` or log in to IDMP for you.

Claude Code and Codex share the same packaged skills; no separate copy is needed.

The plugin follows the [portable Agent Plugins format](https://developers.openai.com/plugins/build/plugins#plugin-structure):
root `plugin.json` declares the schema and package identity, OpenAI presentation metadata
lives under `extensions.com.openai.interface`, and skills are discovered from `skills/`.

For OpenAI's Claude plugin submission portal, upload an archive of `plugins/idmp-plugin/`,
not the repository root. The archive root must contain `.claude-plugin/plugin.json` and
`skills/<skill-name>/SKILL.md`; the repository root is the marketplace source used by
`codex plugin marketplace add taosdata/agent-skills`.

Build the archives locally with `make codex` or `make claude`; both write the resulting
ZIP files to `dist/`.

## Step 7: Reuse the packaged skills for other agents

This repository does not publish a separate top-level standalone `skills/` bundle. If another agent supports filesystem-based skills, copy the packaged plugin skills directly:

```bash
mkdir -p /path/to/other-agent/skills
cp -R plugins/idmp-plugin/skills/* /path/to/other-agent/skills/
```

If the target agent does not support a dedicated skills directory, import the relevant `SKILL.md` files and their sibling `references/` directories into that agent's reusable prompt or instruction system manually.

## Repository layout

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

This repository is the source of truth for:

- Claude Code marketplace metadata
- Claude Code plugin metadata
- Codex marketplace and plugin metadata
- `plugins/idmp-plugin/skills/` as the packaged skills bundle shipped with the plugin
