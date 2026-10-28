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

const currentPath = () => router.currentRoute.value.fullPath

describe("useDonationDialog", () => {
	const dialog = useDonationDialog()

	beforeEach(async () => {
		dialog.isOpen.value = false
		dialog.isOverLanding.value = false
		await router.replace("/donate?category=education")
	})

	it("swaps the category for the project while open over the landing page, and restores it on close", async () => {
		await dialog.openDonationDialog(openProject)
		expect(currentPath()).toBe("/donate?project=wheelchairs&donate=1")
		expect(dialog.isOverLanding.value).toBe(true)

		await dialog.closeDonationDialog()
		expect(currentPath()).toBe("/donate?category=education")
		expect(dialog.isOverLanding.value).toBe(false)
	})

	it("adds donate=1 on the project page and removes only that on close", async () => {
		await router.replace("/donate?project=wheelchairs&utm_source=sms")

		await dialog.openDonationDialog(openProject)
		expect(currentPath()).toBe("/donate?project=wheelchairs&utm_source=sms&donate=1")
		expect(dialog.isOverLanding.value).toBe(false)

		await dialog.closeDonationDialog()
		expect(currentPath()).toBe("/donate?project=wheelchairs&utm_source=sms")
	})

	it("opens the dialog for a shared donate=1 link", async () => {
		await router.replace("/donate?project=wheelchairs&donate=1")

		dialog.openFromQuery([openProject])

		expect(dialog.isOpen.value).toBe(true)
		expect(dialog.activeProject.value).toEqual(openProject)
	})

	it("drops donate=1 when the project is closed", async () => {
		await router.replace("/donate?project=school-bag&donate=1")

		dialog.openFromQuery([closedProject])
		await router.isReady()
		await new Promise((resolve) => setTimeout(resolve))

		expect(dialog.isOpen.value).toBe(false)
		expect(currentPath()).toBe("/donate?project=school-bag")
	})
})
