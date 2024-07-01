frappe.ready(function() {
    function checkRegistrationAndUpdateButton() {
        if ($('body').data('path') === 'beneficiary-request3/list') {
            frappe.call({
                method: "frappe.client.get_list",
                args: {
                    doctype: "Beneficiaries Registration",
                    fields: ["name"],
                    filters: {
                        status: "Accepted",
                        user: frappe.session.user
                    },
                    limit_page_length: 1
                },
                callback: function(r) {
                    console.log(r.message)
                    if (r.message && r.message.length > 0) {
                        $('.web-list-actions a.button-new').text('New Aid Request').show();
                    } else {
                        $('.web-list-actions a.button-new').hide();
                    }
                }
            });
        }
    }

    checkRegistrationAndUpdateButton();

    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            mutation.addedNodes.forEach(function(node) {
                if (node.nodeType === 1 && $(node).hasClass('no-result')) {
                    if ($('body').data('path') === 'registration-afif2/list') {
                        $(node).css('flex-direction', 'column');

                        // Check if the HTML tag has dir="rtl"
                        let isRTL = $('html').attr('dir') === 'rtl';
                        let custom_text = isRTL ?
                        $(`<p style="text-align: center; margin-top: 20px; margin-bottom: 40px;">حتى تتمكن من التقدم لطلب مساعدة، يجب تسجيل نفسك كمستفيد. بعد التسجيل كمستفيد، تذهب بياناتك للادارة للتحقق والاعتماد. يمكنك بعد اعتماد تسجيلك كمستفيد من التقدم بطلب مساعدة.</p>`) :
                            $(`<p style="text-align: center; margin-top: 20px; margin-bottom: 40px;">In order to apply for assistance, you must register yourself as a beneficiary. After registering as a beneficiary, your data goes to the administration for verification and approval. After your registration as a beneficiary is approved, you can apply for assistance.</p>`);

                        $(node).prepend(custom_text);
                    }
                }
            });
        });
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});
