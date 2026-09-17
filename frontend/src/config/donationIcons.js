// Fallback heroicons-outline path used when a Donation Program has no uploaded
// icon image, following the same svgPath + v-html pattern already used in
// AppSidebar.vue (this app has no icon library).
export const programIconFallback =
  '<path stroke-linecap="round" stroke-linejoin="round" d="M11.48 3.499a.562.562 0 0 1 1.04 0l2.125 5.111a.563.563 0 0 0 .475.345l5.518.442c.499.04.701.663.321.988l-4.204 3.602a.563.563 0 0 0-.182.557l1.285 5.385a.562.562 0 0 1-.84.61l-4.725-2.885a.562.562 0 0 0-.586 0L6.982 20.54a.562.562 0 0 1-.84-.61l1.285-5.386a.562.562 0 0 0-.182-.557l-4.204-3.602a.562.562 0 0 1 .321-.988l5.518-.442a.563.563 0 0 0 .475-.345L11.48 3.5Z" />'

export const locationIcon =
  '<path stroke-linecap="round" stroke-linejoin="round" d="M3 3v1.5M3 21v-6m0 0 2.77-.693a9 9 0 0 1 6.208.682l.108.054a9 9 0 0 0 6.086.71l3.114-.732a48.524 48.524 0 0 1-.005-10.499l-3.11.732a9 9 0 0 1-6.085-.711l-.108-.054a9 9 0 0 0-6.208-.682L3 4.5M3 15V4.5" />'

// Simplified two-tone Qatar flag (maroon field, serrated white hoist band) - used as a
// standalone <svg> markup (fill-based) rather than the stroke `<path>` icons above.
export const qatarFlagSvg =
  '<svg viewBox="0 0 25 25" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">' +
  '<rect x="0.5" y="0.5" width="24" height="24" rx="4" fill="#8D1B3D" stroke="#EEEEEE" stroke-width="0.5" />' +
  '<path d="M0.5 4.5 L6 4.5 L3.5 8.5 L6 12.5 L3.5 16.5 L6 20.5 L0.5 20.5 Z" fill="#EEEEEE" />' +
  '</svg>'

// 2x2 grid glyph used for the "All" filter button — drawn as four filled
// squares (not a stroke path) so it can share the same v-html slot.
export const gridIconSvg =
  '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="currentColor">' +
  '<rect x="3" y="3" width="7.5" height="7.5" rx="1.5" />' +
  '<rect x="13.5" y="3" width="7.5" height="7.5" rx="1.5" />' +
  '<rect x="3" y="13.5" width="7.5" height="7.5" rx="1.5" />' +
  '<rect x="13.5" y="13.5" width="7.5" height="7.5" rx="1.5" />' +
  '</svg>'

// Shield-check glyph for the "no administrative fees" trust badge.
export const noFeesIconSvg =
  '<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%" fill="currentColor">' +
  '<path d="M12 2.25 4.5 5.25v6c0 5.14 3.24 9.53 7.5 10.5 4.26-.97 7.5-5.36 7.5-10.5v-6L12 2.25Zm-1.19 12.44L7.5 11.38l1.06-1.06 2.25 2.25 4.63-4.63 1.06 1.06-5.69 5.69Z" />' +
  '</svg>'
