# Donation shareable URLs

## Requirement
- A category chosen on the donation landing page must show in the URL, so a copied link opens the same filter.
- The project detail URL must include the category. *Superseded in phase 3:* a shared project link shows only the project slug, and a shared category link shows only the category slug.
- Opening the donate popup must put the project ID in the URL, so GA can tell which category and project each donation started from.

## Decisions
- Category = **Donation Program**. Its `name` is a random hash, so it gets a readable `slug`.
- The slug is generated on save from the English translation of the title and stays editable. If the slug is empty and there's no English translation, the save fails. Generated slugs that collide get `-2`, `-3`, ….
- Landing page: `/donate?category=<slug>`. The chips use `router.replace`. An unknown slug falls back to "All" and the parameter is removed.
- Detail page (phase 3): `/donate/<project-slug>`. Project slugs are unique, capped at 60 characters at a word boundary, and can't use `form`, `success` or `project`. Legacy `/donate/project/<id>` links redirect. Everything stays under `/donate`, so `hooks.py` route rules don't change.
- Popup (phase 3): opening it sets `?donate=<project-slug>` and hides `?category=` while it's open. Closing it restores the category. A link that contains `?donate=` opens the popup. GA's existing `page_view` (on every `fullPath` change) records it, so GA stays URL-only with no code changes.
- Slug edits follow Frappe's website convention: a slug is generated once and never follows title edits.
  - If a project slug is edited by hand, an admin adds a Website Settings › Route Redirect for the old path.
  - Category slugs live in `?category=`, which Route Redirects can't match, so editing one breaks old category links.
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
