# IDMP MCP 接口配置参考

> 来源：https://idmpdocs.taosdata.com/integrating-with-other-systems/mcp-interface/

IDMP 通过反向代理对外提供 MCP 接口。AI 智能体无需在本地安装 MCP 服务端，只需连接 IDMP 提供的远程地址，即可读取元素上下文、时序属性、事件、分析结果、面板与 Dashboard，并在权限范围内执行受控写操作。

---

## 获取 API Key

1. 登录 IDMP Web UI。
2. 打开右上角头像菜单，点击账户项，打开个人设置对话框。
3. 切换到**密钥**页签。
4. 点击 **新增 API Key**，填写唯一标题，选择到期日期（或永不过期）。
5. 复制完整 API Key（列表页仅显示掩码）。
6. 复制得到的值以 `api_` 开头，**不包含** `Bearer` 前缀。需要完整 `Authorization` Header 时，请自行拼接为 `Bearer <IDMP_API_KEY>`。

---

## Streamable HTTP 接入（推荐）

### 接入地址与鉴权

| 字段 | 值 |
|------|-----|
| 推荐访问地址 | `https://<IDMP_HOST>:6034` |
| Transport 类型 | `http` |
| MCP URL | `https://<IDMP_HOST>:6034/api/v1/mcp/stream` |
| 鉴权方式 | `Authorization: Bearer <IDMP_API_KEY>` |
| 默认 HTTPS 端口 | `6034` |
| HTTP 排障地址 | `http://<IDMP_HOST>:6042/api/v1/mcp/stream` |

### VS Code GitHub Copilot CLI（通用表单）

| 字段 | 值 |
|------|-----|
| Server Name | `tdengine-idmp` |
| Server Type | `HTTP` |
| URL | `https://<IDMP_HOST>:6034/api/v1/mcp/stream` |
| HTTP Headers | `{"Authorization":"Bearer <IDMP_API_KEY>"}` |

### VS Code GitHub Copilot CLI（JSON 配置 `~/.copilot/mcp-config.json`）

```json
{
  "mcpServers": {
    "tdengine-idmp": {
      "type": "http",
      "url": "https://<IDMP_HOST>:6034/api/v1/mcp/stream",
      "headers": {
        "Authorization": "Bearer <IDMP_API_KEY>"
      }
    }
  }
}
```

### Claude Code（命令行）

```bash
claude mcp add --transport http tdengine-idmp \
  https://<IDMP_HOST>:6034/api/v1/mcp/stream \
  --header "Authorization: Bearer <IDMP_API_KEY>"
```

### Codex（`~/.codex/config.toml`）

```toml
[mcp_servers.tdengine-idmp]
url = "https://<IDMP_HOST>:6034/api/v1/mcp/stream"
bearer_token_env_var = "IDMP_API_KEY"
```

启动 Codex 前需在终端设置环境变量：`export IDMP_API_KEY=api_...`（原始值，不含 `Bearer` 前缀）。

---

## SSE 接入（仅在 Agent 明确要求时使用）

### 接入地址与鉴权

| 字段 | 值 |
|------|-----|
| 推荐访问地址 | `https://<IDMP_HOST>:6034` |
| Transport 类型 | `sse` |
| MCP URL | `https://<IDMP_HOST>:6034/api/v1/mcp/sse` |
| 鉴权方式 | `Authorization: Bearer <IDMP_API_KEY>` |
| 默认 HTTPS 端口 | `6034` |
| HTTP 排障地址 | `http://<IDMP_HOST>:6042/api/v1/mcp/sse` |

### 通用表单

| 字段 | 值 |
|------|-----|
| Server Name | `tdengine-idmp` |
| Type / Transport | `sse` |
| URL | `https://<IDMP_HOST>:6034/api/v1/mcp/sse` |
| HTTP Headers | `{"Authorization":"Bearer <IDMP_API_KEY>"}` |

### JSON 配置示例

```json
{
  "mcpServers": {
    "tdengine-idmp": {
      "type": "sse",
      "url": "https://<IDMP_HOST>:6034/api/v1/mcp/sse",
      "headers": {
        "Authorization": "Bearer <IDMP_API_KEY>"
      }
    }
  }
}
```

---

## 接入方式选择建议

1. 新接入场景或新版 MCP 客户端，优先使用 **Streamable HTTP**。
2. 现有 Agent 明确只支持 SSE 时，再使用 **SSE**。
3. 排障时保留接口路径，临时将协议和端口从 HTTPS `6034` 切换为 HTTP `6042`。

---

## Tool 功能概览

| 功能分类 | 能力描述 | 典型场景 |
|----------|----------|----------|
| 元素与层级 | 读取元素上下文、层级路径、子元素和分支范围 | 元素定位、资产树浏览、范围查询 |
| 属性数据 | 查询当前值、历史值和跨元素批量属性数据 | 趋势分析、状态核查、跨元素对比 |
| 事件与告警 | 查询事件、确认告警、补充标注、查看通知历史 | 告警分诊、事件复盘、通知追踪 |
| 分析任务 | 查询、创建、暂停、恢复和删除分析任务或告警规则 | 实时分析、规则下发、告警自动化 |
| 面板 | 查询、生成、创建和删除面板 | 单个元素的可视化配置与展示 |
| Dashboard | 搜索和关联 Dashboard | 跨面板汇总、场景级数据展示 |
| AI 与系统元数据 | 调用 IDMP AI，并读取系统配置、分类和推荐结果 | 自然语言问答、能力推荐、元数据读取 |
| 受控写入 | 创建属性、元素标注、事件标注和通知规则更新等 | 在权限范围内完成受控配置变更 |

---

## 变量说明

| 变量 | 说明 |
|------|------|
| `<IDMP_HOST>` | IDMP 实际域名或 IP 地址 |
| `<IDMP_API_KEY>` | 从 IDMP 界面复制的原始 API Key，形如 `api_<key_id>.<secret>`，**不含** `Bearer` 前缀 |