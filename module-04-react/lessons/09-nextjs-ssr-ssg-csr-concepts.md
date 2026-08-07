# Lesson 09 — Next.js: SSR, SSG, CSR, and When Each Matters

**Verified against (August 2026):** Next.js **16.3**, the current stable line. The **App Router** (introduced in Next.js 13) is now the standard, recommended approach for new Next.js projects; the older Pages Router still exists but is legacy and not covered here. **This lesson is conceptual only.** Per [`RUNNING_PROJECT.md`](../../RUNNING_PROJECT.md)'s fixed technology decisions: QuestLog stays exactly what it already is — a Vite-built, client-side React SPA — for the rest of this course. You will not install Next.js, run `create-next-app`, or build anything with it in this lesson or in QuestLog. The goal here is narrower and specific: know what SSR, SSG, CSR, ISR, and PPR actually mean, know what Next.js is and isn't, and be able to reason about which rendering strategy fits a given real page — so that on some future project where these trade-offs genuinely matter, you're making an informed choice rather than cargo-culting a framework because it's popular.

## What you'll learn

- What Next.js actually is, and how it's genuinely different from Vite — not two versions of the same thing.
- **CSR (Client-Side Rendering)** — the strategy QuestLog already uses, named and defined precisely.
- **SSR (Server-Side Rendering)** — what it means for a server to run your component code per-request, and what **hydration** is.
- **SSG (Static Site Generation)** — rendering once, at build time, instead of per-request.
- **ISR (Incremental Static Regeneration)** and **Partial Prerendering (PPR)** — two middle-ground strategies, briefly.
- A practical decision framework: given a real page, which strategy fits, and why.
- Exactly why QuestLog, right now, is correctly built as a pure CSR app — and why that could change later without this module needing to guess at it.

## Why this matters

"Should this be SSR or CSR?" is a real, common question in professional frontend work, and Next.js is the dominant framework built around answering it. You don't need to build a Next.js app to hold an informed conversation about this — but you do need to actually understand what each term means, concretely, not just recognize them as buzzwords. This lesson gives you that vocabulary and judgment before you ever need to reach for the tool itself.

## Prerequisites

Lesson 07 of this module (data fetching, loading/error states) — this lesson's CSR section is a direct re-framing of exactly what that lesson already had you build. Module 03, Lesson 07 (`fetch`/Promises/`async`-`await`) — the browser-side data fetching this lesson calls CSR is the same mechanism that lesson taught. Lesson 08 (React Router) — its brief mention of "framework mode" is picked back up here.

## The concept, explained simply

Here's the distinction worth getting precise before any of the acronyms: **Vite is a build tool. Next.js is a framework.** Vite's entire job ends the moment it hands you a `dist/` folder full of static HTML/CSS/JS files (recall [`00-setup.md`](./00-setup.md)'s `npm run build`) — from that point on, Vite has no opinion whatsoever about *where* those files are hosted or *how* they get to a browser; a plain static file host, a CDN, anything that can serve files works, and once a browser has them, 100% of the actual work (rendering the UI, fetching data, everything) happens client-side, in that browser, by that same JavaScript bundle you already know how to build.

Next.js is a much bigger claim: it's an opinionated framework that controls your app's routing *and* can run real server-side code as an actual, ongoing part of serving each page — not just a one-time build step. A live Next.js app has a running server behind it (or a serverless-function-based equivalent) that can execute your component code freshly, per incoming request, right at the moment a specific user asks for a specific page. Vite genuinely cannot do this at all — there's no "Vite server" concept that runs your React components on every request; Vite serves the same built files to everyone. This is the actual, structural reason Next.js exists as a separate thing from "React + a build tool," not a marketing distinction.

**Game-dev framing:** think of the difference between baking lighting into a level once, offline (SSG — do the expensive work once, ship the result to everyone) versus a shader that recomputes lighting live, every single frame, based on whatever's happening right now (SSR — recompute for this exact situation, every time it's needed). CSR is closer to a client downloading a level's raw geometry and running all the lighting/physics/logic locally, with the "server" having done nothing more than hand over the raw files.

## The details

### CSR (Client-Side Rendering) — the one you already know

This is worth naming precisely first, because you didn't just learn about it today — you've been building it since Lesson 01. **Client-Side Rendering (CSR)** means: the server sends the browser a nearly-empty HTML page (typically just an empty `<div id="root"></div>` and a `<script>` tag), and then JavaScript, running *in the browser*, builds the entire actual UI from scratch, including fetching any data it needs.

```html
<!-- roughly what QuestLog's real dist/index.html contains, structurally -->
<!DOCTYPE html>
<html>
  <head><!-- ... --></head>
  <body>
    <div id="root"></div>
    <script type="module" src="/assets/index-a1b2c3.js"></script>
  </body>
</html>
```

**What this means concretely, and the real trade-off it carries:** view this file's raw HTML directly (no JS execution — e.g., `curl` it, or your browser's "View Page Source," which shows the document *as delivered*, before any JS ran) and there is genuinely nothing there — no quest list, no header, nothing a search engine's crawler or a user with JavaScript disabled would ever see. Every bit of visible content appears only after the browser downloads `index-a1b2c3.js`, executes it, React renders into `#root`, and — this is the exact scenario Lesson 07 built — `QuestListPage`'s `useEffect`-driven fetch resolves and the loading spinner is replaced with real quest data. **Nothing is visible until that JS loads and runs, and anything relying on fetched data shows a loading state first** — this isn't a bug or a QuestLog-specific limitation; it's the literal definition of CSR, and it's the exact same "Loading..." state Lesson 07's `LoadingSpinner` component exists to handle gracefully.

### SSR (Server-Side Rendering) — and hydration, explained precisely

**Server-Side Rendering (SSR)** flips the CSR story: instead of sending an empty shell, a server actually *runs your component code* for this one specific incoming request, produces real, fully-filled-in HTML (an actual quest list, actual text, actual structure — not an empty `<div>`), and sends that HTML to the browser. The browser can display something meaningful — real content — the instant that HTML arrives, before a single line of JavaScript has even been downloaded, let alone executed.

But a fully-rendered static HTML page, by itself, has no working `onClick` handlers, no live state, none of React's actual interactivity — it's just inert markup at that point. So the browser *also* downloads the same JavaScript bundle CSR would have needed, and once it runs, React does something specific called **hydration**: it walks the already-present HTML, matches it up against the component tree it would have rendered anyway, and attaches real event handlers and live state to that existing markup — "waking it up" into a fully interactive React app, in place, without throwing away and re-building the HTML that's already sitting there. The user experience is: real content appears near-instantly, and a moment later (however brief), it becomes genuinely clickable/interactive.

**Why this is a real, non-trivial engineering trade-off and not a strict upgrade over CSR:** SSR requires an actual server (or serverless function) capable of running your React component code *per request*, on demand — genuinely more infrastructure than "a folder of static files on a CDN," and genuinely more moving parts that can be slow, fail, or need scaling. SSR earns that cost specifically for pages whose content is **personalized or depends on data specific to this exact request** — a logged-in user's own dashboard, a page that reads a cookie/auth token to decide what to show — where pre-baking one static version at build time (SSG, next) simply isn't possible, because there is no single correct version; it's different per request.

### SSG (Static Site Generation) — like SSR, but done once

**Static Site Generation (SSG)** is SSR's sibling, with one crucial difference: the HTML is generated **once, at build time** — not fresh for every incoming request — because the page's content genuinely doesn't depend on who's asking or when. A blog post's content is the same for every visitor; a marketing page's content is the same for every visitor. Next.js generates that HTML once, during `next build`, and from then on serving it is exactly as cheap and simple as Vite serving a static file — no per-request server work at all, despite the page having started life as server-rendered-once rather than client-rendered.

**When SSG fits:** public marketing pages, blog posts, documentation — anything where "the same content for everyone, that doesn't change from one request to the next" is true. **When it doesn't:** anything genuinely personalized (an SSG page can't read "this specific logged-in user's data," since it was rendered once, long before that user ever visited) or anything that must reflect truly live, rapidly-changing data at the moment of each request.

### ISR and PPR — two middle grounds, briefly

**Incremental Static Regeneration (ISR)** sits between SSG and SSR: a page is statically generated (like SSG — cheap to serve, no per-request work most of the time), but Next.js automatically regenerates it in the background after a configured time interval, so it can go somewhat stale between regenerations without ever being fully out of date for long. Good for content that changes occasionally but not on every single request — a product listing whose price updates a few times a day, for instance.

**Partial Prerendering (PPR)**, introduced in Next.js 15 and still current, mixes both approaches on the *same page*: a static shell (the parts of a page that are the same for everyone — SSG-style) is sent instantly, with genuinely dynamic, per-request parts (a personalized recommendation widget, say) streamed in afterward as they become ready. Both of these are worth recognizing by name; neither is graded content in this course, and neither changes anything about how you'd reason through this lesson's decision framework below — they're refinements of SSR/SSG, not a fourth fundamentally different strategy.

One more term worth defining precisely, since it underpins all of this in the current App Router: **React Server Components (RSC)** are components that run *only* on the server, never ship any of their own JavaScript to the browser at all, and can access server-side resources directly (a database, a filesystem, a secret API key) inside the component itself, safely, since that code never reaches the client. This is what makes Next.js's App Router's SSR genuinely different from "just running React on a Node.js server" — some components in an App Router page may never become interactive client-side JavaScript at all, by design, because they don't need to be.

### A concrete decision framework

Walk through four realistic pages and reason through each:

1. **A public blog post.** Same content for every visitor; no personalization; benefits enormously from being fast and crawlable by search engines (real, complete HTML present immediately, with no JS execution required to see it) — **SSG** fits well. If the post's content is edited occasionally after publishing, ISR is a reasonable refinement so a stale cached version doesn't linger forever.
2. **A logged-in user's personal dashboard.** Content is different per user, depends on who's authenticated and what their own data looks like, and that data can change between visits — a single build-time-generated version simply cannot serve every user correctly. **SSR** fits: render this specific user's specific dashboard fresh, on this specific request, using whatever their session/cookie says.
3. **A search-as-you-type widget** (type a few letters, results update instantly as you type, with no full-page navigation happening at all). This is inherently an *ongoing, client-side, interactive* experience that keeps working after the initial page load, not a one-time "produce some HTML" decision — **CSR** fits, exactly the pattern Lesson 07 already taught, using `fetch` from inside the browser in response to each keystroke.
4. **A product landing page** for a SaaS company (fixed marketing copy, a pricing table, testimonials — same for every visitor, rarely changes). Nearly identical reasoning to the blog post: no personalization, benefits from instant, crawlable HTML — **SSG**, possibly with ISR if pricing updates periodically without a full redeploy.

Notice the actual pattern underneath all four: the real question is never "which is *better*" in the abstract — it's "does this page's content depend on the specific request/user, and does it need to update live after the page loads, or is one shared version, computed once, genuinely correct for everyone?" That single question, asked honestly about a real page, gets you most of the way to the right answer every time.

### Why QuestLog, right now, is deliberately 100% CSR

QuestLog, as built through this module, is entirely CSR — and that's a deliberate, reasoned choice, not an oversight:

- **There's no real backend yet.** SSR's entire value proposition is running server-side code that can access request-specific or server-only resources (a database, an authenticated session) — QuestLog doesn't gain anything from "server-rendering" data that's genuinely all sitting in client-side React state (via `QuestsContext`) already, with no server involved at all until Module 05 introduces FastAPI.
- **No public-facing, SEO-sensitive content.** QuestLog is a personal task tracker, not a blog or marketing site — nobody needs a search engine to crawl and index a quest board, so SSG/SSR's "real HTML visible before any JS runs" benefit doesn't apply here the way it would for a public blog post.
- **Rule 1's "don't add incidental complexity."** Per [`RUNNING_PROJECT.md`](../../RUNNING_PROJECT.md): introducing a second frontend build system and a genuinely different runtime model (a live server process, not just static files) mid-course, for an app that doesn't currently need any of SSR's specific benefits, would be complexity this module's actual learning goals don't require. Vite + CSR is not a compromise here — it's the *correct*, deliberately chosen tool for what QuestLog currently is.

This isn't a permanent verdict on QuestLog's entire future — if a later module's needs genuinely called for SSR (they may not), that would be a legitimate, re-evaluated decision at that point, made with real requirements in front of it rather than guessed at now. That decision is explicitly out of scope for this module.

## Common mistakes & gotchas

- **Conflating "React" and "Next.js" as the same thing.** They are not. React is the UI library (Lesson 01) — the actual thing describing components, state, and JSX. Next.js is *a* framework built *on top of* React that adds routing, SSR/SSG, and more — one of several such frameworks (Remix, which as Lesson 08 mentioned is now largely what React Router's "framework mode" absorbed, is another). You can use React with Vite and no framework at all (exactly what QuestLog does), or with Next.js, or with something else — "I'm using React" doesn't imply any particular one of these.
- **Assuming SSR is strictly "better" than CSR.** It's a genuine trade-off, not a strict upgrade: SSR buys you faster meaningful first paint and better crawlability, at the real cost of needing actual server infrastructure that can execute your code per-request — infrastructure a pure CSR app (a folder of static files) simply doesn't need at all. A search-as-you-type widget, an admin tool behind a login wall with no SEO need, or (right now) QuestLog itself are all cases where CSR is the *correct* choice, not a lesser one.
- **Assuming SSG means "no JavaScript ships at all."** It doesn't — SSG pages still hydrate (unless a page is genuinely, entirely static with zero interactivity), and still ship a JS bundle for whatever interactive parts they do have; SSG only changes *when* the initial HTML was produced (once, at build time) and *who* produced it (a build-time process, not a live per-request server), not whether React eventually becomes interactive on the client.
- **Thinking this lesson means you now need Next.js for future projects by default.** Reaching for Next.js should follow from an actual requirement (SEO on public content, genuinely per-request personalized server rendering) — not from "it's the popular choice." Plenty of real, professional apps (internal tools, dashboards behind a login, QuestLog itself) are entirely and correctly CSR, with no framework beyond a build tool at all.

## How this connects

This lesson's CSR section is, precisely, what Module 03, Lesson 07 and this module's Lesson 07 already had you build by hand — "Next.js calls this CSR" is a new name for a mechanism you already know deeply, not a new mechanism. Lesson 08's brief mention of React Router's "framework mode" is the same territory Next.js's App Router occupies, approached from a different starting point (a router growing server-rendering features, vs. a framework built around server-rendering from day one) — recognizing both by name is enough for now. Forward: nothing in this module commits you to ever using Next.js — but Module 05 onward, once QuestLog has a real FastAPI backend and (starting Module 07) real per-user authenticated data, is exactly the point in this course where an SSR/Next.js conversation would become concretely relevant *if* a future module's requirements genuinely called for it. That's a deliberate "not yet, and not decided" — not a promise this course will introduce Next.js later.

## Quick self-check

1. State, precisely, the structural difference between what Vite does and what Next.js does — not "one is newer," an actual difference in capability.
2. In CSR, what does the raw HTML actually contain before any JavaScript executes, and what specifically becomes visible only after JS runs?
3. Define hydration in your own words: what does React do to already-present, server-rendered HTML once the JS bundle loads?
4. For each of these, say which rendering strategy fits best and why: (a) a public documentation site that rarely changes, (b) a logged-in banking app's account balance page, (c) QuestLog's quest board as it exists right now.
5. Why is "SSR is strictly better than CSR" a wrong way to think about the choice? Name the specific cost SSR carries that CSR doesn't.
