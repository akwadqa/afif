# Donation shareable URLs

## Requirement
- A category chosen on the donation landing page must show in the URL, so a copied link opens the same filter.
- The project detail URL must include the category.
- Opening the donate popup must put the project ID in the URL, so GA can tell which category and project each donation started from.

## Decisions
- Category = **Donation Program**. Its `name` is a random hash, so it gets a readable `slug`.
- The slug is generated on save from the English translation of the title and stays editable. If the slug is empty and there's no English translation, the save fails. Generated slugs that collide get `-2`, `-3`, ….
- Landing page: `/donate?category=<slug>`. The chips use `router.replace`. An unknown slug falls back to "All" and the parameter is removed.
- Detail page: `/donate/<slug>/project/<id>`. Legacy `/donate/project/<id>` links and a wrong category both redirect to the canonical URL. Everything stays under `/donate`, so `hooks.py` route rules don't change.
- Popup: opening it adds `?donate=<project-id>` (on landing and detail), and closing it removes it. A link that contains `?donate=` opens the popup. GA's existing `page_view` (on every `fullPath` change) records it, so no GA code changes.
- The breadcrumb category link goes to the filtered landing page. The share buttons copy the canonical detail URL.

## Data model
- Donation Program: new `slug` (Data, unique, in list view, in search fields).
- Patch `set_donation_program_slugs` backfills existing programs. It falls back to the program name when there's no usable title.

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
