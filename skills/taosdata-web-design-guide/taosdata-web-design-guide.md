---
name: taosdata-design-guide
description: TDengine 官网 ([taosdata.com](http://taosdata.com/)) 设计指南与规范。用于指导与 TDengine 中文官网相关的设计工作，包括颜色系统、排版、组件模式、间距布局等。在需要为 TDengine 创建网页相关设计时使用此 skill。
---

# TDengine 官网设计指南

本指南文档化 TDengine 官网 ([taosdata.com](http://taosdata.com/)) 的视觉设计系统，用于指导所有与 TDengine 品牌相关的设计工作。

## 1. 品牌概述

### 1.1 品牌定位

TDengine 是涛思数据开发的 AI 驱动的物联网工业大数据平台。

- **品牌名称**: TDengine / 涛思数据
- **核心产品**:
    - TDengine TSDB (高性能、分布式的时序数据库)
    - TDengine IDMP (AI 原生的工业数据管理平台)
- **目标受众**: 开发者、工业领域工程师、数据工程师、企业决策者

### 1.2 设计语言特点

- **专业可信**: 体现工业级产品的稳定性和可靠性
- **现代科技感**: 面向 AI 时代的工业数据管理平台
- **清晰简洁**: 信息架构清晰，内容易于理解
- **开放透明**: 开源社区精神，连接一切的开放生态

## 2. 颜色系统

### 2.1 品牌主色

| 颜色名称 | 色值 | 用途 |
| --- | --- | --- |
| **TDengine Blue** | `#0041ce` | 主品牌色，用于按钮、链接、重点强调 |
| **TDengine Dark** | `#141414` | 深色背景，用于页头、页脚、深色区块 |
| **TDengine Light** | `#f0f4ff` | 浅色背景，用于卡片、高亮区域 |

### 2.2 功能色

| 颜色名称 | 色值 | 用途 |
| --- | --- | --- |
| **highlight-green** | `#21e464` | 基础的醒目色，用于常规、次要操作按钮，视觉温和不刺眼 |
| **highlight-yellow** | `#f0a808` | 视觉冲击力中等，用于具有提醒功能的按钮 |
| **highlight-red** | `#d81e06` | 视觉最突出，用于需要强提醒的按钮或icon |

### 2.3 文字颜色

| 颜色名称 | 色值 | 用途 |
| --- | --- | --- |
| **Text Primary** | `#141414` | 主要正文、标题 |
| **Text Secondary** | `#595959` | 次要文字、描述、时间戳 |
| **Text Light** | `#a0aec0` | 占位符、禁用状态 |
| **Text White** | `#ffffff` | 深色背景上的文字 |

### 2.4 背景颜色

| 颜色名称 | 色值 | 用途 |
| --- | --- | --- |
| **Bg home page header** | `#f6faff` | 首页导航栏背景色 |
| **Bg light header** | `#eaf1ff` | 浅色页面导航栏背景色 |
| **Bg dark header** | `#141414` | 深色页面导航栏背景色 |
| **Bg blue** | `#0041ce` | 聚焦区块背景色 |
| **Bg white** | `#ffffff` | 白色区块背景色 |
| **Bg gray** | `#f5f7fa` | 灰色区块背景色 |
| **Bg footer** | `#141414` | 页脚背景色 |

### 2.5 边框颜色

| 颜色名称 | 色值 | 用途 |
| --- | --- | --- |
| **Border Default** | `#0041ce` | 主按钮边框、聚焦状态/活跃按钮按钮边框 |
| **Border Light** | `#f0f0f0` | 浅色边框、非聚焦状态/非活跃按钮边框 |

## 3. 排版系统

### 3.1 字体

- **中文字体**:
    - 优先: `"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei"`
    - 备选: `sans-serif`
- **英文字体**:
    - 优先: `"IBM Plex Sans", -apple-system, BlinkMacSystemFont`
    - 备选: `sans-serif`
- **代码字体**: `"Courier Prime", "JetBrains Mono", monospace`

### 3.2 字号层级

| 层级 | 桌面端 | 平板端 | 移动端 | 用途 |
| --- | --- | --- | --- | --- |
| **Hero** | 48px | 36px | 28px | 首页大标题 |
| **H1** | 32px | 28px | 24px | 页面主标题 |
| **H2** | 26px | 24px | 22px | 区块标题 |
| **H3** | 22px | 20px | 18px | 子区块标题 |
| **H4** | 20px | 16px | 16px | 卡片标题 |
| **Body Large** | 18px | 16px | 16px | 引导文字 |
| **Body** | 16px | 15px | 14px | 正文 |
| **Body Small** | 14px | 13px | 12px | 次要文字 |
| **Caption** | 12px | 12px | 11px | 说明、标签 |

### 3.3 字重

| 字重 | 数值 | 用途 |
| --- | --- | --- |
| **Light** | 300 | 装饰性文字 |
| **Regular** | 400 | 正文、描述 |
| **Medium** | 500 | 按钮、强调 |
| **Semibold** | 600 | 标题、重要文字 |
| **Bold** | 700 | 特别强调 |

### 3.4 行高

| 类型 | 行高 | 用途 |
| --- | --- | --- |
| **Tight** | 1.3em | 大标题、标语 |
| **Normal** | 1.5em | 正文、描述 |
| **Relaxed** | 2em | 长段落、阅读内容 |

## 4. 间距系统

### 4.1 基础间距

| 名称 | 数值 | 用途 |
| --- | --- | --- |
| **xs** | 4px | 行内元素间距 |
| **sm** | 8px | 紧凑间距 |
| **md** | 16px | 默认间距 |
| **lg** | 20px | 网格间距 |
| **lg** | 24px | 区块间距 |
| **xl** | 30px | 大区块间距 |
| **2xl** | 40px | 区域间距 |
| **3xl** | 60px | 大区域间距 |

### 4.2 布局规则

**容器宽度:**

- 最大宽度: `1440px`
- 内容宽度: `1240px`
- 窄内容: `768px`

**页面边距:**

- 桌面端: `100px`
- 平板端: `32px`
- 移动端: `16px`

**区块间距:**

- 大区块: `80-120px` 垂直间距
- 中区块: `48-64px` 垂直间距
- 小区块: `24-32px` 垂直间距

## 5. 组件模式

### 5.1 按钮

### 主按钮 (Primary Button)

```css
background: #0041ce;
color: #ffffff;
border: none;
border-radius: 30px;
padding: 30px 30px;
font-size: 14px;
font-weight: 400;
```

### 次按钮-绿(Secondary Button)

```css
background: transparent;
color: #2e1464;
border: 1px solid #2e1464;
border-radius: 30px;
padding: 30px 30px;
font-size: 14px;
font-weight: 400;
```

### 次按钮-黄 (Secondary Button)

```css
background: transparent;
color: #f0a808;
border: 1px solid #f0a808;
border-radius: 30px;
padding: 30px 30px;
font-size: 14px;
font-weight: 400;
```

### 轮廓按钮 (Outline Button - Dark)

```css
background: transparent;
color: #0041ce;
border: 1px solid #2651f0;
border-radius: 30px;
padding: 30px 30px;
font-size: 14px;
font-weight: 400;
```

### 5.2 卡片

### 博客卡片

```css
background: #ffffff;
border: 1px solid #e2e8f0;
border-radius: 20px;
padding: 30px;
font-color: #595959;
font-size: 14px;

&:hover {
  background:#0041ce
  transition: all 0.2s ease;
  font-color: #ffffff
}

```

### 场景卡片（scenarios-card）

```css
background: #ffffff;
border-radius: 20px;
padding: 20px;
transition: all 0.2s ease;
text-align: center;

.scenarios-text {
  overflow: hidden;
  max-height: 70px; /* 初始显示高度 */
  transition: max-height 0.3s ease; /* 仅文字高度变化有过渡 */
  font-size: 14px;
  font-weight: 400;
  color: #595959;
}

.scenarios-img {
    transition: height 0.3s ease; /* 图片容器高度变化有过渡 */
    box-sizing: border-box;
}

.scenarios-card:hover .scenarios-text {
    max-height: 120px; /* 展开文字高度 */
}

.scenarios-card:hover .scenarios-img {
    height: 100px; /* 悬停时图片显示高度 */
    margin-top: auto; /* 关键：将图片容器推到底部 */
    margin-bottom: -5px;
}

```

### 场景卡片

```css
background: #ffffff;
border: 1px solid #e2e8f0;
border-radius: 12px;
padding: 24px;
display: flex;
gap: 16px;

.icon-wrapper {
  width: 48px;
  height: 48px;
  background: #e8efff;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2651f0;
  flex-shrink: 0;
}

```

### 5.3 导航

### 主导航

```css
.navbar {
    max-width: 1240px;
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    background: transparent;
    padding-right: 20px;
    padding-left: 20px;
    margin-right: auto;
    margin-left: auto;
}

.nav-body {
  color: #141414;
  font-size: 18px;
  font-weight: 400;
  line-height: 1.5;
}

```

### 下拉菜单

```css
.dropdown {
    height: 450px;
    padding-top: 40px;
    padding-bottom: 40px;
    margin-top: 20px;
    border-top: 5px solid #0041ce;
    background-color: #ffffff;
}

```

### 5.4 表单元素

### 弹出框

```css
#popup {
    width: 400px;
    display: block;
    opacity: 1;
    position: fixed;
    height: auto;
    z-index: 1001;
    max-width: calc(100% - 30px);
    background-color: var(--white);
    left: 50%;
    transform: translate(-50%, -50%);
    top: 50%;
    transition: opacity .5s;
    opacity: 0;
    border-radius: .25rem;
    box-shadow: 0 12px 48px 0 rgba(0, 0, 0, .24);
}

```

### 5.5 标签

### 首选标签

```css
.tag-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    column-gap: 0.5em;
    font-size: 12px;
    font-weight: normal;
    text-align: center;
    padding: 5px 10px;
    margin-bottom: 20px;
    border-radius: 5px;
    border: 0px solid var(--accent-3);
    background-color: #e8efff;
    color: var(--contrast-2);
    text-decoration: none;
}
```

### 备选标签

```css
.tag-button-secondary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    column-gap: 0.5em;
    font-size: 12px;
    font-weight: normal;
    text-align: center;
    padding: 5px 10px;
    margin-bottom: 20px;
    border-radius: 5px;
    border: 0px solid var(--accent-3);
    background-color: #ebf8eb;
    color: #04b42a;
    text-decoration: none;
}
```

### 备选标签

```css
.tag-button-secondary {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    column-gap: 0.5em;
    font-size: 12px;
    font-weight: normal;
    text-align: center;
    padding: 5px 10px;
    margin-bottom: 20px;
    border-radius: 5px;
    border: 0px solid var(--accent-3);
    background-color: #ffecec;
    color: #f53f3f;
    text-decoration: none;
}
```

## 6. 布局模式

### 6.1 页面结构

```
┌─────────────────────────────────────────────┐
│  Navbar (100px, white)                      │
│  Logo │ Menu │ CTA Button                   │
├─────────────────────────────────────────────┤
│                                             │
│  Hero Section (full width, gradient/bg)     │
│  Headline + Subhead + CTAs                  │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  Feature Section (bg white)                 │
│  Image + Title + Description + CTA          │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  Application Scenarios Section (bg blue)    │
│  Card grid with image                       │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  Use Cases Section (bg grey)                │
│  Card grid with image                       │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  Blog Section (bg white)                    │
│  blog cards grid with dates                 │
│                                             │
├─────────────────────────────────────────────┤
│  Footer (bg footer)                         │
│  Links grid + Social + Copyright            │
└─────────────────────────────────────────────┘

```

### 6.2 网格系统

**两列布局:**

```css
two-column-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
}

```

**三列布局:**

```css
.three-column-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}

```

**四列布局:**

```css
.four-column-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

```

**响应式:**

```css
.responsive-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 32px;
}

```

### 6.3 对齐规则

- **左对齐**: 正文、标题、表单标签、列表项
- **居中**: 英雄区标题、统计数据、CTA 区域
- **右对齐**: 数值、时间、操作按钮

## 7. 视觉元素

### 7.1 图标

- **风格**: 线性图标 (outline style)
- **描边宽度**: 1.5px
- **圆角**: 2px
- **尺寸**:
    - 小: 16px
    - 中: 20px
    - 大: 24px
    - 超大: 32px

### 7.2 圆角

| 元素 | 圆角 |
| --- | --- |
| 按钮 | 30px |
| 卡片 | 12px |
| 输入框 | 6px |
| 标签 | 20px (pill) |
| 模态框 | 16px |
| 小元素 | 4px |

### 7.3 阴影

```css
/* 小阴影 - 卡片默认 */
shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);

/* 中阴影 - 悬浮状态 */
shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);

/* 大阴影 - 下拉菜单、模态框 */
shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);

/* 强调阴影 - 重点元素 */
shadow-primary: 0 4px 14px rgba(38, 81, 240, 0.25);

```

### 7.4 标签

在进行诸如博客、案例等合集区块时，使用标签来区分博客和案例类别。
- 同一种类别，标签要统一，首选「首选标签」。
- 不同类别，标签颜色要多样化，可选「备选标签」。

## 8. 图片与媒体

### 8.1 图片处理

- **格式**: WebP 优先，PNG/JPG 备选
- **加载**: 懒加载非首屏图片
-**尺寸**: 1920×1080，可适当缩放，但保持等比
- **占位**: 使用模糊占位或骨架屏
- **边框**: 图片添加 1px 边框 `#e2e8f0`
- **圆角**: 架构图、截图使用 8px 圆角

### 8.2 Logo 使用

- **主 Logo**: 蓝色 `#0041ce` 版本用于浅色背景
- **白色 Logo**: 用于深色背景
- **最小尺寸**: 用于 header 宽度不小于 200px；用于 footer 宽度不小于 100px
- **留白**: Logo 周围至少 16px 留白

## 9. 内容规范

### 9.1 文案风格

- **专业但不晦涩**: 使用行业术语，但提供必要解释
- **简洁有力**: 避免冗余，突出重点
- **行动导向**: CTA 使用动词开头
- **中文优先**: 主要面向中文用户，英文用于品牌名和技术术语

### 9.2 CTA 文案

| 场景 | 文案示例 |
| --- | --- |
| 主按钮 | 免费试用、立即体验、开始使用 |
| 次按钮 | 了解更多、查看文档、观看演示 |
| 链接 | 查看详情 →、阅读更多 → |

### 9.3 标题规范

- 使用动词或名词短语
- 避免标点符号（问号除外）
- 控制在 10 个汉字以内
- 突出核心卖点

## 10. 响应式断点

| 断点 | 宽度 | 主要调整 |
| --- | --- | --- |
| **Desktop** | ≥1240px | 完整布局 |
| **Laptop** | 1024-1279px | 缩小间距 |
| **Tablet** | 768-1023px | 两列变一列 |
| **Mobile** | <768px | 堆叠布局，简化导航 |

### 响应式模式

**导航:**

- Desktop: 水平导航链接
- Mobile: 汉堡菜单 + 全屏抽屉

**网格:**

- Desktop: 3-4 列
- Tablet: 2 列
- Mobile: 1 列

**字体:**

- Hero: Desktop 48px → Mobile 32px
- H1: Desktop 42px → Mobile 28px

## 11. 可访问性

### 11.1 颜色对比度

- 正文文字与背景对比度 ≥ 4.5:1
- 大号文字与背景对比度 ≥ 3:1
- 交互元素对比度 ≥ 3:1

### 11.2 交互状态

- 所有可点击元素有明确的 hover 状态
- 焦点状态使用 outline 或阴影
- 禁用状态使用 50% 透明度

### 11.3 动画

- 过渡时长: 200-300ms
- 缓动函数: ease 或 cubic-bezier(0.4, 0, 0.2, 1)
- 支持 prefers-reduced-motion 媒体查询

## 12. 第三方组件

### 12.1 合作伙伴 Logo

- 统一使用灰度处理
- Hover 时恢复彩色
- 等比例缩放，高度统一 40px
- 周围留白充足

### 12.2 认证徽章

- 保持原始比例
- 尺寸: 高度 60-80px
- 排列: 水平居中，间距 32px

## 13. 设计检查清单

创建新页面时检查:

- [ ]  颜色使用符合品牌规范
- [ ]  字体层级清晰
- [ ]  间距一致且充足
- [ ]  按钮样式符合规范
- [ ]  卡片样式统一
- [ ]  图片有适当边框和圆角
- [ ]  响应式在各断点正常
- [ ]  可访问性达标
- [ ]  文案风格一致
- [ ]  Logo 使用正确版本