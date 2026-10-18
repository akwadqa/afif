// @vitest-environment jsdom
import { afterEach, describe, expect, it } from "vitest"
import { getDonationCause, initAnalytics } from "./analytics"

describe("getDonationCause", () => {
	it("maps category and project params to GA fields", () => {
		expect(getDonationCause("?category=zakat&project=water-wells")).toEqual({
			donation_category: "zakat",
			donation_project: "water-wells",
		})
	})

	it("returns nothing for links without a cause", () => {
		expect(getDonationCause("?utm_source=sms")).toEqual({})
	})
})

describe("initAnalytics", () => {
	afterEach(() => {
		document.head.innerHTML = ""
		window.gtag = undefined
		window.dataLayer = undefined
	})

	it("does nothing when the site has no measurement ID", () => {
		initAnalytics(null)

		expect(document.querySelector("script[src*='googletagmanager']")).toBeNull()
		expect(window.gtag).toBeUndefined()
	})

	it("loads gtag and configures the given measurement ID", () => {
		initAnalytics("G-TEST123")

		const script = document.querySelector("script[src*='googletagmanager']")
		expect(script.src).toContain("id=G-TEST123")
		expect(window.dataLayer.at(-1)[0]).toBe("config")
		expect(window.dataLayer.at(-1)[1]).toBe("G-TEST123")
	})
})
