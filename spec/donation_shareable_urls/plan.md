# Donation shareable URLs

## Requirement
- A category chosen on the donation landing page must show in the URL, so a copied link opens the same filter.
- The project detail URL must include the category. *Superseded in phases 3–4:* a shared project link shows only the project slug (`?project=`), and a shared category link shows only the category slug (`?category=`).
- Opening the donate popup must put the project ID in the URL, so GA can tell which category and project each donation started from.

## Decisions
- Category = **Donation Program**. Its `name` is a random hash, so it gets a readable `slug`.
- The slug is generated on save from the English translation of the title and stays editable. If the slug is empty and there's no English translation, the save fails. Generated slugs that collide get `-2`, `-3`, ….
- Landing page: `/donate?category=<slug>`. The chips use `router.replace`. An unknown slug falls back to "All" and the parameter is removed.
- Project page (phase 4): `/donate?project=<project-slug>`, the same way as `?category=`. Project slugs are unique and capped at 60 characters at a word boundary. Legacy `/donate/project/<id>` links redirect. Everything stays under `/donate`, so `hooks.py` route rules don't change.
- Popup (phase 4): opening it sets `?project=<slug>&donate=1`.
  - Opened from the landing page, the landing stays behind it, `?category=` is hidden, and closing it restores the landing URL.
  - A shared `donate=1` link opens the project page with the popup open.
  - GA's existing `page_view` (on every `fullPath` change) records it, so GA stays URL-only with no code changes. `analytics.js` already maps `?project=` to `donation_project`.
- Slug edits follow Frappe's website convention: a slug is generated once and never follows title edits.
  - Both slugs live in the query string, which Website Settings › Route Redirects can't match. Editing a slug therefore breaks links already shared, and the field description warns about this.
- The breadcrumb category link goes to the filtered landing page. The share buttons copy the canonical detail URL.

## Data model
- Donation Program and Donation Project: new `slug` (Data, unique, in search fields). The shared logic lives in `afif/donation_slug.py`.
- Patches `set_donation_program_slugs` and `set_donation_project_slugs` backfill existing records. They fall back to the record name when there's no usable title.

## Affected areas
- `donation_program.py/json`, `donation_api.py` (`get_donation_landing` and `get_project_detail` return the slug).
- Frontend: `router.js`, `Donate.vue`, `DonationProjectDetail.vue`, `DonationProjectCard.vue`, `DonationForm.vue`, `useDonationDialog.js`.

## Out of scope
- The duplicate GA setup (`analytics.js` plus the hard-coded ID in `useGoogleAnalytics.js`).
- GA purchase events.
- Storing the source URL on Donation.

## Phases
1. [Category slug](phase-1-category-slug.md)
2. [URL state](phase-2-url-state.md)
3. [Project slug](phase-3-project-slug.md)
4. [Query-string project URL](phase-4-query-project-url.md)
