---
name: tdengine-ui
description: TDengine IDMP design system guide. Apply when writing any new Vue component, page, or feature for the TDengine IDMP frontend (src/ under TDasset/frontend). Enforces colors, typography, layout, and component patterns so all new UI is visually consistent with the existing app.
user-invocable: false
---

# TDengine IDMP — UI Design System

You are working on the **TDengine Industrial Data Management Platform** frontend.
Tech stack: **Vue 3 + Element Plus + UnoCSS + SCSS + IBM Plex Sans**.
Full reference: [DESIGN_GUIDE.md](../../frontend/DESIGN_GUIDE.md)

---

## Critical Rules (apply every time)

1. **Colors — always use CSS variables, never hardcode hex:**
   - Primary blue: `var(--tda-color-primary)` (#2651f0)
   - Page bg (gray area): `var(--tda-color-background-light-dark)` (#f2f3f3)
   - White surfaces: `var(--tda-color-background)` (#fff)
   - Borders: `var(--tda-color-border)` (#e3e4e6)
   - Body text: `var(--tda-color-text)` / `var(--el-text-color-regular)`
   - Table row text: `rgb(77, 105, 146)` — via `--el-table-text-color`
   - Success/Danger/Warning/Info: `var(--tda-color-success/danger/warning/info)`

2. **Typography:**
   - Font: `'IBM Plex Sans', sans-serif`
   - Default body: 14 px / weight 400
   - Buttons: weight 500
   - Do NOT use weight 700 except pagination active numbers
   - Scale: 12 / 14 / 16 / 18 / 20 px only

3. **Layout structure for a new page:**
   ```
   Content area bg: #f2f3f3, padding ~10px 20px
   └── White card: bg #fff, border 1px #dbdee2, border-radius 8px, padding 16px 20px
       ├── Sub-toolbar bar (38px, white, border-bottom #dcdfe6, padding 9px 0 9px 14px)
       │   ├── Left: breadcrumb + tab links
       │   └── Right: .tda-icon-btn action buttons
       └── Main content
   ```

4. **Buttons:**
   - Toolbar icon buttons: `.el-button.tda-icon-btn` → 36×36px, white bg, border #dcdfe6, radius 4px, icon 16px, color #343537
   - Inline icon-only: `.circle-hover` → 32×32px, transparent, hover gets primary bg at 10% opacity
   - Form/dialog confirm buttons: width 100px, margin 0 20px, centered in footer
   - Rounded pill variant: add `.tda-btn-radius` for border-radius 20px

5. **Tables (all rules are mandatory):**

   **Visual styles:**
   - Header: bg `#e8efff`, text `#343537`, height 40px, `font-weight: normal` (never bold)
   - Rows: text `rgb(77,105,146)`, height 42px, white bg, `cursor: pointer`
   - Row hover: bg `var(--tda-color-background-light-dark-2)` (#ecf2fe)
   - Link/clickable cells only: `color: var(--tda-color-primary)` (#2651f0)
   - Plain data cells: `color: var(--el-text-color-regular)` (#343537) — NOT blue

   **Toolbar button order (left → right):**
   ```
   [filter dropdowns]  [+Add]  [↑Import]  [↓Export CSV]  [🔍Search]  [⊞View]  [↻Refresh]  [⚙Columns]
   ```
   - `+` (Add) is always the **leftmost** icon button, if creation is supported
   - `↓` Export/Download CSV is **always present** on every **list/table** view. **Exception: panel/card views** (when the current view mode is the card layout) do **not** require the download CSV button.
   - `↻` Refresh is **always present**
   - `⚙` Column config is **always the rightmost** icon — no exceptions
   - Every icon button: `.tda-icon-btn` (36×36px), wrapped in `el-tooltip effect="dark"`
   - **Icon spacing must be uniform:** use `display: flex; gap: $layout-space` on the icon button container — never set `margin-left` on individual buttons, which creates uneven gaps
   - **"Back" icon tooltip must be exactly `"Back to the List"`** — never `"back"`, `"Back"`, `"Go back"`, or any other wording

   **Row three-dot menu:**
   - Every row has a `⋮` (MoreFilled) `.circle-hover` button as the **rightmost cell** (48px fixed column, no header label)
   - Always visible (not just on hover)
   - Opens `el-dropdown` menu on click: Edit, then other actions, Delete last in `--tda-color-danger`

   **Column widths:**
   - Use `min-width` (not `width`) on all data columns
   - `min-width` must be wide enough to show the full header label without truncation
   - Fixed `width` only for: checkbox column, status icon columns, `⋮` column (48px)

   **Sorting:**
   - All sortable columns use `sortable="custom"` (server-side)
   - Sort arrows (↑↓) are hidden by default, shown only on header cell hover
   - Active sort column keeps arrows always visible

   **Resizing:**
   - `el-table` must have `:border="true"`
   - All data columns must have `resizable` attribute
   - `min-width` is still enforced as the lower limit

   **Cell content — no wrapping, truncate with tooltip:**
   - All cells: `white-space: nowrap; overflow: hidden; text-overflow: ellipsis`
   - Long content: wrap cell in `el-tooltip` with `effect="dark"` showing full text on hover
   - No cell content ever wraps to a second line
   - `.el-table__body .cell { user-select: text }` — cell text must be selectable and copyable

6. **Dialogs:**
   ```scss
   .el-dialog { border: 1px solid var(--el-color-primary); border-radius: 10px; }
   .tda-dialog { padding: 24px 16px; }
   // Footer buttons centered, 100px wide, margin 0 20px, padding-top 24px
   ```

7. **Forms:**
   - Grid: `.tda-form-wrapper` → `repeat(auto-fit, minmax(300px, 1fr))`, max-width 800px, column-gap 20px
   - Item margin-bottom: 14px
   - Required `*` goes **after** label text (via `::after`, NOT `::before`)
   - View-only mode: label uses `--el-text-color-secondary`, value uses `--el-text-color-regular`

8. **Selects:**
   - Minimum width: 192px
   - Standard: `.tda-select` → height 36px
   - With label prefix: `.tda-select-with-inner-label` (prefix chip bg `#e8efff`, wrapper bg `#f2f3f5`)

9. **Dark mode — mandatory:**
   - Every color MUST use a `--tda-*` or `--el-*` variable so dark mode works automatically
   - Dark bg: `#151518` | dark text: `#fff` | dark primary: `#e5eaf3`
   - Never write `color: #000` or `background: #fff` directly in component styles

10. **Sidebar / left panel:**
    - Width: 279px, white bg, right border 1px #e3e4e6, padding 10px
    - Tree node height: 30px
    - Node icons: 18×18px, margin-right 8px

11. **Spacing tokens:**
    ```scss
    $layout-space: calc(12 * 100vw / 1920);       // ~12px at 1920px
    $layout-space-l-r: calc(24 * 100vw / 1920);   // ~24px at 1920px
    $content-space: 10px;
    ```
    Use `$layout-space` as the `gap` value on the toolbar icon button flex container — not fixed px, not per-button `margin-left`.

12. **Pagination:** always use `el-pagination` with `size="small"` + show-total + go-to field.

13. **Tooltips:** use `el-tooltip` with `effect="dark"` → renders as primary-color background tooltip.

14. **Status tags / severity:** use Element Plus tag semantic types: `success`, `warning`, `danger`, `info`.

15. **Alignment:**
    - All form fields, inputs, and labels: **left-aligned**
    - Table data cells: left-aligned; numeric/count columns: right-aligned
    - Toolbar: filters/dropdowns on the left, action icon buttons on the right (`margin-left: auto`)
    - Dialog content: left-aligned; dialog footer buttons: centered
    - Never center-align inputs or labels in a form

16. **Spacing hierarchy — groups must be visually distinct:**
    - Items **within** a form section: `margin-bottom: 14px` (intra-group)
    - **Between** form sections / panels: `margin-top: 24–28px` (inter-group, always ≥ 2× intra)
    - Between page-level cards: 20px+
    - Rule: if two blocks have the same gap around them, they look related — widen the gap to separate groups

17. **Every input must have a placeholder:**
    - Text is instructive, sentence case: `Enter template name`, `Search by name...`
    - Never repeat the label verbatim as placeholder
    - Color: `var(--el-text-color-placeholder)` (#a8abb2) — never darker
    - Placeholder disappears on input (native behavior — do not override)

18. **Popup / dialog edge spacing:**
    - Minimum 16px between dialog edge and any text, label, or input on all sides
    - `.tda-dialog` padding: `24px 16px`
    - Header → body gap: 10px; body → footer gap: 24px
    - Form sections inside dialogs separated by 24px (not 14px)
    - No element ever touches or crowds the dialog border

19. **Icons — one consistent style only:**
    - Outline icons only, stroke-width 1.5px, `fill="none"`, `stroke="currentColor"`
    - Source: Element Plus icons or project SVG set only — never mix libraries
    - Custom SVGs must declare `stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"`
    - If an icon looks visually heavier/lighter than its neighbors, replace it

20. **Session persistence — restore last page on login:**
    - Save `router.currentRoute.fullPath` to `localStorage` on every `router.afterEach` (skip login route)
    - On app mount after auth check, read `tda:lastRoute` from `localStorage` and navigate there
    - On logout, call `localStorage.removeItem('tda:lastRoute')`

21. **Table cells must be copyable:**
    - `.el-table__body .cell { user-select: text; }` — never suppress selection in table body
    - Do not use `pointer-events: none` on cell text spans

22. **Every dropdown and numeric input must have a default value:**
    - Selects: pre-populate `v-model` with the most common value, or "All" for filters
    - `el-input-number`: always set `:default-value` or initial `v-model` — never leave blank
    - Never show an empty unselected dropdown to the user on first load

23. **Text formatting — no leading double spaces:**
    - Trim leading whitespace from all user-supplied text before rendering: `text.replace(/^\s+/, '')`
    - Never render raw text that starts with `"  "` (two spaces)

24. **Text formatting — no widow on last line:**
    - Apply `text-wrap: pretty` to all `.tda-description`, `.prose-text`, tooltip content containers
    - For static copy, review at 1280/1440/1920px widths and reword to avoid a lone word on the last line

25. **Image spacing — minimum clearance:**
    - Inline images (next to text): `margin: 0 16px 12px 0` minimum
    - Section/empty-state illustrations: `margin: 24px auto`
    - Never let text sit flush against an image edge

26. **Image color harmony:**
    - Images on white cards: add `border: 1px solid var(--tda-color-border)` or use `--tda-panel-back-color` as image bg
    - Do not place high-saturation images next to muted ones in the same view
    - Empty-state illustrations must use the app's blue/gray palette with transparent or matching backgrounds

---

## Component Checklist for New Pages

Before finishing any new page/feature, verify:

**General:**
- [ ] All colors use `--tda-*` / `--el-*` CSS variables
- [ ] Page renders correctly in dark mode (`html[data-theme='dark']`)
- [ ] White card wrapper on gray content area background (`#f2f3f3`)
- [ ] All inputs and labels are left-aligned; toolbar action buttons are right-aligned
- [ ] Inter-group spacing is ≥ 2× intra-group spacing (sections 24–28px apart, items 14px apart)
- [ ] Every input field has a descriptive placeholder in `--el-text-color-placeholder` color
- [ ] Every dropdown and numeric input has a default value pre-set
- [ ] All icons are outline style, stroke-width 1.5px, same source library throughout
- [ ] Route is saved to `localStorage` on navigation; restored on login; cleared on logout

**Text content (if page displays user-supplied or dynamic text):**
- [ ] Leading whitespace trimmed before rendering any user-supplied text
- [ ] `text-wrap: pretty` applied to all description / prose containers
- [ ] No paragraph begins with two or more space characters

**Images (if page contains images):**
- [ ] Inline images have minimum 12px margin from adjacent text
- [ ] Section illustrations have 24px vertical margin
- [ ] Images on white cards have `border: 1px solid var(--tda-color-border)` or tinted bg
- [ ] No high-saturation image placed next to a muted one in the same view

**Tables (if page contains a table):**
- [ ] Header bg `#e8efff`, `font-weight: normal`
- [ ] Row text `rgb(77,105,146)`, height 42px, `cursor: pointer`
- [ ] Only link cells are primary blue; plain data cells are `#343537`
- [ ] Rightmost toolbar button is `⚙` column config
- [ ] `↓` Export CSV button is present in toolbar **unless** this is a panel/card view
- [ ] `↻` Refresh button is present in toolbar
- [ ] `+` Add is leftmost icon button (if creation supported)
- [ ] Toolbar icon buttons use `display: flex; gap: $layout-space` — not per-button `margin-left`
- [ ] Any "Back" navigation icon tooltip is exactly `"Back to the List"`
- [ ] Every row has `⋮` three-dot button as rightmost cell (48px fixed column)
- [ ] `⋮` dropdown: Delete is last item, in `--tda-color-danger` color
- [ ] All data columns use `min-width` wide enough to show full header label
- [ ] Sortable columns use `sortable="custom"`, sort arrows show on hover only
- [ ] `el-table` has `:border="true"`, data columns have `resizable`
- [ ] All cells: `white-space: nowrap; text-overflow: ellipsis`
- [ ] Long cell content has `el-tooltip effect="dark"` showing full text on hover
- [ ] All toolbar icon buttons have `el-tooltip effect="dark"` with descriptive label

**Dialogs:**
- [ ] `border: 1px solid primary`, `border-radius: 10px`, `.tda-dialog` class
- [ ] Footer buttons centered, 100px wide, `margin: 0 20px`
- [ ] Minimum 16px between dialog edge and all content on every side
- [ ] Form sections inside dialog separated by 24px (not 14px)
- [ ] No text, label, or input touches the dialog border

**Forms:**
- [ ] Required `*` appears after label text (via `::after`, not `::before`)
- [ ] Uses `.tda-form-wrapper` grid
- [ ] Select inputs have `min-width: 192px`

**Pagination:**
- [ ] Uses `el-pagination` small size with go-to field
