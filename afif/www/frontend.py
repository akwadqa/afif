import frappe

no_cache = 1


def get_context(context):
	# Kept in site_config (not Website Settings / google_analytics_id) so each site
	# carries its own ID without also enabling Frappe's legacy GA script on desk/web pages.
	context.boot = {"ga_measurement_id": frappe.conf.get("afif_ga_measurement_id")}
