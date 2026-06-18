---
name: design-audit
description: Compare a reference design (Figma, external website, Framer, HTML file, or screenshot) against the current implementation. Produces a thorough categorized audit of all visual discrepancies, then fixes them in batches by category after user approval. Use when the user says "design audit", "compare design", "check against Figma", "pixel audit", "match the design", "visual diff", or provides a reference URL/file to compare against.
argument-hint: "[reference-url-or-file-path] [optional: implementation-url-or-file-path]"
---

# Design Audit: Reference vs Implementation Comparison

Compare a reference design against the live implementation. Identify every visual discrepancy. Present a categorized audit. Fix in batches after user approval.

## Input

- `$ARGUMENTS` — One or two arguments:
  1. **Reference source** (required): Figma URL, external website URL, Framer URL, local HTML file path, or local screenshot/image path
  2. **Implementation target** (optional): URL or file path of the implementation to compare. If omitted, auto-detect from the reference.

## Prerequisites

- Local dev server running at `http://localhost:3000` (for implementation capture)
- `agent-browser` CLI available
- Figma MCP tools available (for Figma URLs)

## Critical: Mandatory Tooling

This skill MUST use `agent-browser` to render and capture both the reference and the implementation. **Never** use `web_fetch`, `curl`, or raw CSS/HTML parsing as a substitute. CSS extraction cannot detect visual composition like featured cards, subscribe forms, filter tabs, search bars, or layout arrangements.

If `agent-browser` is unavailable, **stop and tell the user the audit cannot proceed.** Never present an audit as complete when it was built from unrendered source code.

This applies to **BOTH** the reference **AND** the implementation. Do not audit the implementation by reading its source code instead of rendering it. Source code does not reveal how components render at specific viewports, how responsive breakpoints change layouts, or how CSS inheritance affects computed styles. Both sides must be captured as rendered pages in `agent-browser`.

## Steps

### 1. Classify the Reference Source

**AI Task:** Determine the reference type from `$ARGUMENTS`:

| Input Pattern | Type | Capture Method |
|---|---|---|
| `figma.com/design/...` or `figma.com/make/...` | Figma | Figma MCP tools |
| `figma.com/board/...` | FigJam | Figma MCP `get_figjam` |
| `*.html` or `*.htm` local path | HTML file | `agent-browser open file://[path]` |
| `*.png`, `*.jpg`, `*.jpeg`, `*.webp`, `*.gif` local path | Screenshot | Read tool (visual) |
| Any other URL (framer.site, external domain, etc.) | External website | `agent-browser open [url]` |

If `$ARGUMENTS` is empty, ask:
> "Please provide a reference design to audit against. This can be a Figma URL, website URL, HTML file path, or screenshot path."

### 2. Capture the Reference Design

**AI Task:** Capture the reference at multiple viewports.

#### For Figma URLs:

1. Parse the URL to extract `fileKey` and `nodeId`:
   - `figma.com/design/:fileKey/:fileName?node-id=:nodeId` — convert `-` to `:` in nodeId
   - `figma.com/design/:fileKey/branch/:branchKey/:fileName` — use branchKey as fileKey

2. Get design context and screenshot:
   ```
   Tool: get_design_context
   Arguments: { fileKey, nodeId }
   ```

3. Get metadata for precise dimensions:
   ```
   Tool: get_metadata
   Arguments: { fileKey, nodeId }
   ```

4. Get design tokens if available:
   ```
   Tool: get_variable_defs
   Arguments: { fileKey }
   ```

5. Document all extracted values:
   - Layout structure (frames, auto-layout direction, spacing)
   - Typography (font family, size, weight, line-height, letter-spacing)
   - Colors (fills, strokes, effects — with exact hex/rgba values)
   - Spacing (padding, gaps, margins)
   - Border radius values
   - Shadow/blur effects
   - Component dimensions (width, height, min/max constraints)

#### For External URLs (websites, Framer, etc.):

1. Open at desktop viewport (1440px):
   ```bash
   agent-browser set viewport 1440 900
   agent-browser open [url]
   agent-browser wait --load networkidle
   agent-browser screenshot ./audit-ref-desktop.png --full
   ```

2. Open at tablet viewport (768px):
   ```bash
   agent-browser set viewport 768 1024
   agent-browser reload
   agent-browser wait --load networkidle
   agent-browser screenshot ./audit-ref-tablet.png --full
   ```

3. Open at mobile viewport (375px):
   ```bash
   agent-browser set viewport 375 812
   agent-browser reload
   agent-browser wait --load networkidle
   agent-browser screenshot ./audit-ref-mobile.png --full
   ```

4. Inspect the full page structure at desktop viewport — **use `--compact --depth 4`, not `-i`**. The `-i` flag returns only interactive elements and misses section containers, content wrappers, and layout parents that carry the most important visual properties:
   ```bash
   agent-browser set viewport 1440 900
   agent-browser reload
   agent-browser wait --load networkidle
   agent-browser snapshot --compact --depth 4
   ```

5. For each section-level container visible in the screenshots, extract computed styles and bounding box. **Do not limit extraction to interactive elements.** Target the following properties that are most commonly missed in audits:

   ```bash
   # For every top-level section container:
   agent-browser get styles @eN    # focus on: background-color, background-image (for gradients)
   agent-browser get box @eN       # bounding box: x, y, width, height — used to calculate inter-section spacing

   # For every content container / inner wrapper:
   agent-browser get styles @eN    # max-width, width, padding (top/right/bottom/left), display, flex-direction

   # For every grid or flex row of cards:
   agent-browser get styles @eN    # gap, row-gap, column-gap, justify-content, align-items

   # For every image container (the wrapper <div>, not the <img>):
   agent-browser get styles @eN    # width, height, border-radius, overflow, object-fit on child img

   # For every CTA button:
   agent-browser get styles @eN    # background (may be gradient), padding, border-radius, font-size,
                                   # font-weight, letter-spacing, text-transform, box-shadow, border

   agent-browser get text @eN      # text content for all elements
   ```

   Save all extracted values as structured working notes in this format — these become the source of truth for Pass 2 comparisons:

   ```markdown
   ## Reference Layout Working Notes

   ### Sections
   | Section | Background | Padding-Top | Padding-Bottom | Max-Width |
   |---|---|---|---|---|
   | Hero | linear-gradient(135deg, #1a1a2e, #16213e) | 120px | 120px | 1200px |
   | Features | #ffffff | 80px | 80px | 1200px |

   ### Grids & Gaps
   | Section | Layout | Gap | Row-Gap | Justify |
   |---|---|---|---|---|
   | Features grid | flex-wrap | 32px | 32px | center |

   ### Image Containers
   | Section | Width | Height | Border-Radius | Overflow | Object-Fit |
   |---|---|---|---|---|---|
   | Hero | 640px | 420px | 16px | hidden | cover |

   ### CTA Buttons
   | Label | Background | Padding | Border-Radius | Font-Size | Font-Weight | Letter-Spacing | Shadow | Border |
   |---|---|---|---|---|---|---|---|---|
   | Book a Demo | linear-gradient(90deg, #6366f1, #8b5cf6) | 14px 28px | 8px | 16px | 600 | 0 | 0 4px 24px rgba(...) | none |

   ### Inter-Section Spacing (from bounding boxes)
   | Between | Gap |
   |---|---|
   | Hero → Features | 0px (sections touch) |
   | Features → Pricing | 80px |
   ```

6. Document everything captured (same list as Figma above).

#### For HTML Files:

Same as external URLs, but open with:
```bash
agent-browser open file:///[absolute-path]
```

#### For Screenshots:

Use the Read tool to visually inspect the screenshot. Document all observable properties:
- Layout structure and hierarchy
- Approximate typography (size, weight, style)
- Colors (describe what you observe)
- Spacing patterns
- Component shapes and borders
- Any text content visible

**Note:** Screenshot-only audits will be less precise for exact values (colors, spacing, font sizes). Flag this in the report.

### 2b. Section-by-Section Deep Extraction (Reference)

**AI Task:** Full-page snapshots miss interior layout details. After capturing the full-page screenshots and the initial snapshot in Step 2, go back through the reference page section by section to extract computed styles for **layout-critical elements only** — not every child element.

For each distinct visual section visible in the desktop screenshot:

1. **Run a snapshot scoped to that section's container** to identify the section's structure:
   ```bash
   agent-browser snapshot --compact --depth 6 @eN   # where @eN is the section container's element ref
   ```

2. **Identify layout-critical elements** from the snapshot output. These are:
   - The **section container** itself (background, padding, display, flex-direction)
   - **Visually meaningful layout children** — the elements a human would point to as the section's primary structural units. Examples: the two column containers in a two-column section, the individual cards in a card grid, the text block and image block in a hero section. If the DOM has wrapper `<div>`s between the section and these meaningful children, **skip the wrappers** and target the meaningful elements.
   - **All images** (both `<img>` elements and their wrapper containers)
   - **All CTA buttons and form elements** (inputs, selects, buttons)

   Do NOT extract styles for deeply nested text elements (individual paragraphs, spans, labels) — their properties are covered by the typography checks in Pass 2.

3. **Extract computed styles and bounding boxes for layout-critical elements only:**
   ```bash
   agent-browser get styles @eN   # extract: padding, display, flex-direction, gap, align-items,
                                  # justify-content, background, width, height, border-radius, box-shadow
   agent-browser get box @eN      # bounding box: x, y, width, height — for first-level layout children only
   ```

4. **Calculate spacing between first-level layout children** using their bounding boxes:
   - Vertical gap between sibling A and sibling B = `B.y - (A.y + A.height)`
   - Horizontal gap between sibling A and sibling B = `B.x - (A.x + A.width)`

5. **Record a mini layout map for each section** capturing the spatial composition:
   ```
   Hero section (measured):
     - Badge label: centered, above heading
     - H1 heading: 800px wide, centered
     - Subtitle paragraph: 600px wide, centered, 20px below heading
     - Input + button row: flex, gap: 12px, 32px below subtitle
       - Input: 320×48px, border-radius: 8px
       - Button: 140×48px, border-radius: 8px
     - Dashboard image: 100% wide, border-radius: 16px, 64px below input row
   ```

Save all per-section extraction results as structured working notes, appended to the Reference Layout Working Notes from Step 2.

> **Why this step is required:** Per-section extraction is the only way to catch: how cards are arranged within a grid, how images sit relative to text, whether a section uses a two-column layout versus stacked, and what the internal spacing is between every element. The full-page screenshot plus the mini layout map provide enough information — cropped section screenshots are not needed.

### 2c. Reference Capture Validation

**AI Task:** Before proceeding, verify that the reference capture is complete and usable. Check all five of the following:

1. **Desktop screenshot file exists and is not zero bytes.** Verify `audit-ref-desktop.png` was created.
2. **Screenshot shows a fully rendered page** with visible content — not a blank page, error page, or loading spinner. Visually inspect the screenshot using the Read tool.
3. **Desktop screenshot height is significantly taller than the viewport height (900px).** If the screenshot height is close to 900px, the `--full` flag likely failed and only above-the-fold content was captured. Re-capture with `--full` if this is the case.
4. **Layout working notes were generated from `agent-browser get styles` commands**, not from CSS file parsing or source code reading. If the working notes reference CSS class names or file paths instead of computed values, they were built wrong — go back to Step 2 and re-extract.
5. **Section mini layout maps from Step 2b exist for every section visible in the screenshot.** Count the sections visible in the desktop screenshot, then count the mini layout maps. If any section is missing a map, go back to Step 2b for that section.

**If any check fails, go back to Step 2 and re-capture before proceeding.**

### 2d. Element Count Verification

**AI Task:** Run programmatic element counts on both the reference and implementation to catch missing elements early — before the detailed Pass 1 inventory.

1. **Count elements on the reference page:**
   ```bash
   agent-browser execute "JSON.stringify({ images: document.querySelectorAll('img').length, buttons: document.querySelectorAll('button, [role=button], a[class*=button], a[class*=btn]').length, inputs: document.querySelectorAll('input, select, textarea').length, links: document.querySelectorAll('a').length, h1: document.querySelectorAll('h1').length, h2: document.querySelectorAll('h2').length, h3: document.querySelectorAll('h3').length, h4: document.querySelectorAll('h4').length })"
   ```

2. **Count elements on the implementation page** (run the same query after opening the implementation in Step 4).

3. **Present the count comparison as a table:**
   ```
   | Element Type | Reference | Implementation | Delta |
   |---|---|---|---|
   | Images | 12 | 8 | -4 ⚠️ |
   | Buttons | 5 | 5 | 0 ✓ |
   | Inputs | 2 | 0 | -2 ⚠️ |
   | Links | 24 | 20 | -4 ⚠️ |
   | H1 | 1 | 1 | 0 ✓ |
   | H2 | 6 | 4 | -2 ⚠️ |
   | H3 | 8 | 8 | 0 ✓ |
   ```

4. **Any count mismatch is an early signal** for where to look deeper during Pass 1. If the reference has 2 input fields and the implementation has 0, that is a Critical miss (likely a missing subscribe form or search bar). If the reference has 12 images and the implementation has 8, four images are missing somewhere.

> **Note:** Run the implementation count query in Step 4 after capturing the implementation. Record both counts here so they are available for Pass 1.

### 3. Identify the Implementation Target

**AI Task:** Determine which files and routes correspond to the reference design.

1. **If implementation URL was provided as second argument:** Use it directly.

2. **If not provided, auto-detect:**

   a. **From Figma:** Use the frame/page name and any Code Connect mappings:
      ```
      Tool: get_code_connect_suggestions
      Arguments: { fileKey, nodeId }
      ```

   b. **From the reference content:** Identify the page type (homepage, dashboard, settings, etc.) and search the codebase:
      - Search `apps/web/app/` for matching page routes
      - Search `apps/web/components/` for matching component names
      - Use Glob and Grep to find the implementation files

   c. **If multiple candidates found**, ask the user:
      > "I found multiple potential implementation files. Which one should I compare against?"
      > - [list candidates]

3. **Document the implementation files** that will be audited (page file + child components).

### 4. Capture the Implementation

**AI Task:** Capture the live implementation at the same viewports as the reference.

1. Read the implementation source code to understand the component structure:
   - Read the main page/component file
   - Read key child components
   - Note the Tailwind CSS v4 utility classes used, props passed, and layout structure

2. Capture at desktop viewport (1440px):
   ```bash
   agent-browser set viewport 1440 900
   agent-browser open http://localhost:3000/[route]
   agent-browser wait --load networkidle
   agent-browser screenshot ./audit-impl-desktop.png --full
   ```

3. Capture at tablet viewport (768px):
   ```bash
   agent-browser set viewport 768 1024
   agent-browser reload
   agent-browser wait --load networkidle
   agent-browser screenshot ./audit-impl-tablet.png --full
   ```

4. Capture at mobile viewport (375px):
   ```bash
   agent-browser set viewport 375 812
   agent-browser reload
   agent-browser wait --load networkidle
   agent-browser screenshot ./audit-impl-mobile.png --full
   ```

5. Inspect the full page structure at desktop viewport — **use `--compact --depth 4`, not `-i`**, matching the same extraction used for the reference:
   ```bash
   agent-browser set viewport 1440 900
   agent-browser reload
   agent-browser wait --load networkidle
   agent-browser snapshot --compact --depth 4
   ```

6. For each section-level container, extract the same layout properties used during reference capture. The goal is matching data on both sides for a direct comparison:
   ```bash
   # Section containers:
   agent-browser get styles @eN    # background-color, background-image, padding
   agent-browser get box @eN       # bounding box for inter-section spacing

   # Content wrappers:
   agent-browser get styles @eN    # max-width, width, padding, display, flex-direction

   # Grid/flex rows:
   agent-browser get styles @eN    # gap, row-gap, column-gap, justify-content, align-items

   # Image containers:
   agent-browser get styles @eN    # width, height, border-radius, overflow, object-fit on child img

   # CTA buttons:
   agent-browser get styles @eN    # background, padding, border-radius, font-size, font-weight,
                                   # letter-spacing, text-transform, box-shadow, border

   agent-browser get text @eN      # text content
   ```

   Save as implementation working notes in the same table structure as the reference notes — you will diff these against the reference values row-by-row during Pass 2.

### 4b. Section-by-Section Deep Extraction (Implementation)

**AI Task:** Mirror Step 2b exactly, applied to the live implementation. For each section visible in the implementation desktop screenshot:

1. Run `agent-browser snapshot --compact --depth 6` scoped to the section container.
2. Identify layout-critical elements (same criteria as Step 2b: section container, visually meaningful layout children, images, CTA buttons/form elements — skip wrapper divs and deeply nested text).
3. Extract computed styles and bounding boxes for layout-critical elements only.
4. Calculate measured gaps between first-level layout children from bounding boxes.
5. Record a mini layout map for each section in the same format as the reference.

Save all results as "Implementation Section Working Notes" to diff against the Reference Section Working Notes during Pass 2.

### 5. Perform the Audit

**AI Task:** Systematically compare every visual property between reference and implementation. This is a **two-pass** process — first a completeness inventory, then a property-level comparison.

#### Pass 1: Completeness Inventory (Missing & Extra Elements)

Before comparing styles, perform a **full content inventory** of the reference. Go section by section from top to bottom and list every discrete element. Then verify each one exists in the implementation.

**For each section in the reference, catalog:**

1. **Sections & containers** — every distinct page section (hero, features, pricing cards, testimonials, FAQ, footer, etc.). Note their order. **Use the mini layout maps generated in Step 2b as the structural inventory for each section.** Do not regenerate them — the maps already document each section's complete internal structure (element composition, spatial arrangement, layout direction). Cross-reference each reference map against the implementation's corresponding map from Step 4b. Flag any structural differences (wrong element order, missing elements within a section, wrong layout direction, missing form/input, stacked vs side-by-side) as **Critical**.
2. **Headings & text blocks** — every heading (h1-h6), subheading, paragraph, caption, label, and inline text. Record the **exact text content**.
3. **Buttons & CTAs** — every button, link-button, or call-to-action. Record label text, variant (filled, outline, ghost), and placement.
4. **Images & media** — every image, illustration, icon, video, animation, or decorative graphic. Note what it depicts and where it appears.
5. **Navigation elements** — nav links, dropdowns, hamburger menus, breadcrumbs, tabs. Record labels and order.
6. **Lists & repeated items** — feature lists, pricing tiers, team member cards, testimonial cards, FAQ items. Count them and note content.
7. **Form elements** — inputs, selects, checkboxes, toggles, search bars. Note placeholder text and labels.
8. **Badges, tags & indicators** — status badges, "NEW" tags, notification dots, progress bars, rating stars.
9. **Dividers & decorative elements** — horizontal rules, gradient lines, background shapes, patterns, overlays.
10. **Footer content** — footer columns, links, copyright text, social icons, legal links.
11. **Background treatments** — for each section, explicitly record whether it has: a white or light solid background, a dark solid background, a gradient background (note the gradient direction and colors), or an image/texture background. This is the single most missed category in Framer-to-code audits because backgrounds are container properties, not elements, and won't appear in interactive snapshots. Record each section's background as a named entry: e.g., "Hero: dark gradient (#1a1a2e → #16213e, 135deg)", "Features: white (#ffffff)", "Pricing: light grey (#f9fafb)".

**Then cross-reference against the implementation:**

- **Missing in implementation** — elements present in reference but absent in implementation. These are **Critical** severity by default.
- **Extra in implementation** — elements present in implementation but absent in reference. Flag for user review.
- **Wrong content** — elements that exist in both but have different text, different images, different labels, or different counts (e.g., reference shows 4 pricing tiers, implementation shows 3).
- **Wrong order** — elements that exist in both but appear in a different sequence.

Document every finding from this pass before proceeding to Pass 2.

#### Pass 2: Visual Property Comparison

Now compare ALL of the following for every visible element that exists in both reference and implementation:

**Section-Level Visual Properties ⚠️ HIGHEST PRIORITY — check these first:**

These are the properties most commonly missed because they live on container elements rather than interactive elements. Compare them using the working notes tables generated during capture steps 5/6.

- **Section background colors and gradients** — compare exact values, not just "looks dark". A section with `background: linear-gradient(135deg, #1a1a2e, #16213e)` that is implemented as `background: #f9fafb` is a Critical issue, not a color nitpick.
- **Content container max-width** — compare the inner wrapper width for each section (e.g., reference: 1200px, implementation: 100% or 1400px).
- **Section padding top and bottom** — compare exact values extracted from computed styles (e.g., reference: 120px 0, implementation: 80px 0).
- **Inter-section spacing** — calculated from bounding boxes: the vertical gap between each pair of adjacent sections. A missing margin-collapse or an extra `gap` on a flex column can cause large deviations.
- **Card and grid gaps** — the `gap`, `row-gap`, `column-gap` between sibling card/grid items. These are invisible in screenshots but cause the entire grid to feel wrong.
- **Image container dimensions and border-radius and object-fit** — compare wrapper `width`, `height`, `border-radius`, and `overflow` along with `object-fit` on the child `<img>`.
- **CTA button background** — whether it is a solid color vs a gradient, and the exact gradient definition. Also compare `padding`, `border-radius`, `font-size`, `font-weight`, `letter-spacing`, `text-transform`, `box-shadow`, and `border`.
- **Toggle and switch component styling** — track background color in unchecked and checked states, thumb color, dimensions (width × height), and border-radius. These are frequently wrong in dark-themed pages.
- **Accordion styling** — header padding, expand icon type and color, content area padding, divider style between items.
- **Internal layout pattern per section** — for every section, compare the layout pattern between reference and implementation: is it a single column, two-column side-by-side, grid of cards, or something else? Use the mini layout maps from Steps 2b/4b. A section that should be two-column is rendered as one column is a **Critical** issue.
- **Order of elements within each section** — compare the sequence of children inside each section: does the image come before or after the text block? Is the badge/label above the heading? Is the CTA below the description or above it? Wrong element order is a **Critical** issue even when all elements are present.
- **Image placement** — for every image, compare: is it left-aligned, right-aligned, centered, full-width, or overlapping another element? Compare its exact measured dimensions (width × height) and border-radius. An image that is present but in the wrong position or alignment is a **Major** or **Critical** issue.
- **Card layouts** — for sections with repeating cards: how many cards per row in the reference vs implementation? What is each card's internal padding, border-radius, shadow, and border? How is content arranged inside each card (image on top, then heading, then description? or side-by-side)? Use the per-section bounding boxes and mini layout maps to answer these precisely.
- **Hero and feature section content arrangement** — is there a badge or label above the heading? What is the heading hierarchy (h1 + h2 subtext, or just h1)? Where does the subtext sit relative to the CTA (above, below, beside)? Is there a form or input field inline with a button, or is the input missing/stacked? These structural differences are **Critical** when the reference shows one composition and the implementation shows another.
- **Container spacing (padding, margin, border-radius)** — compare padding, margin, and border-radius using shorthand values first. Normalize shorthand before comparing: `padding: 40px` = all four sides 40px; `padding: 40px 20px` = top/bottom 40px, left/right 20px; `padding: 10px 20px 30px 40px` = top/right/bottom/left. Only break down into individual sides when the normalized values differ between reference and implementation. Only flag a difference when the actual per-side values differ — not when one uses shorthand notation and the other uses longhand for the same values. Also compare the `gap` between children.
- **Z-index / layering order** — compare stacking order for overlapping elements (modals, sticky headers, overlapping cards, decorative elements).
- **Overflow behavior** — compare `overflow` (hidden, scroll, visible) on containers that clip content, especially image wrappers and card containers.
- **Content alignment** — compare text-align, justify-content, and align-items for content positioning within each section (left, center, right, justified).

**Spacing:**
- Padding (top, right, bottom, left) on every container
- Margins between sections
- Gaps between elements within groups
- Line spacing between text blocks
- Spacing between icon and adjacent text

**Typography:**
- Font family
- Font size (exact px/rem)
- Font weight (100-900)
- Line height
- Letter spacing
- Text transform (uppercase, lowercase, capitalize, none)
- Text decoration (underline, strikethrough, none)
- Text alignment
- Text color
- Text truncation / overflow behavior

**Colors:**
- Background colors (solids, gradients)
- Text colors (primary, secondary, muted)
- Border colors
- Icon colors
- Shadow colors and opacity
- Hover state colors (if observable in reference)
- Active/pressed state colors
- Selection/focus colors

**Components:**
- Button sizes, variants, and styles
- Input field sizes and styles
- Badge/tag appearances
- Card/paper appearances
- Icon sizes and types
- Avatar sizes and shapes
- Divider styles
- Tooltip appearances

**Interactive States (if observable):**
- Hover effects (color changes, shadows, transforms)
- Focus indicators
- Active/pressed states
- Disabled appearance
- Loading states
- Transition/animation timing

**Responsive Behavior:**
- Layout changes at tablet breakpoint
- Layout changes at mobile breakpoint
- Element visibility changes across breakpoints
- Font size scaling
- Spacing adjustments
- Navigation changes (hamburger menu, etc.)
- Image scaling behavior

**Content & Completeness:**
- Text content accuracy — **exact** match for every heading, subheading, paragraph, label, and description
- Placeholder text in inputs and search bars
- CTA / button text — exact label wording and casing
- Navigation labels and their order
- Footer content — all columns, all links, copyright text, social icons
- Number of repeated items (e.g., 4 pricing cards vs 3, 6 feature items vs 5)
- Image/illustration presence — every image in the reference must exist in the implementation
- Badge/tag text and presence
- Any decorative or informational element (tooltips, annotations, "most popular" labels, discount callouts)

### 5b. Thoroughness Cross-Check

**AI Task:** Before generating the report, perform a final thoroughness sweep to ensure nothing was missed.

1. **Re-read the reference screenshots** (all viewports) one more time. For each section visible in the reference, confirm you have a corresponding finding or explicit "matches" note. If you spot something you missed in Pass 1 or Pass 2, add it now.

2. **Scroll inventory check** — If the reference page is long, verify you audited below-the-fold content. Check:
   - Did you capture the full page (`--full` flag on screenshots)?
   - Are there sections at the bottom of the reference (footer, final CTA, trust badges) that you haven't compared yet?

3. **Interactive element check** — For buttons, links, tabs, and accordions visible in the reference:
   - Do they exist in the implementation?
   - Do they have the correct label text?
   - Are they the correct variant/style (filled vs outline, size, color)?

4. **Count verification** — For any repeated elements (cards, list items, grid items, nav links, footer links):
   - Count them in the reference
   - Count them in the implementation
   - Flag any mismatch

5. **Text diff** — For every heading and paragraph visible in the reference, verify the **exact wording** matches the implementation. Flag any differences in wording, casing, or punctuation.

6. **Color environment check** — For each section, compare the background color or gradient between reference and implementation. Then verify that all child element colors (text, buttons, icons, borders) are appropriate for that background. A section that should be dark with light text but is implemented as white with dark text is a **Critical** issue, not a color nitpick. Specifically check:
   - Does the section background match (solid vs gradient, correct color value)?
   - Is the text color correct for this background (light text on dark, dark text on light)?
   - Do buttons use the correct variant for this background context?
   - Are border/divider colors appropriate for the background?

Only proceed to the report once you are confident the audit is exhaustive.

### 6. Generate the Audit Report

**AI Task:** Produce a structured report categorized by severity.

#### Severity Definitions

| Severity | Definition | Examples |
|---|---|---|
| **Critical** | Missing sections/components/elements, visually broken layout, wrong structure, completely wrong colors/branding, wrong background environment | Missing hero section, missing CTA button, missing pricing card, missing image/illustration, navigation renders vertically instead of horizontally, section has wrong background color or gradient (should be dark with gradient but is plain white), CTA button is wrong color or missing gradient, pricing toggle has wrong styling, image is missing border-radius or has wrong aspect ratio, wrong number of feature cards |
| **Major** | Noticeable differences that affect the design quality | Wrong font size by 4px+, missing border-radius, section padding off by 16px or more, card gap off by 12px or more, content container has wrong max-width, button has wrong padding or border-radius by 4px or more, missing hover effects, wrong button variant |
| **Minor** | Small differences that only a careful reviewer would notice | Off by 1-2px spacing, slightly different shadow, minor color shade difference (e.g., gray-500 vs gray-600), section padding off by less than 16px |
| **Nitpick** | Extremely subtle, potentially acceptable variations | Sub-pixel rendering differences, font anti-aliasing, minor letter-spacing differences |

#### Report Format

Present the report as follows:

```markdown
# Design Audit Report

**Reference:** [source type and URL/path]
**Implementation:** [URL and file paths]
**Date:** [current date]
**Viewports tested:** Desktop (1440px), Tablet (768px), Mobile (375px)

---

## Summary

| Severity | Count |
|---|---|
| Critical | X |
| Major | Y |
| Minor | Z |
| Nitpick | W |
| **Total** | **N** |

---

## Critical Issues

### C1: [Short description]
- **Section:** [Which section of the page]
- **Reference:** [What it should look like — describe or reference screenshot]
- **Implementation:** [What it actually looks like]
- **Affected file(s):** [file path(s) and line numbers]
- **Fix category:** [Layout / Spacing / Typography / Color / Component / Responsive / Content]

### C2: ...

---

## Major Issues

### M1: [Short description]
- **Section:** [Which section]
- **Reference:** [Expected]
- **Implementation:** [Actual]
- **Affected file(s):** [paths]
- **Fix category:** [category]

### M2: ...

---

## Minor Issues

### m1: [Short description]
...

---

## Nitpicks

### n1: [Short description]
...

---

## Responsive-Specific Issues

### Tablet (768px)
- [List issues specific to tablet that weren't caught in desktop audit]

### Mobile (375px)
- [List issues specific to mobile]

---

## Screenshots

Reference (desktop): [audit-ref-desktop.png]
Implementation (desktop): [audit-impl-desktop.png]
Reference (tablet): [audit-ref-tablet.png]
Implementation (tablet): [audit-impl-tablet.png]
Reference (mobile): [audit-ref-mobile.png]
Implementation (mobile): [audit-impl-mobile.png]
```

### 7. Present and Wait

**AI Task:** Present the audit report to the user and wait for instructions.

Display the full audit report, then say:

> **Please review the audit above.** Each issue is categorized by severity (Critical > Major > Minor > Nitpick) and grouped by fix category.
>
> When you're ready, you can:
> 1. **"Fix all"** — I'll apply fixes category by category (Layout first, then Spacing, Typography, Colors, Components, Responsive, Content), confirming after each category.
> 2. **"Fix critical and major only"** — I'll skip Minor and Nitpick items.
> 3. **"Fix [specific IDs]"** — e.g., "Fix C1, M2, M5, m3" to cherry-pick specific issues.
> 4. **"Skip [specific IDs]"** — Fix everything except the listed items.
>
> What would you like to do?

**STOP HERE.** Do not proceed to fixes until the user responds.

### 8. Apply Fixes (Hybrid Category-by-Category)

**AI Task:** Apply fixes grouped by category, confirming between each group.

#### Fix Order (most impactful first):

1. **Layout & Structure** — Missing sections, wrong order, container issues
2. **Spacing** — Padding, margins, gaps
3. **Typography** — Font sizes, weights, line-heights, colors
4. **Colors** — Backgrounds, borders, shadows
5. **Components** — Button variants, badge styles, card appearances
6. **Images & Media** — Sizes, aspect ratios, object-fit
7. **Responsive** — Breakpoint-specific fixes
8. **Content** — Text labels, placeholders

#### For each category:

1. List the issues in this category that are approved for fixing
2. Apply all fixes in this category
3. Read back the changed code to verify correctness
4. Run linting and typecheck:
   ```bash
   pnpm --filter web run lint
   pnpm --filter web run typecheck
   ```
5. If dev server is running, take a new screenshot to verify:
   ```bash
   agent-browser set viewport 1440 900
   agent-browser reload
   agent-browser wait --load networkidle
   agent-browser screenshot ./audit-fix-[category].png --full
   ```
6. Present the result:
   > **[Category] fixes applied.** [N] issues fixed: [list IDs].
   > [Show screenshot if captured]
   > Ready to proceed to [next category]? Or would you like to adjust anything?

7. **Wait for user confirmation** before proceeding to next category.

#### After all categories:

Take final screenshots at all three viewports and present:

```markdown
## Fix Summary

| Category | Issues Fixed | Issues Skipped |
|---|---|---|
| Layout | C1, C2 | — |
| Spacing | M1, M3, m2 | — |
| ... | ... | ... |

**Total fixed:** X / Y approved issues

Final screenshots captured:
- Desktop: [audit-final-desktop.png]
- Tablet: [audit-final-tablet.png]
- Mobile: [audit-final-mobile.png]
```

Ask:
> Would you like me to:
> 1. Run another audit pass to catch any remaining discrepancies?
> 2. Commit these changes?
> 3. Both?

### 9. Close Browser

```bash
agent-browser close
```

## Important Rules

1. **Never guess values.** If you can't determine an exact color, spacing, or font size from the reference, flag it as "approximate" in the audit and note the uncertainty.
2. **Screenshot-only references are inherently less precise.** Always note this limitation in the report header.
3. **Follow project design tokens.** When fixing, prefer Tailwind v4 theme tokens (defined in the project's `globals.css` / `@theme` block) over hardcoded hex colors or arbitrary pixel values. Map reference values to the nearest design token; use arbitrary values only when no token fits.
4. **Respect dark mode if the project uses it.** If a dark variant exists, fixes must work in both modes — use Tailwind's `dark:` variant and CSS variables, not static one-off shades for backgrounds.
5. **Don't break functionality.** Fixes are visual only. Never remove event handlers, state, hooks, or business logic.
6. **Don't over-fix.** Only fix what the user approved. If a discrepancy exists but wasn't in the reference (e.g., the reference has a bug), note it but don't fix it.
7. **Preserve theme defaults.** Check the Tailwind `@theme` config before adding utilities — a token may already cover it.
8. **Audit layout composition, not just properties.** The most common audit failures are not wrong colors or font sizes — they are wrong layout structures: a section that should be two columns is implemented as one column, an image that should be on the right is on the left or missing entirely, a card grid that should be three columns is two columns, a featured card that should span full width is the same size as other cards, a subscribe form that should be inline is stacked or absent. Always compare the spatial arrangement and composition of elements, not just their individual CSS properties. If the reference shows a two-column layout with image on the left and text on the right, and the implementation shows a single column with text above image, that is a **Critical** issue even if every individual property on the text and image is pixel-perfect. Use the mini layout maps from Steps 2b/4b as the primary source for these comparisons — do not rely on visual impression alone.
9. **Prioritize composition over precision.** An audit that correctly identifies that a section is missing a subscribe form, has the wrong column layout, or is missing a featured card is more valuable than one that precisely measures every padding value but misses the structural problem. To enforce this priority: **always complete Pass 1 and the Section-Level Visual Properties comparison in Pass 2 before starting any other Pass 2 category.** Only after Pass 1 and Section-Level comparisons are done should you proceed to the remaining Pass 2 categories (Spacing, Typography, Colors, Components, Interactive States, Responsive). This ordering ensures that if context compaction occurs, it discards property-level details rather than structural findings. **If you must cut corners due to context limits, cut from the bottom of Pass 2, not from the top.**
