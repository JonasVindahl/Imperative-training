# Improvement Backlog

Tasks to raise the quality of the Imperative-training exam practice app across frontend, backend, security, testing, content, and ops. File paths reference the repo root.

---

## Backend — Architecture & Code Quality

- [ ] Replace `db.create_all()` in `app.py` with proper migrations using Flask-Migrate / Alembic; add `migrations/` and a `flask db` workflow.
- [ ] Move route logic out of `routes/practice.py` (289 lines) into thin controllers + service methods; e.g., extract `SessionService`, `AnswerService`.
- [ ] Centralise session keys (`practice_questions`, `current_index`, `active_exam_id`, etc.) in a `services/session_keys.py` constants module to avoid typos.
- [ ] Split `services/grader.py` (382 lines) into per-question-type modules (`graders/multiple_choice.py`, `graders/fill_blanks.py`, etc.) registered through a dispatch table.
- [ ] Replace string-based `correct_answer = "A"|"B"|...` indexing with explicit option ids; eliminates fragile letter math in the grader and templates.
- [ ] Introduce a `QuestionSchema` (e.g. pydantic / marshmallow) and validate every JSON file at boot; fail fast on malformed questions instead of returning empty lists.
- [x] Replace the `print(...)` warnings in `services/question_loader.py` with proper `logging` at WARNING/ERROR; add a `LOG_LEVEL` env var.
- [ ] Add `flask shell` helpers / management CLI (`flask seed`, `flask validate-questions`, `flask reload-cache`).
- [ ] Cache the parsed `exams.json` with file-mtime invalidation rather than the current load-once-forever cache; same for `QuestionLoader`.
- [ ] Pull `MAX_CODE_EXECUTION_TIME`, `MAX_MEMORY_MB`, hint counts, etc. into a typed `Settings` dataclass in `config.py`.
- [ ] Type-annotate the public surface of every service (`grader`, `adaptive`, `question_loader`, `exam_service`, `compiler`) and run `mypy --strict` in CI.
- [x] Remove the duplicate cwd assumption in `config.py` (`os.path.join(os.getcwd(), ...)`); resolve relative to `__file__` so the app works from any CWD.

## Backend — Performance

- [ ] Profile dashboard and stats routes; replace the per-request `for attempt in all_attempts` aggregation in `routes/progress.py` with a SQL `GROUP BY` query.
- [ ] Add database indexes on `attempts(user_id, exam_id, timestamp)` and `progress(user_id, exam_id, category)`; verify with `EXPLAIN`.
- [ ] Eager-load `User.attempts` only where used; audit for N+1 with `flask_sqlalchemy` query logging.
- [ ] Cache rendered category lists / dashboard tiles per user with Flask-Caching (memory or Redis).
- [ ] Stream large question JSON files only on demand; lazily load categories rather than the whole exam at boot.
- [ ] Add gzip / brotli compression for static assets in `Dockerfile`/gunicorn config.
- [ ] Enable HTTP caching headers (`Cache-Control`, `ETag`) for `/static/*`.

## Backend — Security

- [x] Refuse to start when `FLASK_SECRET_KEY` is the default `'dev-secret-key'` and `DEBUG=False`.
- [ ] Add CSRF protection (Flask-WTF) to every POST route (`/auth/login`, `/auth/register`, `/practice/*`, `/exam/switch`).
- [ ] Add per-IP rate limiting (Flask-Limiter) on `/auth/login`, `/auth/register`, and `/practice/submit` to deter brute-force and spam.
- [ ] Enforce password policy at registration: minimum length, mixed character classes, `zxcvbn`-style strength meter on the client.
- [ ] Switch password hashing to `argon2` (or at least bcrypt with explicit rounds); document the migration of existing hashes.
- [x] Set secure cookie attributes (`SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`, `SESSION_COOKIE_SAMESITE='Lax'`) when not in DEBUG.
- [x] Add `Content-Security-Policy`, `X-Frame-Options=DENY`, `Referrer-Policy=strict-origin-when-cross-origin`, `Permissions-Policy`, and HSTS via Flask-Talisman.
- [ ] Audit `services/compiler.py` for sandbox escape: drop privileges, mount tmpfs, set ulimits/cgroups, disable network in the child process, kill on wall-clock timeout (not just CPU).
- [ ] Whitelist compile/run flags; reject user-controlled headers, includes outside `<stdio.h>/<stdlib.h>/<string.h>`, and `system()`/`exec*()` calls before compilation.
- [x] Disable directory traversal in `_resolve_category_path`: validate exam_id and category against an allowlist derived from `exams.json`.
- [ ] Add an `auth.logout` confirmation step or POST-only logout to prevent CSRF logout attacks.
- [ ] Run `pip-audit` / `safety` in CI on every PR; pin all transitive deps with `pip-tools` (`requirements.in` + `requirements.txt`).
- [ ] Add a `SECURITY.md` with vulnerability reporting instructions.

## Backend — Testing & CI

- [x] Create `tests/` package with `pytest` configuration (`conftest.py` providing app, client, db fixtures using SQLite in-memory).
- [x] Unit tests for each grader method in `services/grader.py` (one test class per question type).
- [x] Tests for `QuestionLoader` covering: per-exam subdir layout, legacy flat layout, missing files, malformed JSON, unicode answers.
- [ ] Tests for `AdaptiveLearningService`: weak-category recommendation, session generation 70/30 split, progress update upserts.
- [x] Tests for `ExamService`: switching exams, default fallback, invalid exam id rejection.
- [ ] Route tests for `auth` (register, login, logout, login-required redirects).
- [ ] Route tests for `practice` (start session, navigate, submit, finish), including session-expiry edge cases.
- [ ] Route tests for `progress` (dashboard, stats, JSON endpoints if any).
- [ ] Snapshot test that every `.json` under `questions/<exam>/` validates against the schema.
- [x] Add a GitHub Actions workflow (`.github/workflows/ci.yml`): lint (ruff), type-check (mypy), test (pytest with coverage gate ≥ 80%). _(coverage gate deferred)_
- [ ] Add `pre-commit` hooks: ruff, ruff-format, mypy, end-of-file-fixer, trailing-whitespace, json-validate.
- [ ] Add a smoke-test script (`tests/smoke.sh`) that boots the app, registers a user, completes one question per question type, and asserts the response.

## Frontend — UX & Visual Design

- [ ] Decompose `templates/practice.html` (723 lines) into reusable Jinja partials: `_question_header.html`, `_options.html`, `_fill_blanks.html`, `_drag_drop.html`, `_recursive_trace.html`, `_feedback.html`.
- [ ] Split `static/css/style.css` (1544 lines) into purpose files (`base.css`, `forms.css`, `practice.css`, `dashboard.css`, `stats.css`) and bundle with a build step or `@import` carefully.
- [ ] Introduce CSS custom properties for spacing, colour, radius, shadow, and font-size; use them everywhere instead of hard-coded values.
- [ ] Add a dark-mode toggle that persists in `localStorage` and respects `prefers-color-scheme`.
- [ ] Replace ad-hoc hover/focus styling with a consistent focus ring (visible, ≥ 3:1 contrast against the background).
- [ ] Show progress within a session (e.g., `Q3 of 10` plus a thin top progress bar) and time-per-question.
- [ ] Add a question-card-skeleton loading state; never flash unstyled content during navigation.
- [ ] Disable the submit button while a request is in flight; show a small spinner inside the button.
- [ ] Provide explicit per-blank validation feedback (red ring + helper text) for `fill_blanks` and `drag_drop` instead of relying on a single banner.
- [ ] Animate the correct/incorrect feedback (subtle scale + colour) without breaking `prefers-reduced-motion`.
- [ ] Add an "explain answer" expandable section that shows the explanation and the source lecture wikilink (when applicable).
- [ ] Add a session-summary screen that shows accuracy, time, hardest topic, and a "review wrong answers" button.
- [ ] Add a per-exam landing page that lists categories with question counts and a recommended-next category badge.
- [ ] Move the exam switcher out of the header dropdown into the dashboard as a prominent course-card row.
- [ ] Add empty-state illustrations and copy for: no attempts yet, no progress data, no questions in a category.

## Frontend — Accessibility (WCAG 2.2 AA)

- [ ] Run `axe-core` against every page in CI; fix all critical/serious issues.
- [ ] Verify colour contrast ≥ 4.5:1 for body text and ≥ 3:1 for large text and interactive components.
- [ ] Add semantic landmarks: `<header>`, `<nav>`, `<main>`, `<footer>`, with one `<h1>` per page.
- [ ] Ensure every interactive control is reachable by keyboard and has a visible focus indicator.
- [ ] Add `aria-live` regions for dynamic feedback (correct/incorrect, hint reveal).
- [ ] Label all form inputs with `<label for=...>`; associate error messages via `aria-describedby`.
- [ ] Add `aria-pressed`/`aria-expanded` to toggles (hint button, exam switcher).
- [ ] Provide a "skip to main content" link as the first focusable element.
- [ ] Make drag-and-drop questions operable via keyboard (arrow keys to move tokens between zones).
- [ ] Add accessible names to all icon-only buttons.
- [ ] Verify the page is usable at 200% browser zoom without horizontal scroll.

## Frontend — Performance

- [ ] Audit with Lighthouse; target Performance ≥ 90 and Best Practices ≥ 95 on `/dashboard` and `/practice/question`.
- [ ] Lazy-load non-critical JS (`editor.js` only on practice pages).
- [ ] Defer or async all `<script>` tags in `base.html`.
- [ ] Inline critical CSS in `<head>` and load the rest with `media="print" onload="this.media='all'"`.
- [ ] Self-host fonts and preload them; remove third-party CDN font requests.
- [ ] Add `<link rel="preconnect">` / `<link rel="dns-prefetch">` for any external origins.
- [ ] Compress and dimensionally constrain images in `static/images/`; serve `webp`/`avif` with `<picture>`.
- [ ] Add a service worker for offline read-only access to last-seen questions and the dashboard shell.

## Frontend — Mobile & Responsive

- [ ] Audit every template at 360px wide; fix horizontal overflow on `practice.html` and `stats.html`.
- [ ] Make touch targets ≥ 44×44px (option buttons, hint button, navigation arrows).
- [ ] Replace hover-only affordances with click/tap equivalents.
- [ ] Ensure the question text area expands smoothly on small viewports; never crop code blocks.
- [ ] Add a sticky footer action bar on mobile with `Hint`, `Submit`, `Next`.
- [ ] Test in iOS Safari and Chrome Android; capture screenshots in `docs/screenshots/`.

## Frontend — JavaScript Quality

- [ ] Move inline `<script>` from templates into `static/js/` modules.
- [ ] Convert `auth.js`, `editor.js`, `practice_start.js` to ES modules; add a small bundler step (esbuild or vite) or use native `<script type="module">`.
- [ ] Add JSDoc types or migrate to TypeScript with `tsc --noEmit` in CI.
- [ ] Replace string concatenation HTML with `textContent`/`createElement` to remove latent XSS risk.
- [ ] Centralise `fetch` calls in a single `api.js` with consistent error handling, CSRF token injection, and JSON parsing.

## Content & Data Quality

- [x] **Unify question-JSON schemas so the runtime adapters can be deleted.** _(Done 2026-04-30. `scripts/migrate_questions.py` converted 229 `multiple_choice` options-dicts (5 agil_sysudv files) and 40 legacy nested `fill_blanks` (6 c_programming files) to canonical shape. Removed: `_normalize_options` in `services/question_loader.py`, the legacy branch in `grade_fill_blanks`, and the legacy template block in `templates/practice.html`. The validator promotes both non-canonical shapes to ERRORs (`non_canonical_options_dict`, `non_canonical_fill_blanks_nested`) and CI runs `--strict`. CSS rule on `.fill-blanks-inline .blank-text` (`white-space: pre-line`) preserves the per-prompt newlines in the migrated descriptions.)_
- [x] Add a JSON-schema validator for question files (jsonschema or pydantic) that rejects unknown shapes; wire it into the CI job below so regressions can't sneak in. _(`services/question_validator.py`; loader logs ERROR/WARNING and skips broken questions, raises with `STRICT_QUESTION_VALIDATION=1`. `scripts/validate_questions.py` runs in CI.)_
- [x] Add a CI job that runs `validate_improvements.py` (or its successor) on every PR and blocks merge on schema/duplicate-id failures. _(via `scripts/validate_questions.py` in `.github/workflows/ci.yml`; defaults to ERROR-gate, `--strict` also gates on WARNINGs.)_
- [ ] Enforce question-id namespacing per exam (e.g., `c_*`, `ds_*`, `oop_*`, `agil_*`); validator rejects collisions.
- [ ] Add a content-style guide to `docs/`: tone, language (Danish vs English), LaTeX usage, code formatting, length limits.
- [ ] Translate Danish/English mixed questions to a single language per exam, or add an `i18n` field per question with both.
- [ ] Add `source` and `lecture` metadata fields to every question (mirroring CCT-AAU frontmatter) for traceability.
- [ ] Add a "report a problem" button on every question that opens a prefilled GitHub issue.
- [ ] Track per-question difficulty calibration: log accuracy stats and flag questions whose observed difficulty diverges from the labelled one.
- [ ] Add at least 5 hard-difficulty questions per category that currently has fewer than 5 (`algorithms_correctness` is at 3, `data_structures_basic` at 3).

## Adaptive Learning

- [ ] Replace the fixed 70/30 weak-vs-review ratio in `services/adaptive.py` with a configurable spaced-repetition schedule (SM-2 or FSRS).
- [ ] Track per-question Elo / IRT difficulty rather than relying solely on the static `difficulty` label.
- [ ] Let users override the adaptive recommendation with "drill this topic" mode.
- [ ] Surface recommended next topic on the dashboard with reasoning ("you scored 40% on K3 Induction, last practiced 12 days ago").

## Observability

- [ ] Add structured JSON logging (`logging` + `python-json-logger`) with request id and user id.
- [x] Wire up `/healthz` (liveness) and `/readyz` (readiness with DB ping) endpoints.
- [ ] Add a Prometheus `/metrics` endpoint with per-route latency, error rate, and active-user gauges.
- [ ] Capture errors with Sentry (DSN via env var); scrub PII before sending.
- [ ] Log every grading decision (question id, user id, correct, time spent, hints used) for offline analysis.

## DevOps & Deployment

- [ ] **Replace the manual `docker buildx … --push` script with a GitHub Actions image-publish workflow.** Currently a local `build-and-push.sh` is the only path to ghcr.io, so deploys depend on one developer's laptop, builds aren't reproducible, and there's no SHA-tagged artefact for rollback. Workflow should: build the `Dockerfile` for `linux/amd64` (and `linux/arm64` if useful), log in via `GITHUB_TOKEN`, push `ghcr.io/jonasvindahl/imperative-training:latest` plus `:sha-<short>` and `:<git-tag>` on releases, and use SHA-pinned `docker/login-action` and `docker/build-push-action`. Trigger on push to `main` and on tags.
- [ ] Add a `:sha-<short>` tag to every published image so TrueNAS can pin to a specific build instead of the floating `:latest` (enables clean rollback by changing one field in the iX App).
- [ ] Document the deploy flow end-to-end in `DEPLOYMENT.md`: push to main → workflow builds & pushes → TrueNAS *Update* pulls new image → readiness check via `/readyz`. Include rollback steps.
- [ ] Add a smoke job after publish that pulls the freshly-pushed image, runs the container, and `curl`s `/healthz` + `/readyz` so a broken image never reaches `:latest`.
- [ ] Configure Dependabot (or Renovate) for the `Dockerfile` base image and the GitHub Actions versions used by the publish workflow.
- [ ] Multi-stage `Dockerfile`: separate build, install, and runtime stages; produce a < 200 MB final image with non-root user.
- [ ] Pin Python base image by digest; renovate-bot or dependabot to update.
- [ ] Replace `app.run(...)` for production with `gunicorn` invocation in `Dockerfile`/`docker-compose.yml`; document worker count guidance.
- [ ] Run gunicorn with `--worker-tmp-dir=/dev/shm` and a sensible `--timeout`.
- [ ] Define a `docker-compose.yml` for local dev that includes app + Postgres + Redis (for caching and Flask-Limiter).
- [ ] Migrate from SQLite to Postgres in production; document `DATABASE_URL` format.
- [ ] Add `.env.example` with every supported variable and a one-line description.
- [ ] Set up automated daily DB backups with retention policy in TrueNAS deployment docs.
- [ ] Add a `Makefile` (or `justfile`) with `make dev`, `make test`, `make lint`, `make docker-build`, `make deploy`.
- [ ] Document the deployment in a single `DEPLOYMENT.md` superseding the scattered `TRUENAS_*.md` files.

## Documentation

- [ ] Rewrite `README.md` to lead with a 60-second screenshot tour, then setup, then architecture.
- [ ] Add `CONTRIBUTING.md` covering branching, commit style, question-format conventions, and how to add a new exam.
- [ ] Add `ARCHITECTURE.md` with a system diagram (request → blueprint → service → DB) and module responsibilities.
- [ ] Document the question schema in `docs/question-schema.md`, one section per `type`.
- [ ] Add an "adding a new exam" tutorial that walks through `exams.json`, the `questions/<exam>/` layout, and how the loader auto-discovers categories.
- [ ] Generate API/service docs from docstrings with `pdoc` or `sphinx`; publish on GitHub Pages.

## Internationalisation

- [ ] Wrap all user-facing strings in templates with Flask-Babel `_()` and produce `da` and `en` `.po` files.
- [ ] Detect language from `Accept-Language` and let users override in settings.
- [ ] Localise dates, numbers, and difficulty labels.

## User Account & Profile

- [ ] Add a `/profile` page where users can change name, email, password, preferred language, and default exam.
- [ ] Add email verification on registration.
- [ ] Add password reset via email token.
- [ ] Add account deletion (GDPR), with explicit confirm and cascading attempt/progress deletes.
- [ ] Export user data as JSON on demand (GDPR portability).

## Power-User Features

- [ ] Bookmark / favourite questions; show them as a virtual category.
- [ ] "Mistakes only" practice mode that pulls questions the user has answered incorrectly in the last N days.
- [ ] Timed exam mode (e.g., 30 questions in 45 minutes) that mimics the real exam, with no hints.
- [ ] Leaderboards (opt-in) per exam and per category.
- [ ] Streak tracking and gentle reminders ("you have practiced 4 days in a row").

## Refactor / Cleanup Debt

- [x] Audit which of the `improve_*.py` scripts at the repo root are still relevant; archive the rest under `scripts/legacy/` or delete.
- [x] Move `BEFORE_AFTER_EXAMPLES.md`, `FINAL_SUMMARY.md`, `IMPROVEMENT_REPORT.md`, `MASSIVE_EXPANSION_SUMMARY.md`, `EXAM_QUESTIONS_EXPANSION.md`, `PROJECT_STATUS.md` into `docs/history/` to keep the root clean.
- [ ] Resolve duplication between `README.md` and `README_TRUENAS.md`; one canonical README + a deployment doc.
- [ ] Run a dead-code audit (`vulture`); remove unused functions and imports.
- [x] Add `ruff` and run `ruff check --fix .`; commit the diff.
- [ ] Add `ruff format .` (or `black`) and commit; configure `pre-commit` to keep formatting enforced.

---

## Suggested Skills To Run Before Picking Tasks

- `audit` — technical quality pass across accessibility, performance, security to baseline current state and prioritise.
- `code-quality` — comprehensive review of services and routes for clean-code violations.
- `owasp-security` — security-focused pass to confirm and expand the security backlog above.
- `optimize` — UI performance pass to validate the frontend perf backlog.
- `harden` — error handling, empty states, loading states pass on every template.
- `polish` — final visual pass once `harden` and `audit` items land.
- `critique` — UX evaluation of dashboard, practice, and stats pages to refine the visual-design backlog.
- `test-master` — generate the missing `tests/` skeleton.
