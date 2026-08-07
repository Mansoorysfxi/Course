# Glossary

Every term defined anywhere in the course, alphabetical, appended as each
module is generated. If you hit a term mid-lesson that you don't remember,
check here first before asking — it's probably already defined in plain
language with a pointer back to where it was taught.

---

**Absolute path** — A filesystem path that always points to the same
location no matter where you currently are (e.g. `/c/Users/YourName/Desktop`),
as opposed to a relative path. *Taught in: [Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Access control** — The general term for the rules deciding who can do
what to a given resource; QuestLog's own access-control rule is simply "a
user may read, update, or delete only the quests they themselves
created." *Taught in: [Module 07, Lesson 01](module-07-auth-security/lessons/01-authentication-vs-authorization.md).*

**Access token** — The actual credential a client presents on real
requests once authenticated — in QuestLog, its own JWT; in a third-party
OAuth2 flow, the "valet key" a client exchanges an authorization code
for. *Taught in: [Module 07, Lesson 05](module-07-auth-security/lessons/05-oauth2-conceptual.md).*

**Accessibility** — The practice of designing software (a webpage, in this
course) so it's genuinely usable by people with disabilities, including
people relying on assistive technology like a screen reader; on the web,
largely achieved through correct semantic HTML and properly labeled form
fields. *Taught in: [Module 03, Lesson 01](module-03-html-css-javascript/lessons/01-html-structure-forms-and-accessibility.md).*

**ACID** — The four guarantees a database transaction makes: **A**tomicity
(all-or-nothing), **C**onsistency (never leaves data violating its own
rules), **I**solation (concurrent transactions don't see each other's
uncommitted changes), **D**urability (once committed, survives a crash).
*Taught in: [Module 06, Lesson 02](module-06-databases/lessons/02-indexes-transactions-and-acid.md).*

**Aggregate function** — A SQL function (e.g. `COUNT`, `SUM`) that computes
one result across every row *within* a `GROUP BY` group, rather than one
row at a time. *Taught in: [Module 06, Lesson 04](module-06-databases/lessons/04-joins-and-group-by.md).*

**Alembic** — The migration tool used alongside SQLAlchemy, generating and
applying versioned, chained migration files that bring a real database's
structure in line with a project's ORM model classes. *Taught in:
[Module 06, Lesson 07](module-06-databases/lessons/07-alembic-migrations.md).*

**API (Application Programming Interface)** — A defined way one piece of
software lets another use its functionality without needing to know how
it's implemented internally; a **web API** narrows this to functionality
exposed over HTTP to any client that can make a request. *Taught in:
[Module 02, Lesson 05](module-02-internet-and-web-fundamentals/lessons/05-clients-servers-apis-and-json.md).*

**App Router** — Next.js's current, recommended routing approach (the
default since Next.js 13), built around React Server Components, that
replaced its older "Pages Router." *Taught in: [Module 04, Lesson 09](module-04-react/lessons/09-nextjs-ssr-ssg-csr-concepts.md).*

**apt (Advanced Package Tool)** — Ubuntu/Debian's system-level package
manager, installing whole programs (Nginx, PostgreSQL) for the entire
machine, as opposed to `pip`/`npm`, which install libraries scoped to
one project. *Taught in: [Module 09, Lesson 01](module-09-linux-networking-servers/lessons/01-linux-processes-and-permissions.md).*

**`*args`** — A parameter prefixed with a single `*` that collects any
number of extra positional arguments a function is called with into a
tuple. *Taught in: [Module 01, Lesson 02](module-01-python-properly/lessons/02-functions-and-scope.md).*

**Argon2** — A newer password-hashing algorithm that OWASP and FastAPI's
own current documentation lead with ahead of bcrypt; this course teaches
bcrypt specifically because its embedded, directly inspectable salt makes
an unusually clear first example of what a salt is, while noting Argon2
as the current state of the art. *Taught in: [Module 07, Lesson 02](module-07-auth-security/lessons/02-password-hashing.md).*

**Arrow function** — A shorter JavaScript syntax for writing a function
expression, using `=>` instead of the `function` keyword (e.g.
`(a, b) => a + b`), often with an implicit return when the whole body is
one expression. *Taught in: [Module 03, Lesson 05](module-03-html-css-javascript/lessons/05-javascript-fundamentals-and-the-event-loop.md).*

**ASGI (Asynchronous Server Gateway Interface)** — The standard, agreed-upon
shape of function calls that lets any compliant Python web server (an
**ASGI server**, e.g. Uvicorn) hand a request to any compliant web
framework (e.g. FastAPI) without the two needing to know anything about
each other's internals; the modern, `async`-capable successor to the
older WSGI standard, which could only hand a server one request at a
time. *Taught in: [Module 05, Lesson 00](module-05-backend-fastapi/lessons/00-setup.md).*

**ASGI transport** — `httpx`'s mechanism (`ASGITransport`) for handing a
request directly to an ASGI app's own code, in-process, with no real
network socket at all — what lets a test call a real FastAPI app the
same way a real server would, at a fraction of the cost. *Taught in:
[Module 08, Lesson 05](module-08-testing-and-quality/lessons/05-testing-fastapi-endpoints.md).*

**Assertion introspection** — `pytest`'s ability to show the actual
runtime values on both sides of a failed plain `assert` (e.g. `assert 5
== 6`), without needing special assertion methods like `assertEqual`.
*Taught in: [Module 08, Lesson 02](module-08-testing-and-quality/lessons/02-pytest-fundamentals-and-fixtures.md).*

**Asymmetric algorithm** — A signing scheme (e.g. `RS256`) where a private
key signs and a separate, publicly shareable public key verifies —
useful when other services must verify tokens without ever being trusted
to create new ones; contrasted with the symmetric algorithm QuestLog
actually uses. *Taught in: [Module 07, Lesson 04](module-07-auth-security/lessons/04-jwt-structure-in-depth.md).*

**Async / await** — Python's syntax for writing functions that can pause at
specific points (`await`) and hand control back to an event loop while
waiting on something slow, instead of blocking the whole program. *Taught
in: [Module 01, Lesson 11](module-01-python-properly/lessons/11-async-await-fundamentals.md).*

**Async/await (JavaScript)** — JavaScript's own syntax for writing a
function (`async function`) that can pause at specific points (`await`)
and hand control back to the browser's event loop while waiting on a
Promise, instead of blocking; the same underlying idea as Python's
`async`/`await` above, applied to JavaScript's Promise objects rather than
Python's coroutines. *Taught in: [Module 03, Lesson 07](module-03-html-css-javascript/lessons/07-fetch-promises-and-async-await.md).*

**Attribute (HTML)** — Extra information carried inside an HTML element's
opening tag, written as `name="value"` pairs (e.g. `href` on an `<a>` tag).
*Taught in: [Module 03, Lesson 01](module-03-html-css-javascript/lessons/01-html-structure-forms-and-accessibility.md).*

**Authentication** — The process of verifying a claimed identity — "who
are you?" — answered exactly once in QuestLog, at `POST /api/auth/login`;
contrasted with authorization, below, which is a separate question asked
afterward. *Taught in: [Module 07, Lesson 01](module-07-auth-security/lessons/01-authentication-vs-authorization.md).*

**Authorization** — A separate check, made after authentication has
already succeeded, deciding whether an already-identified principal is
allowed to perform a specific action on a specific resource; QuestLog's
own rule is "you may only touch quests you created." *Taught in:
[Module 07, Lesson 01](module-07-auth-security/lessons/01-authentication-vs-authorization.md).*

**Authorization Code flow** — OAuth2's most common real-world flow (the
one behind nearly every "Login with X" button): the user is redirected to
the authorization server's own domain to log in and consent, which then
redirects back with a short-lived authorization code the client's server
exchanges, along with its own client secret, for a real access token —
all so the client application never sees the user's real password.
*Taught in: [Module 07, Lesson 05](module-07-auth-security/lessons/05-oauth2-conceptual.md).*

**Authorization header** — An HTTP request header used to carry
credentials (e.g. a token) identifying the requester to the server.
*Taught in: [Module 02, Lesson 04](module-02-internet-and-web-fundamentals/lessons/04-headers-cookies-and-statelessness.md).*

**Authorization Server** — The OAuth2 role played by the service that
knows a user's real password and issues tokens (e.g. Google's own
login/consent infrastructure); distinct from the Resource Server, below,
which actually holds the protected data. *Taught in: [Module 07, Lesson 05](module-07-auth-security/lessons/05-oauth2-conceptual.md).*

**Authorized_keys file** — A per-user file (`~/.ssh/authorized_keys`)
listing the public keys an SSH server will accept for that user, one per
line; only accepted at all if it and its containing `.ssh` folder have
sufficiently strict permissions. *Taught in: [Module 09, Lesson 02](module-09-linux-networking-servers/lessons/02-ssh-and-key-based-auth.md).*

**Backend framework** — A library (also called a **web framework**) that
handles the tedious, generic work of turning raw, incoming HTTP requests
into ordinary function calls with already-parsed, convenient values, and
turning a function's plain return value back into a correctly-formatted
HTTP response — letting a developer write application logic without
reading raw network bytes by hand. FastAPI is this course's choice.
*Taught in: [Module 05, Lesson 01](module-05-backend-fastapi/lessons/01-what-a-backend-does-and-your-first-routes.md).*

**bcrypt** — The password-hashing library this course uses directly (not
through the now-unmaintained `passlib`), providing `gensalt()`/
`hashpw()`/`checkpw()` functions whose output string embeds its own
random salt and cost factor. *Taught in: [Module 07, Lesson 02](module-07-auth-security/lessons/02-password-hashing.md).*

**Bind address** — The specific network address a running program asks
the operating system to accept incoming connections on; `127.0.0.1`
means "only this same machine," while `0.0.0.0` means "every network
interface this machine has." *Taught in: [Module 09, Lesson 04](module-09-linux-networking-servers/lessons/04-networking-ports-and-ips.md).*

**Bind mount** — A Docker volume type that maps a specific, named folder on
the host machine directly into a container at a chosen path, keeping both
in sync live — unlike a named volume, Docker doesn't manage where the data
actually lives; you already know, because you chose the exact host path.
*Taught in: [Module 10, Lesson 05](module-10-docker-and-containers/lessons/05-docker-volumes-and-persistence.md).*

**Boolean attribute** — An HTML attribute (e.g. `required`, `disabled`)
whose mere presence in a tag turns a behavior on, with no value needed.
*Taught in: [Module 03, Lesson 01](module-03-html-css-javascript/lessons/01-html-structure-forms-and-accessibility.md).*

**Box model** — The rule that every element on a webpage is a rectangular
box built from four concentric layers — content, padding, border, and
margin — each affecting the element's true rendered size and spacing
differently; `box-sizing: border-box` changes what an element's `width`
actually measures, from content-only to content-plus-padding-plus-border.
*Taught in: [Module 03, Lesson 02](module-03-html-css-javascript/lessons/02-css-the-box-model.md).*

**Branch** — A movable, named pointer to a specific commit in a Git
repository's history. Creating a branch is instant and cheap because it's
just a new label, not a copy of the project. *Taught in: [Module 00, Lesson 04](module-00-developer-environment-and-tooling/lessons/04-git-branching-and-merging.md).*

**Breakpoint (responsive design)** — The specific viewport width at which a
`@media` query's condition switches a layout from one arrangement to
another. *Taught in: [Module 03, Lesson 04](module-03-html-css-javascript/lessons/04-css-grid-and-responsive-design.md).*

**Brute-force attack** — Trying enormous numbers of password guesses
against a stolen hash (or a login endpoint directly) at high speed; the
specific attack bcrypt's deliberately slow, tunable cost factor exists to
make impractical. *Taught in: [Module 07, Lesson 02](module-07-auth-security/lessons/02-password-hashing.md).*

**Cache** — A copy of an expensive-to-produce answer, kept somewhere
faster to read from than the original source, so a repeated request for
the same answer can skip redoing the expensive work — QuestLog caches a
signed-in user's own quest list in Redis rather than re-querying Postgres
on every page load. *Taught in: [Module 10, Lesson 06](module-10-docker-and-containers/lessons/06-docker-compose-multi-service-apps.md).*

**Cache hit / cache miss** — A "hit" is a request answered directly from a
cache, without touching the original, slower data source; a "miss" is a
request the cache couldn't answer (because nothing was cached yet, or a
cached entry expired), forcing the original source to be queried, with
the result usually then stored in the cache for next time. *Taught in:
[Module 10, Lesson 06](module-10-docker-and-containers/lessons/06-docker-compose-multi-service-apps.md).*

**Cache invalidation** — Deliberately removing or discarding a cached
value the moment the underlying data it represents changes, so a later
read doesn't return a stale answer; QuestLog does this by deleting a
user's cached quest list the instant that user creates, updates, or
deletes a quest. Famously one of the two hardest problems in computer
science (alongside naming things), because it's easy to invalidate too
little (stale data lingers) or too much (a cache that's cleared so often
it stops helping). *Taught in: [Module 10, Lesson 06](module-10-docker-and-containers/lessons/06-docker-compose-multi-service-apps.md).*

**Cache-Control header** — An HTTP response header stating whether, and
for how long, a response may be cached and reused instead of re-fetched.
*Taught in: [Module 02, Lesson 04](module-02-internet-and-web-fundamentals/lessons/04-headers-cookies-and-statelessness.md).*

**Caching** — Keeping a copy of an expensive-to-compute or
expensive-to-fetch result somewhere fast to read (often a key-value store
like Redis) so repeated requests for the same thing skip redoing the
expensive work, trading a small amount of staleness for reduced load.
*Taught in: [Module 06, Lesson 08](module-06-databases/lessons/08-nosql-overview.md).*

**Call stack** — The JavaScript engine's running record of which function
is currently executing and which function called it; determines exactly
when a pending callback (e.g. from `setTimeout`) is allowed to run, once
it's empty. *Taught in: [Module 03, Lesson 05](module-03-html-css-javascript/lessons/05-javascript-fundamentals-and-the-event-loop.md).*

**Cascade (CSS)** — The set of rules CSS uses to decide which declaration
wins when more than one rule could apply to the same element: higher
specificity wins first, with source order (later wins) as the tiebreaker
between equally specific rules. *Taught in: [Module 03, Lesson 02](module-03-html-css-javascript/lessons/02-css-the-box-model.md).*

**`cat`** — Shell command that prints a file's contents to the screen
("concatenate"). *Taught in: [Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Catch-all route** — A route (`path="*"` in React Router) that matches any
URL not matched by an earlier sibling route, conventionally used to render
a "not found" page. *Taught in: [Module 04, Lesson 08](module-04-react/lessons/08-react-router.md).*

**`cd`** — Shell command to change your current/working directory.
*Taught in: [Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Cgroups (control groups)** — A Linux kernel feature that limits and
measures how much of the host's own CPU, memory, and other resources a
given process (or group of processes) is allowed to use — one of the two
kernel features (alongside namespaces) a container actually is, under the
hood: not a lightweight VM, just an ordinary Linux process with cgroups
capping what it can consume and namespaces limiting what it can see.
*Taught in: [Module 10, Lesson 01](module-10-docker-and-containers/lessons/01-containers-vs-vms-and-your-first-container.md).*

**chmod** — The Linux command that changes a file or directory's
permissions, in letter form (`chmod u+x file`) or numeric/octal form
(`chmod 600 file`, where `r=4`, `w=2`, `x=1` are summed per owner/group/
others digit). *Taught in: [Module 09, Lesson 01](module-09-linux-networking-servers/lessons/01-linux-processes-and-permissions.md).*

**chown** — The Linux command that changes a file or directory's owner
and/or group (`chown newowner:newgroup path`). *Taught in: [Module 09, Lesson 01](module-09-linux-networking-servers/lessons/01-linux-processes-and-permissions.md).*

**Claim (JWT)** — One named piece of information inside a JWT's payload
(e.g. `sub`, `iat`, `exp`); a **registered claim** (below) is one whose
three-letter name is part of the official JWT specification itself.
*Taught in: [Module 07, Lesson 04](module-07-auth-security/lessons/04-jwt-structure-in-depth.md).*

**Class** — A blueprint for creating objects, defining the attributes and
methods every instance built from it will have. *Taught in: [Module 01,
Lesson 05](module-01-python-properly/lessons/05-oop-classes-and-dunders.md).*

**Class attribute** — A value defined directly in a class's body (not
inside `__init__`) that is shared by every instance of that class, rather
than belonging to one instance individually. *Taught in: [Module 01,
Lesson 05](module-01-python-properly/lessons/05-oop-classes-and-dunders.md).*

**Class (CSS)** — A reusable label (`class="..."` in HTML, targeted with a
leading `.` in CSS) that many elements can share at once, used as the
primary hook for applying CSS rules and, later, for JavaScript to select
elements. Distinct from a Python class, above. *Taught in: [Module 03,
Lesson 02](module-03-html-css-javascript/lessons/02-css-the-box-model.md).*

**Cleanup function** — The function returned from a React `useEffect`
callback; React calls it right before running that effect again (if its
dependencies changed) and when the component unmounts, giving the effect
a controlled place to undo whatever it set up (clear a timer, cancel a
subscription, ignore a now-stale async response). *Taught in: [Module 04,
Lesson 03](module-04-react/lessons/03-useeffect-the-dependency-array-in-depth.md).*

**Client** — Whichever side of an interaction initiates a request; a role,
not a fixed identity — the same program can be a client in one interaction
and a server in another. *Taught in: [Module 02, Lesson 05](module-02-internet-and-web-fundamentals/lessons/05-clients-servers-apis-and-json.md).*

**Client (OAuth2)** — The OAuth2 role played by the application requesting
delegated access on a user's behalf (e.g. a photo-printing site wanting
to read someone's Google Photos); a different, specific meaning from the
general "client" above, already defined in Module 02. *Taught in:
[Module 07, Lesson 05](module-07-auth-security/lessons/05-oauth2-conceptual.md).*

**Client-Side Rendering (CSR)** — A rendering strategy where the server
sends a nearly-empty HTML shell and JavaScript running in the browser
builds the actual UI (and fetches any data it needs) entirely client-side;
the strategy every app built in Module 04 uses, with no framework beyond
Vite. *Taught in: [Module 04, Lesson 09](module-04-react/lessons/09-nextjs-ssr-ssg-csr-concepts.md).*

**Client-side routing** — Using JavaScript and the browser's History API
to update the displayed URL and swap which components render, without a
full page reload or a new document requested from a server. *Taught in:
[Module 04, Lesson 08](module-04-react/lessons/08-react-router.md).*

**Clone (`git clone`)** — Downloads a full copy of a remote repository's
entire history into a new local folder, automatically setting up `origin`.
*Taught in: [Module 00, Lesson 05](module-00-developer-environment-and-tooling/lessons/05-github-and-pull-requests.md).*

**Closure** — A nested function that "remembers" the variables from the
function it was defined inside, even after that outer function has
finished running. *Taught in: [Module 01, Lesson 02](module-01-python-properly/lessons/02-functions-and-scope.md).*

**Column** — A named, fixed-type field every row in a database table has,
comparable to one field of a spreadsheet's header row. *Taught in:
[Module 06, Lesson 01](module-06-databases/lessons/01-why-a-database-and-the-relational-model.md).*

**Commit** — A permanent, timestamped snapshot of a Git repository's
staged changes, identified by a unique commit hash. *Taught in:
[Module 00, Lesson 03](module-00-developer-environment-and-tooling/lessons/03-git-fundamentals.md).*

**Commit hash** — A unique fingerprint (computed from a commit's content)
identifying one specific commit. *Taught in: [Module 00, Lesson 03](module-00-developer-environment-and-tooling/lessons/03-git-fundamentals.md).*

**Component** — A JavaScript/TypeScript function that returns a
description of UI, reusable and callable ("instanced") as many times as
needed with different inputs — comparable to a reusable Widget Blueprint
you can drop into a HUD multiple times, configured differently each time.
*Taught in: [Module 04, Lesson 01](module-04-react/lessons/01-why-react-components-props-and-jsx.md).*

**Composition** — Building a class by holding instances of other classes
as attributes ("has a") rather than inheriting from them ("is a"). *Taught
in: [Module 01, Lesson 05](module-01-python-properly/lessons/05-oop-classes-and-dunders.md).*

**Conflict markers** — The `<<<<<<<`, `=======`, and `>>>>>>>` lines Git
inserts directly into a file when it can't automatically resolve a merge
conflict, delimiting "your version" from "the incoming version." *Taught
in: [Module 00, Lesson 04](module-00-developer-environment-and-tooling/lessons/04-git-branching-and-merging.md).*

**Container** — A running instance of a container image: an isolated
process (or small group of processes) that believes it has its own
filesystem, network, and process list, but is actually just an ordinary
process on the host machine, isolated using Linux namespaces and cgroups
rather than running inside a separate virtual machine — the game-dev
analogy: one packaged build (the image) can be launched as many running
game-server instances (containers), each isolated from the others but all
sharing the same underlying hardware and OS kernel. *Taught in: [Module 10, Lesson 01](module-10-docker-and-containers/lessons/01-containers-vs-vms-and-your-first-container.md).*

**Container image** — A packaged, versioned snapshot of an application
plus the exact runtime, libraries, and files it needs to run — built once
from a Dockerfile, then run, unchanged, as a container on any machine with
a compatible container engine. The game-dev analogy: an image is like a
packaged build of your game plus the exact runtime/libraries it needs, so
it runs identically anywhere, instead of shipping source code and hoping
the target machine already has the right SDK installed. *Taught in: [Module 10, Lesson 02](module-10-docker-and-containers/lessons/02-dockerfiles-layers-and-caching.md).*

**Container registry** — A server that stores and serves container images
by name and tag (e.g. `python:3.14-slim`, `redis:8-alpine`) — Docker Hub
is the default, public registry `docker pull`/`docker build` reach out to
unless configured otherwise. *Taught in: [Module 10, Lesson 02](module-10-docker-and-containers/lessons/02-dockerfiles-layers-and-caching.md).*

**Content-Type header** — An HTTP header stating the format of a message
body (e.g. `application/json`), telling the receiving side how to
interpret the bytes that follow. *Taught in: [Module 02, Lesson 04](module-02-internet-and-web-fundamentals/lessons/04-headers-cookies-and-statelessness.md).*

**Context manager** — An object usable after Python's `with` keyword,
implementing `__enter__` (setup) and `__exit__` (guaranteed cleanup), so
risky code always gets cleaned up even if it raises an exception. *Taught
in: [Module 01, Lesson 08](module-01-python-properly/lessons/08-file-io-and-json.md)
and [Lesson 10](module-01-python-properly/lessons/10-decorators-and-context-managers.md).*

**Context (React)** — A built-in React feature (`createContext`, a
`Provider`, `useContext`) for making a value available to any descendant
component, at any depth, without manually passing it through every
intermediate component's props. Distinct from a Python context manager,
above. *Taught in: [Module 04, Lesson 06](module-04-react/lessons/06-context.md).*

**Controlled component** — An input whose current value lives in React
state (`value` + `onChange`) rather than in the browser's own internal DOM
state; contrasted with an **uncontrolled component**, below. *Taught in:
[Module 04, Lesson 05](module-04-react/lessons/05-forms-controlled-components-and-lifting-state.md).*

**`createContext`** — The function that creates a Context object — a
named "channel" a value can be broadcast into (via a `Provider`) and read
from (via `useContext`) by any descendant. *Taught in: [Module 04,
Lesson 06](module-04-react/lessons/06-context.md).*

**Cookie** — A small piece of data a server asks a client to store (via a
`Set-Cookie` response header) and automatically resend (via a `Cookie`
request header) on every future request to that site. *Taught in:
[Module 02, Lesson 04](module-02-internet-and-web-fundamentals/lessons/04-headers-cookies-and-statelessness.md).*

**Coroutine** — The paused, not-yet-started object returned by calling an
`async def` function; running it (and getting a result) requires
`await`-ing it or scheduling it on the event loop. *Taught in: [Module 01,
Lesson 11](module-01-python-properly/lessons/11-async-await-fundamentals.md).*

**CORS (Cross-Origin Resource Sharing)** — The controlled, explicit
mechanism letting a server opt back into the Same-Origin Policy's
(below) default restriction, via specific response headers:
`Access-Control-Allow-Origin` (which origin(s) may read this response),
`-Methods` and `-Headers` (which methods/headers are permitted, answered
to a preflight request, below), and `-Credentials` (whether cookies may
be included — unrelated to a manually-set `Authorization` header). A
CORS failure almost always means the server already processed the
request fine; the browser just refused to hand your JavaScript the
response. *Taught in: [Module 07, Lesson 10](module-07-auth-security/lessons/10-cors-in-depth.md).*

**Cost factor (bcrypt)** — The adjustable parameter (default `12`)
controlling how many times bcrypt's internal algorithm repeats itself;
doubling it roughly doubles how long one hash takes, deliberately, so
brute-forcing stays impractical even as hardware gets faster. *Taught in:
[Module 07, Lesson 02](module-07-auth-security/lessons/02-password-hashing.md).*

**Coverage (test coverage)** — A measurement of which lines of
application code actually ran at least once while a test suite executed,
reported as a percentage; useful for finding code with zero tests at
all, but it says nothing about whether the tests that *do* exist checked
the right thing — 100% coverage is not, by itself, a goal worth chasing.
*Taught in: [Module 08, Lesson 02](module-08-testing-and-quality/lessons/02-pytest-fundamentals-and-fixtures.md).*

**Credential** — Proof of a claimed identity presented on a request — a
password at login, or the token/cookie presented afterward to avoid
re-proving it every time. *Taught in: [Module 07, Lesson 01](module-07-auth-security/lessons/01-authentication-vs-authorization.md).*

**CRUD** — A shorthand for the four basic operations almost any "manage a
collection of things" API needs: **C**reate, **R**ead, **U**pdate,
**D**elete — mapped, in this course's APIs, onto `POST`, `GET`, `PATCH`,
and `DELETE` respectively. *Taught in: [Module 05, Lesson 08](module-05-backend-fastapi/lessons/08-building-the-questlog-api.md).*

**CSRF (Cross-Site Request Forgery)** — An attack where a malicious page
gets a victim's browser to send a genuine, valid credential (a cookie) to
a real site, causing a real side effect the victim never intended —
possible only because browsers attach cookies to a request
*automatically*, regardless of which page initiated it. Standard defenses
include the `SameSite` cookie attribute (below) and anti-CSRF tokens (a
random value a legitimate page must resubmit with a request, which a
forged cross-site request has no way to know). QuestLog's own
header-based JWT (never a cookie) sidesteps this attack's usual mechanism
entirely, at the cost of exposure to XSS instead. *Taught in: [Module 07,
Lesson 09](module-07-auth-security/lessons/09-xss-and-csrf.md).*

**CSS (Cascading Style Sheets)** — The language that describes how HTML
elements should look — layout, color, spacing, sizing — kept deliberately
separate from HTML's own job of describing structure and meaning. *Taught
in: [Module 03, Lesson 02](module-03-html-css-javascript/lessons/02-css-the-box-model.md).*

**CSS Grid** — A CSS layout mode for arranging a container's children into
an explicit two-dimensional grid of rows and columns, with items placeable
into specific cells and able to span multiple rows/columns; the tool of
choice when items must align across both dimensions, unlike one-dimensional
Flexbox. *Taught in: [Module 03, Lesson 04](module-03-html-css-javascript/lessons/04-css-grid-and-responsive-design.md).*

**Cross axis** — In a Flexbox container, the axis perpendicular to
whichever direction `flex-direction` points; controlled primarily by
`align-items`. *Taught in: [Module 03, Lesson 03](module-03-html-css-javascript/lessons/03-css-flexbox.md).*

**Custom exception** — A programmer-defined exception class, typically
inheriting from `Exception` (directly or through another custom
exception), used to give callers of your code specific, meaningful error
types to catch. *Taught in: [Module 01, Lesson 06](module-01-python-properly/lessons/06-error-handling.md).*

**Custom hook** — A plain function whose name starts with `use` that
itself calls other hooks (`useState`, `useEffect`, etc.) to package up and
reuse stateful logic across components. *Taught in: [Module 04,
Lesson 04](module-04-react/lessons/04-useref-and-custom-hooks.md).*

**Daemon** — A process that runs continuously in the background, waiting
to handle requests (e.g. an SSH server, Nginx, `systemd` itself),
instead of doing one thing and exiting. *Taught in: [Module 09, Lesson 02](module-09-linux-networking-servers/lessons/02-ssh-and-key-based-auth.md).*

**dangerouslySetInnerHTML** — A React prop that inserts a string as raw,
unescaped HTML, bypassing React's normal automatic escaping entirely; the
one deliberate way to reintroduce stored XSS into an otherwise-safe React
app, and a prop QuestLog uses nowhere at all. *Taught in: [Module 07,
Lesson 09](module-07-auth-security/lessons/09-xss-and-csrf.md).*

**Data mode (React Router)** — React Router's `createBrowserRouter` +
loader/action style of routing, which fetches data before a route renders;
mentioned but not used by QuestLog, which stays in declarative mode.
*Taught in: [Module 04, Lesson 08](module-04-react/lessons/08-react-router.md).*

**Debugger** — A tool that pauses a running program at a specific point
and lets you inspect its live variables and step through its code one
line at a time, instead of only rereading source code and guessing;
Python's built-in one is `pdb`, reachable via `breakpoint()`. *Taught in:
[Module 08, Lesson 04](module-08-testing-and-quality/lessons/04-debugging-techniques.md).*

**Declarative mode (React Router)** — React Router's classic, JSX-based
routing style (`<BrowserRouter>`, `<Routes>`, `<Route>`), with no server
concerns or data-loading conventions — the mode this course's QuestLog
uses throughout. *Taught in: [Module 04, Lesson 08](module-04-react/lessons/08-react-router.md).*

**Decorator** — A function that takes another function (or class) as input
and returns a new, usually wrapping, function/class as output, applied
with the `@decorator_name` syntax directly above a definition. *Taught in:
[Module 01, Lesson 10](module-01-python-properly/lessons/10-decorators-and-context-managers.md).*

**Default argument** — A value a function parameter uses automatically
when the caller doesn't supply one. *Taught in: [Module 01, Lesson 02](module-01-python-properly/lessons/02-functions-and-scope.md).*

**DELETE (HTTP method)** — The HTTP method meaning "remove this resource";
idempotent by contract, since deleting an already-deleted resource still
leaves it deleted. *Taught in: [Module 02, Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**Dependency array** — `useEffect`'s second argument, determining whether
its effect runs after every render (no array), once on mount (`[]`), or
whenever a listed value differs from the previous render (compared by
reference via `Object.is`). *Taught in: [Module 04, Lesson 03](module-04-react/lessons/03-useeffect-the-dependency-array-in-depth.md).*

**Dependency injection** — A general software design idea: instead of a
function reaching out and constructing something it needs itself, deep in
its own body, that something is handed ("injected") to it from outside —
making the function easier to test and avoiding duplicated setup logic
across every function that needs the same thing. FastAPI's `Depends()`
(below) is a specific, concrete implementation of this idea for route
functions. *Taught in: [Module 05, Lesson 04](module-05-backend-fastapi/lessons/04-dependency-injection-and-depends.md).*

**`Depends`** — The FastAPI function that marks a route (or another
dependency's) parameter as something FastAPI itself should resolve, by
calling a given plain function on your behalf and passing its return
value in — usually written `Annotated[SomeType, Depends(some_function)]`.
By default, FastAPI calls a given dependency at most once per incoming
request, reusing the result if it's referenced more than once in the same
request's dependency tree. *Taught in: [Module 05, Lesson 04](module-05-backend-fastapi/lessons/04-dependency-injection-and-depends.md).*

**Destructuring** — JavaScript syntax for pulling values out of an object
or array directly into named variables in one step (e.g.
`const { name, difficulty } = quest;`), comparable to Python's tuple/dict
unpacking. *Taught in: [Module 03, Lesson 08](module-03-html-css-javascript/lessons/08-es6-plus-features-and-modules.md).*

**devDependency** — An entry in a `package.json`'s `"devDependencies"`
section, marking a package (e.g. `typescript`) as a tool needed only while
developing/building a project, not something a finished app needs to
actually run for a user. *Taught in: [Module 03, Lesson 00](module-03-html-css-javascript/lessons/00-setup.md).*

**Dialect (SQL)** — The specific extensions, data types, and edge-case
behaviors that differ between two database products (e.g. PostgreSQL vs.
SQLite) that otherwise both implement the core SQL language similarly;
the reason testing against a different database product than production
uses carries some real, if often small, risk. *Taught in: [Module 08,
Lesson 06](module-08-testing-and-quality/lessons/06-testing-with-a-database.md).*

**Dict (dictionary)** — An unordered (but insertion-order-preserving)
collection of key→value pairs, optimized for fast lookup by key. *Taught
in: [Module 01, Lesson 03](module-01-python-properly/lessons/03-data-structures.md).*

**DNS (Domain Name System)** — A distributed system that answers "what IP
address does this domain name currently point to?", via a resolver
consulting cached answers, root servers, TLD servers, and finally the
domain's authoritative server. *Taught in: [Module 02, Lesson 01](module-02-internet-and-web-fundamentals/lessons/01-networks-ip-addresses-and-dns.md).*

**DNS resolver** — The server (typically run by your ISP or a public
provider) your computer asks to perform a DNS lookup on its behalf.
*Taught in: [Module 02, Lesson 01](module-02-internet-and-web-fundamentals/lessons/01-networks-ip-addresses-and-dns.md).*

**Docker** — The dominant container platform: a container engine (build
and run images), a CLI, and an image format/ecosystem (Docker Hub) that
together made containers a practical, everyday development tool rather
than a niche kernel feature. *Taught in: [Module 10, Lesson 00](module-10-docker-and-containers/lessons/00-setup.md).*

**Docker Compose** — A tool (`docker compose`, built into the modern
Docker CLI as of this course, August 2026 — the older, standalone,
hyphenated `docker-compose` binary is now legacy/deprecated) for defining
and running a multi-container application from one YAML file
(`docker-compose.yml`): one command (`docker compose up`) builds/pulls
every service's image and starts them all, wired together on a shared,
private network. *Taught in: [Module 10, Lesson 06](module-10-docker-and-containers/lessons/06-docker-compose-multi-service-apps.md).*

**Docker Desktop** — The application Windows and macOS developers install
to get a working Docker environment; on Windows it runs Docker Engine
inside a lightweight WSL2-backed Linux VM so `docker`/`docker compose`
commands work the same as they would on real Linux. *Taught in: [Module 10, Lesson 00](module-10-docker-and-containers/lessons/00-setup.md).*

**Docker Engine** — The actual background service (`dockerd`) that builds
images, starts/stops containers, and manages networks and volumes — what
the `docker` CLI command talks to; Docker Desktop is the packaged,
Windows/macOS-friendly way of getting a Docker Engine running at all.
*Taught in: [Module 10, Lesson 00](module-10-docker-and-containers/lessons/00-setup.md).*

**Docker network** — A private, virtual network Docker creates so a
group of containers can reach each other by name; `docker compose`
automatically creates one such network per project and gives every
service in `docker-compose.yml` a DNS entry equal to its own service
name, so `backend` can reach `postgres` at the hostname `postgres`, never
`localhost` (each container has its own private `localhost`, separate
from every other container's). *Taught in: [Module 10, Lesson 04](module-10-docker-and-containers/lessons/04-docker-networking.md).*

**Dockerfile** — A plain-text file of instructions (`FROM`, `COPY`, `RUN`,
`CMD`, etc.) describing exactly how to build a container image, one
instruction at a time, each producing its own cacheable layer. *Taught
in: [Module 10, Lesson 02](module-10-docker-and-containers/lessons/02-dockerfiles-layers-and-caching.md).*

**Document store** — A NoSQL database (e.g. MongoDB) storing whole,
often JSON-shaped "documents" that don't all have to share the same
structure, trading a relational database's strict schema enforcement for
flexibility when a record's shape varies a lot or changes often. *Taught
in: [Module 06, Lesson 08](module-06-databases/lessons/08-nosql-overview.md).*

**DOM (Document Object Model)** — The live, in-memory tree of objects a
browser builds from a page's HTML, which JavaScript reads and changes;
changing it is what makes a static page interactive, and the browser
automatically re-renders whenever it changes — comparable to a running
Unreal level's live scene graph vs. its saved `.umap` file. *Taught in:
[Module 03, Lesson 06](module-03-html-css-javascript/lessons/06-the-dom-and-events.md).*

**Domain name** — The human-readable name identifying a server (e.g.
`pokeapi.co`), resolved to an IP address via DNS; one part of a full URL.
*Taught in: [Module 02, Lesson 01](module-02-internet-and-web-fundamentals/lessons/01-networks-ip-addresses-and-dns.md).*

**Dunder method** — A method named with leading and trailing double
underscores (e.g. `__init__`, `__str__`, `__eq__`) that Python calls
automatically in response to a built-in operation like printing, comparing,
or looping. *Taught in: [Module 01, Lesson 05](module-01-python-properly/lessons/05-oop-classes-and-dunders.md).*

**Dynamic segment (route param)** — A portion of a React Router route's
`path` starting with `:` (e.g. `:id`) that matches any value at that
position and captures it by name, always as a string, via `useParams()`.
*Taught in: [Module 04, Lesson 08](module-04-react/lessons/08-react-router.md).*

**Dynamically typed** — Describes a language (like Python or JavaScript)
where a variable's type is determined by whatever value it currently holds
at runtime, rather than being fixed at compile time. *Taught in: [Module 01,
Lesson 01](module-01-python-properly/lessons/01-variables-types-and-control-flow.md)
and [Module 03, Lesson 05](module-03-html-css-javascript/lessons/05-javascript-fundamentals-and-the-event-loop.md).*

**Ed25519** — The current recommended algorithm for new SSH key pairs
(OpenSSH's own `ssh-keygen` default since version 9.5, October 2023),
chosen over RSA for its speed and small key size at an equivalent
security level. *Taught in: [Module 09, Lesson 02](module-09-linux-networking-servers/lessons/02-ssh-and-key-based-auth.md).*

**Encryption** — A *reversible* transformation: something locked with a
key can later be unlocked with that same (or a related) key to recover
the original content; the right tool when a system genuinely needs the
original data back later, unlike hashing, below, used for passwords.
*Taught in: [Module 07, Lesson 02](module-07-auth-security/lessons/02-password-hashing.md).*

**End-to-end test (E2E test)** — The top, smallest, slowest, most
realistic layer of the testing pyramid: driving an entire real system,
usually through the same interface a real user would (a real browser),
start to finish. *Taught in: [Module 08, Lesson 01](module-08-testing-and-quality/lessons/01-why-tests-and-the-testing-pyramid.md).*

**Engine (SQLAlchemy)** — The SQLAlchemy object that knows how to open and
pool real network connections to a database; an application typically
creates exactly one, at startup. *Taught in: [Module 06, Lesson 05](module-06-databases/lessons/05-orms-and-sqlalchemy-basics.md).*

**Environment variable** — A named piece of text data available to the
shell and every program it launches, functioning like a small set of
global settings (e.g. `HOME`, `PATH`). *Taught in: [Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Ephemeral port** — A temporary port (roughly 49152–65535) an operating
system automatically assigns for a short time whenever a program
initiates an outgoing connection, distinct from a well-known port a
server deliberately listens on. *Taught in: [Module 09, Lesson 04](module-09-linux-networking-servers/lessons/04-networking-ports-and-ips.md).*

**ES module** — JavaScript's standardized module system (`export`/
`import`), letting code be split across files with an explicit, enforced
public surface — comparable to Python's own `import` system, but with
non-exported names genuinely inaccessible rather than merely conventionally
private. *Taught in: [Module 03, Lesson 08](module-03-html-css-javascript/lessons/08-es6-plus-features-and-modules.md).*

**Event (JavaScript)** — Something the browser notifies your code about as
it happens — a click, a keystroke, a form submission — that a function
attached via `addEventListener` can react to. *Taught in: [Module 03,
Lesson 06](module-03-html-css-javascript/lessons/06-the-dom-and-events.md).*

**Event listener** — A function registered with
`addEventListener(eventType, handler)` to run automatically whenever a
specific event happens on a specific element. *Taught in: [Module 03,
Lesson 06](module-03-html-css-javascript/lessons/06-the-dom-and-events.md).*

**Event loop** — The single-threaded mechanism, at the heart of Python's
`asyncio`, that runs multiple coroutines by resuming each one when whatever
it was waiting on becomes ready, rather than executing them truly
simultaneously. *Taught in: [Module 01, Lesson 11](module-01-python-properly/lessons/11-async-await-fundamentals.md).*

**Event loop (JavaScript)** — The browser's own single-threaded scheduling
mechanism, built on the same "single thread, cooperative scheduling" idea
as Python's `asyncio` event loop above, but applied to keeping a user
interface responsive: slow operations (timers, network requests) are
handed off, and any pending callback only runs once the call stack is
completely empty. *Taught in: [Module 03, Lesson 05](module-03-html-css-javascript/lessons/05-javascript-fundamentals-and-the-event-loop.md).*

**Exception** — An object Python raises to signal that something went
wrong, immediately interrupting normal execution and propagating upward
until something catches it. *Taught in: [Module 01, Lesson 06](module-01-python-properly/lessons/06-error-handling.md).*

**Factory fixture** — A `pytest` fixture whose value is itself a
function, so a test can call it more than once, with different
arguments each time, rather than receiving one fixed, pre-built value.
*Taught in: [Module 08, Lesson 02](module-08-testing-and-quality/lessons/02-pytest-fundamentals-and-fixtures.md).*

**Fast-forward merge** — A merge where the target branch hadn't moved
since the branch being merged split off, so Git can just slide the
pointer forward with nothing to actually combine. *Taught in: [Module 00,
Lesson 04](module-00-developer-environment-and-tooling/lessons/04-git-branching-and-merging.md).*

**Fetch (`git fetch`)** — Downloads new commits from a remote without
merging them into your current branch (unlike `git pull`, which does
both). *Taught in: [Module 00, Lesson 05](module-00-developer-environment-and-tooling/lessons/05-github-and-pull-requests.md).*

**`fetch` (Fetch API)** — The built-in browser/JavaScript function for
making an HTTP request from code, returning a Promise that fulfills as
soon as response headers arrive — including for HTTP error status codes,
which is why `response.ok` must be checked explicitly rather than relying
on the Promise to reject. Not to be confused with `git fetch`, above.
*Taught in: [Module 03, Lesson 07](module-03-html-css-javascript/lessons/07-fetch-promises-and-async-await.md).*

**Firewall** — A checkpoint every network packet must pass before
reaching any program on a machine, deciding, per port, whether incoming
traffic is allowed at all; `ufw` (below) is this course's Ubuntu-
specific tool for configuring one. *Taught in: [Module 09, Lesson 05](module-09-linux-networking-servers/lessons/05-firewalls-with-ufw.md).*

**Fixture** — A `pytest` function, decorated with `@pytest.fixture`,
whose job is doing setup (and, via `yield`, cleanup) a test needs, made
available to any test simply by naming it as a parameter — `pytest`
resolves it automatically, the same dependency-injection idea (above)
FastAPI's own `Depends()` uses for routes. *Taught in: [Module 08, Lesson
02](module-08-testing-and-quality/lessons/02-pytest-fundamentals-and-fixtures.md).*

**Flex container** — An element with `display: flex` set on it, causing
its direct children to become flex items arranged along a single row or
column. *Taught in: [Module 03, Lesson 03](module-03-html-css-javascript/lessons/03-css-flexbox.md).*

**Flex item** — A direct child of a flex container, positionable and
sizable via properties like `flex-grow`, `flex-shrink`, and alignment
along the main/cross axes. *Taught in: [Module 03, Lesson 03](module-03-html-css-javascript/lessons/03-css-flexbox.md).*

**Flexbox** — A CSS layout mode for arranging a container's children along
a single row or column, with built-in control over spacing, alignment, and
how items grow/shrink to fill available space — comparable to a UMG
Horizontal/Vertical Box. *Taught in: [Module 03, Lesson 03](module-03-html-css-javascript/lessons/03-css-flexbox.md).*

**Floor division (`//`)** — Division that rounds its result down to the
nearest whole number, discarding the remainder. *Taught in: [Module 01,
Lesson 01](module-01-python-properly/lessons/01-variables-types-and-control-flow.md).*

**Formatter** — A tool that rewrites a source file's whitespace, quote
style, and line breaks into one consistent shape, with no opinion about
whether the code's actual logic is correct; this course uses `ruff
format` (Python) and `prettier` (JS/TS). *Taught in: [Module 08, Lesson
08](module-08-testing-and-quality/lessons/08-linters-and-formatters.md).*

**f-string** — A string literal prefixed with `f`, allowing Python
expressions inside `{curly braces}` to be evaluated and inserted directly
into the text. *Taught in: [Module 01, Lesson 01](module-01-python-properly/lessons/01-variables-types-and-control-flow.md).*

**`fr` unit** — A CSS Grid track-sizing unit meaning "one share of
whatever space remains" after fixed-size tracks are accounted for, directly
comparable to Flexbox's `flex-grow` ratio. *Taught in: [Module 03,
Lesson 04](module-03-html-css-javascript/lessons/04-css-grid-and-responsive-design.md).*

**Foreign key** — A column storing another table's primary key value,
creating a real, enforced reference between two rows instead of copying
data between them; the mechanism behind every table relationship. *Taught
in: [Module 06, Lesson 01](module-06-databases/lessons/01-why-a-database-and-the-relational-model.md).*

**Fragment** — JSX's `<>...</>` syntax for grouping multiple sibling
elements into one return value without adding a real wrapping element to
the page. *Taught in: [Module 04, Lesson 01](module-04-react/lessons/01-why-react-components-props-and-jsx.md).*

**Framework mode (React Router)** — React Router's full server-rendering
framework mode, effectively absorbing what used to be a separate project
(Remix); conceptually similar territory to Next.js. *Taught in: [Module 04,
Lesson 08](module-04-react/lessons/08-react-router.md).*

**Generator** — A function containing `yield` that, when called, returns a
paused generator object producing values one at a time on demand, rather
than running its body immediately or building a whole collection upfront.
*Taught in: [Module 01, Lesson 04](module-01-python-properly/lessons/04-comprehensions-generators-and-iterators.md).*

**Generator expression** — A comprehension written with `()` instead of
`[]`/`{}`, producing a lazy generator rather than building the full
collection immediately. *Taught in: [Module 01, Lesson 04](module-01-python-properly/lessons/04-comprehensions-generators-and-iterators.md).*

**GET (HTTP method)** — The HTTP method meaning "give me this resource,
don't change anything"; both safe and idempotent. *Taught in: [Module 02,
Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**Git** — A distributed version control program that tracks the history
of changes to files, letting you save checkpoints, roll back, and combine
changes from multiple sources. *Taught in: [Module 00, Lesson 00](module-00-developer-environment-and-tooling/lessons/00-setup.md)
and [Lesson 03](module-00-developer-environment-and-tooling/lessons/03-git-fundamentals.md).*

**Git Bash** — A terminal program bundled with Git for Windows that runs
the `bash` shell, giving Windows users Linux-style commands. *Taught in:
[Module 00, Lesson 00](module-00-developer-environment-and-tooling/lessons/00-setup.md).*

**Git Credential Manager (GCM)** — A tool bundled with Git for Windows
that handles authenticating you to services like GitHub (e.g. via a
browser login popup) so you don't have to manually manage credentials.
*Taught in: [Module 00, Lesson 00](module-00-developer-environment-and-tooling/lessons/00-setup.md).*

**`.gitignore`** — A plain text file, one pattern per line, listing files
Git should never track, even if they exist in the project folder. *Taught
in: [Module 00, Lesson 03](module-00-developer-environment-and-tooling/lessons/03-git-fundamentals.md).*

**GitHub** — A website that hosts Git repositories online and adds
collaboration features (Pull Requests, issues, etc.) on top of plain Git.
*Taught in: [Module 00, Lesson 00](module-00-developer-environment-and-tooling/lessons/00-setup.md)
and [Lesson 05](module-00-developer-environment-and-tooling/lessons/05-github-and-pull-requests.md).*

**GitHub CLI (`gh`)** — An official command-line tool for interacting with
GitHub (creating repos, opening PRs, etc.) without leaving the terminal.
*Taught in: [Module 00, Lesson 00](module-00-developer-environment-and-tooling/lessons/00-setup.md).*

**Glob / wildcard** — A pattern (e.g. `*.txt`) used by shell commands to
match multiple filenames at once. `*` means "match anything." *Taught in:
[Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Global keyword** — Inside a function, declares that assigning to a given
name should modify the module-level variable of that name rather than
creating a new local one. *Taught in: [Module 01, Lesson 02](module-01-python-properly/lessons/02-functions-and-scope.md).*

**GROUP BY** — A SQL clause that collapses every row sharing the same
value(s) in given column(s) into one summary row, meant to be used
alongside aggregate functions computing across each group. *Taught in:
[Module 06, Lesson 04](module-06-databases/lessons/04-joins-and-group-by.md).*

**Hashable** — Describes a value that can be run through a hash function
to produce a fixed lookup key, which is why only hashable (effectively
immutable) objects can be dict keys or set elements. *Taught in:
[Module 01, Lesson 03](module-01-python-properly/lessons/03-data-structures.md).*

**Hash table** — The underlying data structure behind Python's `dict` and
`set`, which uses a hash function to locate entries directly rather than
scanning them one by one, giving roughly constant-time lookups. *Taught
in: [Module 01, Lesson 03](module-01-python-properly/lessons/03-data-structures.md).*

**Hashing** — A one-way transformation: running data through a hash
function produces a fixed-size, scrambled result with no operation that
reverses it back to the original input — the right tool for a password,
since a system never actually needs the original value back, only "does
this new attempt match what's on file." Contrasted with encryption,
above. *Taught in: [Module 07, Lesson 02](module-07-auth-security/lessons/02-password-hashing.md).*

**HATEOAS (Hypermedia As The Engine Of Application State)** — The REST
sub-constraint that a response should include links guiding a client to
related/next actions (e.g. a `next` page link) rather than the client
constructing further URLs from prior knowledge alone; the constraint
most real-world "REST APIs" only partially satisfy. *Taught in:
[Module 02, Lesson 06](module-02-internet-and-web-fundamentals/lessons/06-rest-from-first-principles.md).*

**HEAD** — A special pointer in Git that tracks which branch (and
therefore which commit) you currently have checked out. *Taught in:
[Module 00, Lesson 04](module-00-developer-environment-and-tooling/lessons/04-git-branching-and-merging.md).*

**HEAD (HTTP method)** — The HTTP method identical to `GET` except the
server sends back only headers, never a body — useful for cheaply
checking whether a resource exists or how large it is. *Taught in:
[Module 02, Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**Header (HTTP header)** — A `Name: Value` line of metadata riding
alongside an HTTP request or response line's body, describing facts about
the message (format, size, caching rules, identity) rather than being the
main content itself. *Taught in: [Module 02, Lesson 04](module-02-internet-and-web-fundamentals/lessons/04-headers-cookies-and-statelessness.md).*

**Heredoc** — A shell syntax (`<< 'EOF' ... EOF`) for writing multiple
lines of text into a file directly from the command line, without an
editor. *Taught in: [Module 00, Lesson 03](module-00-developer-environment-and-tooling/lessons/03-git-fundamentals.md).*

**History API** — The browser's built-in `pushState`/`replaceState`/
`popstate` functions that let a script change the displayed URL and
history entries without triggering a real page navigation; what React
Router is built on top of. *Taught in: [Module 04, Lesson 08](module-04-react/lessons/08-react-router.md).*

**HMAC (Hash-based Message Authentication Code)** — A signature computed
over some data using a secret key, such that anyone holding the key can
verify it, but nobody lacking the key can forge a new, valid one for
different data; the exact mechanism behind a JWT's own signature (`HS256`
= HMAC using SHA-256). *Taught in: [Module 07, Lesson 04](module-07-auth-security/lessons/04-jwt-structure-in-depth.md).*

**Hook** — A specially-named function, starting with `use`, that lets a
component tap into React features like state or effects (e.g. `useState`,
`useEffect`). *Taught in: [Module 04, Lesson 02](module-04-react/lessons/02-state-and-the-rendering-model.md).*

**Hot Module Replacement (HMR)** — Vite's dev-server feature that pushes
just a changed file into an already-running page and updates it live,
instead of reloading the whole page from scratch. *Taught in: [Module 04,
Lesson 00](module-04-react/lessons/00-setup.md).*

**HTML (HyperText Markup Language)** — A markup language (not a
programming language — no variables, loops, or logic) that wraps plain
text in tags describing what each piece of content *is*, structurally,
leaving how it looks to CSS and how it behaves to JavaScript. *Taught in:
[Module 03, Lesson 01](module-03-html-css-javascript/lessons/01-html-structure-forms-and-accessibility.md).*

**HTTP (Hypertext Transfer Protocol)** — The application-level protocol,
built on TCP, that structures a request (method, path, headers, optional
body) and a response (status, headers, body) exchanged between a client
and a server; currently and authoritatively specified by RFC 9110.
*Taught in: [Module 02, Lesson 02](module-02-internet-and-web-fundamentals/lessons/02-tcp-tls-and-the-request-response-journey.md)
and [Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**HTTP method** — The "verb" of an HTTP request line, stating what the
client is asking the server to do (e.g. `GET`, `POST`); each method has
defined "safe" and "idempotent" properties. *Taught in: [Module 02,
Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**HTTPS** — Plain HTTP sent over a connection TLS has already encrypted;
not a separate protocol or request/response format, just HTTP wrapped in
TLS, conventionally on port 443. *Taught in: [Module 02, Lesson 02](module-02-internet-and-web-fundamentals/lessons/02-tcp-tls-and-the-request-response-journey.md).*

**Hydration** — The process where React attaches event handlers and live
state to already-present, server-rendered HTML, making static markup
interactive without discarding and re-building it. *Taught in: [Module 04,
Lesson 09](module-04-react/lessons/09-nextjs-ssr-ssg-csr-concepts.md).*

**Idempotent** — A property of an HTTP method meaning that making the
exact same request multiple times has the same effect as making it once
(e.g. `PUT`, `DELETE`, `GET`) — contrasted with methods like `POST`, where
repeating a request can create additional side effects each time. *Taught
in: [Module 02, Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**IDOR (Insecure Direct Object Reference)** — A vulnerability where a
system correctly denies access to a resource's *contents* but
accidentally still reveals, via a different response, that the resource
*exists* (e.g. returning `403` instead of `404` for someone else's
quest); avoided in QuestLog by combining an id check and an ownership
check into one database query, rather than two separate steps. *Taught
in: [Module 07, Lesson 07](module-07-auth-security/lessons/07-protecting-routes-with-dependencies.md).*

**Incremental Static Regeneration (ISR)** — A Next.js rendering strategy
between SSG and SSR: a page is statically generated but automatically
regenerated in the background after a configured time interval, trading
perfect freshness for cheap serving most of the time. *Taught in:
[Module 04, Lesson 09](module-04-react/lessons/09-nextjs-ssr-ssg-csr-concepts.md).*

**Index (database)** — A separate, sorted data structure (typically a
B-tree) a database maintains alongside a table so it can find matching
rows directly instead of scanning every row; speeds up reads on the
indexed column at the cost of slightly slower writes to that table.
*Taught in: [Module 06, Lesson 02](module-06-databases/lessons/02-indexes-transactions-and-acid.md).*

**Index route** — In React Router, the child route that renders when its
parent's path matches exactly, with no further URL segment. *Taught in:
[Module 04, Lesson 08](module-04-react/lessons/08-react-router.md).*

**Inheritance** — Defining a class based on another class, automatically
gaining its attributes/methods and optionally overriding them; expresses
an "is-a" relationship. *Taught in: [Module 01, Lesson 05](module-01-python-properly/lessons/05-oop-classes-and-dunders.md).*

**`__init__.py`** — A (often empty) file that marks a folder as an
importable Python package, and can optionally re-export names from its
submodules. *Taught in: [Module 01, Lesson 07](module-01-python-properly/lessons/07-modules-packages-and-virtual-environments.md).*

**Instance** — One concrete object built from a class's blueprint. *Taught
in: [Module 01, Lesson 05](module-01-python-properly/lessons/05-oop-classes-and-dunders.md).*

**Instance attribute** — A value set on `self` (typically inside
`__init__`), belonging to one specific instance rather than being shared
across all instances of the class. *Taught in: [Module 01, Lesson 05](module-01-python-properly/lessons/05-oop-classes-and-dunders.md).*

**Integration test** — A test that exercises several real pieces of a
system working together (e.g. real routing, real dependency injection,
and a real database), one layer up the testing pyramid from a unit test
(below). *Taught in: [Module 08, Lesson 01](module-08-testing-and-quality/lessons/01-why-tests-and-the-testing-pyramid.md).*

**Interface (TypeScript)** — A TypeScript declaration describing the
required shape of an object — which properties it must have and their
types — checked by `tsc` at compile time and erased entirely from the
compiled JavaScript output; comparable to a C++ `struct`'s member
declarations or a Python type-hinted dict shape. *Taught in: [Module 03,
Lesson 09](module-03-html-css-javascript/lessons/09-typescript-introduction.md).*

**Interpreter (Python interpreter)** — The program that reads a `.py`
file and executes it directly, line by line, with no separate compile
step. *Taught in: [Module 01, Lesson 00](module-01-python-properly/lessons/00-setup.md).*

**IP address** — A unique numeric address (e.g. `104.26.14.6`) identifying
a device on a network, so packets know where to be delivered; can be
public (reachable from the whole Internet) or private (only meaningful
inside one local network). *Taught in: [Module 02, Lesson 01](module-02-internet-and-web-fundamentals/lessons/01-networks-ip-addresses-and-dns.md).*

**Iterable** — Any object that knows how to produce an iterator (via
`__iter__`), and can therefore be looped over with `for`. *Taught in:
[Module 01, Lesson 04](module-01-python-properly/lessons/04-comprehensions-generators-and-iterators.md).*

**Iterator** — An object that hands out one item at a time via
`__next__`, remembering its position, until it raises `StopIteration`.
*Taught in: [Module 01, Lesson 04](module-01-python-properly/lessons/04-comprehensions-generators-and-iterators.md).*

**JOIN** — A SQL clause combining rows from two tables based on a matching
condition (typically a foreign key); an `INNER JOIN` (plain `JOIN`) only
returns rows with a match on both sides, while a `LEFT JOIN` (below) keeps
every row from the left-hand table regardless. *Taught in: [Module 06,
Lesson 04](module-06-databases/lessons/04-joins-and-group-by.md).*

**journalctl** — The command that reads logs `systemd` automatically
captured from every service it manages, filterable to one unit with
`-u <name>` and followable live with `-f`. *Taught in: [Module 09, Lesson 03](module-09-linux-networking-servers/lessons/03-systemd-and-services.md).*

**jsdom** — A plain-JavaScript implementation of a browser's DOM that
runs inside plain Node.js, with no actual browser window at all, letting
a frontend component test render and query real-seeming HTML. *Taught
in: [Module 08, Lesson 00](module-08-testing-and-quality/lessons/00-setup.md).*

**JSON** — A plain-text data format (JavaScript Object Notation) mapping
almost directly onto Python's `dict`/`list`/`str`/`int`/`float`/`bool`/`None`,
used constantly for file persistence and for data sent over the web.
*Taught in: [Module 01, Lesson 08](module-01-python-properly/lessons/08-file-io-and-json.md)
and [Module 02, Lesson 05](module-02-internet-and-web-fundamentals/lessons/05-clients-servers-apis-and-json.md)
(its full grammar and why it displaced XML as the web's default format).*

**JSX** — An XML-like syntax extension to JavaScript/TypeScript that
compiles to plain function calls (`jsx`/`createElement`) producing
lightweight UI-description objects; it is not HTML, and no browser
understands it natively. *Taught in: [Module 04, Lesson 01](module-04-react/lessons/01-why-react-components-props-and-jsx.md).*

**JWT (JSON Web Token)** — A plain text credential made of three
base64url-encoded, dot-separated parts — a header (naming the signing
algorithm), a payload (the actual claims, above), and a signature (an
HMAC proving the first two haven't been tampered with) — readable by
anyone holding it, but forgeable by nobody lacking the signing secret;
**signed, not encrypted**, since reading the payload requires no key at
all. *Taught in: [Module 07, Lesson 04](module-07-auth-security/lessons/04-jwt-structure-in-depth.md).*

**Key-value store** — A NoSQL database (e.g. Redis) offering simple,
extremely fast lookups of a value by an exact key, trading away
relational features (joins, filtering by arbitrary columns) for raw
speed; commonly used as a cache in front of a relational database.
*Taught in: [Module 06, Lesson 08](module-06-databases/lessons/08-nosql-overview.md).*

**Keyword argument** — An argument passed to a function by explicitly
naming its parameter (e.g. `greet(name="Aria")`) rather than by position.
*Taught in: [Module 01, Lesson 02](module-01-python-properly/lessons/02-functions-and-scope.md).*

**`**kwargs`** — A parameter prefixed with `**` that collects any number
of extra keyword arguments a function is called with into a dict. *Taught
in: [Module 01, Lesson 02](module-01-python-properly/lessons/02-functions-and-scope.md).*

**Label (HTML)** — A `<label>` element paired with a form field via
matching `for`/`id` attributes, making the field's purpose available to
screen readers and letting a click on the label's text focus/activate the
field itself. *Taught in: [Module 03, Lesson 01](module-03-html-css-javascript/lessons/01-html-structure-forms-and-accessibility.md).*

**Layer (image layer)** — One instruction's worth of filesystem change in
a Dockerfile, stacked on top of the layers before it to form a complete
container image; Docker caches each layer independently and reuses a
cached layer unchanged whenever the instruction that produced it, and
everything it depends on, hasn't changed since the last build. *Taught
in: [Module 10, Lesson 02](module-10-docker-and-containers/lessons/02-dockerfiles-layers-and-caching.md).*

**Layer caching** — Docker's build-speed optimization built on image
layers: ordering a Dockerfile so files that change rarely (like
`requirements.txt`) are copied and installed before files that change
constantly (like application source) means an ordinary code edit only
ever invalidates and rebuilds the cheap, fast layers below it, not the
expensive dependency-install layers above. *Taught in: [Module 10, Lesson 02](module-10-docker-and-containers/lessons/02-dockerfiles-layers-and-caching.md).*

**LEFT JOIN** — A SQL `JOIN` variant that keeps every row from the
left-hand table even when there's no match on the right (filling
unmatched columns with `NULL`), unlike a plain `JOIN`, which would omit
that row entirely. *Taught in: [Module 06, Lesson 04](module-06-databases/lessons/04-joins-and-group-by.md).*

**Lifting state up** — Moving state that two or more sibling components
need to share into their common parent, which passes the value down as
props and update functions down as props. *Taught in: [Module 04,
Lesson 05](module-04-react/lessons/05-forms-controlled-components-and-lifting-state.md).*

**Linter** — A tool that reads source code without running it and
reports real bugs, suspicious patterns, and style problems, some
auto-fixable; this course uses `ruff` (Python) and `oxlint` (JS/TS, from
Module 04). *Taught in: [Module 08, Lesson 08](module-08-testing-and-quality/lessons/08-linters-and-formatters.md).*

**List** — An ordered, mutable sequence of values, allowing duplicates.
*Taught in: [Module 01, Lesson 03](module-01-python-properly/lessons/03-data-structures.md).*

**List comprehension** — A compact expression, `[transform for item in
iterable if condition]`, that builds a new list from an existing iterable
in one line. *Taught in: [Module 01, Lesson 04](module-01-python-properly/lessons/04-comprehensions-generators-and-iterators.md).*

**Literal type** — A Pydantic/Python type hint meaning "this value must be
*exactly* one of these specific values" (e.g. `Literal["low", "medium",
"high"]`), rejecting any other value outright, including ones of the
right underlying type — distinct from a plain `str`, which accepts any
string at all. Comparable to a TypeScript string-literal union (e.g.
`"low" | "medium" | "high"`), applied on the Python/Pydantic side. *Taught
in: [Module 05, Lesson 03](module-05-backend-fastapi/lessons/03-request-bodies-and-pydantic-validation.md).*

**Load balancer** — Something that sits in front of multiple identical
copies of a backend process and distributes incoming requests across
them; mechanically the same idea as a reverse proxy (below), just aimed
at several equivalent backends instead of one. *Taught in: [Module 09, Lesson 06](module-09-linux-networking-servers/lessons/06-nginx-and-reverse-proxies.md).*

**Localhost** — The special address (`127.0.0.1`) that always means "this
same machine," with no real network, router, or ISP involved. *Taught in:
[Module 02, Lesson 01](module-02-internet-and-web-fundamentals/lessons/01-networks-ip-addresses-and-dns.md).*

**Location header** — An HTTP response header, sent alongside a 3xx
redirect status, stating the URL a client should go to next. *Taught in:
[Module 02, Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**Main axis** — In a Flexbox container, the axis `flex-direction` points
along (horizontal for `row`, vertical for `column`); controlled primarily
by `justify-content`. *Taught in: [Module 03, Lesson 03](module-03-html-css-javascript/lessons/03-css-flexbox.md).*

**Markup language** — A language (like HTML) with no variables, loops, or
logic, used to wrap plain text in tags that describe what each piece of
content *is*, rather than to compute anything. *Taught in: [Module 03,
Lesson 01](module-03-html-css-javascript/lessons/01-html-structure-forms-and-accessibility.md).*

**Media query** — A CSS block (`@media (...) { ... }`) whose rules only
apply when a stated condition — most commonly a minimum/maximum viewport
width — is true. *Taught in: [Module 03, Lesson 04](module-03-html-css-javascript/lessons/04-css-grid-and-responsive-design.md).*

**Merge** — Combining the changes introduced on one Git branch into
another. *Taught in: [Module 00, Lesson 04](module-00-developer-environment-and-tooling/lessons/04-git-branching-and-merging.md).*

**Merge commit** — A commit with two parent commits, created when merging
two branches whose histories had genuinely diverged (as opposed to a
fast-forward merge). *Taught in: [Module 00, Lesson 04](module-00-developer-environment-and-tooling/lessons/04-git-branching-and-merging.md).*

**Merge conflict** — What happens when the same lines of the same file
were changed differently on two branches being merged, and Git can't
automatically decide which version to keep. *Taught in: [Module 00,
Lesson 04](module-00-developer-environment-and-tooling/lessons/04-git-branching-and-merging.md).*

**Migration** — A small, version-controlled file describing one specific
database schema change, applied (and ideally un-applied) consistently
across every environment, the way a Git commit is a small, ordered,
reproducible record of a code change; Alembic (above) is this course's
migration tool. *Taught in: [Module 06, Lesson 07](module-06-databases/lessons/07-alembic-migrations.md).*

**`mkdir`** — Shell command to create a new directory/folder. *Taught in:
[Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Middleware** — Code that runs on every request/response passing through
a web application, unconditionally, before/after routing decides which
specific route applies — comparable to a component in an Unreal Actor's
tick chain that every actor passes through, rather than something a
specific piece of gameplay code opts into (contrast with a dependency,
above, which a specific route chooses to use). *Taught in: [Module 05,
Lesson 05](module-05-backend-fastapi/lessons/05-middleware.md).*

**Mobile-first (responsive design)** — A responsive-design convention
where the unconditional, default CSS describes the narrowest (typically
mobile) layout, with `min-width` media queries adding more elaborate
layouts as the viewport widens. *Taught in: [Module 03, Lesson 04](module-03-html-css-javascript/lessons/04-css-grid-and-responsive-design.md).*

**Mock** — A fake stand-in object, used in a test, that records how it
was called so the test can assert on that history afterward, and can be
told in advance what to return; one specific kind of test double
(below). *Taught in: [Module 08, Lesson 03](module-08-testing-and-quality/lessons/03-parametrize-and-mocking.md).*

**Module** — A single Python file, importable by its filename (minus
`.py`) into other files. *Taught in: [Module 01, Lesson 07](module-01-python-properly/lessons/07-modules-packages-and-virtual-environments.md).*

**Module search path (`sys.path`)** — The ordered list of folders Python
searches, stopping at the first match, when resolving an `import`
statement. *Taught in: [Module 01, Lesson 07](module-01-python-properly/lessons/07-modules-packages-and-virtual-environments.md).*

**Monkeypatch** — `pytest`'s own built-in fixture for temporarily
replacing one attribute, function, or environment variable for the
duration of a single test, automatically restored afterward; a simpler
alternative to `unittest.mock.patch` (see Mock, above) for
straightforward substitutions. *Taught in: [Module 08, Lesson 03](module-08-testing-and-quality/lessons/03-parametrize-and-mocking.md).*

**Mount / Unmount** — The moment a component first appears in the page
(mount) or is removed from it (unmount); an empty `useEffect` dependency
array (`[]`) means "run only on mount." *Taught in: [Module 04, Lesson 03](module-04-react/lessons/03-useeffect-the-dependency-array-in-depth.md).*

**Multi-stage build** — A Dockerfile with more than one `FROM` instruction,
each starting a fresh, separate build "stage"; later stages can selectively
`COPY --from=<earlier stage>` only the specific files they need, leaving
everything else that earlier stage produced (a compiler, a full npm
`node_modules`, pip's own cache) behind. This is how QuestLog's frontend
image ends up as plain Nginx serving static files, with no Node.js runtime
inside it at all, despite needing a full Node/npm toolchain to actually
build those files. *Taught in: [Module 10, Lesson 03](module-10-docker-and-containers/lessons/03-multi-stage-builds-and-image-size.md).*

**Mutable default argument bug** — A common Python bug where a mutable
default argument value (like `[]`) is created only once, when the
function is defined, and is then silently shared and accumulated across
every call that doesn't supply its own value. *Taught in: [Module 01,
Lesson 02](module-01-python-properly/lessons/02-functions-and-scope.md).*

**Named volume** — A Docker-managed storage location, identified by name
(e.g. `questlog_pgdata`), that persists a container's data independently
of the container's own lifecycle — deleting and recreating the container
that uses it (the normal result of `docker compose up --build`) leaves the
volume, and everything stored in it, untouched; only an explicit
`docker compose down -v` or `docker volume rm` removes it. The game-dev
analogy: a volume is like an external save-game file living outside the
build itself, so wiping and reinstalling the build doesn't lose player
progress. *Taught in: [Module 10, Lesson 05](module-10-docker-and-containers/lessons/05-docker-volumes-and-persistence.md).*

**Namespace (Linux)** — A Linux kernel feature that gives a process its
own, isolated view of some global system resource — its own process list,
its own network interfaces, its own filesystem mount points — so it can't
see, and doesn't know about, the equivalent resources any other process
(or the host itself) has. Alongside cgroups, this is the other kernel
feature that a container fundamentally *is*: an ordinary process, made to
believe it's alone on the machine. *Taught in: [Module 10, Lesson 01](module-10-docker-and-containers/lessons/01-containers-vs-vms-and-your-first-container.md).*

**NAT (Network Address Translation)** — The mechanism a router uses to
let many devices share one public IP address, rewriting outgoing packets
and routing replies back to the right internal device; incidentally
means a device behind NAT isn't directly reachable by an unsolicited
inbound connection, unlike a VPS. *Taught in: [Module 09, Lesson 04](module-09-linux-networking-servers/lessons/04-networking-ports-and-ips.md).*

**Node.js** — A standalone program that runs JavaScript (and, via
TypeScript's compiler, TypeScript) directly on a machine, outside any
browser, by packaging the same kind of JavaScript engine a browser uses
internally. *Taught in: [Module 03, Lesson 00](module-03-html-css-javascript/lessons/00-setup.md).*

**Normalization** — Organizing a database schema so every real-world fact
is stored in exactly one place, preventing update/insertion/deletion
anomalies caused by the same fact being duplicated across rows. *Taught
in: [Module 06, Lesson 09](module-06-databases/lessons/09-normalization-and-schema-design.md).*

**NoSQL** — An umbrella term for databases not structured as fixed-schema
tables of rows, covering several distinct designs including document
stores and key-value stores (both above/below), unified mainly by what
they're not. *Taught in: [Module 06, Lesson 08](module-06-databases/lessons/08-nosql-overview.md).*

**npm (Node Package Manager)** — Node.js's package manager, bundled with
every Node.js install, used to download reusable JavaScript/TypeScript
packages into a project's own `node_modules/` folder and to record them in
`package.json`. *Taught in: [Module 03, Lesson 00](module-03-html-css-javascript/lessons/00-setup.md).*

**npx** — A helper bundled with npm that runs a command-line tool (like
`tsc`) from the current project's own `node_modules/.bin/` folder, without
needing that tool installed globally. *Taught in: [Module 03, Lesson 00](module-03-html-css-javascript/lessons/00-setup.md).*

**Nullish coalescing (`??`)** — A JavaScript operator that supplies a
default value only when its left-hand side is specifically `null` or
`undefined`, correctly leaving other falsy values (like `0` or `""`)
untouched, unlike `||`. *Taught in: [Module 03, Lesson 08](module-03-html-css-javascript/lessons/08-es6-plus-features-and-modules.md).*

**OAuth2** — An **authorization** framework (not, strictly, an
authentication protocol) for letting one application access resources on
another's behalf without ever handling the resource owner's real
password; the pattern behind every "Login with Google/GitHub/etc."
button. QuestLog does not implement third-party OAuth2 at all — its own
login endpoint just borrows the shape (and FastAPI's OAuth2-named
security utilities) of one specific, narrower OAuth2 grant. *Taught in:
[Module 07, Lesson 05](module-07-auth-security/lessons/05-oauth2-conceptual.md).*

**OAuth2PasswordBearer** — A FastAPI security scheme that reads the
`Authorization` header off an incoming request and extracts a
`Bearer <token>` value, raising a `401` itself if that header is missing
entirely; it does not check whether the extracted token is genuine —
that verification is a separate dependency's job. *Taught in:
[Module 07, Lesson 07](module-07-auth-security/lessons/07-protecting-routes-with-dependencies.md).*

**OpenAPI** — A specification (not a tool or a page) for describing, in a
structured JSON/YAML document, everything about an HTTP API — every
route, every parameter, every possible response shape and status code.
FastAPI generates a valid OpenAPI document automatically from a project's
own type hints and Pydantic models; Swagger UI and ReDoc (below) are two
separate tools that both read the same document and render it
differently. *Taught in: [Module 05, Lesson 07](module-05-backend-fastapi/lessons/07-auto-docs-and-openapi.md).*

**Optional chaining (`?.`)** — A JavaScript operator that safely reads a
nested property, evaluating to `undefined` instead of throwing if any link
in the chain is `null`/`undefined`. *Taught in: [Module 03, Lesson 08](module-03-html-css-javascript/lessons/08-es6-plus-features-and-modules.md).*

**OPTIONS (HTTP method)** — The HTTP method meaning "tell me what methods
are allowed at this URL, without doing any of them"; used by browsers
automatically as a CORS "preflight" request. *Taught in: [Module 02,
Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**`origin`** — The conventional name given to a Git repository's primary
remote. *Taught in: [Module 00, Lesson 05](module-00-developer-environment-and-tooling/lessons/05-github-and-pull-requests.md).*

**Origin** — The exact combination of scheme, host, and port a URL uses
(e.g. `http://localhost:5173`); two URLs share an origin only if all
three match exactly, which is why QuestLog's frontend and backend, both
on `localhost`, still count as two different origins. *Taught in:
[Module 07, Lesson 10](module-07-auth-security/lessons/10-cors-in-depth.md).*

**ORM (Object-Relational Mapper)** — A library (e.g. SQLAlchemy) that maps
database rows to Python objects and tables to Python classes, so queries
can be written as type-checkable Python expressions instead of raw SQL
strings. *Taught in: [Module 06, Lesson 05](module-06-databases/lessons/05-orms-and-sqlalchemy-basics.md).*

**Package** — A folder of related modules, marked importable as one unit
by an `__init__.py` file. *Taught in: [Module 01, Lesson 07](module-01-python-properly/lessons/07-modules-packages-and-virtual-environments.md).*

**`package.json`** — A file at the root of a Node.js project recording its
name, version, dependencies/dev dependencies, and scripts, so the same
project setup can be reproduced elsewhere with `npm install` — the
JavaScript ecosystem's equivalent of Python's `requirements.txt`. *Taught
in: [Module 03, Lesson 00](module-03-html-css-javascript/lessons/00-setup.md).*

**Package manager** — A tool that installs, tracks, and removes software,
scoped either to one project (`pip`, `npm`) or to an entire machine
(`apt`, above). *Taught in: [Module 09, Lesson 01](module-09-linux-networking-servers/lessons/01-linux-processes-and-permissions.md).*

**Parameterized query** — A query sent to a database with its SQL
structure and its actual values kept in two genuinely separate places at
the wire-protocol level (a "prepared statement"), so a value can never be
mis-treated as part of the query's own syntax; the mechanism that makes
SQLAlchemy's query-building API safe from SQL injection by default.
*Taught in: [Module 07, Lesson 08](module-07-auth-security/lessons/08-sql-injection-and-orm-safety.md).*

**Parametrize** — `@pytest.mark.parametrize`, a decorator that runs one
test function multiple times, once per supplied set of inputs, with each
run reported as its own, separately pass/fail-able test. *Taught in:
[Module 08, Lesson 03](module-08-testing-and-quality/lessons/03-parametrize-and-mocking.md).*

**Partial Prerendering (PPR)** — A Next.js rendering approach (introduced
in Next.js 15) that mixes a static shell with dynamic, per-request parts
streamed in afterward, on the same page. *Taught in: [Module 04, Lesson 09](module-04-react/lessons/09-nextjs-ssr-ssg-csr-concepts.md).*

**PATCH (HTTP method)** — The HTTP method meaning "apply a partial update
to this resource"; not guaranteed idempotent by contract, unlike `PUT`,
even though many real implementations happen to behave that way. *Taught
in: [Module 02, Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**PATH** — An environment variable listing folders the shell searches, in
order, to find the program matching a typed command name. The source of
almost every "command not found" error. *Taught in: [Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Path parameter** — A piece of a route's URL *path itself* that stands in
for a specific value (e.g. `{quest_id}` in `/quests/{quest_id}`), matched
by name to a function parameter and automatically converted to that
parameter's declared type; comparable to a React Router dynamic segment
(`:id`), the same idea applied server-side. Used for identifying *which*
specific resource a request is about, contrasted with a query parameter
(below), used for optional filters/modifiers. *Taught in: [Module 05,
Lesson 02](module-05-backend-fastapi/lessons/02-path-and-query-parameters.md).*

**Permissions (Unix)** — The `rwx` (read/write/execute) rules attached to
every file and directory, separately for its owner, its group, and
everyone else, checked by the kernel on every access — displayed by
`ls -l` as a 10-character string like `-rw-r--r--`. *Taught in: [Module 09, Lesson 01](module-09-linux-networking-servers/lessons/01-linux-processes-and-permissions.md).*

**PID (Process ID)** — A unique number the kernel assigns to a process
the moment it starts; no two processes running at the same time ever
share one. *Taught in: [Module 09, Lesson 01](module-09-linux-networking-servers/lessons/01-linux-processes-and-permissions.md).*

**pip** — Python's standard package installer, used to download and
install packages into the currently active environment, typically driven
by a `requirements.txt` file. *Taught in: [Module 01, Lesson 00](module-01-python-properly/lessons/00-setup.md).*

**Pipe (`|`)** — Shell syntax that feeds one command's output directly
into the next command's input. *Taught in: [Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Plugin (Vite)** — A piece of code that hooks into Vite's build process
to add a capability Vite doesn't have on its own (e.g. `@vitejs/plugin-react`
for JSX, `@tailwindcss/vite` for Tailwind). *Taught in: [Module 04,
Lesson 00](module-04-react/lessons/00-setup.md).*

**Port** — A number (0–65535) identifying a specific running program
("door") on a machine; an IP address plus a port together fully specify
which program on which machine to reach. *Taught in: [Module 02, Lesson 01](module-02-internet-and-web-fundamentals/lessons/01-networks-ip-addresses-and-dns.md).*

**Port publishing (Docker)** — Explicitly mapping a container's internal
port to a port on the host machine (`docker-compose.yml`'s
`"8080:80"` syntax, host:container), the only way traffic from outside
Docker's own private network can reach a container at all; a
Dockerfile's `EXPOSE` instruction, by contrast, is documentation only and
publishes nothing by itself. *Taught in: [Module 10, Lesson 04](module-10-docker-and-containers/lessons/04-docker-networking.md).*

**POST (HTTP method)** — The HTTP method meaning "here's data, do
something with it," typically creating a new resource; neither safe nor
idempotent by default. *Taught in: [Module 02, Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**PostgreSQL** — The relational database this course uses, a standalone
server program that listens on a network port and manages data stored
permanently on disk, queried via SQL. *Taught in: [Module 06, Lesson 00](module-06-databases/lessons/00-setup.md).*

**Pre-commit hook** — A script that runs automatically at the moment
right after `git commit` is typed but before the commit is actually
created, able to inspect and refuse what's about to be committed;
**"pre-commit"** is also the name of a specific Python framework
(installed via `pip`) that manages a whole list of such hooks from one
`.pre-commit-config.yaml` file. *Taught in: [Module 08, Lesson 09](module-08-testing-and-quality/lessons/09-pre-commit-hooks.md).*

**Preflight request** — A separate `OPTIONS` request a browser
automatically sends *before* a non-"simple" cross-origin request (e.g.
one with a `Content-Type: application/json` or `Authorization` header —
every real QuestLog API call), asking whether the real request would be
allowed, before actually sending it. *Taught in: [Module 07, Lesson 10](module-07-auth-security/lessons/10-cors-in-depth.md).*

**Primary key** — A column (or set of columns) guaranteed unique across
every row in a table, used to unambiguously identify one specific row.
*Taught in: [Module 06, Lesson 01](module-06-databases/lessons/01-why-a-database-and-the-relational-model.md).*

**Principal** — The general term for an identified entity making a
request — usually a user, sometimes another service; every authenticated
QuestLog request resolves down to exactly one principal, a row in the
`users` table. *Taught in: [Module 07, Lesson 01](module-07-auth-security/lessons/01-authentication-vs-authorization.md).*

**Private IP address** — An IP address (e.g. `192.168.1.42`) reserved for
use only inside one local network, meaningless if used from any other
network. *Taught in: [Module 02, Lesson 01](module-02-internet-and-web-fundamentals/lessons/01-networks-ip-addresses-and-dns.md).*

**Process** — One specific, currently-executing instance of a running
program, with its own private memory and current state, completely
separate from the program's file on disk; inspected with `ps`/`top` and
identified by its PID. *Taught in: [Module 09, Lesson 01](module-09-linux-networking-servers/lessons/01-linux-processes-and-permissions.md).*

**Programmatic navigation** — Changing the current URL from code (via
React Router's `useNavigate()`) rather than as a direct response to a
`<Link>` click — e.g. redirecting after a form successfully submits.
*Taught in: [Module 04, Lesson 08](module-04-react/lessons/08-react-router.md).*

**Promise (JavaScript)** — A JavaScript object representing a value that
isn't ready yet, starting in a `pending` state and settling exactly once
into either `fulfilled` (with a value) or `rejected` (with a reason);
`fetch` and other asynchronous browser APIs return Promises, and
`async`/`await` (JavaScript) is a second, more convenient syntax for
working with them — roughly analogous in role to a Python coroutine,
though a distinct kind of object. *Taught in: [Module 03, Lesson 07](module-03-html-css-javascript/lessons/07-fetch-promises-and-async-await.md).*

**Prop** — A read-only input passed to a component from its parent,
configuring one instance without letting the component itself reassign or
mutate it — comparable to a Blueprint's exposed construction-script
variables. *Taught in: [Module 04, Lesson 01](module-04-react/lessons/01-why-react-components-props-and-jsx.md).*

**Prop drilling** — Passing a prop down through one or more intermediate
components solely because something further below needs it, not because
those intermediate components use it themselves; the specific pain
Context (React) exists to remove. *Taught in: [Module 04, Lesson 06](module-04-react/lessons/06-context.md).*

**Provider** — The `<SomeContext.Provider value={...}>` component that
makes a value available to everything rendered inside it, at any depth.
*Taught in: [Module 04, Lesson 06](module-04-react/lessons/06-context.md).*

**Public IP address** — An IP address reachable from anywhere on the
internet, assigned to a real server like a VPS; contrasted with a
private IP address, above, meaningful only inside one local network.
*Taught in: [Module 09, Lesson 04](module-09-linux-networking-servers/lessons/04-networking-ports-and-ips.md).*

**Pydantic model** — A Python class inheriting from Pydantic's `BaseModel`,
describing a data shape as type-hinted class attributes; simultaneously a
description of what's expected (feeding OpenAPI, above), the real code
that validates incoming data against that shape, and a real Python object
a route function can then use directly. *Taught in: [Module 05, Lesson 03](module-05-backend-fastapi/lessons/03-request-bodies-and-pydantic-validation.md).*

**Pull (`git pull`)** — Downloads new commits from a remote and merges
them into your current branch in one step (fetch + merge). *Taught in:
[Module 00, Lesson 05](module-00-developer-environment-and-tooling/lessons/05-github-and-pull-requests.md).*

**Pull Request (PR)** — A GitHub feature that wraps a proposed merge in a
reviewable format: "please review this branch's diff, and if it looks
good, merge it." *Taught in: [Module 00, Lesson 05](module-00-developer-environment-and-tooling/lessons/05-github-and-pull-requests.md).*

**Push (`git push`)** — Uploads local commits to a remote repository.
*Taught in: [Module 00, Lesson 05](module-00-developer-environment-and-tooling/lessons/05-github-and-pull-requests.md).*

**PUT (HTTP method)** — The HTTP method meaning "replace this exact
resource entirely with what I'm sending"; idempotent by contract, since
repeating it leaves the resource in the same end state. *Taught in:
[Module 02, Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**`pwd`** — Shell command that prints your current working directory
("print working directory"). *Taught in: [Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**py launcher** — A separate program bundled with the python.org Windows
installer that finds and runs a specific installed Python version
regardless of `PATH`, used as `py` (optionally with a version like
`py -3.14`). *Taught in: [Module 01, Lesson 00](module-01-python-properly/lessons/00-setup.md).*

**pydantic-settings** — A separate package (since Pydantic v2 split
settings out of core Pydantic) providing `BaseSettings`, a typed way to
read configuration from environment variables and a `.env` file, making a
missing required value (like a secret key) a loud startup failure instead
of a silent runtime bug. *Taught in: [Module 07, Lesson 00](module-07-auth-security/lessons/00-setup.md).*

**PyJWT** — The JWT library this course uses (FastAPI's own
currently-recommended choice, replacing the now-abandoned `python-jose`),
providing `jwt.encode`/`jwt.decode` for creating and verifying signed
tokens. *Taught in: [Module 07, Lesson 00](module-07-auth-security/lessons/00-setup.md)
and [Lesson 04](module-07-auth-security/lessons/04-jwt-structure-in-depth.md).*

**Query parameter (query string)** — Optional `key=value` pairs appended
to a URL after a `?` (joined by `&` if more than one), commonly used for
filtering, sorting, or paging through results without needing a different
path for every combination. *Taught in: [Module 02, Lesson 05](module-02-internet-and-web-fundamentals/lessons/05-clients-servers-apis-and-json.md).*

**Rainbow table** — A precomputed lookup table mapping common passwords
to their hashes under one specific, unsalted hash function, letting an
attacker instantly reverse any database using that same function;
defeated entirely by a fresh, random salt (below) per password. *Taught
in: [Module 07, Lesson 02](module-07-auth-security/lessons/02-password-hashing.md).*

**Rate limiting** — Restricting how many requests a single client may
make in a given time window, to blunt brute-force login attempts and
simple overload; often implemented outside an application's own code
entirely, at a reverse proxy or load balancer. QuestLog does not
implement this itself — a stated, known gap, not a hidden one. *Taught
in: [Module 07, Lesson 11](module-07-auth-security/lessons/11-secrets-config-and-logging.md).*

**React element** — The plain JavaScript object (roughly
`{ type, props }`) that a JSX expression, or the `createElement`/`jsx`
call it compiles to, returns — a description of what should render, not a
real DOM node. *Taught in: [Module 04, Lesson 01](module-04-react/lessons/01-why-react-components-props-and-jsx.md).*

**React Server Components (RSC)** — Components, in Next.js's App Router,
that run only on the server, never ship their own JavaScript to the
browser, and can access server-side resources (a database, a secret key)
directly. *Taught in: [Module 04, Lesson 09](module-04-react/lessons/09-nextjs-ssr-ssg-csr-concepts.md).*

**React Testing Library (RTL)** — A library for testing React components
by rendering them into a fake DOM (via jsdom, above) and interacting
with them the way a real user would — finding things by visible
text/role/label, never by internal implementation detail. *Taught in:
[Module 08, Lesson 07](module-08-testing-and-quality/lessons/07-frontend-testing-with-vitest-and-rtl.md).*

**Reconciliation** — React's process of comparing a new Virtual DOM tree
against the previous one and computing the minimal set of real-DOM
changes needed, rather than rebuilding the whole page. *Taught in:
[Module 04, Lesson 02](module-04-react/lessons/02-state-and-the-rendering-model.md).*

**Redirection (`>`, `>>`)** — Shell syntax that sends a command's output
into a file instead of the screen; `>` overwrites, `>>` appends. *Taught
in: [Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Redis** — An in-memory key-value store, commonly used as a cache: because
it keeps data in RAM rather than on disk, reads and writes are extremely
fast compared to a full relational-database query, at the cost of being
less durable by default and only ever holding simple key-value(-ish)
shapes rather than a rich relational schema. QuestLog uses Redis
(`redis.asyncio`, the current, non-deprecated async client bundled in the
`redis` PyPI package) to cache a signed-in user's own quest list for 30
seconds. *Taught in: [Module 10, Lesson 06](module-10-docker-and-containers/lessons/06-docker-compose-multi-service-apps.md).*

**ReDoc** — A separate, open-source tool (bundled and auto-configured by
FastAPI, served at `/redoc`) that reads a project's OpenAPI document and
renders it as a clean, three-panel reading layout — no "Try it out"
buttons, unlike Swagger UI (below), which reads the exact same document.
*Taught in: [Module 05, Lesson 07](module-05-backend-fastapi/lessons/07-auto-docs-and-openapi.md).*

**Ref** — The mutable "box" object (with a `.current` property) that
`useRef` returns; short for "reference." *Taught in: [Module 04, Lesson 04](module-04-react/lessons/04-useref-and-custom-hooks.md).*

**Refresh token** — A separate, longer-lived credential a client can
exchange for a new access token once the old one expires, without forcing
a user to log in again; QuestLog does not implement one, relying instead
on a short access-token lifetime and requiring a fresh login after it
expires. *Taught in: [Module 07, Lesson 05](module-07-auth-security/lessons/05-oauth2-conceptual.md).*

**Registered claim** — A JWT claim (above) whose short name (`sub`,
`iat`, `exp`, and others) is part of the official JWT specification
itself, so any JWT library in any language understands it the same way.
*Taught in: [Module 07, Lesson 04](module-07-auth-security/lessons/04-jwt-structure-in-depth.md).*

**Regression** — A bug where something that used to work stops working
because of a change made elsewhere, often in code the person making the
change didn't realize was related; the main category of problem an
automated test suite exists to catch. *Taught in: [Module 08, Lesson 01](module-08-testing-and-quality/lessons/01-why-tests-and-the-testing-pyramid.md).*

**Relational database** — A database organizing data into tables of rows
and columns, with relationships between tables expressed via foreign
keys; PostgreSQL is this course's example. *Taught in: [Module 06,
Lesson 01](module-06-databases/lessons/01-why-a-database-and-the-relational-model.md).*

**Relationship (database)** — A connection between two tables established
by a foreign key (e.g. "one-to-many" — one quest line, many quests);
distinct from SQLAlchemy's `relationship()` function, which is a Python/ORM
convenience for reading across that connection, not the connection itself.
*Taught in: [Module 06, Lesson 01](module-06-databases/lessons/01-why-a-database-and-the-relational-model.md)
and [Lesson 05](module-06-databases/lessons/05-orms-and-sqlalchemy-basics.md).*

**Relative import** — An import written relative to the current package,
using a leading dot (e.g. `from .models import Quest`), rather than a
full/absolute module path. *Taught in: [Module 01, Lesson 07](module-01-python-properly/lessons/07-modules-packages-and-virtual-environments.md).*

**Relative path** — A filesystem path interpreted relative to your current
working directory (e.g. `Desktop`, `../notes.txt`), as opposed to an
absolute path. *Taught in: [Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Reload token** — An incrementing piece of React state whose value is
never read directly; its only job is to serve as a `useEffect` dependency,
so that changing it deliberately re-triggers the effect (e.g. a "Try
again"/refetch button). *Taught in: [Module 04, Lesson 07](module-04-react/lessons/07-data-fetching-loading-and-error-states.md).*

**Remote** — A name Git gives to a URL pointing at another copy of a
repository, most commonly one hosted on GitHub. *Taught in: [Module 00,
Lesson 05](module-00-developer-environment-and-tooling/lessons/05-github-and-pull-requests.md).*

**Render / Re-render** — React calling a component function again and
getting back a new description of UI; not the same thing as the browser
physically repainting the screen. *Taught in: [Module 04, Lesson 02](module-04-react/lessons/02-state-and-the-rendering-model.md).*

**Repository (repo)** — A project folder whose history of changes Git is
tracking, backed by a hidden `.git` folder. *Taught in: [Module 00,
Lesson 03](module-00-developer-environment-and-tooling/lessons/03-git-fundamentals.md).*

**Request body** — Structured data a client sends *inside* an HTTP
request (as opposed to in the URL, like a path/query parameter),
conventionally as JSON, and commonly carried by `POST`/`PUT`/`PATCH`
requests; in FastAPI, a route parameter typed as a Pydantic model,
instead of a simple type, tells FastAPI to expect one. *Taught in:
[Module 05, Lesson 03](module-05-backend-fastapi/lessons/03-request-bodies-and-pydantic-validation.md).*

**Request line** — The first line of an HTTP request, of the form
`METHOD path HTTP/version` (e.g. `GET /api/v2/pokemon/pikachu HTTP/1.1`).
*Taught in: [Module 02, Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**requirements.txt** — A plain text file listing a Python project's
dependencies (typically with exact pinned versions from `pip freeze`), so
the same environment can be reproduced elsewhere with `pip install -r
requirements.txt`. *Taught in: [Module 01, Lesson 00](module-01-python-properly/lessons/00-setup.md).*

**Resource (REST)** — A named "thing" an API exposes and addresses via a
URL (e.g. "the Pokémon Pikachu"), distinct from any particular
representation (JSON, XML, etc.) of it. *Taught in: [Module 02, Lesson 06](module-02-internet-and-web-fundamentals/lessons/06-rest-from-first-principles.md).*

**Resource Owner** — The OAuth2 role played by the actual human who owns
the data being accessed (e.g. you, owning your own Google Photos).
*Taught in: [Module 07, Lesson 05](module-07-auth-security/lessons/05-oauth2-conceptual.md).*

**Resource Server** — The OAuth2 role played by the service that actually
holds the protected data and checks tokens on incoming requests; distinct
from the Authorization Server, above, which issues those tokens in the
first place. *Taught in: [Module 07, Lesson 05](module-07-auth-security/lessons/05-oauth2-conceptual.md).*

**Responsive design** — The practice of building a layout that adapts to
the size of the screen/window displaying it, typically via media queries;
comparable in goal (though not mechanism) to UMG's Anchors and Scale/Size
Boxes. *Taught in: [Module 03, Lesson 04](module-03-html-css-javascript/lessons/04-css-grid-and-responsive-design.md).*

**REST (REpresentational State Transfer)** — An architectural style (not a
protocol or product) for designing networked systems, defined by Roy
Fielding's 2000 dissertation, comprising constraints including
client-server separation, statelessness, cacheability, a uniform
interface, and a layered system. *Taught in: [Module 02, Lesson 06](module-02-internet-and-web-fundamentals/lessons/06-rest-from-first-principles.md).*

**RESTful** — Describes an API that follows REST's constraints; in
practice, most real-world "REST APIs" satisfy the majority of the
constraints while only partially satisfying HATEOAS. *Taught in:
[Module 02, Lesson 06](module-02-internet-and-web-fundamentals/lessons/06-rest-from-first-principles.md).*

**`rm`** — Shell command to delete files (`rm -r` for folders);
permanent, with no undo or Recycle Bin. *Taught in: [Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Reverse proxy** — A program (Nginx, in this course) that sits in front
of an application server, receiving all public traffic itself and
forwarding requests to the real backend on the same machine's internal
address, relaying the response back — letting one public address serve
a static frontend, an API, and other cross-cutting concerns (TLS,
logging) from one place. *Taught in: [Module 09, Lesson 06](module-09-linux-networking-servers/lessons/06-nginx-and-reverse-proxies.md).*

**Root user** — Linux's special superuser account (UID `0`) that bypasses
permission checks entirely; `sudo` (below) is the standard, safer way to
run one specific command with root's power instead of logging in as root
directly. *Taught in: [Module 09, Lesson 01](module-09-linux-networking-servers/lessons/01-linux-processes-and-permissions.md).*

**Row** — One specific record in a database table — one horizontal entry
matching that table's columns. *Taught in: [Module 06, Lesson 01](module-06-databases/lessons/01-why-a-database-and-the-relational-model.md).*

**Rules of Hooks** — The two rules every hook (built-in or custom) must
follow: only call hooks at a component/hook's top level (never inside
conditionals/loops/nested functions), and only from components or other
hooks — so React can reliably track each hook's state by call order
across renders. *Taught in: [Module 04, Lesson 04](module-04-react/lessons/04-useref-and-custom-hooks.md).*

**Safe method** — A property of an HTTP method meaning it must not cause
the server to change anything (e.g. `GET`, `HEAD`) — a read-only contract
that caches, prefetchers, and crawlers all rely on. *Taught in:
[Module 02, Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**Salt** — A random value, generated fresh for every single password,
mixed into the hashing process so identical passwords never produce
identical hashes; stored inside the hash string itself (not separately),
which is exactly what defeats rainbow tables (above). *Taught in:
[Module 07, Lesson 02](module-07-auth-security/lessons/02-password-hashing.md).*

**Same-Origin Policy** — The browser's own default rule that JavaScript
running on one origin cannot read the response of a request it makes to a
different origin, even though the browser can often still send that
request; CORS, above, is the controlled exception a server can opt into.
*Taught in: [Module 07, Lesson 10](module-07-auth-security/lessons/10-cors-in-depth.md).*

**SameSite (cookie attribute)** — A flag a server sets on a cookie
telling the browser not to send it along with requests originating from a
different site; a standard defense against CSRF, above, for systems
using cookie-based authentication. *Taught in: [Module 07, Lesson 09](module-07-auth-security/lessons/09-xss-and-csrf.md).*

**Schema (database)** — The overall design of a database: which tables
exist, their columns, and the relationships between them. *Taught in:
[Module 06, Lesson 09](module-06-databases/lessons/09-normalization-and-schema-design.md)
and [Lesson 10](module-06-databases/lessons/10-designing-questlogs-schema.md).*

**Scope** — The region of code where a given variable name is
visible/accessible; Python's function-level scoping (local, enclosing,
global) differs from block-level scoping in some other languages. *Taught
in: [Module 01, Lesson 02](module-01-python-properly/lessons/02-functions-and-scope.md).*

**Scope (OAuth2)** — A named, specific permission an OAuth2 client
requests (e.g. `photos.readonly`); requesting the narrowest scopes that
get the job done is the general **principle of least privilege**, worth
knowing well beyond OAuth2 itself. Distinct from a Python variable's
scope, above. *Taught in: [Module 07, Lesson 05](module-07-auth-security/lessons/05-oauth2-conceptual.md).*

**Screen reader** — Software that reads a page's content aloud (or
converts it to braille), relying on semantic HTML and correctly labeled
form fields to announce structure and purpose accurately rather than
guessing from visual styling alone. *Taught in: [Module 03, Lesson 01](module-03-html-css-javascript/lessons/01-html-structure-forms-and-accessibility.md).*

**Secrets management** — The discipline of treating configuration values
that fall into three real categories (safe defaults, per-environment
settings, and genuine secrets) differently — never committing a real
secret to Git, and failing loudly at startup rather than silently running
with a missing one. *Taught in: [Module 07, Lesson 11](module-07-auth-security/lessons/11-secrets-config-and-logging.md).*

**Security scheme** — A FastAPI object (e.g. `OAuth2PasswordBearer`,
above) that knows how to extract credentials from a request in one
specific, standard way, and that feeds FastAPI's auto-generated OpenAPI
docs enough information to render an "Authorize" button. *Taught in:
[Module 07, Lesson 07](module-07-auth-security/lessons/07-protecting-routes-with-dependencies.md).*

**Semantic HTML** — Choosing HTML elements that describe what a piece of
content actually *is* (e.g. `<nav>`, `<article>`) rather than generic,
meaning-free containers (`<div>`) for everything, with real consequences
for screen readers and search engines. *Taught in: [Module 03, Lesson 01](module-03-html-css-javascript/lessons/01-html-structure-forms-and-accessibility.md).*

**Server** — Whichever side of an interaction listens for and responds to
requests; a role, not a fixed identity — the same program can be a server
in one interaction and a client in another. *Taught in: [Module 02,
Lesson 05](module-02-internet-and-web-fundamentals/lessons/05-clients-servers-apis-and-json.md).*

**Server-Side Rendering (SSR)** — A rendering strategy where a server
runs component code fresh for each incoming request and sends back real,
filled-in HTML, followed by hydration to make it interactive; good for
personalized/per-request content. *Taught in: [Module 04, Lesson 09](module-04-react/lessons/09-nextjs-ssr-ssg-csr-concepts.md).*

**Session (authentication)** — A server-side record ("user 42 is logged
in") plus a session-id cookie the browser resends automatically;
contrasted with a JWT, which carries the same kind of information itself,
signed, with no server-side record needed at all. Distinct from a
SQLAlchemy Session, below. *Taught in: [Module 07, Lesson 03](module-07-auth-security/lessons/03-sessions-vs-jwts.md).*

**Session (SQLAlchemy)** — A short-lived workspace (`AsyncSession`) for
one unit of database work — opened, used for some queries/changes,
committed or rolled back, then closed; FastAPI provides a fresh one per
request via `Depends(get_db)`. *Taught in: [Module 06, Lesson 05](module-06-databases/lessons/05-orms-and-sqlalchemy-basics.md)
and [Lesson 06](module-06-databases/lessons/06-sqlalchemy-with-fastapi.md).*

**Set** — An unordered collection of unique values, optimized for fast
membership checks (`in`). *Taught in: [Module 01, Lesson 03](module-01-python-properly/lessons/03-data-structures.md).*

**Set-Cookie header** — An HTTP response header instructing the client to
store a cookie and resend it on future requests to that site. *Taught in:
[Module 02, Lesson 04](module-02-internet-and-web-fundamentals/lessons/04-headers-cookies-and-statelessness.md).*

**Shell** — A program that reads typed text, interprets it as a command,
runs it, and prints the result — the mechanism behind every command-line
tool. *Taught in: [Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Side effect** — Code that reaches outside React's own rendering — a
network call, a timer, a subscription, or manual DOM access — kept out of
a component's plain render body and run inside `useEffect` instead.
*Taught in: [Module 04, Lesson 03](module-04-react/lessons/03-useeffect-the-dependency-array-in-depth.md).*

**Single Page Application (SPA)** — A web app that loads one HTML page
once and uses JavaScript to change what's displayed, without the browser
navigating to a new document for each "page" the user perceives. *Taught
in: [Module 04, Lesson 08](module-04-react/lessons/08-react-router.md).*

**Spread operator (`...`)** — JavaScript syntax that expands an array or
object's contents into a new array/object literal, or into individual
function arguments, without mutating the original. *Taught in: [Module 03,
Lesson 08](module-03-html-css-javascript/lessons/08-es6-plus-features-and-modules.md).*

**SQL (Structured Query Language)** — A small, declarative language for
describing what data you want (or how to change it) rather than how to
fetch it, letting the database itself decide the most efficient way to
produce the result. *Taught in: [Module 06, Lesson 03](module-06-databases/lessons/03-sql-select-insert-update-delete.md).*

**SQL injection** — An attack where untrusted input, pasted directly into
a SQL string, gets treated as part of the query's own instructions
rather than as data — e.g. an email field containing `' OR '1'='1`
rewriting a login check's meaning entirely; prevented by parameterized
queries (above), which SQLAlchemy's query-building API already uses by
default. *Taught in: [Module 07, Lesson 08](module-07-auth-security/lessons/08-sql-injection-and-orm-safety.md).*

**SQLAlchemy** — The Python ORM used in this course, providing a
declarative class-based way to describe database tables and an async
session API for querying them. *Taught in: [Module 06, Lesson 05](module-06-databases/lessons/05-orms-and-sqlalchemy-basics.md).*

**`ss` (socket statistics)** — The modern command for listing active
network connections and listening sockets (`ss -tlnp`), showing which
process is bound to which address and port; the current replacement for
the older `netstat`. *Taught in: [Module 09, Lesson 04](module-09-linux-networking-servers/lessons/04-networking-ports-and-ips.md).*

**SSH key pair** — A public/private key pair used for authenticating an
SSH login: the private key never leaves your own machine, while the
public key is placed in a server's `authorized_keys` file; login proves
possession of the private key without ever transmitting it. *Taught in:
[Module 09, Lesson 02](module-09-linux-networking-servers/lessons/02-ssh-and-key-based-auth.md).*

**Staging area (index)** — A holding area in Git where you place exactly
the changes you want included in your next commit, distinct from both the
working directory and the permanent commit history. *Taught in:
[Module 00, Lesson 03](module-00-developer-environment-and-tooling/lessons/03-git-fundamentals.md).*

**Stack trace / traceback** — A list showing the chain of function calls
active at the moment an error occurred, used to trace how execution
reached the point of failure. *Taught in: [Module 00, Lesson 02](module-00-developer-environment-and-tooling/lessons/02-reading-docs-and-errors.md).*

**Stale closure** — A React bug where an effect (or other) function
created on an earlier render keeps running with the variable values it
captured at creation time, never seeing later updates, because a missing
dependency prevented a fresh version from being created. *Taught in:
[Module 04, Lesson 03](module-04-react/lessons/03-useeffect-the-dependency-array-in-depth.md).*

**State (React)** — Data a component owns that, when changed via its
setter, causes React to re-render that component and update the UI —
comparable to an Actor's property whose change should update a bound
widget. *Taught in: [Module 04, Lesson 02](module-04-react/lessons/02-state-and-the-rendering-model.md).*

**Stateless** — Describes a protocol (like HTTP) where each
request/response is fully self-contained, with the server retaining no
memory of any previous request unless an application deliberately adds
one (e.g. via cookies). *Taught in: [Module 02, Lesson 04](module-02-internet-and-web-fundamentals/lessons/04-headers-cookies-and-statelessness.md).*

**Static Site Generation (SSG)** — A Next.js rendering strategy where a
page's HTML is generated once, at build time, rather than per request,
because its content doesn't depend on who's asking or when (marketing
pages, blog posts, docs). *Taught in: [Module 04, Lesson 09](module-04-react/lessons/09-nextjs-ssr-ssg-csr-concepts.md).*

**Status code** — The three-digit number, at the start of an HTTP
response's status line, indicating the outcome of a request; its first
digit gives its category (1xx informational, 2xx success, 3xx redirection,
4xx client error, 5xx server error). *Taught in: [Module 02, Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**Status line** — The first line of an HTTP response, of the form
`HTTP/version status-code reason-phrase` (e.g. `HTTP/1.1 200 OK`). *Taught
in: [Module 02, Lesson 03](module-02-internet-and-web-fundamentals/lessons/03-http-methods-and-status-codes.md).*

**`StopIteration`** — The special exception an iterator raises from
`__next__` to signal there are no more items left — the actual mechanism
that ends every `for` loop. *Taught in: [Module 01, Lesson 04](module-01-python-properly/lessons/04-comprehensions-generators-and-iterators.md).*

**StrictMode** — A React component that renders nothing itself but turns
on extra development-only checks for everything inside it — including,
in React 19, deliberately double-invoking effects (mount → cleanup →
mount) to surface missing-cleanup bugs; it has no effect on a production
build. *Taught in: [Module 04, Lesson 03](module-04-react/lessons/03-useeffect-the-dependency-array-in-depth.md).*

**`super()`** — Inside a subclass, gives access to the parent class's own
version of a method (most commonly `__init__`), letting a subclass extend
rather than completely replace it. *Taught in: [Module 01, Lesson 05](module-01-python-properly/lessons/05-oop-classes-and-dunders.md).*

**Structured logging** — Writing log entries as machine-parseable data
(commonly JSON) with consistent fields (timestamp, level, event, relevant
ids) rather than free-form sentences, so logs can later be queried rather
than manually scanned — and, done right, deliberately excluding fields
like passwords and full tokens. *Taught in: [Module 07, Lesson 11](module-07-auth-security/lessons/11-secrets-config-and-logging.md).*

**Sub-dependency** — A dependency (see Dependency injection, above) that
itself depends on another dependency via its own `Depends(...)`; FastAPI
resolves the whole chain automatically, deepest dependency first, and
stops the entire chain immediately if any link raises an error. *Taught
in: [Module 05, Lesson 04](module-05-backend-fastapi/lessons/04-dependency-injection-and-depends.md).*

**Subquery** — A `SELECT` statement used as a value inside another SQL
statement (e.g. inside an `INSERT`'s `VALUES` or a `WHERE` clause).
*Taught in: [Module 06, Lesson 03](module-06-databases/lessons/03-sql-select-insert-update-delete.md).*

**sudo** — "Superuser do": runs one specific command with root's
elevated permissions, then immediately drops back to the normal user —
the standard, safer alternative to logging in as root directly. *Taught
in: [Module 09, Lesson 01](module-09-linux-networking-servers/lessons/01-linux-processes-and-permissions.md).*

**Swagger UI** — A separate, open-source tool (bundled and auto-configured
by FastAPI, served at `/docs`) that reads a project's OpenAPI document and
renders it as an interactive page, including a "Try it out" button that
sends real requests to the actual running server. *Taught in: [Module 05,
Lesson 07](module-05-backend-fastapi/lessons/07-auto-docs-and-openapi.md).*

**Symmetric algorithm** — A signing scheme (e.g. `HS256`) where the exact
same secret key both creates and verifies signatures; the right fit when
one single backend is the only party that ever needs to do either job,
which is why QuestLog uses one. Contrasted with an asymmetric algorithm,
above. *Taught in: [Module 07, Lesson 04](module-07-auth-security/lessons/04-jwt-structure-in-depth.md).*

**systemd** — Ubuntu's (and most modern Linux distributions') init
system: the first process the kernel starts at boot (always PID 1),
responsible for starting and supervising every other background program,
including any application configured as a **unit file** (below). *Taught
in: [Module 09, Lesson 03](module-09-linux-networking-servers/lessons/03-systemd-and-services.md).*

**Table** — A named collection of rows sharing the same fixed set of
columns in a relational database — comparable to a spreadsheet with a
fixed header row. *Taught in: [Module 06, Lesson 01](module-06-databases/lessons/01-why-a-database-and-the-relational-model.md).*

**TCP (Transmission Control Protocol)** — A set of rules two computers
follow to have a reliable, ordered, two-way conversation over an
unreliable network, opened via a three-way handshake; what HTTP is built
on top of. *Taught in: [Module 02, Lesson 02](module-02-internet-and-web-fundamentals/lessons/02-tcp-tls-and-the-request-response-journey.md).*

**Template literal** — A JavaScript string written with backticks
(`` ` ``) instead of quotes, allowing multi-line text and embedded
expressions inside `${ }` — JavaScript's equivalent of Python's f-strings.
*Taught in: [Module 03, Lesson 05](module-03-html-css-javascript/lessons/05-javascript-fundamentals-and-the-event-loop.md).*

**Terminal** — The window/application that displays text and accepts
typed input; distinct from the shell (the program interpreting that
input) running inside it. *Taught in: [Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Test client** — An object (e.g. an `httpx.AsyncClient` wired to
`ASGITransport`, above) that sends requests directly into an
application's own code for testing, with no real network connection
involved; a different, more specific meaning from the general "Client"
(Module 02) or OAuth2's "Client" (Module 07), both above. *Taught in:
[Module 08, Lesson 05](module-08-testing-and-quality/lessons/05-testing-fastapi-endpoints.md).*

**Test discovery** — The rules a test runner (below) uses to
automatically find test files and test functions on its own, based on
naming conventions (e.g. a file named `test_*.py`, a function named
`test_*`), with no test needing to be manually registered anywhere.
*Taught in: [Module 08, Lesson 02](module-08-testing-and-quality/lessons/02-pytest-fundamentals-and-fixtures.md).*

**Test double** — The general term for any fake object used in place of
a real one inside a test (a mock, above, is one specific kind); borrowed
from the movie industry's "stunt double." *Taught in: [Module 08, Lesson
03](module-08-testing-and-quality/lessons/03-parametrize-and-mocking.md).*

**Test runner** — A program whose job is discovering test files/functions,
running them, and reporting which passed and which failed; `pytest`
(Python) and Vitest (below, JavaScript/TypeScript) are this course's two.
*Taught in: [Module 08, Lesson 01](module-08-testing-and-quality/lessons/01-why-tests-and-the-testing-pyramid.md).*

**Testing pyramid** — A description of a healthy test suite's shape:
mostly fast, isolated unit tests (below) at the bottom; a meaningful but
smaller number of integration tests (above) in the middle; a small
number of slow, realistic end-to-end tests (above) at the top. *Taught
in: [Module 08, Lesson 01](module-08-testing-and-quality/lessons/01-why-tests-and-the-testing-pyramid.md).*

**Three-way handshake** — The SYN / SYN-ACK / ACK exchange that opens a
TCP connection, confirming both sides are ready before any real data is
sent. *Taught in: [Module 02, Lesson 02](module-02-internet-and-web-fundamentals/lessons/02-tcp-tls-and-the-request-response-journey.md).*

**Time complexity** — An intuition/measure of how an operation's cost
grows as a collection's size grows (e.g. a `set`'s membership check stays
roughly constant-time regardless of size, while a `list`'s grows with its
length). *Taught in: [Module 01, Lesson 03](module-01-python-properly/lessons/03-data-structures.md).*

**TLS (Transport Layer Security)** — The modern protocol (formerly called
SSL) that wraps a TCP connection in encryption, integrity protection, and
server authentication via certificates; TLS 1.3 is the current preferred
version, with TLS 1.0/1.1 formally deprecated and disabled in all major
browsers. *Taught in: [Module 02, Lesson 02](module-02-internet-and-web-fundamentals/lessons/02-tcp-tls-and-the-request-response-journey.md).*

**TLS handshake** — The negotiation, immediately after a TCP connection
opens, in which client and server agree on a TLS version/cipher, the
server proves its identity via a certificate, and both sides establish a
shared encryption key. *Taught in: [Module 02, Lesson 02](module-02-internet-and-web-fundamentals/lessons/02-tcp-tls-and-the-request-response-journey.md).*

**`touch`** — Shell command that creates an empty file if it doesn't
already exist (or updates its modified timestamp if it does). *Taught in:
[Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Transaction** — A group of database operations treated as one
all-or-nothing unit — either every operation inside it takes effect once
committed, or none do if rolled back or interrupted; the mechanism behind
Atomicity in ACID. *Taught in: [Module 06, Lesson 02](module-06-databases/lessons/02-indexes-transactions-and-acid.md).*

**Truthiness** — The rule that every Python value is treated as `True` or
`False` in a boolean context, even if it isn't literally `True`/`False` —
e.g. `0`, `""`, `None`, and empty collections are all "falsy." *Taught in:
[Module 01, Lesson 01](module-01-python-properly/lessons/01-variables-types-and-control-flow.md).*

**Truthy/falsy (JavaScript)** — JavaScript's own, separate rule for which
values count as `true`/`false` in a boolean context; its complete falsy
list is exactly `false, 0, "", null, undefined, NaN` — notably different
from Python's truthiness above, since an empty array (`[]`) or object
(`{}`) is truthy in JavaScript despite Python's empty collections being
falsy. *Taught in: [Module 03, Lesson 05](module-03-html-css-javascript/lessons/05-javascript-fundamentals-and-the-event-loop.md).*

**`tsc` (TypeScript compiler)** — The program that reads `.ts` files,
checks their types, and compiles them into plain `.js` files a browser or
Node.js can actually run, stripping out every type annotation in the
process. *Taught in: [Module 03, Lesson 00](module-03-html-css-javascript/lessons/00-setup.md).*

**`tsconfig.json`** — A configuration file telling `tsc` how to compile a
TypeScript project (which JavaScript version to target, where source/
output files live, how strict to be, etc.). *Taught in: [Module 03,
Lesson 00](module-03-html-css-javascript/lessons/00-setup.md).*

**TTL (Time To Live)** — How long a cached value is trusted before it's
treated as stale and discarded, even if nothing ever explicitly
invalidated it — QuestLog's cached quest list uses a 30-second TTL, so
Redis's own `EXPIRE`/`SET ... EX` mechanism deletes it automatically if no
create/update/delete happened to invalidate it sooner. *Taught in: [Module 10, Lesson 06](module-10-docker-and-containers/lessons/06-docker-compose-multi-service-apps.md).*

**Tuple** — An ordered, immutable sequence of values — like a list that
can never be changed after creation. *Taught in: [Module 01, Lesson 03](module-01-python-properly/lessons/03-data-structures.md).*

**Type annotation** — Explicit TypeScript syntax (`: string`, `: number`,
etc.) stating a variable's, parameter's, or return value's intended type,
checked by `tsc` before compilation. *Taught in: [Module 03, Lesson 09](module-03-html-css-javascript/lessons/09-typescript-introduction.md).*

**Type assertion (`as`)** — TypeScript syntax (`value as SomeType`) that
tells the compiler to trust the developer's claim about a value's type,
without performing any actual runtime check that the claim is true.
*Taught in: [Module 03, Lesson 09](module-03-html-css-javascript/lessons/09-typescript-introduction.md).*

**Type checker** — A separate tool (e.g. Pylance, mypy, or TypeScript's
own `tsc`) that reads a program's type hints/annotations without running
it, flagging places where hinted types don't line up. *Taught in:
[Module 01, Lesson 09](module-01-python-properly/lessons/09-type-hints.md)
and [Module 03, Lesson 09](module-03-html-css-javascript/lessons/09-typescript-introduction.md).*

**Type hint** — An annotation on a variable, parameter, or return value
stating its intended type, checked by external tools rather than enforced
by the Python interpreter itself. *Taught in: [Module 01, Lesson 09](module-01-python-properly/lessons/09-type-hints.md).*

**Type inference (TypeScript)** — `tsc`'s ability to automatically
determine a variable's type from its initial value, without an explicit
annotation, then enforce that inferred type just as strictly afterward.
*Taught in: [Module 03, Lesson 09](module-03-html-css-javascript/lessons/09-typescript-introduction.md).*

**TypeScript** — A superset of JavaScript that adds optional, compile-
time-checked type annotations, compiled to plain JavaScript by `tsc`
before it can run in a browser or Node.js. *Taught in: [Module 03,
Lesson 09](module-03-html-css-javascript/lessons/09-typescript-introduction.md)
(tooling installed in [Lesson 00](module-03-html-css-javascript/lessons/00-setup.md)).*

**ufw (Uncomplicated Firewall)** — Ubuntu's standard, beginner-friendly
front end for the kernel's firewall, defaulting to deny all incoming and
allow all outgoing traffic; configured with commands like
`ufw allow OpenSSH` and enabled with `ufw enable`. *Taught in: [Module 09, Lesson 05](module-09-linux-networking-servers/lessons/05-firewalls-with-ufw.md).*

**Uncontrolled component** — An input that manages its own value
internally, the plain-HTML way, with React only touching it (if at all)
via a `ref`; contrasted with a **controlled component**, above. *Taught
in: [Module 04, Lesson 05](module-04-react/lessons/05-forms-controlled-components-and-lifting-state.md).*

**Union type** — A type hint meaning "this value could be one of several
types," written with `|` in modern Python (e.g. `dict | None`). *Taught
in: [Module 01, Lesson 09](module-01-python-properly/lessons/09-type-hints.md).*

**Union type (TypeScript)** — A TypeScript type meaning "one of several
specific types," written with `|` (e.g. `"open" | "closed"` or
`string | undefined`) — the same `|` symbol and a comparable idea to
Python's own union type hints above, but a distinct language feature
enforced by `tsc` rather than Python's optional external type checkers.
*Taught in: [Module 03, Lesson 09](module-03-html-css-javascript/lessons/09-typescript-introduction.md).*

**Unit file** — A small, plain-text configuration file telling `systemd`
about one thing it should manage (most relevantly, a service), with
`[Unit]`/`[Service]`/`[Install]` sections controlling metadata, how to
run it, and when to auto-start it. *Taught in: [Module 09, Lesson 03](module-09-linux-networking-servers/lessons/03-systemd-and-services.md).*

**Unique constraint** — A database rule rejecting any row that would
duplicate an existing value in a given column (or set of columns), used
in QuestLog to guarantee each quest line name has exactly one authoritative
row. *Taught in: [Module 06, Lesson 05](module-06-databases/lessons/05-orms-and-sqlalchemy-basics.md).*

**Unit test** — A test that exercises one small, isolated piece of code
(often a single function), with nothing real set up around it — the
fastest, most isolated, and most numerous layer of the testing pyramid
(above). *Taught in: [Module 08, Lesson 01](module-08-testing-and-quality/lessons/01-why-tests-and-the-testing-pyramid.md).*

**Upstream (Nginx)** — A named group of backend addresses Nginx can
`proxy_pass` requests to and distribute across, the configuration
mechanism underlying a load balancer, above. *Taught in: [Module 09, Lesson 06](module-09-linux-networking-servers/lessons/06-nginx-and-reverse-proxies.md).*

**URL (Uniform Resource Locator)** — The full address of a web resource,
composed of a scheme, host, path, and optionally a query string and
fragment (e.g. `https://pokeapi.co/api/v2/pokemon/pikachu?limit=20#results`).
*Taught in: [Module 02, Lesson 05](module-02-internet-and-web-fundamentals/lessons/05-clients-servers-apis-and-json.md).*

**`useContext`** — The hook a descendant component calls to read the
current value being broadcast on a Context, with no props involved.
*Taught in: [Module 04, Lesson 06](module-04-react/lessons/06-context.md).*

**`useEffect`** — The hook that runs a side effect after React has
rendered, controlled by its dependency array. *Taught in: [Module 04,
Lesson 03](module-04-react/lessons/03-useeffect-the-dependency-array-in-depth.md).*

**`useRef`** — A React hook that returns a mutable object with a
`.current` property that persists across re-renders without ever causing
one when changed. *Taught in: [Module 04, Lesson 04](module-04-react/lessons/04-useref-and-custom-hooks.md).*

**`useState`** — The hook that returns a `[value, setter]` pair and is the
mechanism that tells React "something changed, please re-render." *Taught
in: [Module 04, Lesson 02](module-04-react/lessons/02-state-and-the-rendering-model.md).*

**User-Agent header** — An HTTP request header identifying which software
(browser, `curl`, etc.) is making the request. *Taught in: [Module 02,
Lesson 04](module-02-internet-and-web-fundamentals/lessons/04-headers-cookies-and-statelessness.md).*

**Utility-first CSS** — Styling elements primarily by composing many
small, single-purpose classes directly in markup (each mapping to one CSS
declaration), instead of writing custom named classes with separate rule
blocks. *Taught in: [Module 04, Lesson 10](module-04-react/lessons/10-tailwind-and-utility-first-css.md).*

**Uvicorn** — A specific **ASGI server** (above) — the program that
actually opens a network port, accepts real HTTP connections, and hands
each request to a compliant framework like FastAPI, then sends the
framework's response back out over the network. *Taught in: [Module 05,
Lesson 00](module-05-backend-fastapi/lessons/00-setup.md).*

**Validation error** — The specific, itemized response FastAPI/Pydantic
produce automatically when incoming data doesn't match a described
Pydantic model or a typed path/query parameter, before the matching route
function's own body ever runs — a `422` status with a `detail` list, each
item giving a `type`, `loc` (location), `msg`, and `input`. *Taught in:
[Module 05, Lesson 03](module-05-backend-fastapi/lessons/03-request-bodies-and-pydantic-validation.md).*

**Version control** — A system for tracking the history of changes to
files over time, enabling checkpoints, rollback, and merging contributions
from multiple sources. *Taught in: [Module 00, Lesson 03](module-00-developer-environment-and-tooling/lessons/03-git-fundamentals.md).*

**Viewport meta tag** — The `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
tag telling mobile browsers to render a page at the device's actual width
rather than a zoomed-out desktop-sized layout, required for media queries
to behave correctly on real devices. *Taught in: [Module 03, Lesson 01](module-03-html-css-javascript/lessons/01-html-structure-forms-and-accessibility.md)
(used in [Lesson 04](module-03-html-css-javascript/lessons/04-css-grid-and-responsive-design.md)).*

**Virtual DOM** — A lightweight, in-memory JavaScript object tree
describing what the UI should look like, distinct from the real, heavier
browser DOM; the raw material React's reconciliation process compares
between renders. *Taught in: [Module 04, Lesson 02](module-04-react/lessons/02-state-and-the-rendering-model.md).*

**Virtual environment (venv)** — A self-contained, disposable folder
holding its own private Python package installation, isolated from the
system's global Python and from every other project's environment.
*Taught in: [Module 01, Lesson 00](module-01-python-properly/lessons/00-setup.md).*

**Virtual machine (VM)** — A complete, simulated computer running its own
full guest operating system (kernel included) on top of a hypervisor,
which emulates the hardware that guest OS believes it's running on. Much
heavier than a container (which shares the host's kernel and just isolates
one process using namespaces/cgroups) but more strongly isolated — two
containers on the same host still share one real kernel, while two VMs on
the same host each have their own, completely separate one. *Taught in: [Module 10, Lesson 01](module-10-docker-and-containers/lessons/01-containers-vs-vms-and-your-first-container.md).*

**Vite** — A fast build tool and dev server for JavaScript/TypeScript
frontend projects, providing Hot Module Replacement while developing and
bundling/optimizing files for a production build (`npm run build`).
*Taught in: [Module 04, Lesson 00](module-04-react/lessons/00-setup.md).*

**Vitest** — The test runner (above) this course uses for QuestLog's
React/TypeScript frontend, built to work well with Vite and to feel
familiar to anyone who's used Jest. *Taught in: [Module 08, Lesson 07](module-08-testing-and-quality/lessons/07-frontend-testing-with-vitest-and-rtl.md).*

**Void element** — An HTML element with no closing tag and no content,
like `<img>`, `<br>`, or `<input>`. *Taught in: [Module 03, Lesson 01](module-03-html-css-javascript/lessons/01-html-structure-forms-and-accessibility.md).*

**Volume (Docker)** — A storage mechanism that keeps data alive
independently of any one container's lifecycle, so stopping, removing, or
rebuilding a container never loses what was written to a volume — see
"Named volume" and "Bind mount" above for the two concrete flavors this
course uses. *Taught in: [Module 10, Lesson 05](module-10-docker-and-containers/lessons/05-docker-volumes-and-persistence.md).*

**VPS (Virtual Private Server)** — A rented, isolated slice of a real
computer in a data center, running its own full Linux OS with a real
public IP address anyone can reach — as opposed to WSL2, which runs
inside your own machine's private network. *Taught in: [Module 09, Lesson 00](module-09-linux-networking-servers/lessons/00-setup.md).*

**Well-known port** — A port number from 0–1023, reserved by convention
for a specific common service (`22` SSH, `80` HTTP, `443` HTTPS, `5432`
PostgreSQL); a browser fills in the default for a scheme automatically
when a URL omits a port. *Taught in: [Module 09, Lesson 04](module-09-linux-networking-servers/lessons/04-networking-ports-and-ips.md).*

**Working directory (filesystem sense)** — The folder you are currently
"in" when using a shell; also called the current directory. *Taught in:
[Module 00, Lesson 01](module-00-developer-environment-and-tooling/lessons/01-shell-and-filesystem.md).*

**Working directory (Git sense)** — The actual files on disk as they
currently exist, the first of Git's three areas a change passes through
before staging and committing. *Taught in: [Module 00, Lesson 03](module-00-developer-environment-and-tooling/lessons/03-git-fundamentals.md).*

**XSS (Cross-Site Scripting)** — An attack that gets a browser to run an
attacker's JavaScript as if it were a site's own code, which can then
read anything in the DOM or `localStorage` (including a stored JWT) and
send it anywhere the attacker chooses. Three varieties exist by where the
malicious script comes from: **stored** (saved server-side and served to
every future viewer), **reflected** (echoed straight back from a crafted
URL/form submission), and **DOM-based** (the vulnerability lives entirely
in client-side JavaScript). React's plain `{expression}` JSX
interpolation escapes this automatically; `dangerouslySetInnerHTML`,
above, is the one way to turn that protection off. *Taught in:
[Module 07, Lesson 09](module-07-auth-security/lessons/09-xss-and-csrf.md).*

**`yield`** — The keyword that turns a function into a generator function;
each `yield` pauses execution, hands back a value, and remembers exactly
where to resume on the next call. *Taught in: [Module 01, Lesson 04](module-01-python-properly/lessons/04-comprehensions-generators-and-iterators.md).*
