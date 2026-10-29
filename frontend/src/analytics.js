// The measurement ID comes from the site's boot data (site_config: afif_ga_measurement_id),
// so analytics stays off in dev and on any site that hasn't configured it.
export function initAnalytics(measurementId = window.ga_measurement_id) {
	if (!measurementId) return

	const script = document.createElement("script")
	script.async = true
	script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`
	document.head.appendChild(script)

	window.dataLayer = window.dataLayer || []
	window.gtag = function gtag() {
		// biome-ignore lint/style/noArguments: gtag.js only processes Arguments objects, not arrays
		window.dataLayer.push(arguments)
	}
	window.gtag("js", new Date())
	window.gtag("set", getDonationCause(window.location.search))
	window.gtag("config", measurementId)
}

// Donation links carry the cause as ?category=... or ?project=...
export function getDonationCause(search) {
	const params = new URLSearchParams(search)
	const cause = {}
	if (params.get("category")) cause.donation_category = params.get("category")
	if (params.get("project")) cause.donation_project = params.get("project")
	return cause
}
