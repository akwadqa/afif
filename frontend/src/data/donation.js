import { reactive } from "vue"
import { createResource } from "frappe-ui"

// Module-level so the data outlives the page components: navigating back to a
// donation page reuses what was already loaded instead of calling the API again.
// A full page load (e.g. returning from the payment gateway) starts fresh.

export const donationLanding = createResource({
	url: "afif.donation_api.get_donation_landing",
	method: "GET",
})

export function loadDonationLanding(lang) {
	const sameLang = donationLanding.params?.lang === lang
	if (sameLang && (donationLanding.data || donationLanding.loading)) return
	donationLanding.submit({ lang })
}

// The server closes a project once its Required Amount is reached and rejects further donations
export function isProjectClosed(project) {
	return project?.status === "Closed"
}

// The project filled up while the donor was still on the form
export function isProjectClosedError(error) {
	return error?.exc_type === "ProjectClosedError"
}

export function isAmountExceedsRemainingError(error) {
	return error?.exc_type === "AmountExceedsRemainingError"
}

// create_donation returns the project's remaining amount as the response message alongside the error
export function getAmountExceedsMessage(error, t) {
	const remaining = error.messages?.find((message) => message?.remaining_amount != null)?.remaining_amount
	const message = t("donation.amountExceedsRemaining")
	if (remaining == null) return message
	return `${message} ${t("donation.maxDonation")} ${remaining} ${t("donation.currency")}`
}

// Project details keyed by `${slug or name}:${lang}`
export const projectDetails = reactive({})

export const projectDetail = createResource({
	url: "afif.donation_api.get_project_detail",
	method: "GET",
})

// Pass { slug } for project pages, or { name } for legacy links that still carry the ID
export function loadProjectDetail({ slug, name }, lang) {
	const key = `${slug || name}:${lang}`
	if (projectDetails[key]) return
	projectDetail.submit(
		{ ...(slug ? { slug } : { project_name: name }), lang },
		{
			onSuccess(data) {
				projectDetails[key] = data
				// A legacy link redirects to the slug URL, which can then reuse this result
				projectDetails[`${data.slug}:${lang}`] = data
			},
		},
	)
}
