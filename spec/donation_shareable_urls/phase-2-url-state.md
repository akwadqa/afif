# Phase 2: URL state

**Goal:** the URL reflects the selected category, the project's category, and the open donate popup.

**Scope**
- `router.js`: `:category/project/:name` (`DonationProject`), plus the legacy `project/:name` (`DonationProjectLegacy`).
- `Donate.vue`: the filter is read from `route.query.category`, and an unknown slug is dropped.
- `DonationProjectDetail.vue`: redirect to the canonical URL; breadcrumb links to the filtered landing page; share copies the canonical URL.
- `DonationProjectCard.vue`: the Details link and share use the canonical URL.
- `DonationForm.vue`: its back link uses the legacy route, which then redirects.
- `useDonationDialog.js`: mirror the open project in `?donate=`, and `openFromQuery` opens the popup for shared links.

**Tests:** `useDonationDialog.test.js` (open/close changes the URL; a shared link opens the popup; a closed or unknown project drops the parameter).

**Done when:**
- Vitest passes and `yarn build` succeeds.
- In a browser: the chip, detail, legacy, breadcrumb and popup URLs behave as the plan describes.
