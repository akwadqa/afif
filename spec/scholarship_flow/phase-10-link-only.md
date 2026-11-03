# Phase 10 — Reached only through the link

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `/scholarship` disappears from the sidebar. A signed-out visitor who opens the shared link, then signs in or registers, lands back on `/scholarship` (P9-1).

**Architecture:**
- The router guard puts the requested path in `?redirect=`.
- One pure helper, `getSafeRedirect(value, fallback)`, decides where to go after login, so the parameter can't send users off-site.
- Login and sign-up read the parameter through it.

**Tech Stack:** Vue 3, vue-router, frappe-ui, Vitest.

**Spec:** [plan.md §8](plan.md#8-client-feedback-2026-10-29)

## Global Constraints
- Default after login stays `/beneficiary-profile`; desk users still go to `/desk`.
- No new route; the scholarship route keeps `requiresAuth`.

## Review Focus
- An open redirect: `?redirect=//evil.com`, `?redirect=https://evil.com` or `?redirect=/\evil.com` must fall back to the default.
- Moving between Login and Register must keep the `redirect` parameter, so a new user who registers first still ends on the link.
- `redirect=/signin` must not loop. Fall back for the auth routes.

---

### Task 1: `getSafeRedirect` helper

**Files:**
- Create: `frontend/src/utils/safeRedirect.js`
- Test: `frontend/src/utils/safeRedirect.test.js`

**Interfaces:**
- Produces: `getSafeRedirect(value: unknown, fallback = '/beneficiary-profile'): string`.
  - It returns `value` only when `value` is a string that starts with `/`, does not start with `//` or `/\`, and is not one of `/signin`, `/register` or `/forgot-password` (with or without a query string).
  - In every other case it returns `fallback`.

- [ ] **Step 1: Write a table test.**
  - `'/scholarship'` → `'/scholarship'`.
  - `'/scholarship?x=1'` → kept.
  - `undefined`, `''`, `'scholarship'`, `'//evil.com'`, `'/\\evil.com'`, `'https://evil.com'`, `'/signin'` and `['/a']` → the fallback.
- [ ] **Step 2: Run `yarn test safeRedirect`.** It FAILS because the module is missing.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run it again.** PASS.
- [ ] **Step 5: Commit, together with Task 2.**

### Task 2: Wire the redirect, remove the sidebar item

**Files:**
- Modify:
  - `frontend/src/router.js` (the guard, lines ~118-128)
  - `frontend/src/data/session.js` (`login.onSuccess`)
  - `frontend/src/components/auth/RegisterFormPanel.vue` (`redirect_to`, line ~170)
  - the Login↔Register links (in `components/auth/*`, whichever renders them)
  - `frontend/src/components/sidebar/AppSidebar.vue` (delete the `sidebar.scholarship` item at lines ~140-144)

**Interfaces:**
- Consumes: `getSafeRedirect` (Task 1).

- [ ] **Step 1: Router guard.** When `requiresAuth` sends the visitor to Login: `next({ name: 'Login', query: { redirect: to.fullPath } })`. When a signed-in user opens Login or Register and there is a `redirect`, send them to `getSafeRedirect(to.query.redirect, '/beneficiary-profile')`.
- [ ] **Step 2: Login.** In `session.js`, the website-user branch calls `router.replace(getSafeRedirect(router.currentRoute.value.query.redirect))`.
- [ ] **Step 3: Sign-up.** `redirect_to: getSafeRedirect(route.query.redirect)`. The Login↔Register `router-link`s pass `query: route.query.redirect ? { redirect: route.query.redirect } : {}`.
- [ ] **Step 4: Delete the sidebar item.** Leave the unused `sidebar.scholarship` translation: the scholarship page and Phase 13 still use it.
- [ ] **Step 5: Run `yarn test` and `yarn build`.** Both pass.
- [ ] **Step 6: Commit.** `feat(scholarship): reach the scholarship only through its link`

## Done when
- The unit tests pass.
- The browser check (Phase 13 QA, scenarios 1–2) shows no sidebar item. The link → login → `/scholarship` round trip works, and so does link → register.
