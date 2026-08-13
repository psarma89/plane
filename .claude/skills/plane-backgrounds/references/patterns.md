# Worked layouts

Six patterns. Each one shows the correct level for every element.

## 1. App root and a page

Canvas appears here and nowhere else.

```tsx
// App.tsx or the root layout
<div className="bg-canvas min-h-screen">
  <Routes>
    <Route path="/" element={<HomePage />} />
    <Route path="/dashboard" element={<DashboardPage />} />
  </Routes>
</div>

function HomePage() {
  return (
    <div className="bg-surface-1">
      <header className="border-b border-subtle">
        <div className="bg-layer-1 hover:bg-layer-1-hover px-4 py-2">Header content</div>
      </header>
      <main className="p-6">
        <div className="bg-layer-1 hover:bg-layer-1-hover rounded-md p-4">Content card</div>
      </main>
    </div>
  );
}
```

The header and the main element belong to the page surface. Neither one is a separate surface.

## 2. Card with a nested section

```tsx
<div className="bg-surface-1 p-4">
  <div className="bg-layer-1 hover:bg-layer-1-hover rounded-md p-4">
    <h3 className="text-primary font-semibold">Card Title</h3>
    <div className="bg-layer-2 hover:bg-layer-2-hover rounded p-3 mt-3">
      <p className="text-secondary">Nested content</p>
    </div>
  </div>
</div>
```

## 3. Modal or dropdown

The modal sits on its own plane, so it can use a surface with a surface below it.

```tsx
<div className="bg-surface-1">
  <div>Page content</div>

  {isModalOpen && (
    <div className="fixed inset-0 z-50">
      <div className="bg-backdrop fixed inset-0" />
      <div className="bg-surface-1 rounded-lg shadow-lg p-6">
        <div className="bg-layer-1 hover:bg-layer-1-hover rounded p-2">Modal content</div>
      </div>
    </div>
  )}
</div>
```

## 4. Sidebar layout

The sidebar and the main element are siblings on one page surface. Menu items carry no base background.

```tsx
<div className="bg-surface-1 flex">
  <aside className="border-r border-subtle w-64">
    <div className="hover:bg-layer-1-hover p-4">Sidebar item</div>
  </aside>
  <main className="flex-1 p-6">
    <div className="bg-layer-1 hover:bg-layer-1-hover rounded-md p-4">Main content</div>
  </main>
</div>
```

## 5. List

Every item sits at the same level.

```tsx
<div className="bg-surface-1 p-4">
  <div className="bg-layer-1 hover:bg-layer-1-hover rounded-md mb-2 p-3">List item 1</div>
  <div className="bg-layer-1 hover:bg-layer-1-hover rounded-md mb-2 p-3">List item 2</div>
  <div className="bg-layer-1 hover:bg-layer-1-hover rounded-md p-3">List item 3</div>
</div>
```

## 6. Form

This pattern uses the rare exception from rule 5. The input goes one level above its surface.

```tsx
<div className="bg-surface-1 p-6">
  <form className="bg-layer-1 rounded-md p-4 space-y-4">
    <div>
      <label className="text-primary font-medium">Name</label>
      <input className="bg-surface-1 border border-subtle rounded-md px-3 py-2 text-primary" type="text" />
    </div>
    <button className="bg-layer-2 hover:bg-layer-2-hover rounded-md px-4 py-2 text-primary">Submit</button>
  </form>
</div>
```

Inside a modal, an input can use `bg-layer-2` to separate it from the modal surface.

## State variants

```tsx
// Active, for a pressed state
<button className={cn("bg-layer-1 hover:bg-layer-1-hover", { "bg-layer-1-active": isActive })}>
  Button
</button>

// Selected, only with real selection logic
<div className={cn("bg-layer-1 hover:bg-layer-1-hover", { "bg-layer-1-selected": isSelected })}>
  Selectable item
</div>

// Selected, through a data attribute
<div className="bg-layer-1 hover:bg-layer-1-hover data-[selected]:bg-layer-1-selected">
  Selectable item
</div>
```
