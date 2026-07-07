import router from "@/router"
import { createResource } from "frappe-ui"
import { computed, reactive } from "vue"

import { userResource } from "./user"

// Frappe's template renderer replaces <!-- csrf_token --> in frontend.html with
// <script>frappe.csrf_token = "TOKEN";</script> on every request.
// frappe-ui's frappeRequest reads window.csrf_token for the X-Frappe-CSRF-Token header.
// This copies the Frappe-injected token to the window key frappe-ui expects.
function syncCsrfToken() {
	if (window.frappe && window.frappe.csrf_token) {
		window.csrf_token = window.frappe.csrf_token
	}
}
syncCsrfToken()

export function sessionUser() {
	const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
	let _sessionUser = cookies.get("user_id")
	if (_sessionUser === "Guest") {
		_sessionUser = null
	}
	return _sessionUser
}

export const session = reactive({
	login: createResource({
		url: "login",
		makeParams({ email, password }) {
			return {
				usr: email,
				pwd: password,
			}
		},
		onSuccess(data) {
			syncCsrfToken()
			userResource.reload()
			session.user = sessionUser()
			session.login.reset()
			router.replace(data.default_route || '/beneficiary-profile')
		},
	}),
	logout: createResource({
		url: "logout",
		onSuccess() {
			userResource.reset()
			session.user = sessionUser()
			router.replace({ name: "Login" })
		},
	}),
	user: sessionUser(),
	isLoggedIn: computed(() => !!session.user),
})
