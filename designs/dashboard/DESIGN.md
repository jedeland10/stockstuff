# Design System Strategy: High-Velocity Financial Intelligence

## 1. Overview & Creative North Star: "The Kinetic Observatory"
This design system is engineered to transform raw financial data into a high-fidelity tactical map. Our Creative North Star is **The Kinetic Observatory**: a digital environment that feels like a pressurized, high-tech command center. 

Unlike standard fintech platforms that rely on "friendly" rounded corners and flat cards, this system embraces **Organic Brutalism** and **Precision Glassmorphism**. We break the "template" look by utilizing sharp 0px corners, extreme typographic contrast, and a layout that favors intentional asymmetry. Elements should feel like they are floating in a void, illuminated only by the data they carry. It is fast, cold, and undeniably authoritative.

---

## 2. Colors & Surface Architecture
The palette is rooted in deep charcoal to reduce eye strain during long trading sessions, punctuated by high-frequency neon accents that signal movement and opportunity.

### The Palette (Material Design Mapping)
*   **Background / Surface:** `#111417` (The Void)
*   **Primary (Neon Blue):** `#a4e6ff` (Core) / `#00d1ff` (Container)
*   **Secondary (Emerald Green):** `#ceffdf` (Core) / `#01f5a0` (Container)
*   **Tertiary (Alert Gold):** `#ffd59c` (Core) / `#feb127` (Container)
*   **Surface Tiers:** From `surface_container_lowest` (#0b0e11) to `surface_container_highest` (#323538).

### The "No-Line" Rule
**Prohibit 1px solid borders for sectioning.** Boundaries are defined strictly through background shifts. 
*   *Implementation:* To separate a sidebar from a main feed, set the sidebar to `surface_container_low` and the feed to `surface`. The change in hex value is the divider.

### Surface Hierarchy & Nesting
Treat the UI as a series of stacked obsidian sheets. 
*   **Deepest Level:** `surface_container_lowest` for the primary background.
*   **Active Workspaces:** `surface_container` for the main dashboard area.
*   **Interactive Modules:** `surface_container_high` for widgets and data cards.

### The "Glass & Gradient" Rule
To escape the "flat" look, use glassmorphism for floating overlays (Modals, Hover states). 
*   **Recipe:** `surface_variant` at 40% opacity + 20px Backdrop Blur.
*   **CTAs:** Use a linear gradient from `primary` (#a4e6ff) to `primary_container` (#00d1ff) at a 135-degree angle to give buttons a "glowing filament" effect.

---

## 3. Typography: The Editorial Scale
We pair the technical precision of **Inter** with the architectural strength of **Manrope**.

*   **Display (Manrope):** Massive, high-contrast values (up to 3.5rem) used for single-ticker prices or market indices. This conveys dominance and clarity.
*   **Headline (Manrope):** Sharp and authoritative. Used for section titles.
*   **Title & Body (Inter):** The "Workhorse" layer. Inter’s tall x-height ensures readability of complex financial strings and micro-copy.
*   **Labels (Inter Mono):** Use `label-sm` (0.6875rem) in uppercase with 0.05rem letter spacing for "Data Meta" (e.g., TIMESTAMP, VOL, AVG).

---

## 4. Elevation & Depth: Tonal Layering
Traditional shadows are too "soft" for this aesthetic. We use light and transparency to simulate height.

*   **The Layering Principle:** Place a `surface_container_highest` card on a `surface` background to create a "lift" without a shadow.
*   **Ambient Shadows:** For floating elements (like a stock-buy modal), use a shadow color tinted with `#00d1ff` (Primary) at 4% opacity with a 40px blur. It should look like a soft blue glow reflecting off a dark surface.
*   **The "Ghost Border" Fallback:** If a border is required for high-density data tables, use `outline_variant` at **15% opacity**. It should be felt, not seen.
*   **Sharp Corners:** All `borderRadius` values are strictly **0px**. This reinforces the "High-Tech/Military" precision of the platform.

---

## 5. Components

### Buttons
*   **Primary:** Sharp edges. Gradient fill (Primary to Primary Container). Text is `on_primary_fixed` (Deep Charcoal) for maximum contrast.
*   **Secondary:** Ghost style. No fill. `outline` border (at 20% opacity). Text in `secondary` (Emerald).
*   **States:** On hover, add a 1px outer glow using the primary color.

### Data Cards
*   **Forbid Dividers:** Use vertical whitespace (Spacing Scale 4 or 5) to separate card sections.
*   **Styling:** Use `surface_container_low` with a subtle 0.5px "Ghost Border" top-edge highlight to simulate a light source from above.

### Input Fields
*   **Unfocused:** `surface_container_highest` background, no border.
*   **Focused:** 1px bottom border using `primary` (#00d1ff). The background shifts to a 5% opacity blue tint.

### Data Visualizers (Charts)
*   **The Sparkline:** Use `secondary` (Emerald) for gains and `error` (Soft Red) for losses. 
*   **Fill:** Area charts should use a gradient fade from the accent color to 0% opacity. No solid fills.

### Navigation (The "Command Bar")
*   An asymmetric left-aligned bar using `surface_container_lowest`. Active states are marked by a vertical `primary` bar (3px wide) and a shift in text color to `primary_fixed`.

---

## 6. Do’s and Don’ts

### Do:
*   **Do** use extreme scale. A price should be significantly larger than its label.
*   **Do** use "Breathing Room." High-density data requires large gutters (Spacing 8 or 10) to prevent cognitive overload.
*   **Do** leverage Inter’s tabular numpropties for price columns so numbers don't jump when updating.

### Don't:
*   **Don't** use a single 100% opaque border for a container. It breaks the "Observatory" immersion.
*   **Don't** use rounded corners (`0px` is the law).
*   **Don't** use standard "drop shadows." Use tonal shifts and soft, tinted ambient glows.
*   **Don't** use "Light Mode." This system is built exclusively for the dark-adapted eye.