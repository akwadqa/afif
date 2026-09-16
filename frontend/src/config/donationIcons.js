// Inline heroicons-outline paths keyed by Donation Program.icon_key, following the same
// svgPath + v-html pattern already used in AppSidebar.vue (this app has no icon library).
export const programIcons = {
  education:
    '<path stroke-linecap="round" stroke-linejoin="round" d="M12 6.042A8.967 8.967 0 0 0 6 3.75c-1.052 0-2.062.18-3 .512v14.25A8.987 8.987 0 0 1 6 18c2.305 0 4.408.867 6 2.292m0-14.25a8.966 8.966 0 0 1 6-2.292c1.052 0 2.062.18 3 .512v14.25A8.987 8.987 0 0 0 18 18a8.967 8.967 0 0 0-6 2.292m0-14.25v14.25" />',
  health:
    '<path stroke-linecap="round" stroke-linejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />',
  social:
    '<path stroke-linecap="round" stroke-linejoin="round" d="M18 18.72a9.094 9.094 0 0 0 3.741-.479 3 3 0 0 0-4.682-2.72m.94 3.198.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0 1 12 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 0 1 6 18.719m12 0a5.971 5.971 0 0 0-.941-3.197m0 0A5.995 5.995 0 0 0 12 12.75a5.995 5.995 0 0 0-5.058 2.772m0 0a3 3 0 0 0-4.681 2.72 8.986 8.986 0 0 0 3.74.477m.94-3.197a5.971 5.971 0 0 0-.94 3.197M15 6.75a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm6 3a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Zm-13.5 0a2.25 2.25 0 1 1-4.5 0 2.25 2.25 0 0 1 4.5 0Z" />',
  relief:
    '<path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75 11.25 15 15 9.75M12 3c2.755 0 5.455.232 8.083.678.533.09.917.556.917 1.096v3.986c0 6.592-4.973 10.937-8.823 12.564a.72.72 0 0 1-.354 0C7.973 19.696 3 15.35 3 8.76V4.774c0-.54.384-1.007.917-1.096A48.32 48.32 0 0 1 12 3Z" />',
  empowerment_training:
    '<path stroke-linecap="round" stroke-linejoin="round" d="M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-.189m-1.5.189a6.01 6.01 0 0 1-1.5-.189m3.75 7.478a12.06 12.06 0 0 1-4.5 0m3.75 2.383a14.406 14.406 0 0 1-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 1 0-7.517 0c.85.493 1.509 1.333 1.509 2.316V18" />',
  seasonal:
    '<path stroke-linecap="round" stroke-linejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 0 1 2.25-2.25h13.5A2.25 2.25 0 0 1 21 7.5v11.25m-18 0A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75m-18 0V11.25a2.25 2.25 0 0 1 2.25-2.25h13.5a2.25 2.25 0 0 1 2.25 2.25v7.5" />',
  orphan_care:
    '<path stroke-linecap="round" stroke-linejoin="round" d="M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.649M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" />',
}

export const locationIcon =
  '<path stroke-linecap="round" stroke-linejoin="round" d="M3 3v1.5M3 21v-6m0 0 2.77-.693a9 9 0 0 1 6.208.682l.108.054a9 9 0 0 0 6.086.71l3.114-.732a48.524 48.524 0 0 1-.005-10.499l-3.11.732a9 9 0 0 1-6.085-.711l-.108-.054a9 9 0 0 0-6.208-.682L3 4.5M3 15V4.5" />'

// Simplified two-tone Qatar flag (maroon field, serrated white hoist band) - used as a
// standalone <svg> markup (fill-based) rather than the stroke `<path>` icons above.
export const qatarFlagSvg =
  '<svg viewBox="0 0 25 25" xmlns="http://www.w3.org/2000/svg" width="100%" height="100%">' +
  '<rect x="0.5" y="0.5" width="24" height="24" rx="4" fill="#8D1B3D" stroke="#EEEEEE" stroke-width="0.5" />' +
  '<path d="M0.5 4.5 L6 4.5 L3.5 8.5 L6 12.5 L3.5 16.5 L6 20.5 L0.5 20.5 Z" fill="#EEEEEE" />' +
  '</svg>'

export function getProgramIcon(iconKey) {
  return programIcons[iconKey] || programIcons.education
}

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
