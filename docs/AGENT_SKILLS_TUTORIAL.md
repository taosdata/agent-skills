# Agent Skills 完全教程（以本仓库为例）

本教程目标：把 Agent Skills 这套“可复用能力封装方式”讲清楚，并以本仓库为例给出 **可操作、可复现** 的落地步骤：

- 仓库：`taosdata/agent-skills`
- 技能源码目录：`skills/`
- 相关文档：
  - Agent Skills 官方站点：agentskills.io
  - 规范：https://agentskills.io/specification

---

## 目录

- 1. 什么是 Agent Skills？为什么需要它？（agentskills.io 介绍）
- 2. Claude 的“渐进式披露（Progressive Disclosure）”与 Skills 的上下文加载
- 3. SKILL.md 规范整理（基于 agentskills.io/specification）
- 4. Skill 设计模式与写作方法（可复用的工程套路）
- 5. 使用 cowork 安装与管理 skills（crates.io）
- 6. 使用 Warp 演示本仓库技能（gen-doc）
- 7. 公司级 Skills 仓库的贡献与治理提议
- 附录 A：SKILL.md 写作模板（建议起步版）
- 附录 B：从 0 到 1 新建 Skill 的完整示例（目录结构 + SKILL.md + references + 最小验收）
- 附录 C：规范检查清单（提交前自检）

---

## 1. 什么是 Agent Skills？为什么需要它？（agentskills.io 介绍）

### 1.1 agentskills.io 是什么

agentskills.io 是 Agent Skills 的官方站点与规范集合，核心定位是：

- 提供一个**简单、开放**的格式，让不同 Agent 产品可以用一致的方式“发现、选择、加载、执行”技能。
- 把技能当成“可移植、可审计、可版本控制”的工程资产：用文件夹 + `SKILL.md`（再配合脚本/模板/参考资料）来封装流程知识。

在 agentskills.io 的 Overview 中，官方强调了几个关键点（对团队落地非常重要）：

- 之所以需要 skills：模型越来越强，但做“真实工作”时常常缺少程序性知识与组织上下文；skills 让这些上下文可以按需加载。
- Open development：该格式最初由 Anthropic 开发并以开放标准形式发布，标准对生态开放贡献。

站点内容通常包含：

- Overview：为什么需要 skills、能带来什么价值
- What are skills?：skills 如何工作
- Specification：`SKILL.md` 格式规范
- Integrate skills：如何让你的 Agent/工具支持 skills（包含 Claude 推荐的 `<available_skills>` XML 结构）
- Reference library：`skills-ref`（校验/生成 prompt XML 的参考实现）

### 1.2 Skill 的价值

将技能从“临时提示词”升级为“工程资产”的好处：

- 复用：同类任务（写文档、做 code review、排障）不再重复写提示词
- 稳定：输出格式、步骤、注意事项稳定，减少“每个人写出来不一样”
- 可维护：技能进入 Git 后，可 Review、可追溯、可回滚
- 可组合：可以用 Router skill 把任务分发给多个子 skill（本仓库 `gen-doc` 就是典型）
- 可互操作：遵循规范的 skill 理论上可被多种支持 skills 的产品消费

补充理解：Agent Skills 真正的“工程价值”来自两点：

1. 可审计（auditable）：skill 是纯文本/脚本/资源文件，任何人都能读、能 review。
2. 可移植（portable）：skill 是文件夹，天然适配 Git、包管理与分发；既能装进个人环境，也能作为项目依赖固化。

---

## 2. Claude 的“渐进式披露（Progressive Disclosure）”与 Skills 的上下文加载

> 这一节是理解 Skill 写法与目录组织的关键：**不要把所有知识一次性塞进系统提示词**，而是让 Agent“按需加载”。

### 2.1 什么是渐进式披露

渐进式披露是一种上下文管理策略：

- 先只加载“选择 skill 所需的最小信息”（metadata：name + description）
- 当确定需要某个 skill 时，再加载该 skill 的完整指令（`SKILL.md` body）
- 只有在执行过程中确实需要时，才继续加载 supporting files（`references/`、`assets/`）或执行脚本（`scripts/`）

Agent Skills 规范给出的推荐分层（核心数字非常实用）：

1. Metadata（约 50–100 tokens / skill）：所有 skills 启动时仅加载 `name/description`
2. Instructions（建议 < 5000 tokens）：激活 skill 时加载完整 `SKILL.md` body
3. Resources（按需）：执行中需要时才加载/运行 `scripts/` / `references/` / `assets/`

并建议：尽量让主 `SKILL.md` **不超过 500 行**，把长篇参考资料拆到 `references/`。

### 2.2 这与 Claude 有什么关系

在 Claude 这类模型中，实践里常见做法是：

- 在系统提示词中注入“可用 skills 列表”（只包含每个 skill 的 name/description/location）
- 当模型决定激活某个 skill，再通过文件读取工具（或宿主工具）把对应 `SKILL.md` body 拉入上下文

agentskills.io 在“Integrate skills”中给出 Claude 推荐的 XML 形态（示意，参考：https://agentskills.io/integrate-skills）：

```xml
<available_skills>
  <skill>
    <name>pdf-processing</name>
    <description>Extracts text and tables from PDF files...</description>
    <location>/path/to/skills/pdf-processing/SKILL.md</location>
  </skill>
</available_skills>
```

实现要点（对“怎么写 description / 怎么拆文件”有直接影响）：

- 对 filesystem-based agents：建议提供绝对路径 `location`，让 Agent 能精确读取对应 `SKILL.md`。
- 对 tool-based agents：如果宿主通过工具接口来加载 skill，`location` 可以省略。
- 元数据要短：官方建议每个 skill 的 metadata 约增加 50–100 tokens。

> 对 skill 作者来说，这意味着：**description 的质量决定了能不能被选中**；而 `SKILL.md` body 的结构决定了“激活后是否高效”。

### 2.3 对 Skill 作者的写作建议（渐进式披露视角）

把“如何写得更容易被选中、更便宜地加载、更稳地执行”拆成可执行规则：

- 把“触发词”写进 `description`
  - 不要写“帮助做 X”这种泛描述
  - 要包含：做什么 + 什么时候用 + 用户会怎么说（关键词）
- 让 `SKILL.md` body 更像“执行手册”，而不是“百科全书”
  - 直接给步骤、输入输出、边界情况
  - 细节解释、长表格、背景知识放 `references/`
- 把高重复、要求确定性的操作放进 `scripts/`
  - “每次都要写同样的脚本/同样的格式转换”就值得脚本化
- 引用文件不要链太深
  - 规范建议引用路径从 skill root 相对路径写起
  - 避免“从 A 引用 B、B 再引用 C…”的深链
- 交互上也做“渐进式披露”
  - 当输入不完整时：先问 **一个** 最关键的澄清问题（不要一次抛一串问题）
  - 当存在破坏性/不可逆操作时：先解释风险，再要求确认

---

## 3. SKILL.md 规范整理（基于 agentskills.io/specification）

> 本节是“你写的 skill 能不能被各类 Agent 正确识别”的底线。

### 3.1 目录结构（Directory structure）

一个 skill 至少是一个目录，目录中至少包含一个 `SKILL.md`：

```
skill-name/
└── SKILL.md
```

可选目录（按规范推荐语义）：

- `scripts/`：可执行脚本（Python/Bash/JS 等，取决于宿主 Agent 支持）
- `references/`：按需加载的参考资料（尽量小而聚焦）
- `assets/`：静态资源（模板、图片、数据文件等）

### 3.2 supporting 目录的写作建议（scripts/references/assets）

#### scripts/（可执行）

推荐把“需要确定性执行”的部分下沉为脚本：

- 脚本尽量自包含，或清晰声明依赖
- 错误信息要可读（失败时能指导用户怎么修）
- 对边界情况要有兜底（例如空输入、路径不存在、权限不足）

> 注意：是否支持脚本执行、支持哪些语言，取决于宿主 Agent。

#### references/（按需阅读）

references 的目标是“省上下文 + 提高可维护性”，建议：

- 每个 reference 文件聚焦一个主题（术语表、错误码、模板说明、FAQ）
- 文件越小越好：Agent 是按需加载，拆得细更利于渐进式披露

#### assets/（静态资源）

assets 常用于：

- 模板文件（文档模板、配置模板）
- 示例数据、lookup 表
- 图片/图表（如果宿主 Agent 支持）

### 3.3 SKILL.md 文件格式

`SKILL.md` 必须是：**YAML frontmatter + Markdown body**。

#### 3.3.1 frontmatter（必填字段）

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

字段约束（规范要点整理）：

- `name`（必填）
  - 1–64 字符
  - 仅允许：小写字母 `a-z`、数字 `0-9`、连字符 `-`
  - 不能以 `-` 开头或结尾
  - 不能出现连续 `--`
  - 必须与父目录名一致
- `description`（必填）
  - 1–1024 字符
  - 必须同时描述：**做什么** + **什么时候用**
  - 建议包含更具体的关键词（用户会怎么说/任务会怎么描述）

#### 3.3.2 frontmatter（可选字段）

规范给出的可选字段包括：

- `license`：许可证名称或对仓库内 license 文件的引用
- `compatibility`：环境要求（例如依赖系统包/网络访问/适用产品；规范限制 max 500 字符）
- `metadata`：任意键值对（string->string），用于额外信息（author/version 等）
- `allowed-tools`：预先批准可用工具（空格分隔，实验性；不同实现支持不同）

建议用法：

- 开源 skill：`license` 建议填写 SPDX（或明确指向 LICENSE 文件）
- 强依赖环境：用 `compatibility` 明确写清楚（避免用户/Agent 误用）
- 团队治理：用 `metadata.author`、`metadata.version`、`metadata.owner_team` 等做维护信息

#### 3.3.3 body（Markdown 正文）

规范对 body **不做强制格式**，但推荐包含：

- Step-by-step instructions（步骤）
- Examples（输入/输出示例）
- Common edge cases（常见坑与边界）

并强调：Agent 激活 skill 时会把 `SKILL.md` 整体读入上下文，因此更推荐把长内容拆分到 `references/`。

### 3.4 文件引用（File references）

- 引用 other files 时使用相对路径（相对 skill root）
- 避免过深的引用链（规范建议保持“一层深度”）

示例（规范风格）：

```md
See [the reference guide](references/REFERENCE.md) for details.

Run the extraction script:
scripts/extract.py
```

### 3.5 校验与参考实现（Validation / skills-ref）

agentskills.io 推荐使用 `skills-ref` 做规范校验：

```bash
skills-ref validate ./my-skill
```

并可生成 Claude 推荐的 `<available_skills>` prompt 片段：

```bash
skills-ref to-prompt <path>...
```

> 你可以把 `skills-ref validate` 放进 CI，作为合并门禁。

---

## 4. Skill 设计模式与写作方法（可复用的工程套路）

### 4.1 Router skill（路由入口）

当你有“一类问题的多个子类型”时，推荐用 Router skill：

- Router 负责：统一输入规范、统一命名/输出约定、统一流程
- 子 skill 负责：薄封装（thin wrapper）、模板/角色定位

本仓库示例：

- `skills/gen-doc/`：统一入口，根据 doc type 路由到 RS/FS/DS/TS/TM
- `skills/gen-doc-rs/` 等：thin wrapper，提示用 `gen-doc` 入口

### 4.2 Thin wrapper（薄封装）

薄封装 skill 的价值：

- 用户可能直接问“写 RS/写 TS”，wrapper 可以把自然语言意图“导流”到统一入口
- 统一入口可以保证输出路径、命名规范一致

### 4.3 Template + Reference 的拆分

一个稳定可维护的 skill 往往长这样：

- `SKILL.md`：让模型快速决策、快速执行
- `references/`：放长篇规则、术语表、错误码表、模板
- `assets/`：放要输出/复用的模板文件

这样既符合渐进式披露，也便于 Review：

- reviewer 可快速看 `SKILL.md` 是否会引导危险操作
- 细节材料单独 Review，不影响主流程可读性

### 4.4 安全写作约定（强烈建议）

Skill 本质是“教 Agent 做事的指令”，建议写清楚：

- 不要引导索要或输出敏感信息（token/password/private key）
- 任何可能破坏性操作（删除/覆盖/重置/写入生产）必须：
  1) 明确标注风险
  2) 要求用户二次确认
  3) 优先给 dry-run 方式

---

## 5. 使用 cowork 安装与管理 skills（crates.io）

> `cowork` / `co` 是 Skills 管理 CLI：安装、更新、依赖管理（Skills.toml）、安全审计、冲突检查等。

### 5.1 安装 cowork

```bash
cargo install cowork
cowork --version
```

初始化内置 skills（可选，但推荐先做）：

```bash
cowork init
```

### 5.2 安装本仓库 skills

#### 安装到项目本地（推荐）

在你的目标项目根目录执行：

```bash
cowork install taosdata/agent-skills --local
```

#### 全局安装（跨项目可用）

```bash
cowork install taosdata/agent-skills
```

#### 只安装某些 skills（示例）

```bash
cowork install taosdata/agent-skills -s gen-doc -s gen-doc-rs --local
```

#### 列出已安装仓库

```bash
cowork install --list
```

### 5.3 用 Skills.toml 管理项目依赖（推荐团队化）

初始化配置：

```bash
cowork config init
```

把依赖写入 `.cowork/Skills.toml` 后：

```bash
cowork config install
```

本仓库提供示例配置：`examples/Skills.toml`。

> 注意：`Skills.toml` 是“消费侧项目”的配置文件；放在业务项目里更合理。本仓库的 `examples/Skills.toml` 只是示例。

### 5.4 质量与安全：audit / verify / test

建议团队把下面三个命令作为“最低门槛”：

```bash
cowork audit
cowork verify
cowork test --check-conflicts
```

开发/贡献本仓库 skills 时，也可针对路径扫描：

```bash
cowork test --path ./skills
```

---

## 6. 使用 Warp 演示本仓库技能（gen-doc）

### 6.1 先理解 `gen-doc` 的设计

本仓库 `gen-doc` 是一个 Router skill：

- 入口：`skills/gen-doc/SKILL.md`
- 模板：`skills/gen-doc/references/{RS,FS,DS,TS,TM}.md`
- thin wrapper：`skills/gen-doc-{rs,fs,ds,ts,tm}/SKILL.md`

核心收益：

- 一个入口统一输入规范（doc type / slug / 内容来源）
- 一个入口统一文件命名与输出路径规则
- 子类型只负责模板与角色定位（避免重复约束）

### 6.2 演示前置：把技能安装到项目可发现的位置

```bash
cowork install taosdata/agent-skills --local
```

> `--local` 会把 skills 安装到目标项目的技能目录（具体位置取决于 cowork/宿主 Agent 的实现）。

### 6.3 演示脚本（可复现）

本仓库提供演示输入脚本：`examples/warp-demo-gen-doc-input.md`。

建议演示步骤：

1. 在 Warp 打开 Agent 对话，工作目录切换到目标项目根目录
2. 执行 Slash Command：`/gen-doc`
3. 按提示输入：doc type=RS，slug=demo-feature-x，并粘贴示例需求
4. 验收：
   - 是否生成符合 `YYYY-MM-DD-{slug}-RS.md` 的文件名
   - 生成后是否打印 `OutputPath: /absolute/path/to/file`

---

## 7. 公司级 Skills 仓库的贡献与治理提议

> 目标：让技能像代码一样可维护、可审计、可协作。

### 7.1 推荐的仓库分层

- 通用工程技能：code review、性能分析、排障、生成 release notes 等
- 领域技能：数据库/时序/前端/安全/云原生等（按域划分目录）
- 项目绑定技能：强依赖某仓库结构的技能（建议放项目内而不是公司通用仓库）

### 7.2 贡献规范（建议强制）

- 每个 skill 必须：`<skill-dir>/SKILL.md` + frontmatter（name/description）
- `name` 与目录名一致、全局唯一（遵循 agentskills.io/specification 的约束）
- 必须写清楚：Input / Output / Safety
- supporting files 必须放同目录并在文档中引用

### 7.3 Review 与责任边界

- 建议使用 CODEOWNERS 或约定“领域 Reviewer”
- 会修改文件/执行命令/涉及凭据与网络请求的 skill 必须安全 reviewer 过目

### 7.4 质量门禁（CI 建议）

建议把以下命令加入 CI（PR 必跑）：

```bash
cowork audit
cowork verify
cowork test --check-conflicts
```

### 7.5 版本化建议

- 内部滚动发布：main 分支即最新
- 稳定可回滚：tag + lockfile 固定依赖

---

## 附录 A：SKILL.md 写作模板（建议起步版）

> 这是一个“适配渐进式披露”的最小模板：主文件短、引用清晰。

```md
---
name: my-skill
description: 说明你能做什么 + 什么时候用 + 触发关键词（用户会怎么说）。
compatibility: （可选）需要的环境/工具/网络条件。
metadata:
  author: your-team
  version: "0.1"
---

# My Skill

## When to use
- ...

## Inputs
- ...

## Steps
1. ...

## Output
- ...

## Safety
- ...

## References
- references/REFERENCE.md
```

## 附录 B：从 0 到 1 新建 Skill 的完整示例（目录结构 + SKILL.md + references + 最小验收）

本附录用一个“从零开始”的示例，演示如何在 `skills/` 下新增一个 skill，并做到：

- 满足 `SKILL.md` 规范（name/description/目录结构）
- 支持渐进式披露（主流程短、长内容放 references）
- 有最小可验收步骤（本地冲突检查 + 演示触发）

### B.1 目标：做一个“生成问题排查报告”的 skill

示例 skill 名称：`triage-report`

- 用途：把用户提供的报错/日志/复现步骤，整理成一份可交付的排查报告（含：信息缺口、定位思路、下一步动作）。
- 为什么选它：
  - 足够通用（适合工程团队）
  - 很容易写出“输入/步骤/输出/安全”
  - 很适合把长内容下沉到 `references/`

### B.2 目录结构（建议）

在仓库里新增：

```
skills/
└── triage-report/
    ├── SKILL.md
    └── references/
        ├── QUESTIONS.md
        └── REPORT_TEMPLATE.md
```

- `SKILL.md`：主流程（短、可执行）
- `references/QUESTIONS.md`：面向用户的“补充信息问题清单”（按需加载）
- `references/REPORT_TEMPLATE.md`：排查报告模板（按需加载）

### B.3 编写 `skills/triage-report/SKILL.md`

> 注意：下面示例在 `description` 中刻意加入了触发词（triage / 排查 / 报错 / bug / incident），提升自动选中概率。

```md
---
name: triage-report
description: Generate a reproducible triage report from errors/logs (triage, incident, bug, 报错, 排查, 复现, 日志).
compatibility: Requires access to user-provided logs and repo context; does not execute scripts by default.
metadata:
  author: your-team
  version: "0.1"
---

# triage-report

## When to use

Use this skill when the user says:

- “帮我排查这个报错/崩溃/异常”
- “给我一份 incident/bug 的排查报告”
- “把这段日志整理成可交付的问题单/报告”

## Inputs (ask the user)

1. What happened?（现象）
2. Expected behavior?（预期）
3. How to reproduce?（复现步骤，最少 3 步）
4. Environment（OS/版本/部署方式/commit/配置）
5. Logs & error messages（原始日志，尽量完整）

If any of the above is missing, ask only ONE most critical clarification question first.

## Steps

1. Normalize the raw input
   - Extract error messages, stack traces, timestamps, and any IDs.
2. Identify information gaps
   - Use the question list in `references/QUESTIONS.md` if needed.
3. Form hypotheses
   - List 3–5 likely causes, ordered by probability.
4. Propose next actions
   - Give concrete commands/checkpoints the user can run.
   - Prefer safe/read-only commands first.
5. Produce a triage report
   - Follow `references/REPORT_TEMPLATE.md`.

## Output

Return a report in Markdown with these sections:

- Summary
- Environment
- Reproduction steps
- Evidence (logs)
- Hypotheses
- Next actions

## Safety

- Do not ask for secrets (tokens/passwords/private keys).
- Do not suggest destructive commands (e.g. `rm -rf`) unless the user explicitly asks and confirms.
- If commands might modify state, label them clearly and offer a dry-run alternative.

## References

- references/QUESTIONS.md
- references/REPORT_TEMPLATE.md
```

### B.4 编写 references（按需加载材料）

#### `skills/triage-report/references/QUESTIONS.md`

```md
# Triage questions (ask only when needed)

## Repro & scope
- Can you reproduce reliably? If yes, what is the minimal reproduction?
- When did it start (first bad version/commit)?
- Does it happen in production only, or also locally?

## Environment
- Exact versions (app/db/driver/runtime)
- Deployment mode (docker/k8s/systemd)
- Configuration differences vs working environment

## Logs & signals
- Full error + surrounding context (± 50 lines)
- Correlation IDs / request IDs
- Metrics anomalies (CPU/memory/latency)

## Recent changes
- Recent deploys / config changes
- Dependency updates
```

#### `skills/triage-report/references/REPORT_TEMPLATE.md`

```md
# Triage Report

## Summary

- What broke:
- Impact:
- Severity:

## Environment

- OS:
- Version:
- Deployment:
- Relevant config:

## Reproduction

1.
2.
3.

## Evidence

- Error message:
- Logs:

## Hypotheses

1.
2.
3.

## Next actions

- [ ] Step 1 (safe/read-only)
- [ ] Step 2
- [ ] Step 3
```

### B.5 最小验收步骤（你新增 skill 后至少做这些）

#### 1) 基础自检

- `skills/triage-report/SKILL.md` 存在
- frontmatter 包含 `name`/`description`
- `name` 与目录名一致，并满足格式约束

#### 2) 触发冲突检查（cowork）

在仓库根目录执行：

```bash
cowork test --path ./skills
cowork test --check-conflicts
```

#### 3) 在 Warp / Agent 中做一次手动演示

- 在目标项目里安装 skills（项目本地安装更方便验证）：

```bash
cowork install taosdata/agent-skills --local
```

- 然后在 Warp 中运行：
  - `/triage-report`

并粘贴一段报错日志，观察是否能按模板输出完整报告。

## 附录 C：规范检查清单（提交前自检）

- [ ] `skills/<name>/SKILL.md` 存在
- [ ] `name` 满足格式约束且与目录名一致
- [ ] `description` 包含“做什么 + 什么时候用 + 关键词”
- [ ] 主 `SKILL.md` 控制在可读范围（建议 < 500 行）
- [ ] 参考资料放 `references/`，脚本放 `scripts/`，模板资源放 `assets/`
- [ ] 引用路径为相对 skill root 的路径，且不要深链
- [ ] 对潜在危险操作要求二次确认
- [ ] 运行：`cowork test --check-conflicts`
- [ ] 运行：`cowork audit`（可选但推荐）
