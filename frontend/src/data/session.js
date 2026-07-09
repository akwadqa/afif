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
		onSuccess() {
			syncCsrfToken()
			userResource.reload()
			session.user = sessionUser()
			session.login.reset()
			const cookies = new URLSearchParams(document.cookie.split("; ").join("&"))
			if (cookies.get("system_user") === "yes") {
				window.location.href = '/desk'
			} else {
				// Frappe's `home_page` from the login response can be hijacked by unrelated
				// installed apps (get_default_path() picks up their add_to_apps_screen route),
				// so Website Users always go straight to the registration flow.
				router.replace('/beneficiary-profile')
			}
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
