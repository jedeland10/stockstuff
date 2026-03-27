# The Kinetic Ledger: Design System Documentation

## 1. Overview & Creative North Star
The Creative North Star for this design system is **"The Sovereign Architect."** 

Unlike standard consumer fintech that relies on rounded corners and playful friendly cues, this system adopts a posture of absolute authority and brutalist precision. It is designed for the high-stakes environment of a financial terminal—where data is the only truth. We break the "template" look by utilizing intentional asymmetry, where massive, bold headlines (`display-lg`) sit alongside hyper-dense monospace data grids. The interface should feel like a high-end physical machine: cold, fast, and engineered to a sub-pixel level of accuracy.

## 2. Colors & Surface Philosophy
The palette is rooted in the "Deepest Obsidian" to minimize eye strain during long sessions while allowing high-frequency data to "pop" with neon-like intensity.

### The "No-Line" Rule
Traditional 1px solid borders are strictly prohibited for sectioning. Structural separation is achieved through **Background Color Shifts**. 
*   Use `surface_container_lowest` (#0c0e12) against the primary `background` (#111417) to define workspace regions.
*   The only exception is the **Razor-Thin Edge**: a 1px `outline_variant` at 20% opacity used exclusively to define the perimeter of active glassmorphism overlays.

### Surface Hierarchy & Nesting
Treat the UI as a series of stacked slabs. 
*   **Level 0 (Base):** `surface_dim` (#111417) - The main workspace.
*   **Level 1 (Panels):** `surface_container_low` (#191c1f) - Navigation or sidebar containers.
*   **Level 2 (Data Modules):** `surface_container_high` (#282a2e) - High-priority interactive modules.

### Glass & Gradient Rules
To inject "soul" into the brutalist layout:
*   **Active States:** Use a subtle linear gradient on primary CTAs transitioning from `primary_container` (#00f0ff) to `primary` (#dbfcff).
*   **Modals/Popovers:** Apply `surface_bright` with a 40px `backdrop-blur`. This creates a frosted-glass effect that keeps the user anchored in the terminal's data stream while focusing on a specific task.

## 3. Typography
The typographic hierarchy is the backbone of the "Kinetic Ledger."

*   **Headings (Manrope):** Used for structural labeling. Apply `heavy tracking` (letter-spacing: 0.05rem) and `uppercase` for `headline-sm` to evoke a premium, architectural feel.
*   **UI Elements (Inter):** Used for navigation, tooltips, and labels. It provides a neutral, highly readable counterpoint to the aggressive headings.
*   **Financial Data (Monospace):** All numerical values, ticker symbols, and timestamps must use a crisp Monospace. This ensures that columns of changing numbers do not "jitter" as values fluctuate.

## 4. Elevation & Depth: Tonal Layering
We reject the soft, "pillowy" shadows of web 2.0. This system communicates depth through **Luminance and Translucency**.

*   **The Layering Principle:** Rather than "lifting" an object with a shadow, we "illuminate" it by moving it up the `surface_container` scale. An active window is simply a lighter shade of slate than the background beneath it.
*   **Ambient Shadows:** If a floating element (like a context menu) risks blending into the background, use a 64px blur shadow with 4% opacity, tinted with `primary_fixed_dim` (#00dbe9) to create a subtle electronic glow rather than a dark void.
*   **The Ghost Border:** For high-density data tables, use a 1px border of `outline_variant` at 10% opacity. It should be felt, not seen.

## 5. Components

### Buttons
*   **Primary:** Sharp 0px corners. Background: `primary_container`. Text: `on_primary` (Bold, Uppercase).
*   **Secondary:** Ghost style. 1px `outline` border. On hover, background fills to `surface_container_highest`.
*   **Kinetic State:** On click, buttons should trigger a 150ms flash of `secondary_container` (#27ff97) to signal transaction confirmation.

### Input Fields
*   **Standard:** `surface_container_lowest` background, 1px bottom-border only (`outline_variant`).
*   **Focus:** The bottom border transforms into a 2px `primary_container` line. Use Monospace for numerical inputs.

### Cards & Data Modules
*   **Constraint:** Zero dividers. Use `spacing-8` (1.75rem) to separate logical groups.
*   **Trend Indicators:** `Emerald Pulse` (#00FF94) for gains, `System Red` (#FF3B3B) for losses. Use these sparingly as "pips" or glow-lines to avoid visual fatigue.

### Additional: The "Data Ribbon"
A bespoke component for this system. A thin, 24px high horizontal ticker at the top or bottom of panels using `surface_container_highest` and Monospace `label-sm` text for real-time telemetry.

## 6. Do's and Don'ts

### Do:
*   **Embrace the Grid:** Use the `spacing-px` and `spacing-0.5` for ultra-tight data density.
*   **Use Monospace for Alignment:** Ensure all decimal points in data columns align vertically.
*   **Asymmetric Layouts:** Allow a large "Hero Data" point to dominate 60% of a view, with dense "Supporting Data" occupying the remaining 40%.

### Don't:
*   **No Rounded Corners:** `0px` is the absolute rule. Any radius breaks the brutalist intent.
*   **No Generic Icons:** Use razor-thin (1pt) stroke icons. Avoid filled or "bubbly" iconography.
*   **No Color Overuse:** If everything is `Cyber Cyan`, nothing is important. Keep 90% of the UI in the Obsidian/Slate spectrum.