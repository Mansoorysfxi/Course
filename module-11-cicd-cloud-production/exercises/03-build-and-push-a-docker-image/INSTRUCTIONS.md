# Exercise 03 — Build and Push a Docker Image in CI (Guided/Independent)

**Concepts this exercise uses (all taught in
[`lessons/08-deploying-questlog-with-ci-cd.md`](../../lessons/08-deploying-questlog-with-ci-cd.md)'s
"Part 1 — Building and pushing images to GHCR" section, and
[`lessons/02-github-actions-from-zero.md`](../../lessons/02-github-actions-from-zero.md)
for `needs:`, `if:`, `permissions:`, and secrets):**
`docker/setup-buildx-action`, `docker/login-action`,
`docker/build-push-action`, `ghcr.io`, `secrets.GITHUB_TOKEN`,
`permissions:`, image tagging, lowercase image names.

**Where to work:** `exercises/03-build-and-push-a-docker-image/starter/`
— Exercise 02's finished CI workflow, plus a real, provided
`Dockerfile` for this same toy app (Module 10 already taught you how to
write one — this exercise's own new material is the CI *pipeline* around
it, not the Dockerfile itself).

Confirm the image builds locally first (this part uses only Module 10
knowledge):
```bash
cd exercises/03-build-and-push-a-docker-image/starter
docker build -t toy-ci-app .
docker run --rm -p 8000:8000 toy-ci-app
curl http://localhost:8000/add/2/3
```
**Expected:** `{"result":5}`. Stop the container (`Ctrl+C`) before
continuing.

## Your task

Add a second job, `build-and-push`, to `.github/workflows/ci.yml`, that:

1. Only runs after `test` succeeds (`needs:`), and only for a real push
   to `main` — never for a pull request.
2. Has `permissions: contents: read` and `permissions: packages: write`.
3. Normalizes `github.repository_owner` to lowercase (Lesson 08's own
   real gotcha — GHCR image names must be lowercase, GitHub usernames
   aren't guaranteed to be).
4. Sets up Docker Buildx, logs into `ghcr.io` using `github.actor` and
   `secrets.GITHUB_TOKEN` (no separate account or password needed).
5. Builds and pushes this image, tagged BOTH `:latest` and with the exact
   commit SHA (`github.sha`) that triggered the run.

## Verify it yourself

Push this to a real repo (per Exercise 02's own "which repo" note).
**Expected:** after `test` passes, `build-and-push` runs and succeeds;
your GitHub profile's own **Packages** tab (`github.com/YOUR_USERNAME?tab=packages`)
shows a new `toy-ci-app` package with (at least) two tags — `latest` and
one matching a real, full commit SHA.

## Acceptance criteria

- [ ] `build-and-push` only runs after `test` succeeds, and only for a
      push to `main` (verify by opening a pull request instead and
      confirming this job does NOT run at all).
- [ ] The job explicitly declares `permissions: contents: read` and
      `permissions: packages: write`.
- [ ] The pushed image name is entirely lowercase, regardless of your own
      GitHub username's actual casing.
- [ ] The image is tagged with both `:latest` and the triggering commit's
      exact SHA.
- [ ] You can explain, without looking it up, why GitHub Actions'
      expression language has no built-in way to lowercase a string, and
      what this workflow does instead.

## Hints

<details>
<summary>Hint 1</summary>

Lesson 08's own `build-and-push-images` job for QuestLog is structurally
identical to what this exercise wants, just for one image instead of
two — copy its shape, not its exact image name.

</details>

<details>
<summary>Hint 2</summary>

The lowercase trick is a plain bash parameter expansion inside a `run:`
step, writing its result to `$GITHUB_OUTPUT` so a later step (or this
same step, later in the same job) can read it back as
`steps.<id>.outputs.<name>`.

</details>

<details>
<summary>Hint 3</summary>

`docker/build-push-action`'s `tags:` input accepts multiple tags as a
YAML multi-line string (`|`), one per line — you don't need two separate
build steps to produce two tags of the same image.

</details>

A reference solution is in `solution/`.
