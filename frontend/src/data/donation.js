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

// Project details keyed by `${project}:${lang}`
export const projectDetails = reactive({})

export const projectDetail = createResource({
	url: "afif.donation_api.get_project_detail",
	method: "GET",
})

export function loadProjectDetail(projectName, lang) {
	const key = `${projectName}:${lang}`
	if (projectDetails[key]) return
	projectDetail.submit(
		{ project_name: projectName, lang },
		{
			onSuccess(data) {
				projectDetails[key] = data
			},
		},
	)
}
