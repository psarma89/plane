---
name: plane-backgrounds
description: Plane's Canvas / Surface / Layer background system. Read this before you write or review any bg-*, text-*, or border-* utility class in apps/ or packages/ui. Use it when you build a page, card, modal, dropdown, sidebar, list, or form, when you add a hover, active, or selected state, or when a review asks whether a background is on the right level. Covers which of bg-canvas, bg-surface-1..3, and bg-layer-1..3 to pick, how to pair a layer with its surface, and the semantic text and border colors.
---

# Plane background system

Three levels. Pick one per element.

```
bg-canvas                     app root, exactly once
  └── bg-surface-1..3         top-level containers, siblings
        └── bg-layer-1..3     depth inside a surface, stack 1 → 2 → 3
```

## The rules

1. **Canvas loads once.** Use `bg-canvas` only on the single root container that wraps the app. Never on a page, card, modal, sidebar, or any nested container. Pages use a surface.
2. **Surfaces are siblings.** A surface never nests inside another surface on the same plane.
3. **Exception for a different plane.** A modal, overlay, or popover sits on its own z-index plane. It can use a surface even when a surface is below it.
4. **Match the layer number to the surface number.** `bg-surface-1` takes `bg-layer-1`, `bg-surface-2` takes `bg-layer-2`, `bg-surface-3` takes `bg-layer-3`.
5. **Rare exception, form controls only.** An input, button, or switch can go one level above its surface for visual separation. Never do this for a content box or a card.
6. **Hover must match the base.** Write `bg-layer-X hover:bg-layer-X-hover`. Never cross the numbers.
7. **Sidebar menu items carry no base background.** Use a transparent base plus `hover:bg-layer-1-hover`.
8. **State variants.** Use `-active` for a pressed state. Use `-selected` only when real selection logic exists.
9. **Do not over-nest.** Most components need `bg-layer-1` and nothing deeper.

## Semantic colors

| Purpose | Classes |
|---|---|
| Text | `text-primary`, `text-secondary`, `text-tertiary`, `text-placeholder` |
| Border | `border-subtle`, `border-subtle-1`, `border-strong`, `border-strong-1` |
| Modal backdrop | `bg-backdrop` |

Match text color to importance. `text-primary` is for headings and main content. `text-tertiary` is for labels and metadata.

## Decision order

1. Is this the root container of the whole app? Use `bg-canvas`.
2. Is this a top-level container, a sibling to other containers, or a modal on its own plane? Use `bg-surface-1`.
3. Is this nested inside a surface? Use the matching `bg-layer-N`.
4. None of the above? Re-check whether the element must be a surface.

## More detail

Read these only when you need them.

- `references/patterns.md` — six worked layouts: app root, card, modal, sidebar, list, form.
- `references/mistakes.md` — the five anti-patterns, each with a fix, plus a review checklist.
