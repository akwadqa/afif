# Phase 13 — Assistance type on My Requests, and the browser QA

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** My Requests shows an "Assistance type" column next to "Type". Scholarship rows read «منحة الشيخ خالد بن ناصر» (P9-8). Then all of phases 9–13 are verified end to end in a real browser.

**Architecture:** A pure function maps a request row to its sub-category label key, using `SUBCATEGORY_MAP` from `requestCategories.js` (Phase 9, Task 3). `Request.vue` fetches the 7 sub-category fields and renders the column.

**Tech Stack:** Vue 3, Vitest, the agent-browser skill.

**Spec:** [plan.md §8](plan.md#8-client-feedback-2026-10-29)

## Global Constraints
- Column header: AR «نوع المساعدة الفرعي», EN "Assistance type". "Type" keeps its current label.
- A row without a sub-category shows `—`.

## Review Focus
- **A request of the Akwad test category, or one with an unknown sub-category value.** It must show `—` or the raw value, not break the row.
- **At phone width** the table must scroll inside its container, not the page.

---

### Task 1: The column

**Files:**
- Modify: `frontend/src/components/request/requestCategories.js`, `frontend/src/pages/Request.vue`, `frontend/src/locales/translations.js`
- Test: `frontend/src/components/request/requestCategories.test.js`

**Interfaces:**
- Consumes: `SUBCATEGORY_MAP` (Phase 9).
- Produces: `SUBCATEGORY_FIELDS: string[]` (the 7 field names) and `getAssistanceTypeKey(row): string`.
  - It returns `'sidebar.scholarship'` when `row.is_scholarship`.
  - Otherwise, when the row's category has a sub-category value, it returns `request.subtypes.<key>.<value>`.
  - Otherwise it returns `''`.

- [ ] **Step 1: Write the failing tests.**
  - A scholarship row → `'sidebar.scholarship'`.
  - `{ request_category: 'Medical Assistance', medical_assistance: 'Medication' }` → `'request.subtypes.medical.Medication'`.
  - No sub-category → `''`.
  - An unknown category → `''`.
- [ ] **Step 2: Run `yarn test requestCategories`.** FAIL.
- [ ] **Step 3: Implement.** `Request.vue` adds `is_scholarship` and `...SUBCATEGORY_FIELDS` to the `get_list` fields. Add the header after `type` and the cell `{{ key ? t(key) : '—' }}`. Add the i18n key `myRequests.columns.assistanceType`.
- [ ] **Step 4: Run `yarn test` and `yarn build`.** PASS.
- [ ] **Step 5: Commit.** `feat(requests): show the assistance type on My Requests`

### Task 2: Browser QA (agent-browser)

Load the `agent-browser` skill. The live gunicorn needs `bench restart` (sudo); if that isn't available, start a temporary `bench serve --port 8010` and stop it afterwards, as in Phase 8. Run `yarn build` first. Browser runs need `libasound.so.2` (see the progress.md blockers).

Take a screenshot at each check, in AR. Repeat scenarios 1, 3 and 6 in EN and at phone width (390px). Save the screenshots to the session scratchpad and list them in progress.md.

| # | Scenario | Expected |
|---|---|---|
| 1 | Signed in as a beneficiary, look at the sidebar | No scholarship item |
| 2 | Signed out, open `/scholarship`, sign in. Then, with a new user: `/scholarship` → Register → verify → sign in | Each lands on `/scholarship` |
| 3 | A new user runs the wizard | Marital status offers only أعزب; step 4 shows the consents only; step 5 has the 4 required uploads and «مرفقات أخرى»; submit succeeds |
| 4 | In the desk, open that request and its registration | The request has the 4 files plus the extras in the sidebar; the registration has no files and no scholarship-documents tab |
| 5 | As a Supervisor, set "Account Restricted" on it; reload the student's profile, `/scholarship` and `/request` | The red banner shows; no apply button; the create button is disabled with the reason |
| 6 | My Requests | The "Assistance type" column shows «منحة الشيخ خالد بن ناصر» for the scholarship row |
| 7 | A normal beneficiary: `/request` → new → Education | No Scholarship option |
| 8 | A scholarship student whose last request was rejected yesterday | Apply again is enabled and the submit succeeds |
| 9 | The profile of the scholarship user from scenario 3 | Step 5 shows the request documents as links, read only |

- [ ] **Step 1:** Run the scenarios. Record pass/fail and the evidence in progress.md.
- [ ] **Step 2:** Fix any failure in its owning phase's files (systematic-debugging), with a regression test.
- [ ] **Step 3: Whole-branch review** (superpowers:requesting-code-review) on `upstream/master..feature/scholarship-flow`, limited to the phase 9–13 commits.
- [ ] **Step 4: Commit the progress.** `docs(scholarship): log phases 9-13 progress`

## Done when
- Every scenario passes.
- The review findings are fixed or answered.
- `progress.md` is up to date.
