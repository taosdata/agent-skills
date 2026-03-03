# Warp 演示脚本：gen-doc

目标：用 `/gen-doc` 生成一份 RS 文档，并验证输出路径与文件命名规范。

## 0. 前置：在你的目标项目根目录安装 skills

```bash
cowork install taosdata/agent-skills --local
```

## 1. 在 Warp 中开始

在 Warp Agent 对话中输入：

```text
/gen-doc
```

## 2. 按照提示填写输入（示例）

- doc type: RS
- slug: demo-feature-x
- content inputs: 直接粘贴下面内容

### 需求内容（示例，可复制粘贴）

背景：我们希望把“文档生成”流程标准化，减少不同团队输出格式不一致导致的沟通成本。

目标：
1. 支持生成 RS/FS/DS/TS/TM 五类文档；
2. 文件名必须包含日期与 slug；
3. 生成完成后必须打印 OutputPath，便于 CI/脚本后处理。

功能点：
- 支持 doc type 选择或自动推断；
- 支持模板化输出；
- 支持输出路径按环境变量或项目 docs 目录路由。

## 3. 验收要点

- 输出文件名是否符合：`YYYY-MM-DD-demo-feature-x-RS.md`
- 是否打印了：`OutputPath: /absolute/path/to/file`
