# Phase 2: Atomic upload in the SPA

## Goal

The SPA never leaves a request without its files: it uploads every file first, then inserts the request once with all attachment fields set.

## Files

- `frontend/src/components/request/BeneficiaryRequest.vue`: `handleSubmit` and `uploadFile`; remove `setFieldValue`
- `afif/public/frontend/`: the rebuilt assets

## Done when

`yarn lint` and `yarn build` pass. When an upload fails, no request is created. A full submission creates one request with every file attached.
