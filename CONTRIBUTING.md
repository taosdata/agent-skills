# Contributing

本仓库用于沉淀可复用的 Agent Skills。欢迎贡献新技能、改进现有技能、补充模板与示例。

## 1. 新增一个 Skill

### 1.1 目录结构

在 `skills/` 下创建一个新目录：

- `skills/<skill-name>/SKILL.md`

建议 `<skill-name>` 使用 kebab-case，并与 `SKILL.md` frontmatter 中的 `name` 保持一致。

### 1.2 SKILL.md 必备字段

`SKILL.md` 顶部使用 YAML frontmatter：

- `name`: 全局唯一标识（kebab-case）
- `description`: 一句话说明“做什么 + 什么时候用”（影响自动触发）

建议正文至少包含：

- When to use（适用场景）
- Input（向用户确认哪些信息、默认值）
- Output（输出文件/格式/关键字段）
- Safety（禁止行为：索要密钥、建议危险命令、prompt 注入等）

### 1.3 Supporting files（可选）

如需模板/示例/脚本，请放在同一目录：

- `skills/<skill-name>/references/...`
- `skills/<skill-name>/examples/...`

并在 `SKILL.md` 中显式引用路径。

## 2. 本地验证（推荐）

> 提交前建议至少做一次冲突检查与安全检查。

### 2.1 cowork 安装

```bash
cargo install cowork
```

### 2.2 触发冲突检查

对当前仓库的 `skills/` 目录做扫描：

```bash
cowork test --path ./skills
cowork test --check-conflicts
```

### 2.3 安全审计与校验（可选但推荐）

```bash
cowork audit
cowork verify
```

## 3. 提交 PR 的建议

- PR 描述中说明：
  - 新增/修改了哪些 skill
  - 为什么需要（目标与场景）
  - 如何验收（建议给一段最小输入与期望输出）
- 尽量避免把“硬编码路径/组织内部链接/凭据”写死在 skill 中
- 若 skill 会引导执行 shell 命令：
  - 明确标注风险
  - 避免破坏性操作（如 `rm -rf`）
  - 避免泄露敏感信息（token/password/private key）

## 4. 讨论与约定（建议）

若计划把本仓库作为“公司级 skills 仓库”，建议补充：

- CODEOWNERS（按领域目录分配 reviewer）
- CI：`cowork audit/verify/test --check-conflicts`
- 版本策略：tag 发布或滚动更新
