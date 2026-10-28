# Phase 4: Query-string project URL

**Goal:** the project page is addressed like the category filter, with `/donate?project=<slug>`. The open popup adds `&donate=1`.

**Scope**
- `router.js`:
  - `/donate` renders `DonateHome.vue`, which shows `DonationProjectDetail` when `?project=` is set and `Donate` otherwise.
  - The `/donate/:slug` route is removed. `/donate/project/<id>` still redirects.
- `DonationProjectDetail.vue` reads `route.query.project`. It redirects legacy links and drops `?category=`.
- `DonationProjectCard.vue`: the Details link and share use `?project=`.
- `useDonationDialog.js`:
  - Open sets `?project=<slug>&donate=1` and keeps other parameters (e.g. `utm_*`). From the landing page, `isOverLanding` keeps the landing rendered and its query is restored on close.
  - `openFromQuery` only acts on `donate=1`.
- Backend: reserved project slugs are removed, since slugs are no longer in the path.

**Tests**
- `useDonationDialog.test.js`:
  - Landing swap and restore.
  - On the project page only `donate=1` is toggled, and `utm_*` survives.
  - A shared link opens the popup.
  - A closed project drops `donate`.
- Backend slug tests updated.

**Done when:** the backend tests and Vitest pass, and `yarn build` succeeds.
