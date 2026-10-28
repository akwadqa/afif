# Progress: Request required attachments

| Phase | Status | Commits |
|---|---|---|
| 1. Server validation | done | fix: block beneficiary request submission without required attachments |
| 2. Atomic upload in the SPA | done | fix: upload request attachments before inserting the request |

## Deviations

- The tests patch `afif.hooks_call.before_insert_request`, because it requires the session user to own an Accepted registration, which these tests do not exercise.

- The built assets in `afif/public/frontend` are gitignored, so there is no build commit.

## Open issues

- **Python changes need `bench restart` (sudo)** before the live site enforces the check.
- **Not yet checked in a real browser.** The upload-then-insert flow has been verified only through `yarn build` and by reading Frappe's `upload_file` and `attach_files_to_document`.
- **Server and SPA upload rules don't match.** The SPA allows `audio/ogg` and `video/webm`, but `upload_file` rejects them for non-desk users. This was already the case before this fix.
