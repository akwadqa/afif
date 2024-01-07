frappe.ready(function() {
    function overridePreviousButton() {
        let webForm = frappe.web_form;
        if (webForm && webForm.$previous_button) {
            webForm.$previous_button.off('click').on('click', function() {
                for (let idx = webForm.current_section; idx < webForm.sections.length; idx--) {
					let is_empty = webForm.is_previous_section_empty(idx);
					webForm.current_section =
					webForm.current_section > 0 ? webForm.current_section - 1 : webForm.current_section;
	
					if (!is_empty) {
						break;
					}
				}
				webForm.toggle_section();
				return false;
            });
        }
	}

	// Create an observer instance to monitor for changes
    let observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes && mutation.addedNodes.length > 0) {
                overridePreviousButton();
            }
        });
    });

    // Configuration of the observer
    let config = { childList: true, subtree: true };

    // Select the target node to observe (body or a more specific element if known)
    let target = document.body;

    // Start observing the target node
    observer.observe(target, config);
});