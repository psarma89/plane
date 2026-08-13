# Anti-patterns

Five mistakes. Each one shows the wrong code and the fix.

## 1. Canvas on a page or a card

Canvas belongs to the app root and nowhere else.

```tsx
// Wrong
function Page() {
  return <div className="bg-canvas">Page content</div>;
}
<div className="bg-canvas p-4 rounded-md">Card content</div>

// Fix
function Page() {
  return <div className="bg-surface-1">Page content</div>;
}
<div className="bg-layer-1 p-4 rounded-md">Card content</div>
```

## 2. A surface nested in a surface

Two surfaces on the same plane must be siblings.

```tsx
// Wrong
<div className="bg-surface-1">
  <div className="bg-surface-2">Nested</div>
</div>

// Fix, as siblings
<div className="bg-canvas">
  <div className="bg-surface-1">First area</div>
  <div className="bg-surface-2">Second area</div>
</div>

// Fix, as a layer
<div className="bg-surface-1">
  <div className="bg-layer-1">Nested</div>
</div>
```

A modal is the one exception. It sits on a different z-index plane.

## 3. A layer that does not match its surface

```tsx
// Wrong
<div className="bg-surface-1 p-4">
  <div className="bg-layer-2">Content box</div>
</div>

// Fix
<div className="bg-surface-1 p-4">
  <div className="bg-layer-1">Content box</div>
</div>
```

An input, a button, or a switch can break this rule for visual separation. A content box or a card cannot.

## 4. A hover that does not match the base

```tsx
// Wrong
<div className="bg-layer-1 hover:bg-layer-2-hover">Item</div>

// Fix
<div className="bg-layer-1 hover:bg-layer-1-hover">Item</div>
```

## 5. A missing hover prefix

The bare `-hover` token sets a permanent background. It does not create a hover state.

```tsx
// Wrong
<div className="bg-layer-1 bg-layer-1-hover">Item</div>

// Fix
<div className="bg-layer-1 hover:bg-layer-1-hover">Item</div>
```

## Review checklist

- [ ] `bg-canvas` appears once, at the app root.
- [ ] Pages use a surface, not the canvas.
- [ ] Surfaces are siblings. Modals and overlays are the exception.
- [ ] Every layer number matches its surface number, except for form controls.
- [ ] Sidebar menu items use a transparent base plus a hover state.
- [ ] Every hover matches its base layer.
- [ ] Layers stack 1 → 2 → 3 with no gaps.
- [ ] Text colors are semantic.
- [ ] Border colors are semantic.
- [ ] Nesting goes no deeper than the design needs.
