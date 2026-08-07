# Lesson 08 — React Router: Real URLs for a Single-Page App

**Verified against (August 2026):** React Router **8.3.0**. The package name is simply `react-router` — `react-router-dom` was fully removed as of v8 and no longer exists; every import this lesson uses (`BrowserRouter`, `Routes`, `Route`, `Outlet`, `Link`, `NavLink`, `useNavigate`, `useParams`) comes from that one package. Installation was already covered in [`00-setup.md`](./00-setup.md) — this lesson does not repeat `npm install react-router`; if you skipped that step, go do it now.

## What you'll learn

- What a **Single Page Application (SPA)** actually is, precisely, and the specific problem that causes.
- How React Router solves that problem without full page reloads: declarative mode's `<BrowserRouter>`, `<Routes>`, and `<Route>`.
- `<Link>` and `<NavLink>` — why they're not just "prettier `<a>` tags," and exactly what mechanism they use to avoid a reload.
- **Nested routes** and `<Outlet />` — how one parent route's UI can wrap whichever child route currently matches.
- **Dynamic segments** (`:id`) and reading them with `useParams()`.
- **Index routes** and the **catch-all route** for "nothing matched."
- **Programmatic navigation** with `useNavigate()` — moving to a new URL from code, not a click.
- The real route table QuestLog actually uses, read end to end.

## Why this matters

Every real website you've ever used has URLs that mean something: `/quests/17` takes you straight to quest #17, the back button works, refreshing the page doesn't dump you back to square one, and you can bookmark or share a link to one specific thing. A plain React app, built only with the tools from Lessons 01–07 (components, state, conditional rendering), has none of that by default — it's genuinely just one HTML page, no matter how many different "screens" it can show. React Router is the tool that closes this gap, and it's used in nearly every real-world React app you'll ever touch professionally, including QuestLog from this point forward.

## Prerequisites

Lessons 01–07 of this module (components, props, JSX, `useState`, `useEffect`, conditional rendering, forms, `useContext`, data-fetching/loading/error patterns) — this lesson assumes all of that is comfortable and adds navigation on top of it, without re-explaining any of it. [`00-setup.md`](./00-setup.md) — `react-router` must already be installed and importing correctly.

## The concept, explained simply

Before Lesson 01 even existed, here's roughly what a React app with multiple "pages" but no router looks like: a piece of state, say `const [page, setPage] = useState("list")`, and a big conditional — `{page === "list" ? <QuestListPage /> : <QuestDetailPage />}` — that swaps which component renders based on that state. Clicking a "quest" button doesn't navigate anywhere in the browser's sense; it just calls `setPage("detail")`, and React re-renders. This actually works, in the sense that the user sees different content. But look at what's genuinely missing: the address bar still says the exact same URL the whole time, no matter what's showing. The back button does nothing meaningful — there's no browser history entry for "was viewing the list" vs. "was viewing quest #17," because nothing about the URL ever changed. Refreshing the page always dumps you back to whatever the initial state was, losing your place entirely. And you can't send a friend a link to one specific quest, because there is no per-quest link — there's only ever one single URL for the whole app.

This is the precise, technical meaning of a **Single Page Application (SPA)**: a web app that loads a single HTML page once, and then uses JavaScript to change what's displayed, without the browser ever navigating to a new HTML document for each "page" the user perceives. QuestLog, as built so far, already is one (recall `npm run build`'s single `dist/index.html`, from [`00-setup.md`](./00-setup.md)) — this isn't a new problem introduced today, it's one that's been sitting under the surface since Lesson 01.

**React Router's job** is to make an SPA behave, from the user's and browser's point of view, like a real multi-page site — with genuine, distinct, bookmarkable URLs for each "page" — while still keeping every single one of an SPA's actual advantages (no full page reload, no re-downloading the whole JS bundle, instant transitions). It pulls this off through a real, unglamorous browser feature called the **History API**: a set of JavaScript functions (`pushState`, `replaceState`, and listening for `popstate`, the "back/forward button was pressed" event) that lets a script change what URL the address bar displays and what entry sits in the browser's back/forward history, *without* triggering an actual navigation/page-reload. React Router calls these functions for you, at the right moments, and re-renders whichever components match the new URL — so what the user experiences is "clicking things changes the page and the URL," while what the browser experiences under the hood is "the URL bar was quietly updated by a script; no new page was ever requested from a server."

**Game-dev framing, since you already have a mental model for this from Unreal:** think of React Router as something like a **level-streaming / sub-level manager** in a persistent level. The "persistent level" (the one HTML page, loaded once) never reloads — but a manager swaps which sub-level's actors are currently spawned in based on where the player currently is, and it keeps a record of "where the player has been" so a "return to previous location" command works. React Router's route table is that manager's rulebook: "when the player's location matches this path, spawn this sub-level's actors."

## The details

Everything in this lesson uses React Router's **declarative mode** — plain JSX components (`<BrowserRouter>`, `<Routes>`, `<Route>`) describing your route table directly in your component tree. This is what QuestLog uses, and what fits a plain client-side SPA with no server-rendering concerns. React Router 8 also ships **data mode** (`createBrowserRouter` plus `loader`/`action` functions that fetch data *before* a route renders — genuinely useful, but out of scope here, since it adds real complexity QuestLog's simple `useEffect`-based fetching from earlier lessons doesn't need) and **framework mode** (a full server-rendering framework, effectively React Router absorbing what used to be a separate project called Remix — this connects directly to Lesson 09's Next.js discussion, since framework mode does some of the same job Next.js does). You only need declarative mode for this module; the other two are worth knowing exist, not worth learning deeply right now.

### Step 1 — `<BrowserRouter>` at the root, and two bare routes

Every app using React Router needs exactly one `<BrowserRouter>`, wrapped around the *entire* app, once, at the root. This mirrors QuestLog's actual `src/main.tsx`:

```tsx
// src/main.tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router";
import App from "./App.tsx";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
);
```

**Line by line:** `import { BrowserRouter } from "react-router";` — one import, from the one package this version uses. `<BrowserRouter>` is a component whose entire job is to connect to the real browser History API described above and make routing information (the current URL, functions to change it) available to every component nested inside it, however deep. It renders nothing visible itself — it's purely plumbing. Everything that uses routing (`<Routes>`, `<Link>`, `useParams()`, `useNavigate()` — every one of them) **must** be rendered somewhere inside a `<BrowserRouter>`, or it breaks; this lesson's Common Mistakes section covers exactly what that failure looks like.

Now, inside `App`, a minimal route table with two unrelated pages, no nesting yet:

```tsx
// src/App.tsx (a simplified, two-route starting point — not the real file yet)
import { Route, Routes } from "react-router";

function QuestListPage() {
  return <h1>Quest Board</h1>;
}

function AboutPage() {
  return <h1>About QuestLog</h1>;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<QuestListPage />} />
      <Route path="/about" element={<AboutPage />} />
    </Routes>
  );
}

export default App;
```

**Line by line:** `<Routes>` is a container — it looks at the browser's *current* URL and renders exactly one of its child `<Route>`s: whichever one's `path` matches. It's a bit like a `switch` statement over the current URL, except it's declared as JSX and re-evaluated automatically every time the URL changes. `<Route path="/" element={<QuestListPage />} />` says: "when the URL's path is exactly `/`, render `<QuestListPage />`." `element` takes actual JSX (a rendered component), not a component reference — note the `<QuestListPage />` with angle brackets, not bare `QuestListPage`. Visiting `http://localhost:5173/` renders the quest board; visiting `http://localhost:5173/about` renders the about page — genuinely different URLs, genuinely different rendered output, and neither one ever asked a server for a new HTML document.

**Try it yourself:** add a third route, `<Route path="/settings" element={<h1>Settings</h1>} />`, and manually type `http://localhost:5173/settings` into your browser's address bar. Confirm it renders. Then predict, before trying, what happens if you visit `/setting` (missing the final `s`) — nothing matches any `path`, and (until this lesson's catch-all section) React Router currently renders nothing at all for an unmatched URL. That gap is exactly what the catch-all route later in this lesson fixes.

### Step 2 — `<Link>`, and exactly why it beats a plain `<a href>`

Typing a URL manually or clicking a plain `<a href="/about">` both work today — a browser always knows how to follow a link. But a plain `<a href>` does something genuinely undesirable here: it triggers a **real, full page navigation** — the browser throws away the entire current page, including all React state, and re-requests and re-downloads everything from scratch. `<Link>` exists specifically to avoid that:

```tsx
import { Link } from "react-router";

function QuestListPage() {
  return (
    <div>
      <h1>Quest Board</h1>
      <Link to="/about">About QuestLog</Link>
    </div>
  );
}
```

**Line by line:** `<Link to="/about">...</Link>` renders a real, genuine `<a>` tag in the actual DOM (open your browser's DevTools and inspect it — it's an `<a href="/about">` underneath, so right-click → "open in new tab" and screen readers both still work exactly as expected). The difference is behavioral, not visual: `<Link>` attaches its own `onClick` handler that calls `event.preventDefault()` — **the exact same method** Module 03's forms lesson already taught you, stopping the browser's default action (there, submitting a form and reloading the page; here, following the link and reloading the page) — and then calls the History API's `pushState` itself to update the URL and re-render the matching route, entirely in JavaScript, with zero network request for a new document. This isn't a new mechanism you're learning from scratch — it's the exact same "intercept the default browser behavior, then do something smarter instead" pattern applied to navigation instead of form submission.

**Why this matters concretely:** if QuestLog held quest data only in React state (which, as built through Lesson 07, it does, before a backend exists starting Module 05), a plain `<a href>` navigating from the quest board to a quest's detail page would wipe out that entire in-memory state on the full reload that follows — any unsaved filter, any in-progress edit, gone, replaced by a completely fresh page load. `<Link>` keeps the whole app instance alive in memory across the "navigation," exactly preserving an SPA's core benefit.

### Step 3 — `<NavLink>`: a `<Link>` that knows when it's "active"

QuestLog's real header needs its nav links to visibly highlight whichever page you're currently on. A plain `<Link>` has no idea what the current URL is; `<NavLink>` does:

```tsx
// src/components/Layout.tsx (the real file)
import { Link, NavLink, Outlet } from "react-router";

const navLinkClasses = ({ isActive }: { isActive: boolean }) =>
  `rounded-md px-3 py-2 text-sm font-medium ${
    isActive ? "bg-indigo-600 text-white" : "text-slate-600 hover:bg-slate-100"
  }`;

export function Layout() {
  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-4xl items-center justify-between px-4 py-3">
          <Link to="/" className="text-lg font-bold text-slate-900">
            🗒️ QuestLog
          </Link>
          <nav className="flex gap-1">
            <NavLink to="/" className={navLinkClasses} end>
              Quest Board
            </NavLink>
            <NavLink to="/quests/new" className={navLinkClasses}>
              New Quest
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-4xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  );
}
```

**Line by line (ignore the Tailwind class strings for now — Lesson 10 covers those in full; focus on the routing):** `<NavLink to="/" className={navLinkClasses} end>` — everything about this behaves like `<Link>` (real `<a>`, intercepted click, no reload) with one addition: React Router itself tracks whether this link's `to` currently matches the URL, and instead of accepting a plain string for `className`, `<NavLink>` accepts a **function** that receives `{ isActive: boolean }` and returns whatever class string you want based on it — that's `navLinkClasses` above, a small arrow function returning one string or another depending on `isActive`. `end` is a prop specific to this exact link: without it, `to="/"` would count as "active" on *every* URL (since every path technically starts with `/`) — `end` tells `<NavLink>` "only count this as active on an exact match," which is why the "New Quest" link (no `end`) doesn't need it — `/quests/new` isn't a prefix of anything else in this app, so there's no ambiguity to resolve. (You've now seen `<Outlet />` in this real file too — that's the very next section.)

**Try it yourself:** in your own throwaway `react-practice` project (from [`00-setup.md`](./00-setup.md)), build a two-link nav using `navLinkClasses` above, click between the two links, and confirm the highlighted one visibly changes — with zero full-page flash or reload.

### Step 4 — Nested routes and `<Outlet />`

So far, every route has rendered a totally independent component with its own full page. Real apps almost never work that way — QuestLog has one shared header/nav (`Layout`, above) that should stay on-screen across every page, with only the content *below* it changing. This is what **nested routes** solve.

Build it up minimally first:

```tsx
import { Route, Routes, Outlet } from "react-router";

function Layout() {
  return (
    <div>
      <header>Shared header — never unmounts while navigating between children</header>
      <Outlet />
    </div>
  );
}

function ListPage() {
  return <p>List page content</p>;
}

function DetailPage() {
  return <p>Detail page content</p>;
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<ListPage />} />
        <Route path="detail" element={<DetailPage />} />
      </Route>
    </Routes>
  );
}
```

**Line by line, and this is the single most important idea in this section:** `<Route path="/" element={<Layout />}>` is now a **parent route** — note it has children nested inside its own JSX tags, rather than being self-closing. React Router renders `<Layout />` exactly once for any URL starting with `/` that also matches one of its children. `<Outlet />`, inside `Layout`, is a **placeholder** — literally, "render whichever child route currently matches, right here." When the URL is `/`, the child that matches is `<Route index element={<ListPage />} />` (covered next), so `<Outlet />` renders `<ListPage />` — meaning the final rendered tree is `Layout`'s `<header>`, followed by `<ListPage />`'s content, in the *exact* position `<Outlet />` sits in `Layout`'s JSX. Navigate to `/detail` and only the `<Outlet />`'s contents swap to `<DetailPage />` — `Layout`'s header never unmounts, never re-renders from scratch, and never flickers, because React recognizes it as the exact same component instance across that navigation.

This is precisely QuestLog's real shape, now with the pieces you've already read (`Layout`, `Outlet`, `NavLink`) assembled into the real route table:

```tsx
// src/App.tsx (the real file)
import { Route, Routes } from "react-router";
import { Layout } from "./components/Layout";
import { QuestListPage } from "./pages/QuestListPage";
import { NewQuestPage } from "./pages/NewQuestPage";
import { QuestDetailPage } from "./pages/QuestDetailPage";
import { NotFoundPage } from "./pages/NotFoundPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<QuestListPage />} />
        <Route path="quests/new" element={<NewQuestPage />} />
        <Route path="quests/:id" element={<QuestDetailPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

export default App;
```

Notice: `QuestListPage`, `NewQuestPage`, and `QuestDetailPage` are just ordinary React components — components using props, `useState`, `useContext`, and everything else from Lessons 01–07. Routing doesn't introduce a new kind of component; a "page" is simply any component that happens to be the `element` of a `<Route>`.

### Step 5 — Dynamic segments and `useParams()`

`quests/:id` is a **dynamic segment** — a piece of a route's `path` starting with `:` that matches *any* value at that position in the URL, and captures it under that name. `/quests/17`, `/quests/abc`, `/quests/anything-at-all` all match `quests/:id`, with `id` capturing `"17"`, `"abc"`, or `"anything-at-all"` respectively. Reading that captured value is `useParams()`'s entire job:

```tsx
// src/pages/QuestDetailPage.tsx (relevant excerpt from the real file)
import { useParams } from "react-router";

export function QuestDetailPage() {
  const { id } = useParams<{ id: string }>();
  // ...
}
```

**Line by line:** `useParams<{ id: string }>()` is a **hook** (recall Lessons 02–04's rules for hooks — called at the top of the component, never conditionally) that returns an object whose keys match every `:name` segment in the *current* matched route's `path` — here, just `{ id: "..." }`, since `quests/:id` has exactly one dynamic segment. The `<{ id: string }>` part is a TypeScript **generic type argument** (Module 03, Lesson 09's `Promise<number>` was the same pattern) telling `useParams` what shape to type its return value as — you're asserting the params this specific route needs, the same way `QuestDetailPage` is only ever rendered by the `quests/:id` route, so it's always the case that a param named `id` will be present here.

**The one fact worth sitting with carefully: everything `useParams()` returns is a plain string, always, with zero exceptions.** A URL is text — the browser's address bar has never held a JavaScript number, boolean, or object; `/quests/17`'s `17` arrives as the two-character string `"17"`, not the number `17`. If a quest's `id` were compared against a *number* somewhere (`quest.id === 17`), that comparison would silently fail forever, since `"17" === 17` is `false` in both JavaScript and TypeScript (different types, `===` never coerces). QuestLog's real quest `id`s are strings for exactly this reason — sidestepping the conversion entirely rather than needing `Number(id)` (and then handling what happens if that conversion produces `NaN` because someone typed `/quests/hello` by hand) at every single point `id` is used.

**Try it yourself:** in `QuestDetailPage`, temporarily add `console.log(typeof id, id)` and visit `/quests/17` in the browser. Confirm the console prints `string 17`, not `number 17` — proof the value really is text, even though it visually looks like a number.

### Step 6 — Index routes and the catch-all route

Two special `<Route>` shapes appear in the real `App.tsx` above and are worth naming precisely:

- **`<Route index element={<QuestListPage />} />`** is an **index route** — the route that renders when its *parent's* path matches exactly, with no further segment at all. Without it, visiting bare `/` (which does match the parent `<Route path="/" element={<Layout />}>`) would render `Layout` with an empty `<Outlet />` — nothing to show, since none of the other children (`quests/new`, `quests/:id`, `*`) match an empty remaining path. `index` fills that specific gap: "when the parent matched, but nothing more specific did, render *this*."
- **`<Route path="*" element={<NotFoundPage />} />`** is the **catch-all route** — `*` matches literally anything that didn't match any earlier sibling route. Route matching in React Router checks siblings in order and stops at the first match, so `*` is placed last deliberately; if it were first, it would swallow every URL, including ones meant for `quests/new` or `quests/:id`, since a catch-all appearing earlier would never let React Router even reach those.

Try it in your browser right now against the real QuestLog app: visit `/this-does-not-exist`. **Expected:** `NotFoundPage` renders — "404 — Page Not Found," with a link back to the Quest Board — instead of a blank page or a crash.

### Step 7 — Programmatic navigation with `useNavigate()`

Every navigation so far has been a direct response to a click on a `<Link>`/`<NavLink>`. Sometimes you need to navigate *without* a click being the direct trigger — most commonly, right after a form successfully submits. That's `useNavigate()`:

```tsx
// src/pages/NewQuestPage.tsx (the real file)
import { useNavigate } from "react-router";
import { useQuests } from "../context/QuestsContext";
import { QuestForm } from "../components/QuestForm";
import type { NewQuestInput } from "../types/quest";

export function NewQuestPage() {
  const { addQuest } = useQuests();
  const navigate = useNavigate();

  function handleSubmit(values: NewQuestInput) {
    addQuest(values);
    navigate("/");
  }

  return (
    <div className="mx-auto max-w-lg">
      <h1 className="mb-6 text-2xl font-bold text-slate-900">New Quest</h1>
      <QuestForm submitLabel="Add Quest" onSubmit={handleSubmit} onCancel={() => navigate("/")} />
    </div>
  );
}
```

**Line by line:** `const navigate = useNavigate();` — another hook, returning a **function** you call whenever you decide, in your own code, that the user should move to a different URL. `handleSubmit` runs when `QuestForm`'s `onSubmit` prop fires (i.e., after the form's own `event.preventDefault()`-guarded submit handler, from Lesson 05's controlled-forms material, already ran) — it calls `addQuest(values)` to actually save the new quest into context state, and then `navigate("/")`, sending the user back to the Quest Board, *after* that save genuinely completed — not before, and not as a side effect of any click on this page (the actual click was on `QuestForm`'s submit `<button>`, several components away). `onCancel={() => navigate("/")}` shows the same function used for an entirely different reason — abandoning the form — proving `navigate` is a general-purpose "go here now" tool, not tied to any one specific event.

**Try it yourself:** in `NewQuestPage`, change `navigate("/")` (in `handleSubmit`) to `navigate("/quests/new")` (navigating back to itself) and add a new quest through the real UI. Predict what you'll see before trying — since navigating to the *same* route you're already on doesn't remount the page or clear the form's local state the same way a real page reload would, you should notice the previous quest's now-stale form values are still sitting in the fields, a small but genuine demonstration of exactly what "an SPA never fully reloads" means in practice. Change it back to `navigate("/")` afterward.

## Common mistakes & gotchas

- **Forgetting `<BrowserRouter>` at the root.** Every hook this lesson covers (`useParams`, `useNavigate`) and every routing component (`<Routes>`, `<Link>`, `<NavLink>`, `<Outlet>`) only works because `<BrowserRouter>` makes routing information available through React context (Lesson 06) to everything nested inside it. Without it, you'll see an error along the lines of `useNavigate() may be used only in the context of a <Router> component` — this is React Router explicitly telling you "you called a routing hook, but nothing above it in the tree is a router." The fix is always the same: confirm `<BrowserRouter>` genuinely wraps your whole app in `main.tsx`, not just part of it.
- **Using a plain `<a href="/quests/new">` instead of `<Link to="/quests/new">`.** It will visually work — clicking it does navigate — but it triggers Step 2's full page reload, discarding every bit of in-memory React state (any context data, any unsaved form input elsewhere on the page) and re-downloading the entire JS bundle from scratch. This is almost never what you actually want inside an SPA; reserve plain `<a href>` for links that leave your app entirely (an external site) where a full navigation is exactly correct.
- **Typo-ing `element`'s casing or forgetting it entirely** — it's `element`, lowercase, and it must receive actual rendered JSX (`element={<Outlet />}`, not `element={Outlet}` and not `elements={...}`). Getting the prop name wrong doesn't crash — React silently ignores an unrecognized prop — so the actual symptom is a route that matches but renders nothing at all, which can be a confusing, silent failure to debug if you don't already suspect the prop name itself.
- **Placing the catch-all (`path="*"`) route anywhere but last among its siblings.** Route matching checks children top-to-bottom and stops at the first match; a catch-all placed earlier swallows every URL below it, including ones meant for more specific routes.
- **Forgetting `useParams()`'s values are always strings**, and comparing one directly against a number, or passing it straight into a function expecting a number, with no conversion. Revisit Step 5 if this bites you — the fix is almost always "compare as a string" (as QuestLog does, by keeping `Quest.id` a string throughout) rather than converting the param.

## How this connects

Every "page" in this lesson (`QuestListPage`, `NewQuestPage`, `QuestDetailPage`) is, underneath, exactly the kind of component Lessons 01–07 already taught you to build — using `useState`, `useContext` (`useQuests()`), controlled forms, and loading/error patterns you already know. React Router's entire contribution is deciding *which* of these already-familiar components renders for a given URL, and swapping between them without a reload. Forward, this is the backbone of QuestLog's multi-page capstone for this module — and it connects directly to Lesson 09: React Router's **framework mode**, mentioned briefly above, is React Router absorbing what a separate project (Remix) used to do — a full server-rendering framework built around this same router — which is conceptually the same territory Next.js occupies, just from a different starting point. You won't need framework mode for QuestLog, but recognizing the name will make Lesson 09's landscape easier to place.

## Quick self-check

1. Define "Single Page Application" precisely — what, specifically, does *not* happen when the user navigates within one?
2. What does `<Link>` actually render in the DOM, and what specific method does it call to prevent a full page reload — and where else in this course have you already seen that exact method used?
3. In QuestLog's real `App.tsx`, what renders at the URL `/` exactly, and what specific kind of route is responsible for that (name it)? What renders at `/this-page-does-not-exist`, and what kind of route handles that?
4. `useParams<{ id: string }>()` on the route `quests/:id` — if the current URL is `/quests/42`, what is the exact value and exact type of `id`? Why can't it be the number `42`?
5. Give one concrete situation where you'd reach for `useNavigate()` instead of a `<Link>`, and explain why a `<Link>` wouldn't fit that situation.
