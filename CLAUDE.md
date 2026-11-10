# Afif app — Claude instructions

## App and site

- **App:** `afif` (Afif Charity, Qatar). Publisher: Akwad. Module: `Afif`.
- **Bench:** `/home/akwad/dev-afif-bench`. Apps installed: `frappe` (v16), `afif`, `akwad_frappe_fixes`.
- **Site:** `afif.akwad.qa`. Run commands with `bench --site afif.akwad.qa ...`.
- **Web server:** gunicorn under supervisor, with `--preload` on port 8001. Python changes (APIs, controllers) only go live after `bench restart`, which needs sudo. `bench execute` and `migrate` use fresh code, so they don't prove that the live site has the change.
- **Backend:** `afif/afif/` holds the main API (`api.py`, `donation_api.py`), the Dibsy payment gateway (`dibsy.py`) and hooks (`hooks.py`, `hooks_call.py`).
- **DocTypes** (`afif/afif/doctype/`):
  - Beneficiaries: Beneficiaries Registration, Beneficiary Request, Beneficiary Aid, Beneficiary Additional Document, Committee
  - Donations: Donation, Donation Program, Donation Project
  - Settings: Dibsy Settings, Sanadi Integration Settings
- **Reports:** `afif/afif/report/` (e.g. Donation Report).
- **Workspaces:** `Afif` and `Afif Accountant`.
- **Frontend:** `frontend/` is a Vue 3 + Frappe-UI + Tailwind SPA built with Vite and served at `/frontend`. Website route rules in `hooks.py` map routes such as `/signin` and `/register` to it.
  - Auth uses the Frappe session (`/api/method/login`). There is no custom auth API.
  - It is bilingual (Arabic RTL by default, plus English). All strings go through `useLanguage()` → `t('...')` from `src/locales/translations.js`.
  - Brand colour: `#34B0EE`.
  - Commands: `yarn dev`, `yarn build`, `yarn test`, `yarn lint` (Biome).

## New features: plan first

Before implementing any new feature (report, doctype, API, page, etc.):

1. Write a short plan as a Markdown file in `spec/` at the app root (`apps/afif/spec/`).
2. Name the file after the feature, in snake_case, e.g. `spec/donation_report.md`. Do not use generic names like `plan.md`.
3. Include what's needed to build it: the name, doctypes/fields involved, filters, columns, files to touch, and open questions.
4. Wait for the user to approve the plan before writing any code.

* Don't mention Claude as co-authors
* Always use semantic commit messages, and follow the conventional commit format.

## Planning / Spec-ing

Use tracer bullets, an idea from The Pragmatic Programmer. Write code that gets you feedback as fast as possible. A tracer bullet is a small slice of functionality that goes through every layer of the system (DocType → controller → API → client script/UI), so you can test and validate the approach early. Problems surface sooner, and the overall architecture is proven before a lot of time goes into development.

### Spec folder structure

Every new feature gets a plan broken into phases, and every phase gets its own plan. All of it lives in `spec/`, at the root of this app:

```
spec/
└── <feature-name>/
    ├── plan.md                 # overall plan: requirement, decisions, data model, affected areas, phases list
    ├── phase-1-<short-name>.md # detailed plan for phase 1 (scope, files to change, tests, done criteria)
    ├── phase-2-<short-name>.md
    ├── ...
    └── progress.md             # live progress log of the feature
```

* `plan.md` covers the requirement, the decisions made, the data model changes, what is affected (other DocTypes, ERPNext overrides, APIs, reports), go-live prerequisites, open items and the ordered list of phases. Each phase links to its own file.
* `phase-N-<name>.md` covers that phase's goal, scope, files to change, tests to add, and the criteria for calling it done. Write it before starting the phase.
* `progress.md` has a checklist of the phases with their status (`todo` / `in progress` / `done`), the commit(s) for each phase, deviations from the plan, and open issues or blockers. Update it at the end of every phase.

## Implementation Guidelines

* Work on the feature's own branch (e.g. `feature/walima`). If that branch already exists, commit directly to it. Don't create sub-branches, and never commit to `release/*` or `main`.
* Create a new branch only for a feature that doesn't have one yet. Name it with the prefixes `feature/`, `fix/`, `refactor/`, `chore/`, etc.
* Reconcile the spec and log the progress in `progress.md` after each phase of development.
* Commit after each meaningful phase.
* Commit the spec (`plan.md` + phase plans + `progress.md`) before the development commits.
* Use conventional commit messages (`feat: ...`, `fix: ...`).
* Use comments only when necessary, to explain "why?" and not "how?". The "how" must be clear from the code itself.
* Never modify existing patches. Add new ones to `patches/` and register them in `patches.txt`.
* Prefer the narrowest, upgrade-safe extension point (`doc_events`, `override_doctype_class`, Property Setters, fixtures) over monkey patches or global method overrides.
* Custom whitelisted endpoints return through `gen_response(status_code, message, data)`.

## Frontend / Backend Sync

* Whenever a new field is added to a backend DocType and that field is surfaced in the frontend (client scripts in `public/js`, `doctype_js`, portal pages in `www/`, or the mobile app API responses), handle it in the matching frontend code/API too, so the two stay in sync. This is a convention/reminder only. There is no automatic syncing mechanism, because the frontend and API payloads list fields explicitly.
* After changing anything in `hooks.py` or fixtures, run `migrate --skip-failing` and `clear-cache`.

## Regression tests

* When we fix a bug, add at least a unit test. Verify it before and after by temporarily reverting the fix, to make sure the test checks what is intended.
* Bigger features/workflows (checkout, delivery trip flow, sales order status workflow) must have integration tests that cover the full flow, and e2e Playwright tests when there is UI behaviour.
* Put tests in `afif/tests/` or next to the DocType (`doctype/<name>/test_<name>.py`).

## Commits, Pushing & Pull Requests

* The canonical repo is `akwadqa/afif` (git remote `upstream`).
* During development, commit directly to the feature branch and push it: `git push upstream feature/walima`. Don't open a PR per phase or per change.
* Changes stay on the feature branch only. Never merge, cherry-pick or push them into `release/*` or `main` unless explicitly asked.
* Open a PR only when the whole feature is done and the user asks for it: one PR from the feature branch to the target branch the user names, e.g. `gh pr create --repo akwadqa/afif --base main --head feature/walima`.
    * Before raising, sanity-check that the diff contains only the feature's files: `git diff --stat upstream/<base>..feature/walima`. A huge diff means the base is wrong. Fix it before opening the PR.
* Keep pull request descriptions stupid simple, and link the spec folder.
* Some formats:
    1. h2 Problem (1-2 sentences), h2 Solution: good for bugs, etc.
    2. h2 Why? h2 What? h2 How?: good for new features and enhancements

* Don't mention Claude as co-authors
* Always use semantic commit messages, and follow the conventional commit format.
6. Git and Pull Requests
Use Conventional Commits with appropriate types, such as feat, fix, refactor, test, docs, build, and chore.
Do not include AI co-author attribution, session information, or agent metadata in commits.
Follow the repository's established branching and review workflow.
Create a feature or fix branch when required by the project's workflow.
Commit meaningful, reviewable units of work.
Do not commit or push without the required authorization.
When working from a specification, keep the specification and progress record synchronized with the implementation.
Link the relevant issue in a pull request when applicable.
Include a clear summary of changes and instructions for testing in pull requests.
Create draft pull requests when required by the project's workflow.
* do not push all changes together in one commit, divide them according to its logic related
