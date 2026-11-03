const AUTH_PATHS = ['/signin', '/register', '/forgot-password']

export function getSafeRedirect(value, fallback = '/beneficiary-profile') {
  if (typeof value !== 'string' || !value.startsWith('/')) return fallback
  if (value.startsWith('//') || value.startsWith('/\\')) return fallback

  const path = value.split(/[?#]/)[0]
  return AUTH_PATHS.includes(path) ? fallback : value
}
