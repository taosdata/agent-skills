# TDengine IDMP — Web Design Guide

This guide documents the visual design system used throughout the TDengine Industrial Data Management Platform (IDMP) frontend. All new pages and features must follow these conventions.

---

## 1. Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Vue 3 |
| Component Library | Element Plus |
| CSS Utility | UnoCSS |
| Preprocessor | SCSS |
| Typography | IBM Plex Sans |
| Responsive Base | 1920 × 1080 design grid |

---

## 2. Color System

All colors are exposed as CSS custom properties via `src/styles/variables.scss`. **Always use CSS variables — never hardcode hex values.**

### Brand / Semantic Colors

| Token | Light Value | Dark Value | Use |
|-------|-------------|------------|-----|
| `--tda-color-primary` | `#2651f0` | `#e5eaf3` | Buttons, links, active states, borders |
| `--tda-color-success` | `#49ae18` | `#49ae18` | Success states, positive metrics |
| `--tda-color-danger` | `#f56c6c` | `#f56c6c` | Errors, destructive actions |
| `--tda-color-warning` | `#f6cb6a` | `#f6cb6a` | Warnings, caution states |
| `--tda-color-info` | `#909399` | `#909399` | Neutral info, secondary icons |

### Text Colors

| Token | Light Value | Use |
|-------|-------------|-----|
| `--tda-color-text` | `#000000` | Primary body text |
| `--el-text-color-primary` | `#303133` | Form labels, headings |
| `--el-text-color-regular` | `#343537` | Default text in components |
| `--tda-color-text-light-dark` | `#bec0c0` | Placeholder, disabled, muted |
| `--el-text-color-placeholder` | `#a8abb2` | Input placeholders |
| Table link text | `#2651f0` | Clickable links in tables |
| Table row text | `#4d6992` (rgb(77,105,146)) | Data rows in tables |

### Background Colors

| Token | Light Value | Use |
|-------|-------------|-----|
| `--tda-color-background` | `#ffffff` | Page/card default background |
| `--tda-color-background-dark` | `#ffffff` | Header/sidebar background |
| `--tda-color-background-light-dark` | `#f2f3f3` | Page content area background |
| `--tda-color-background-1` | `#f7f7f7` | Subtle section backgrounds |
| `--tda-color-background-light-dark-2` | `#ecf2fe` | Selected/highlighted rows |
| `--tda-color-bg-hover` | `#f3f4f6` | Hover state backgrounds |
| `--tda-panel-back-color` | `#f8fafb` | Panel/chart card backgrounds |
| `--el-disabled-bg-color` | `#f5f7fa` | Disabled form fields |
| Table header bg | `#e8efff` | `--el-table-header-bg-color` |
| Input group prefix bg | `#f2f3f5` | `.tda-select-with-inner-label` |
| Input group label bg | `#e8efff` | Label prefix chips |

### Border Colors

| Token | Light Value | Use |
|-------|-------------|-----|
| `--tda-color-border` | `#e3e4e6` | Card, section, and area borders |
| `--tda-panel-border-color` | `#dbdee2` | Panel card borders |
| `--el-border-color` | `#dcdfe6` | Element Plus component borders |
| `--el-border-color-light` | `#e4e7ed` | Light variant borders |
| `--tda-color-border-lighter` | `#2651f0` | Active / focus borders (primary) |
| Header bottom border | `#eaecef` (rgb 234,236,239) | Navbar separator |
| Sub-toolbar bottom border | `#dcdfe6` | Content toolbar separator |
| Sidebar right border | `#e3e4e6` | Left panel separator |

---

## 3. Typography

### Font Family

```css
font-family: 'IBM Plex Sans', sans-serif;
```

### Responsive Base Size

The root font size scales between 10.5 px (≤800 px viewport) and 16 px (≥1920 px):

```css
html {
  font-size: calc(10.5px + 3.5 * (100vw - 1440px) / 480);
}
```

| Breakpoint | Body font-size |
|-----------|---------------|
| ≤ 800 px | 12 px |
| 801–1024 px | 13 px |
| 1025–1920 px | **14 px** (default design target) |
| > 1920 px | 16 px |

### Type Scale

| Size | px | Usage |
|------|-----|-------|
| `xs` | 12 px | Pagination numbers, tags, small labels |
| `sm` (default) | 14 px | Body text, table cells, nav items, form labels |
| `md` | 16 px | Icon button icons, section headings |
| `lg` | 18 px | Dialog content text, large headings |
| `xl` | 20 px | Page-level headings |

### Font Weights

| Weight | Usage |
|--------|-------|
| 300 | Thin labels, timestamps |
| **400** | Default body text |
| **500** | Buttons, emphasis |
| (700 only for active pagination numbers) |

### Line Heights

- Body/components: `normal`
- Detail items: `20 px` (`.td-detail-item`)
- Collapse headers: `46 px` height, centered vertically

---

## 4. Spacing & Layout

### Responsive Spacing Variables

```scss
$vw-base: calc(100vw / 1920);       // 1 vw unit on 1920 px base
$layout-space: calc(12 * $vw-base); // ~12 px at 1920 px
$layout-space-l-r: calc(24 * $vw-base); // ~24 px at 1920 px (always 2× $layout-space)
$content-space: 10px;
```

### Page Layout Regions

```
┌──────────────────────────────────────────────┐  ← height: 56 px
│  NAVBAR (white, border-bottom: 1px #eaecef)  │  ← padding: 0 ~20px
│  Logo │ Nav tabs          │ User avatar       │
└──────────────────────────────────────────────┘
┌──────────────────────────────────────────────┐  ← height: 38 px
│  SUB-TOOLBAR (white, border-bottom #dcdfe6)  │  ← padding: 9px 0 9px 14px
│  Breadcrumb / Tab nav     │ Action buttons    │
└──────────────────────────────────────────────┘
┌────────────┐ ┌─────────────────────────────────┐
│  SIDEBAR   │ │   CONTENT AREA                  │
│ (white)    │ │   (bg: #f2f3f3)                 │
│ 279 px wide│ │   padding: ~10px ~20px           │
│ border-right│ │                                 │
│ #e3e4e6   │ │                                 │
│ padding:  │ │                                 │
│ 10px      │ │                                 │
└────────────┘ └─────────────────────────────────┘
┌──────────────────────────────────────────────┐  ← ~26px
│  STATUS BAR (white, tiny text)               │
│  Version info          │ Theme toggle  │ Lang │
└──────────────────────────────────────────────┘
```

### Content White Card

When content lives inside the content area it is wrapped in a white card:

```scss
background: var(--tda-color-background);  // #fff
border: 1px solid var(--tda-panel-border-color); // #dbdee2
border-radius: 5px; // or 8px for larger cards
padding: 16px 20px;
```

### Alignment Rules

All content within a working area must follow a consistent alignment axis. **Never mix arbitrary alignments within the same region.**

| Context | Alignment |
|---------|-----------|
| Form labels | Left-aligned |
| Form input fields | Left-aligned, full width of their column |
| Input text typed by the user | Left-aligned |
| Table column headers | Left-aligned (except numeric columns → right-aligned) |
| Table cell data | Left-aligned (except counts/numbers → right-aligned) |
| Numeric / metric values in stat displays | Right-aligned within their cell |
| Toolbar left side (filters, dropdowns) | Left-aligned |
| Toolbar right side (action icon buttons) | Right-aligned |
| Dialog / popup content | Left-aligned for labels and fields |
| Dialog footer buttons | Centered |
| Detail view labels | Left-aligned in a fixed-width column |
| Detail view values | Left-aligned, starting after the label column |

**The working area has two alignment anchors:**
- Everything on the **left side** of a split layout (labels, nav items, tree) is **left-aligned**.
- Everything on the **right side** of the toolbar row (action buttons) is **right-aligned** using `margin-left: auto` or `justify-content: flex-end`.

```scss
// Correct toolbar layout
.toolbar {
  display: flex;
  align-items: center;

  .toolbar-left  { display: flex; align-items: center; gap: $layout-space; }
  .toolbar-right { display: flex; align-items: center; gap: $layout-space; margin-left: auto; }
}
```

### Spacing Hierarchy — Group Separation

Spacing must visually communicate which items belong together. The space **between groups** must always be larger than the space **within a group**. This is the primary way users perceive that content is related.

```
┌─ Group A ──────────────────────────────────┐
│  Label 1        [Input field      ]        │  ← 14px between items inside group
│  Label 2        [Input field      ]        │
│  Label 3        [Input field      ]        │
└────────────────────────────────────────────┘
                                               ← 28px between groups (2× intra-group gap)
┌─ Group B ──────────────────────────────────┐
│  Label 4        [Input field      ]        │
│  Label 5        [Input field      ]        │
└────────────────────────────────────────────┘
```

**Spacing scale:**

| Level | Value | Usage |
|-------|-------|-------|
| Intra-item (lines within a paragraph) | 4–6 px | `line-height`, adjacent inline elements |
| Intra-group (items within a form section) | 14 px | `margin-bottom` on `el-form-item` |
| Inter-group (between sections/panels) | 24–28 px | `margin-bottom` between `el-collapse-item`, sections |
| Page-level (between major blocks) | 32–40 px | `padding` on page wrapper, between cards |

```scss
// Form item spacing (intra-group)
.el-form-item--default { margin-bottom: 14px; }

// Section spacing (inter-group) — always at least 2× intra-group
.form-section + .form-section { margin-top: 28px; }
.tda-detail-section + .tda-detail-section { margin-top: 24px; }

// Page-level card spacing
.content-card + .content-card { margin-top: 20px; }
```

**Rule of thumb:** if two items have the same gap around them, they look like they belong to the same group. Always increase the gap when a new group starts.

---

## 5. Component Patterns

### 5.1 Buttons

#### Icon Button (toolbar action) — `.tda-icon-btn`

```scss
width: 36px;
height: 36px;
padding: 8px 10px;
font-size: 16px;
background: var(--tda-color-background);  // white
border: 1px solid #dcdfe6;
border-radius: 4px;
color: #343537;
margin-left: $layout-space;  // spaced from siblings
```

Use for: search, refresh, export, settings icons in toolbars.

#### Circle Hover Button — `.circle-hover`

```scss
width: 32px;
height: 32px;
padding: 8px;
background: transparent;
border: none;
border-radius: 50%;
// Icon inside:
font-size: 18px; // or svg 18×18px

&:hover {
  background: rgba(primary-rgb, var(--tda-circle-hover-bg-opacity));
  border-radius: 50%;
}
```

Use for: inline edit, delete, expand actions next to content.

#### Primary Button

```scss
background: var(--tda-color-primary);
color: #fff;
border-radius: 4px; // or 20px for .tda-btn-radius
```

#### Form / Dialog Buttons

```scss
width: 100px;
margin: 0 20px;
// Centered in footer via flexbox
```

### 5.2 Tables

Every list/table view in the app follows a strict, consistent pattern. All rules below are **mandatory**.

#### 5.2.1 Visual Styles

```scss
// Header row
--el-table-header-bg-color: #e8efff;
--el-table-header-text-color: #343537;
font-weight: normal;  // NOT bold — always override Element Plus default
height: 40px;
padding: 8px 0;

// Data rows
color: #4d6992;       // rgb(77, 105, 146) for regular data cells
height: 42px;
padding: 8px 0;
cursor: pointer;      // every row is clickable
background: #fff;

// Hover row
background: var(--tda-color-background-light-dark-2); // #ecf2fe

// Clickable link cells only
color: var(--tda-color-primary); // #2651f0
// Non-link data cells use --el-text-color-regular (#343537), NOT blue
```

#### 5.2.2 Toolbar Button Order

The toolbar above every table has a strictly defined left-to-right button order:

```
LEFT SIDE                          RIGHT SIDE
┌─────────────────────────────────────────────────────────────────────┐
│  [Filter/Select dropdowns]    [+]  [↑]  [↓]  [🔍]  [⊞]  [↻]  [⚙] │
└─────────────────────────────────────────────────────────────────────┘
```

Rules for the right-side icon buttons (each is a `.tda-icon-btn`, 36×36px):

| Position | Icon | Purpose | Required? |
|----------|------|---------|-----------|
| Leftmost of icon group | `+` (Add) | Create a new record | Only if creation is supported |
| After `+` | `↑` (Import) | Import / upload from file | Only if import is supported |
| After import | `↓` (Export / Download CSV) | Export table data to CSV | **Always present** |
| After export | `🔍` (Search) | Toggle inline search bar | Only if search is supported |
| After search | `⊞` (Grid/List toggle) | Switch between card and table view | Only if dual-view exists |
| After toggle | `↻` (Refresh) | Reload data | **Always present** |
| **Rightmost** | `⚙` (Column config) | Show/hide columns chooser | **Always present — must be last** |

Key rules:
- The **column configuration button is always the rightmost** icon in the toolbar.
- The **download/export CSV button is always present** on every table view.
- If `+` (add) exists, it is the **leftmost** icon button, before all others.
- All icon buttons must be wrapped in `el-tooltip` with `effect="dark"` and a descriptive label.
- Icon buttons are separated by `margin-left: $layout-space` from each other.

#### 5.2.3 Row Actions — Three-dot Context Menu

**Every row** must have a three-dot (`⋮`) action button as the **rightmost element** in that row.

```
│  Name           │  Count  │  Description           │  Categories  │  ⋮  │
```

- The `⋮` button is a `.circle-hover` button (32×32px, transparent, hover shows primary bg).
- It is **always visible** (not just on hover) so users know it exists.
- Clicking it opens an `el-dropdown` / popover menu directly below or beside the button.
- Typical menu items: Edit, Duplicate, Delete (Delete always last, always in danger color `--tda-color-danger`).
- The column containing `⋮` has a fixed width (~48px) and no header label.

```vue
<el-table-column width="48" fixed="right">
  <template #default="{ row }">
    <el-dropdown trigger="click" @command="handleCommand($event, row)">
      <el-button class="circle-hover" :icon="MoreFilled" />
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item command="edit">Edit</el-dropdown-item>
          <el-dropdown-item command="delete" style="color: var(--tda-color-danger)">
            Delete
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>
  </template>
</el-table-column>
```

#### 5.2.4 Column Width Rules

- Every column must be **wide enough to display its full header title** without truncation.
  Set `min-width` explicitly — do not rely on auto-sizing from data content alone.
- Use `min-width` (not `width`) on data columns so they grow if the viewport allows.
- Use fixed `width` only for fixed-size columns like checkboxes, status icons, and the `⋮` column.

```vue
<!-- Good -->
<el-table-column prop="name" label="Template Name" min-width="160" />
<el-table-column prop="elementCount" label="Element Count" min-width="130" />

<!-- Bad — header may be truncated -->
<el-table-column prop="name" label="Template Name" width="80" />
```

#### 5.2.5 Column Sorting

Every sortable column shows sort indicators **on header hover** — not always visible.

```vue
<el-table-column prop="name" label="Name" min-width="160" sortable="custom" />
```

```scss
// Sort arrows only appear when hovering the header cell
.el-table__header th .cell {
  .caret-wrapper { display: none; }

  &:hover .caret-wrapper { display: inline-flex; }
}
```

- Use `sortable="custom"` (server-side) rather than `sortable` (client-side) for large datasets.
- The sort arrow pair (↑↓) appears inside the header cell, right-aligned after the label text.
- Only one column can be sorted at a time; the active sort column keeps its arrows always visible.

#### 5.2.6 Column Resizing

All data columns (except fixed-width columns like checkboxes and `⋮`) must be resizable by the user.

```vue
<el-table border :resizable="true">
  <el-table-column prop="name" label="Name" min-width="160" resizable />
</el-table>
```

- Set `:border="true"` on `el-table` to enable column resize drag handles.
- `min-width` still applies — the user cannot shrink a column below its `min-width`.
- Column widths should be persisted to `localStorage` if the user resizes them.

#### 5.2.7 Cell Content — No Wrapping, Truncate with Tooltip

**Row content must never wrap onto multiple lines.** All cell text is single-line, truncated with ellipsis (`…`) when too long. The full text is shown in a tooltip on hover.

```vue
<el-table-column prop="description" label="Description" min-width="200">
  <template #default="{ row }">
    <el-tooltip
      :content="row.description"
      placement="top"
      effect="dark"
      :disabled="!isOverflowing(row.description)"
    >
      <span class="cell-text-truncate">{{ row.description }}</span>
    </el-tooltip>
  </template>
</el-table-column>
```

```scss
.cell-text-truncate {
  display: block;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

// Apply globally to all table cells
.el-table .cell {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

- The tooltip uses `effect="dark"` (primary blue background) to match the app tooltip style.
- `max-width: 400px` and `word-break: break-word` apply to the tooltip itself (already set globally).
- Applies to **all** columns except those with structured content (e.g., action buttons, status icons).

#### 5.2.8 Cell Content Must Be Selectable and Copyable

Every text cell in a table must be **selectable by the user** so they can copy values without opening an edit dialog. Do not suppress text selection in table cells.

```scss
// Do NOT set this on table cells — it blocks copy
// user-select: none;  ← forbidden on .el-table .cell

// Correct: allow text selection everywhere in table body
.el-table__body .cell {
  user-select: text;
  cursor: text; // only when hovering text, not the row action area
}

// The row itself can still be cursor: pointer for row-click navigation
.el-table__row {
  cursor: pointer;
}
```

- The `⋮` button column and checkbox column are exempt (they use default cursor).
- If a cell uses a custom component (tag, badge, icon), the text inside it must still be selectable.
- Do **not** use `pointer-events: none` on cell text spans — this blocks both clicking and selecting.

#### 5.2.9 Complete Table Checklist

Before shipping any new table view, verify:

- [ ] Header bg is `#e8efff`, font-weight is `normal`
- [ ] Row height is 42px, text color is `rgb(77, 105, 146)`
- [ ] Only link/clickable cells are primary blue; plain data cells are `#343537`
- [ ] Rightmost toolbar icon is the column config (⚙) button
- [ ] A Download CSV (↓) button is present in the toolbar
- [ ] Every row has a `⋮` three-dot button as the rightmost cell
- [ ] All column `min-width` values are wide enough to show the full header label
- [ ] All sortable columns use `sortable="custom"` with hover-only sort arrows
- [ ] `el-table` has `:border="true"` and columns have `resizable`
- [ ] All cell text is `white-space: nowrap` with `text-overflow: ellipsis`
- [ ] Long cell content shows full text in a dark tooltip on hover
- [ ] All toolbar icon buttons have `el-tooltip` with `effect="dark"`
- [ ] Table body cells have `user-select: text` — cell content is copyable

### 5.3 Navigation Tabs (Sub-header)

The second bar below the navbar contains:
- **Breadcrumb** showing current path (left side)
- **Tab links** for sub-views (e.g., General | Attributes | Panels…)
- **Action buttons** (right side)

Active tab style: `color: var(--tda-color-primary)` with bottom underline.
Inactive tab: `color: var(--el-text-color-regular)`.
Separator character: `|` between tabs.

### 5.4 Left Sidebar Tree

```scss
width: 279px;
background: #fff;
border-right: 1px solid #e3e4e6;
padding: 10px;

// Tree nodes
--el-tree-node-content-height: 30px;

// Node icons: 18×18px, margin-right: 8px
// Dropdown icons: 14×14px
```

### 5.5 Forms

```scss
// Grid layout for form fields
.tda-form-wrapper {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  column-gap: 20px;
  max-width: 800px;
}

// Form items
.el-form-item--default {
  margin-bottom: 14px;
}

// Labels
.el-form-item__label {
  color: var(--el-text-color-primary); // #303133
}

// Required indicator: asterisk AFTER label text (not before)
.el-form-item.is-required .el-form-item__label::after {
  content: '*';
  color: var(--el-color-danger);
  margin-left: 4px;
}
```

#### Default Values for Dropdowns and Numeric Inputs

Every dropdown (select) and numeric input **must have a sensible default value** pre-selected or pre-filled. Users should never see a completely blank select or a zero-filled number field that has no meaning.

Rules:
- **Select dropdowns**: always pre-select the most common or safest option. If no default is appropriate, show a disabled placeholder option (`Please select`) and mark the field as required so the user knows they must choose.
- **Numeric inputs** (`el-input-number`): always set a `:default-value` or initial `v-model` value. Never leave it blank or `undefined`. Use `0` only if zero is a valid meaningful value; otherwise default to the minimum valid value.
- **Date/time pickers**: default to the current date/time unless there is a specific reason not to.
- **Filters and search dropdowns** in table toolbars: always default to "All" so the table starts fully unfiltered.

```vue
<!-- Good: select with default -->
<el-select v-model="form.category" placeholder="Select a category">
  <!-- pre-populated v-model = 'default-value' on component mount -->
</el-select>

<!-- Good: numeric with sensible default -->
<el-input-number v-model="form.count" :min="1" :default-value="1" />

<!-- Good: filter toolbar always defaults to "All" -->
<el-select v-model="filter.category" :default-first-option="true">
  <el-option label="All" value="" />
  ...
</el-select>

<!-- Bad: no default, field starts empty -->
<el-input-number v-model="form.count" />
```

#### Input Placeholder Text

**Every input field must have a placeholder** that describes what to enter. The placeholder disappears automatically as soon as the user starts typing (this is the native browser/Element Plus default behavior — do not override it).

Rules:
- Placeholder text is written in sentence case, concise, and descriptive: e.g., `Enter template name`, `Select a category`, `Search by name`.
- Placeholder color is `--el-text-color-placeholder` (`#a8abb2`) — never use a darker color that could be mistaken for real content.
- **Never** use the field label text as the placeholder verbatim — the placeholder should give an example or instruction, not repeat the label.
- For select dropdowns, the placeholder is `Please select` or a more specific prompt.
- For search inputs, the placeholder describes what is being searched: `Search elements...`.

```vue
<!-- Good -->
<el-input placeholder="Enter a unique template name" v-model="form.name" />
<el-input placeholder="Search by name or category..." v-model="search" />
<el-select placeholder="Select base template">

<!-- Bad — too vague, or repeats the label -->
<el-input placeholder="Name" v-model="form.name" />
<el-input placeholder="" v-model="form.name" />
```

```scss
// Placeholder color — do not override darker
.el-input__inner::placeholder,
.el-textarea__inner::placeholder {
  color: var(--el-text-color-placeholder); // #a8abb2
}
```

### 5.6 Select Dropdowns

```scss
// Base select
.el-select { min-width: 192px; }

// Standard height
.tda-select .el-select__wrapper { height: 36px; }

// Select with labeled prefix (e.g., "Categories | All")
.tda-select-with-inner-label {
  .el-select__wrapper {
    height: 36px;
    padding: 0 12px 0 1px;
    background-color: #f2f3f5;
  }
  .label-prefix {
    padding: 3px 12px;
    color: var(--el-text-color-regular);
    background: #e8efff;
    border-top-left-radius: 4px;
    border-bottom-left-radius: 4px;
  }
}
```

### 5.7 Dialogs — `.tda-dialog`

All popups, dialogs, and drawers must maintain **consistent, generous spacing** between the dialog edge and all internal content. Never let text, labels, or inputs touch or crowd the dialog border.

**Spacing rules for popups:**

| Area | Spacing |
|------|---------|
| Dialog outer padding (all sides) | 24px top/bottom, 16px left/right (`.tda-dialog`) |
| Between dialog edge and first label/input | Minimum 16px |
| Between header title and first content item | 10px (padding-bottom on header) |
| Between last content item and footer | 24px (padding-top on footer) |
| Between footer edge and buttons | Buttons are centered; 20px margin each side |
| Between form sections inside a dialog | 24px (follow inter-group spacing rule) |
| Between form items inside a section | 14px (`el-form-item--default margin-bottom`) |

```scss
.el-dialog {
  border: 1px solid var(--el-color-primary); // #2651f0
  border-radius: 10px;
}

.tda-dialog {
  padding: 24px 16px;  // consistent outer padding — never reduce below 16px

  .el-dialog__header {
    padding-bottom: 10px;  // breathing room below title
  }

  .el-dialog__header.show-close {
    padding-right: 0 !important;
  }

  .el-dialog__body {
    flex-direction: column;
    // body content naturally inherits the 16px side padding from .tda-dialog
  }

  // Footer: buttons centered
  .el-dialog__footer,
  .tda-dialog__footer {
    display: flex;
    align-items: center;
    justify-content: center;
    padding-top: 24px;  // clear separation from body content

    .el-button {
      width: 100px;
      margin: 0 20px;  // equal spacing between buttons
    }
  }
}
```

**Confirm / Message Box edge spacing:**

```scss
.el-message-box {
  min-width: 600px;
  border: 1px solid var(--tda-color-border-lighter);
  border-radius: 10px;

  .el-message-box__content {
    padding: 24px 10px 0;  // 24px top, minimum 10px sides
    font-size: 18px;
    text-align: center;
  }

  .el-message-box__btns {
    display: flex;
    flex-direction: row-reverse;
    justify-content: center;
    margin: 20px 0;  // 20px clear above and below button row

    .el-button { width: 100px; margin: 0 20px; }
  }
}
```

**Popup checklist:**
- [ ] All sides have at least 16px between edge and content
- [ ] Header, body, and footer each have distinct spacing that separates them visually
- [ ] Form sections inside a dialog are separated by 24px (not the same 14px as form items)
- [ ] No text, icon, or input sits flush against the dialog border

### 5.8 Confirm Message Box

```scss
.el-message-box {
  min-width: 600px;
  border: 1px solid var(--tda-color-border-lighter); // primary blue
  border-radius: 10px;

  .el-message-box__content {
    padding: 24px 10px 0;
    font-size: 18px;
    text-align: center;
  }

  .el-message-box__btns {
    display: flex;
    flex-direction: row-reverse;
    justify-content: center;
    margin: 20px 0;

    .el-button { width: 100px; margin: 0 20px; }
  }
}
```

### 5.9 Tooltips & Popovers

```scss
// Dark (primary-colored) tooltip
.el-popper.is-dark {
  color: #fff;
  background: var(--el-color-primary);
  border-color: var(--el-color-primary);
}

// All popovers: rounded, padded
.el-popper {
  padding: 0 12px;
  border-radius: 16px;
  max-width: 400px;
  line-height: 1.5;
  word-break: break-word;
}
```

### 5.10 Collapse Sections

```scss
.el-collapse-item__header {
  height: 46px;
  font-size: 14px;
  // Arrow icon placed BEFORE text
  .el-collapse-item__arrow { order: -1; margin-right: 5px; }
}
.el-collapse-item__content {
  padding-bottom: 15px;
  margin-left: 16px;
}
```

### 5.11 Pagination

```scss
// Always use small style with page-size selector
// .el-pagination--small .pg-bottom
.el-pagination__editor.el-input { width: 30px; }
.el-pagination__sizes .el-select { min-width: 80px; }
```

### 5.12 Panel Cards (Visualization)

```scss
background: var(--tda-panel-back-color); // #f8fafb
border: 1px solid var(--tda-panel-border-color); // #dbdee2
border-radius: 8px;
```

Card titles are shown below the visualization, left-aligned, in regular 14px body text.
Thumb-up/thumb-down rating icons appear below each card.

---

## 6. Dark Mode

The app fully supports dark mode via `html[data-theme='dark']`. Every color token has a dark variant defined in `variables.scss`.

**Rules:**
- Always use `var(--tda-color-*)` tokens — never hardcoded colors.
- Page background in dark: `#151518`
- Text in dark: `#ffffff`
- Primary accent in dark: `#e5eaf3`
- Backgrounds flip from white → near-black; borders become lighter grays.

---

## 7. Icons

### 7.1 Style Consistency

All icons across the entire app must share the **same visual style**. Mixing filled icons, outline icons, thick-stroke icons, and thin-stroke icons in the same interface creates visual noise and signals an unfinished product.

**The single approved icon style:**
- **Outline / line icons only** — no filled/solid variants except for active/selected state indicators
- **Consistent stroke width: 1.5px** — never mix hairline (1px) and thick (2px+) icons in the same context
- **Simple geometry** — minimal detail, no decorative elements, recognizable at 16px
- **No mixed sources** — use only Element Plus icons (`@element-plus/icons-vue`) or the project's own SVG set (`<svg-icon>`). Do not import icons from other libraries (FontAwesome, Material, Heroicons, etc.) unless the entire icon set is replaced.

```vue
<!-- Good: consistent Element Plus outline icons -->
<el-icon><Search /></el-icon>
<el-icon><Refresh /></el-icon>
<el-icon><Download /></el-icon>
<el-icon><Setting /></el-icon>

<!-- Bad: mixing SVG from external library with El Plus icons -->
<svg class="heroicon">...</svg>
<el-icon><Setting /></el-icon>
```

### 7.2 Sizes

| Context | Size | How set |
|---------|------|---------|
| Toolbar icon buttons (`.tda-icon-btn`) | 16px | `font-size: 16px` |
| Circle hover buttons (`.circle-hover`) | 18px | `font-size: 18px` / SVG 18×18 |
| Sidebar tree node icons | 18×18px | `width/height: 18px` |
| Sidebar tree expand/collapse arrows | 14×14px | `width/height: 14px` |
| Inline text icons (next to labels) | 14px | Match surrounding text size |
| Empty state illustrations | 64–96px | Scaled SVG |

### 7.3 Color

- Icons inherit the **parent element's `color`** by default — do not hardcode icon colors.
- Active / selected icons use `var(--tda-color-primary)`.
- Disabled icons use `var(--el-disabled-text-color)` (`#a8abb2`).
- Destructive action icons (delete, remove) use `var(--tda-color-danger)` (`#f56c6c`).
- Neutral / secondary icons use `var(--tda-color-info)` (`#909399`).

### 7.4 Stroke Width Rule

When using custom SVG icons, set `stroke-width` explicitly to `1.5` and `fill="none"`:

```svg
<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"
     stroke-linecap="round" stroke-linejoin="round">
  ...
</svg>
```

If an icon from the approved set visually appears heavier or lighter than its neighbors, it must be replaced, not used as-is.

---

## 8. Borders & Radius Summary

| Context | Radius |
|---------|--------|
| Buttons (default) | 4 px |
| Dialogs / Message boxes | 10 px |
| Popovers | 16 px |
| Rounded pills (`.tda-btn-radius`) | 20 px |
| Circular hover buttons | 50% |
| Panel cards | 5–8 px |
| Area borders (`.area-border`) | 4 px |

---

## 9. Shadows

```scss
// Heavy card shadow
--el-box-shadow-dark:
  0px 16px 48px 16px rgba(0,0,0,.08),
  0px 12px 32px rgba(0,0,0,.12),
  0px 8px 16px -8px rgba(0,0,0,.16);
```

---

## 10. Utility Classes

```scss
.flex-center   { display: flex; align-items: center; justify-content: center; }
.flex-start    { display: flex; align-items: center; justify-content: flex-start; }
.flex-between  { display: flex; align-items: center; justify-content: space-between; }
.flex-1        { flex: 1; }
.overflow-hidden { overflow: hidden; }

.mb-base       { margin-bottom: $layout-space; }
.mr-base       { margin-right: $layout-space; }
.page-wrapper  { padding: 20px; }
.sticky-bottom { position: sticky; bottom: 0; z-index: 10; background: var(--tda-color-background); }

// UnoCSS utilities (via uno.config)
// py-9px, px-*, gap-*, w-*, h-*, text-*, font-*
```

---

## 11. Detail View Pattern

Two-column key/value layout for entity detail pages:

```scss
.td-detail-item {
  display: flex;
  align-items: center;
  padding: 5px 0;
  margin-right: 20px;
  line-height: 20px;

  &__label {
    flex-shrink: 0;
    padding-right: 6px;
    font-size: 14px;
    color: var(--tda-color-text); // secondary gray
  }
  &__value {
    flex: 1;
    padding-left: 4px;
    font-size: 14px;
  }
}
```

Fields in view mode use `.tda-form-view`:
- Label: `--el-text-color-secondary` color
- Value: `--el-text-color-regular` color, `word-break: break-all`

---

## 12. Links & Navigation

```scss
a { color: var(--tda-color-primary); }
.el-link.el-link--primary { font-weight: unset; } // no bold on links
```

Menu/sidebar active item color: `--el-menu-active-color: #2651f0`.

---

## 13. Status / Severity Indicators

Use Element Plus semantic colors for severity tags:

| Severity | Color token | Value |
|----------|-------------|-------|
| Success / Normal | `--tda-color-success` | `#49ae18` |
| Warning | `--tda-color-warning` | `#f6cb6a` |
| Danger / Critical | `--tda-color-danger` | `#f56c6c` |
| Info | `--tda-color-info` | `#909399` |

---

## 14. Text Formatting Rules

These rules apply to all text displayed in the UI: descriptions, tooltips, labels, AI-generated content, documentation panels, and any multi-line text area.

### 14.1 No Leading Double Spaces

A paragraph or text block must **never begin with two or more space characters**. This is a common artifact of copy-pasting from code, documents, or AI-generated output. It creates invisible indentation that looks broken in HTML rendering (extra whitespace collapses to one space, or is visible as a gap in `pre`/`white-space: pre-wrap` contexts).

```
// Bad — starts with double space
"  This is the description of the element template."

// Good
"This is the description of the element template."
```

When rendering user-supplied text, always trim leading whitespace before display:

```js
// In computed / formatter
const formatted = text.replace(/^\s+/, '')
```

### 14.2 No Widows on the Last Line

The **last line of any paragraph must not contain a single word, punctuation mark, or symbol alone**. A lone word dangling on its own line (called a "widow") looks unfinished and wastes whitespace.

This applies to:
- Description fields in detail views
- Tooltip content
- AI-generated text blocks
- Any `<p>`, `<div>`, or `<span>` containing multi-sentence text

**Prevention strategy:**
- When displaying static copy (labels, empty-state messages, section descriptions), review the line break at all common viewport widths (1280px, 1440px, 1920px) and reword to avoid the widow.
- For dynamic content, use a CSS non-breaking space trick between the last two words, or use a `text-wrap: balance` / `text-wrap: pretty` rule on paragraph containers:

```scss
// Modern CSS widow prevention — supported in Chrome 114+
.prose-text,
.tda-description,
.el-tooltip__content {
  text-wrap: pretty; // avoids widows automatically
}

// Fallback for older browsers: balance short blocks
.tda-empty-state__message {
  text-wrap: balance;
}
```

### 14.3 Session Persistence — Restore Last Page on Return

When a user logs out and logs back in, or closes a browser tab and reopens the app, the app must **restore them to the exact page they were last on**, not drop them on the home/default page.

**Implementation requirements:**
- Save the current full route path (including query params) to `localStorage` on every route change.
- On app startup (before redirecting to a default route), check `localStorage` for a saved route.
- If found and the user is authenticated, navigate to that saved route.
- If the saved route no longer exists or returns a 404/403, fall back to the default home page.
- On explicit logout, clear the saved route from `localStorage`.

```js
// router/index.ts — save route on every navigation
router.afterEach((to) => {
  if (to.name !== 'login') {
    localStorage.setItem('tda:lastRoute', to.fullPath)
  }
})

// main.ts / App.vue — restore on mount after auth check
const lastRoute = localStorage.getItem('tda:lastRoute')
if (isAuthenticated && lastRoute && lastRoute !== router.currentRoute.value.fullPath) {
  router.replace(lastRoute)
}

// auth logout action — clear saved route
localStorage.removeItem('tda:lastRoute')
```

---

## 15. Image Rules

### 15.1 Spacing Around Images

Images must never have text or other UI elements crowding them. All images require sufficient breathing room.

| Image context | Minimum margin |
|---------------|---------------|
| Inline image within text content | 12px all sides |
| Section illustration / empty-state image | 24px top and bottom, 16px sides |
| Panel chart / visualization | 8px internal padding within its card |
| Avatar / user thumbnail | 8px from adjacent text |
| Logo | 16px from surrounding elements |

```scss
// General rule for content images
.tda-content-image {
  display: block;
  margin: 24px auto;      // vertical breathing room
  padding: 0;
  max-width: 100%;
}

// Image adjacent to text
.tda-inline-image {
  float: left;            // or right
  margin: 0 16px 12px 0; // right and bottom clearance
}

// Never let text touch an image
img + p,
p + img {
  margin-top: 12px;
}
```

### 15.2 Image Color Harmony

Images must not create visual conflict with the page background or with each other. High-contrast or clashing images break the calm, professional feel of the app.

**Rules:**
- **Avoid pure white or pure black image backgrounds** when the image sits on a white card — the edge becomes invisible or jarring. Add a 1px border (`--tda-color-border`) or subtle shadow to separate it from the card background.
- **Panel chart colors** (line, bar, gauge) are drawn from a consistent palette that works in both light and dark mode — do not introduce arbitrary colors in new chart types.
- **Illustration / empty-state images** must use the app's primary palette (blues, grays) and have transparent or matching backgrounds — no isolated images with mismatched background colors.
- **Do not place a brightly saturated image next to a muted one** in the same view — either use consistently styled assets or separate them with clear spatial distance.
- **Icons and images within the same context** (e.g., all sidebar icons, all empty-state illustrations) must share a consistent visual weight and color saturation level.

```scss
// Image on white card — add subtle separation
.tda-card img {
  border: 1px solid var(--tda-color-border);
  border-radius: 4px;
}

// Avoid harsh white-on-white disappearing edge
.tda-panel-preview img {
  background: var(--tda-panel-back-color); // #f8fafb tinted bg
  padding: 4px;
  border-radius: 4px;
}
```

---

## 16. Writing New Vue Components

1. **Use `var(--tda-*)` and `var(--el-*)` tokens** throughout — avoid hardcoded colors.
2. **Use `$layout-space` / `$layout-space-l-r`** for horizontal gutters — not fixed px.
3. **Table headers must have `font-weight: normal`** (Element Plus default is bold; override it).
4. **Required asterisks go after the label** — use `::after` not `::before`.
5. **Dialog footers center their buttons** at 100px wide with 20px margins.
6. **Toolbar action buttons use `.tda-icon-btn`** class for consistent 36×36 sizing.
7. **New pages wrap content in a white card** on the `#f2f3f3` content area.
8. **Always add dark-mode support** by using tokens — no hardcoded light colors.
9. **Forms use `.tda-form-wrapper`** grid for responsive 2-column layouts.
10. **Pagination always uses `el-pagination` with `small` size** + go-to field.
11. **All form fields and inputs are left-aligned.** Toolbar filters left, action buttons right (`margin-left: auto`). Never center-align inputs.
12. **Inter-group spacing is at least 2× intra-group spacing.** Form sections are separated by 24–28px; items within a section by 14px. Users must be able to visually perceive the grouping from spacing alone.
13. **Every input field must have a placeholder.** Placeholder text is instructive (not a label copy), written in sentence case, shown in `--el-text-color-placeholder` (`#a8abb2`), and disappears automatically on input.
14. **Dialogs have a minimum 16px edge-to-content gap on all sides.** Header, body, and footer are visually separated. No text or input touches the dialog border.
15. **Use only one icon style throughout: outline icons, stroke-width 1.5px.** Never import icons from a different library than the rest of the app. All SVG icons use `fill="none"` and `stroke="currentColor"` with `stroke-width="1.5"`.
16. **Save current route to `localStorage` on every navigation; restore it on login.** On logout, clear the saved route.
17. **Table body cells must have `user-select: text`.** Never suppress text selection in table cells — users must be able to copy any value.
18. **Every dropdown and numeric input must have a default value.** Filter dropdowns default to "All"; numeric inputs default to the minimum valid value; never leave a select blank.
19. **Paragraph text must not start with two or more spaces.** Always trim leading whitespace from user-supplied text before rendering.
20. **The last line of any paragraph must not be a single word or punctuation alone.** Apply `text-wrap: pretty` to all prose/description containers.
21. **Images require minimum 12px margin from surrounding text, 24px from section edges.** Never place text flush against an image.
22. **Images must harmonize with the page background.** Use a 1px `--tda-color-border` border or light card bg (`--tda-panel-back-color`) to separate images from white card backgrounds. Do not place high-saturation images next to muted ones in the same view.
