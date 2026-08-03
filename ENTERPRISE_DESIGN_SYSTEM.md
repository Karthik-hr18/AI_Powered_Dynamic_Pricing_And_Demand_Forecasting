# Enterprise Design System v1 — Master Specification

This single master document contains the complete specification for **Enterprise Design System v1**, a high-performance, accessible, and scalable design language for modern enterprise applications, executive analytics dashboards, SaaS portals, and multi-tier management applications.

---

## Table of Contents
1. [Design Philosophy & System Architecture](#1-design-philosophy--system-architecture)
2. [Design Tokens Specification](#2-design-tokens-specification)
3. [UI Component Library](#3-ui-component-library)
4. [Universal Page Templates](#4-universal-page-templates)
5. [UX Guidelines & Behavioral Architecture](#5-ux-guidelines--behavioral-architecture)
6. [Adoption & Migration Guide](#6-adoption--migration-guide)

---

# 1. Design Philosophy & System Architecture

## 1.1 Executive Summary
Enterprise Design System v1 is engineered for complex data-dense web applications. It balances high-density information display with crisp visual hierarchy, ensuring low cognitive load during intensive workflows.

## 1.2 Core Visual Principles
- **Enterprise Precision**: Clean geometry, 4px-aligned baseline grids, predictable vertical rhythms, and deliberate whitespace hierarchy.
- **Selective Glassmorphism & Depth**: Subtle backdrop blurs (`backdrop-filter: blur(12px)`), translucent border overlays (`rgba(255, 255, 255, 0.12)`), and multi-layered elevation shadows to establish visual depth without compromising accessibility.
- **Theme-Adaptive High Contrast**: High-contrast typography hierarchy built on WCAG 2.1 AAA standards for text readability across both dark-mode hero stages and light-mode analytical workspaces.
- **Dynamic Interaction Feedback**: Subtle micro-animations, tactile button press-down scales (`transform: scale(0.98)`), smooth focus rings (`outline: 2px solid var(--accent)`), and state-driven color transitions (`200ms cubic-bezier(0.4, 0, 0.2, 1)`).

## 1.3 Fundamental System Rules
1. **Strict Generalization**: All components, layouts, and interaction patterns are domain-agnostic. Business logic is strictly decoupled from presentation layers.
2. **Predictable Layout Containment**: Interactive elements must never overflow container boundaries. All cards, tables, and modal dialogs enforce explicit container bounds (`box-sizing: border-box`, `overflow: hidden` or `overflow-x: auto`).
3. **Responsive Grid Integrity**: Layouts scale fluidly from mobile touch devices (`320px`) to ultra-wide enterprise monitors (`1920px+`). Mobile navigation features dedicated slide-over drawers with touch-friendly targets (minimum 44px height).
4. **Accessible Color Independence**: System status (Success, Warning, Danger, Info) is never communicated by color alone. Every badge, alert, and indicator pairs a distinct HSL color token with a semantic icon and text label.

---

# 2. Design Tokens Specification

## 2.1 Color System

### A. Surface & Neutral Palette
| Token Name | CSS Variable | Hex / RGBA Value | Purpose / Usage |
| :--- | :--- | :--- | :--- |
| **Canvas Background (Light)** | `--gray-bg` | `#F8FAFC` | Main application background for analytical & data views |
| **Surface Card (Light)** | `--gray-surface` | `#FFFFFF` | Primary surface for cards, table containers, forms |
| **Border Neutral** | `--gray-border` | `#E2E8F0` | Subtle borders separating cards, rows, and form fields |
| **Text Primary** | `--gray-text-primary` | `#0F172A` | High-contrast headings, main body text, and active labels |
| **Text Muted** | `--gray-text-muted` | `#64748B` | Secondary descriptions, timestamps, placeholders, metadata |
| **Canvas Background (Dark)** | `--dark-bg` | `#090D16` | Hero stage, landing headers, and dark modal canvases |
| **Surface Card (Dark Glass)**| `--dark-surface` | `rgba(15, 23, 42, 0.95)` | Translucent glass surface for dark mode containers |
| **Border Glass Translucent** | `--dark-border` | `rgba(99, 102, 241, 0.3)`| Accent-tinted glass border for dark containers |

### B. Accent & Status Color Tokens
| Status / Role | Token Name | Primary Color | Light Fill | Translucent Border |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Accent** | `--accent` | `#4F46E5` (Indigo-600) | `#EEF2FF` (Indigo-50) | `rgba(79, 70, 229, 0.25)` |
| **Accent Hover** | `--accent-hover` | `#4338CA` (Indigo-700) | `#E0E7FF` (Indigo-100)| `rgba(67, 56, 202, 0.4)` |
| **Success State** | `--success` | `#10B981` (Emerald-500)| `#F0FDF4` (Emerald-50)| `rgba(16, 185, 129, 0.25)` |
| **Warning State** | `--warning` | `#D97706` (Amber-600) | `#FFFBE6` (Amber-50) | `rgba(217, 119, 6, 0.25)` |
| **Danger / Error** | `--error` | `#EF4444` (Red-500) | `#FEF2F2` (Red-50) | `rgba(239, 68, 68, 0.25)` |
| **Info / Special** | `--info` | `#3B82F6` (Blue-500) | `#EFF6FF` (Blue-50) | `rgba(59, 130, 246, 0.25)` |
| **Purple Highlight**| `--purple` | `#7E22CE` (Purple-700) | `#FAF5FF` (Purple-50)| `rgba(126, 34, 206, 0.25)` |

## 2.2 Typography Scale
- **Primary Interface Font**: `'Inter', system-ui, -apple-system, BlinkMacSystemFont, sans-serif`
- **Monospace & Data Font**: `'JetBrains Mono', Consolas, monospace`

| Style Level | Font Size | Weight | Line Height | Letter Spacing | Target Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Display Title (H1)** | `36px` | `800` (ExtraBold) | `1.2` | `-0.025em` | Main page titles, hero headers |
| **Section Header (H2)**| `24px` | `700` (Bold) | `1.3` | `-0.015em` | Major section headers, card group titles |
| **Sub-Header (H3)** | `20px` | `700` (Bold) | `1.3` | `-0.010em` | Card titles, modal headers |
| **Card Title (H4)** | `17px` | `600` / `700` | `1.4` | `normal` | Sub-card headers, list headers |
| **Body Primary** | `15px` | `400` / `500` | `1.6` | `normal` | Default body text, form field text |
| **Body Compact** | `14px` | `400` / `500` | `1.5` | `normal` | Table rows, secondary body text |
| **Caption / Label** | `13px` | `600` | `1.4` | `0.01em` | Input labels, table headers, metadata |
| **Badge / Mini Tag** | `12px` | `700` | `1.2` | `0.05em` | Status badges, chip tags (uppercase) |

## 2.3 Spacing Scale (4px Base Grid)
```css
--space-1: 4px;    /* Micro gaps, inline badge padding */
--space-2: 8px;    /* Element gaps, label-to-input spacing */
--space-3: 12px;   /* Small padding, compact button padding */
--space-4: 16px;   /* Default input padding, table cell padding */
--space-5: 24px;   /* Card padding, grid gaps, section gaps */
--space-6: 32px;   /* Large container padding, section margins */
--space-7: 48px;   /* Hero section padding, modal padding */
--space-8: 64px;   /* Major page division padding */
```

### Layout Constraints
- **Max Application Container Width**: `1240px` (centered via `margin: 0 auto; padding: 0 24px;`)
- **Max Form Container Width**: `760px` (centered for multi-column inputs)
- **Compact Auth/Modal Width**: `440px` – `520px`

## 2.4 Border Radius Scale
```css
--radius-input: 6px;     /* Form inputs, select dropdowns, textareas */
--radius-default: 8px;   /* Secondary buttons, tooltips, action badges */
--radius-card: 16px;     /* Dashboard cards, table containers, dialogs */
--radius-modal: 20px;    /* Floating modals, slide-over drawer headers */
--radius-pill: 9999px;   /* Primary pill buttons, status badges, chips */
```

## 2.5 Elevation, Shadows & Glass Effects
- **Base Card Shadow**: `0 4px 20px rgba(0, 0, 0, 0.04)`
- **Hover Lift Shadow**: `0 12px 30px rgba(0, 0, 0, 0.08)`
- **Elevated Modal Shadow**: `0 20px 50px rgba(0, 0, 0, 0.15)`
- **Dark Stage Ambient Shadow**: `0 20px 50px rgba(0, 0, 0, 0.5)`
- **Accent Glow Shadow**: `0 4px 14px rgba(79, 70, 229, 0.25)`

## 2.6 Motion & Timing Scale
```css
--transition-speed-fast: 150ms;
--transition-speed-normal: 200ms;
--transition-speed-slow: 300ms;
--transition-timing: cubic-bezier(0.4, 0, 0.2, 1);
```

## 2.7 Responsive Breakpoints
| Breakpoint Name | Min Width | Target Devices | Primary Layout Shift |
| :--- | :--- | :--- | :--- |
| **Mobile (`xs`/`sm`)** | `< 640px` | Phones (portrait/landscape) | 1-Column grid, stacked buttons, full-width drawers |
| **Tablet (`md`)** | `640px – 991px` | Tablets & small laptops | 2-Column KPI grid, collapsible navigation |
| **Desktop (`lg`)** | `992px – 1239px`| Standard laptops & desktops | Full multi-column grid, persistent sidebar/header |
| **Wide Desktop (`xl`)**| `1240px+` | High-res enterprise displays | Centered 1240px max-width container with full gutters |

---

# 3. UI Component Library

## 3.1 Button Components

### A. Primary Action Button (`.btn-primary` / `.btn-primary-lg`)
- **Purpose**: Main call-to-action per section or view.
- **Visual Hierarchy**: High prominence, filled accent background (`#4F46E5`), white text (`#FFFFFF`), subtle drop shadow (`0 4px 14px rgba(79, 70, 229, 0.25)`).
- **Sizing & Spacing**:
  - Regular: `height: 40px`, `padding: 0 16px`, `fontSize: 14px`
  - Large (`-lg`): `height: 44px`, `padding: 0 24px`, `fontSize: 15px`
  - Border Radius: `--radius-pill` (`9999px`) or `--radius-default` (`8px`)
- **States**:
  - **Hover**: Background shifts to `#4338CA`, `transform: translateY(-1.5px) scale(1.01)`, shadow deepens (`0 6px 18px rgba(79, 70, 229, 0.4)`).
  - **Active / Press**: `transform: scale(0.98)`
  - **Focus**: `outline: 2px solid #4F46E5`, `outline-offset: 2px`
  - **Disabled**: `opacity: 0.5`, `cursor: not-allowed`, no hover transform
- **Accessibility**: Minimum 44px touch height on mobile; high contrast ratio (7.5:1).

### B. Secondary Button (`.btn-secondary` / `.btn-secondary-lg`)
- **Purpose**: Secondary or alternative actions (e.g., Cancel, Export, Filter).
- **Visual Hierarchy**: Medium prominence. Light mode: Surface `#FFFFFF`, border `1px solid #CBD5E1`, text `#0F172A`. Dark mode / Scrolled stage: Translucent `#F1F5F9` or `rgba(255, 255, 255, 0.12)` fill.
- **Hover**: Light mode fills with `#F8FAFC`, border `#94A3B8`.
- **Active / Disabled**: Matches Primary scale rules (`scale(0.98)`, disabled `opacity: 0.5`).

### C. Danger / Destructive Button (`.btn-danger`)
- **Purpose**: Destructive or irreversible actions (e.g., Delete, Revoke, Terminate).
- **Visual Hierarchy**: Red fill (`#EF4444`) or light red fill (`rgba(239, 68, 68, 0.15)`), red text (`#DC2626` / `#FCA5A5`), red border (`rgba(239, 68, 68, 0.3)`).

### D. Icon Button (`.btn-icon`)
- **Purpose**: Compact inline actions within tables, cards, or navigation headers.
- **Dimensions**: Square `36px × 36px` or `40px × 40px`, centered icon (`18px` – `20px`).

## 3.2 Form Control Components

### A. Text / Select / Textarea Input (`.form-input`)
- **Visual Spec**: `min-height: 44px`, `padding: 12px 16px`, `border: 1px solid #E2E8F0` (Dark glass: `1px solid rgba(99, 102, 241, 0.3)`), `background-color: #F8FAFC`, `border-radius: 6px`, `font-size: 15px`, `color: #0F172A`.
- **States**:
  - **Focus**: `border-color: #4F46E5`, `outline: none`, glow (`box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15)`).
  - **Error**: `border-color: #EF4444`, red validation helper text below.
  - **Disabled**: `background-color: #E2E8F0`, `color: #94A3B8`, `cursor: not-allowed`.

### B. Drag-and-Drop File Upload Card
- **Structure**: Dotted border container (`2px dashed #C7D2FE`), centered upload icon, primary callout text, format/size metadata text.
- **Interactive File State**: Displays selected file name, file size (`MB`), status indicator, and a red inline remove button (`<X /> Remove`).

## 3.3 Data Presentation & Card Components

### A. Executive KPI / Statistics Card
- **Structure**: Top row: Metric label (`fontSize: 13px`, `color: #64748B`) + Icon Container (`34px × 34px`, rounded 10px, themed background/color tint). Bottom row: Large bold metric value (`fontSize: 34px`, `fontWeight: 800`, `color: #0F172A`).
- **Container**: White surface (`#FFFFFF`), `18px` border radius, `1px solid #E2E8F0`, `box-shadow: 0 4px 20px rgba(0,0,0,0.04)`.
- **Hover Micro-Interaction**: `transform: translateY(-2px) scale(1.01)`, shadow deepens (`0 12px 30px rgba(0, 0, 0, 0.08)`).

### B. Status & Pipeline Badges (`.badge`)
- **Structure**: Inline pill (`padding: 4px 12px`, `borderRadius: 9999px`, `fontSize: 12px`, `fontWeight: 700`, uppercase, `letter-spacing: 0.04em`).
- **Color Matrix**:
  - **Applied / Initial**: Blue fill (`#EFF6FF`), border (`#93C5FD`), text (`#1D4ED8`)
  - **Active / Review**: Amber fill (`#FFFBE6`), border (`#FDBA74`), text (`#C2410C`)
  - **In Progress / Phase 2**: Purple fill (`#FAF5FF`), border (`#D8B4FE`), text (`#7E22CE`)
  - **Completed / Approved**: Green fill (`#F0FDF4`), border (`#86EFAC`), text (`#15803D`)
  - **Rejected / Terminated**: Red fill (`#FEF2F2`), border (`#FCA5A5`), text (`#B91C1C`)

## 3.4 Table & Data Grid Components
- **Container**: Elevated white card (`#FFFFFF`), `20px` radius, overflow hidden, subtle border (`#E2E8F0`).
- **Sticky Header**: `background-color: #F8FAFC`, `border-bottom: 1px solid #E2E8F0`, text `fontSize: 12px`, `fontWeight: 700`, `color: #475569`, uppercase, `sticky top: 0`.
- **Rows**: `border-bottom: 1px solid #F1F5F9`, `padding: 18px 20px`, smooth hover highlight (`background-color: #F8FAFC`).
- **Action Buttons**: Inline text buttons with background pill badge (`#EEF2FF` bg, `#4F46E5` text, hover `#E0E7FF`).

## 3.5 Overlay, Modal & Slide-Over Drawer Components

### A. Modal Dialog (`.modal-backdrop` & `.modal-container`)
- **Backdrop**: Fixed full-screen overlay (`rgba(9, 13, 22, 0.8)`, `backdrop-filter: blur(10px)`), `z-index: 99999`.
- **Container**: Centered dialog (`max-width: 520px` – `760px`), white/dark surface, `20px` radius, `padding: 32px`, elevation shadow (`0 20px 50px rgba(0,0,0,0.4)`).
- **Header**: Icon badge + Title + Description + Absolute top-right close icon (`<X />`).
- **Footer**: Action button row aligned to the right (Secondary + Primary).

### B. Slide-Over Detail Drawer (`.slide-drawer`)
- **Drawer**: Fixed right-aligned container (`width: 380px` – `520px`, `max-width: 85vw`, `height: 100vh`), `background: #0F172A` or `#FFFFFF`, `z-index: 100000`.
- **Animation**: Entrance via `transform: translateX(100%)` to `translateX(0)` (250ms cubic-bezier).

## 3.6 Feedback & State Indicator Components
- **Skeleton Loader**: Animated placeholder blocks mimicking table rows/cards. Keyframes `skeletonPulse` alternating opacity `0.4` to `0.9` over `1.5s`.
- **Empty State**: Centered layout (`padding: 60px 24px`, `max-width: 520px`), themed icon badge (`56px × 56px`), bold header (`20px`), descriptive text (`14px`), and primary CTA button.

---

# 4. Universal Page Templates

## 4.1 Executive Analytics & Dashboard Template
- **Layout Grid**: Max width `1240px`, centered, `padding: 40px 24px 80px`.
- **Responsive Behavior**: Desktop: 4 KPI metric cards in a single row; Tablet: 2 × 2 grid; Mobile: Single column stacked KPI cards.

## 4.2 Standard Data Table & Filter Management Template
- **Header Bar**: Title, global search input (`width: 320px`), filter dropdown trigger buttons, and primary action button (e.g., "+ Create Record").
- **Table Specs**: Card container with `border-radius: 20px`, `background: #FFFFFF`, `box-shadow: 0 4px 20px rgba(0,0,0,0.05)`. Sticky header (`#F8FAFC`).
- **Pagination Footer**: Status text, page size selector, and previous/next pill buttons.

## 4.3 Detail Workspace with Slide-Over Drawer Template
- **Main Screen**: Primary record list or summary table.
- **Drawer Spec**: Width `440px` (desktop) / `100vw` (mobile). Sections: Record Metadata Header -> Quick Action Toolbar -> Key Properties Grid -> Activity Timeline -> Documents & Attachments. Dismiss via backdrop click, `Esc` key, or close icon.

## 4.4 Multi-Step Form & Wizard Template
- **Header**: Progress Stepper (`Step 1 of 3: General -> Step 2: Config -> Step 3: Verify`).
- **Form Card**: Centered card (`maxWidth: 760px`), `padding: 40px`, white surface.
- **Input Grouping**: 2-Column grid for short fields, 1-Column for textareas and file upload cards.

## 4.5 Authentication Portal Template (Login / Register / Reset)
- **Canvas**: Dark stage background (`#090D16`), centered auth card container (`maxWidth: 760px` dual-panel or `440px` single-panel), `paddingTop: 130px` to clear the fixed header.
- **Dual Panel Structure**: Gradient toggle panel (`linear-gradient(135deg, #4F46E5, #4338CA)`) + White form panel with social OAuth and inputs.

## 4.6 Public Landing / Hero Page Template
- **Top Navigation**: Translucent sticky bar (`rgba(9, 13, 22, 0.8)` on hero stage, turning white `#FFFFFF` when scrolled).
- **Hero Stage**: Dark background (`#090D16`), centered bold typography (`fontSize: 48px – 64px`), badge callout, and dual action CTAs.
- **Feature Grid**: 3-Column grid of glassmorphic feature cards (`rgba(15, 23, 42, 0.85)` fill, `1px solid rgba(99, 102, 241, 0.3)` border).

## 4.7 Utility & Feedback Page Templates
- **404 / 403 / Error View**: Centered card (`maxWidth: 480px`), red/amber icon badge (`56px × 56px`), error code header, explanatory message, and primary recovery button.
- **Skeleton Loading View**: Replaces page content with 4 pulsing skeleton rows.

---

# 5. UX Guidelines & Behavioral Architecture

## 5.1 Interaction Models & Tactile Feedback
- **Press Down**: Interactive elements apply `transform: scale(0.98)` on `:active`.
- **Hover Micro-Interactions**: Interactive cards lift by `-2px` with a subtle scale (`scale(1.01)`) and deepened drop shadow (`0 12px 30px rgba(0, 0, 0, 0.08)`).
- **Cursor Standards**: `cursor: pointer` on all buttons, select triggers, table rows, and clickable tags. Disabled controls enforce `cursor: not-allowed`.

## 5.2 Keyboard Navigation & Accessibility (WCAG 2.1 AAA)
- **Universal Focus Ring**: Enforce `outline: 2px solid #4F46E5 !important; outline-offset: 2px !important;` on `:focus-visible`.
- **Keyboard Shortcuts**: `Esc` key closes active modals, drawers, and menus. `Tab` key traps focus inside active modal dialogs.

## 5.3 Responsive Breakpoint Strategy
- **Mobile (`< 640px`)**: Touch targets minimum 44px height; multi-column cards condense into single-line expandable rows; desktop nav collapses into a 320px slide-over drawer with frameless close icon.
- **Tablet (`640px – 991px`)**: 2-Column KPI grid; collapsible navigation.
- **Desktop (`992px – 1239px`)**: Multi-column grid; persistent navigation.
- **Wide Desktop (`1240px+`)**: Centered 1240px container with fixed gutters.

## 5.4 Motion System & Rules
- **Timing Scale**: Fast micro-interactions (`150ms`), Structural transitions (`200ms`), Spatial transitions (`250ms`–`300ms`).
- **Motion Constraints**: Never animate layout shifts that cause surrounding text or elements to jump reflows. Respect `@media (prefers-reduced-motion: reduce)`.

## 5.5 Feedback & Error Prevention Architecture
- **Optimistic Updates**: Display inline status spinner or state change immediately during async processing.
- **Destructive Action Confirmation**: Require explicit 2-step modal confirmation with red accent styling (`#EF4444`) for destructive actions.

---

# 6. Adoption & Migration Guide

## 6.1 Step 1: Establish Root Design Tokens
Define the core tokens in your root CSS file:
```css
:root {
  /* Typography */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;

  /* Surfaces & Neutrals */
  --gray-bg: #f8fafc;
  --gray-surface: #ffffff;
  --gray-border: #e2e8f0;
  --gray-text-primary: #0f172a;
  --gray-text-muted: #64748b;

  /* Accent Branding */
  --accent: #4f46e5;
  --accent-hover: #4338ca;

  /* Status Tokens */
  --success: #10b981;
  --warning: #d97706;
  --error: #ef4444;
  --info: #3b82f6;

  /* Spacing Scale (4px Base) */
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 24px;
  --space-6: 32px;

  /* Border Radii */
  --radius-input: 6px;
  --radius-default: 8px;
  --radius-card: 16px;
  --radius-pill: 9999px;
}
```

## 6.2 Step 2: Implement Component Wrappers
1. Enforce strict prop interfaces (`variant: 'primary' | 'secondary' | 'danger'`, `size: 'sm' | 'md' | 'lg'`).
2. Wrap raw HTML controls in system components (`<Button>`, `<Input>`, `<Card>`, `<Badge>`, `<Table>`).
3. Ensure every form input includes a minimum 44px touch height (`min-height: 44px`) and explicit focus rings (`:focus-visible`).

## 6.3 Step 3: Customizing Branding Without Breaking System Integrity
- **Swap Primary Accent Colors**: Override `--accent` and `--accent-hover` with your brand's signature color (e.g., Emerald `#059669`, Cyan `#0891B2`, or Royal Blue `#2563EB`).
- **Keep Spacing & Radius Rules Intact**: Maintain the 4px baseline grid (`--space-1` to `--space-6`) and border radius scale to preserve proportional harmony.
- **Decouple Domain Terms**: Use generic component names (`DataCard`, `MetricGrid`, `StatusBadge`, `ActionDrawer`).

## 6.4 Step 4: Page Rollout Checklist
- [ ] Does the page container enforce `max-width: 1240px; margin: 0 auto; padding: 0 24px;`?
- [ ] Are all KPI metric numbers using high-contrast bold typography (`#0F172A`, font-weight 800)?
- [ ] Are status badges pairing colors with semantic text labels and icons?
- [ ] Does mobile view collapse multi-column cards and navigation cleanly without horizontal overflow?
- [ ] Do all focusable controls display a visible focus indicator (`outline: 2px solid var(--accent)`) when navigated via keyboard?
- [ ] Is `prefers-reduced-motion: reduce` respected for all animations?
