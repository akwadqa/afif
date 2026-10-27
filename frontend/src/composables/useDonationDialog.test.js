// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from "vitest"
import { createMemoryHistory, createRouter } from "vue-router"

const router = createRouter({
	history: createMemoryHistory(),
	routes: [{ path: "/donate", component: {} }],
})

vi.mock("@/router", () => ({ default: router }))
vi.mock("@/data/donation", () => ({ isProjectClosed: (project) => project?.status === "Closed" }))

const { useDonationDialog } = await import("./useDonationDialog")

const openProject = { name: "abc123", slug: "wheelchairs", status: "Open" }
const closedProject = { name: "closed1", slug: "school-bag", status: "Closed" }

async function settle() {
	await router.isReady()
	await new Promise((resolve) => setTimeout(resolve))
}

describe("useDonationDialog", () => {
	const dialog = useDonationDialog()

	beforeEach(async () => {
		dialog.isOpen.value = false
		await router.replace("/donate?category=education")
		await settle()
	})

	it("shows only the project while open and restores the category when closed", async () => {
		dialog.openDonationDialog(openProject)
		await settle()
		expect(router.currentRoute.value.fullPath).toBe("/donate?donate=wheelchairs")

		dialog.closeDonationDialog()
		await settle()
		expect(router.currentRoute.value.fullPath).toBe("/donate?category=education")
	})

	it("opens the dialog for a shared ?donate= link", async () => {
		await router.replace("/donate?donate=wheelchairs")

		dialog.openFromQuery([openProject])

		expect(dialog.isOpen.value).toBe(true)
		expect(dialog.activeProject.value).toEqual(openProject)
	})

	it("drops ?donate= when the project is closed or missing", async () => {
		await router.replace("/donate?category=education&donate=school-bag")
		dialog.openFromQuery([closedProject])
		await settle()
		expect(dialog.isOpen.value).toBe(false)
		expect(router.currentRoute.value.fullPath).toBe("/donate?category=education")

		await router.replace("/donate?donate=unknown")
		dialog.openFromQuery([openProject])
		await settle()
		expect(router.currentRoute.value.fullPath).toBe("/donate")
	})
})
