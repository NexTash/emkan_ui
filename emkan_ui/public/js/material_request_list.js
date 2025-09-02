frappe.listview_settings['Material Request'] = {
    onload: function(listview) {
        let interval = setInterval(() => {
            let $dropdown = $(listview.page.wrapper).find('.dropdown-menu');
            
            if ($dropdown.length) {
                if (!$dropdown.find('[data-view="MRList"]').length) {
                    $dropdown.append(`
                        <li data-view="MRList">
                            <a class="grey-link dropdown-item" href="#" onclick="frappe.set_route('query-report', 'MRList With Approval Date'); return false;">
                                <span class="menu-item-icon">
                                    <svg class="icon icon-sm" aria-hidden="true">
                                        <use href="#icon-small-file"></use>
                                    </svg>
                                </span>
                                <span class="menu-item-label" data-label="COO%20Approval%20Report">
                                    <span><span class="alt-underline">C</span>OO Approval Report</span>
                                </span>
                            </a>
                        </li>
                    `);
                }

                clearInterval(interval);
            }
        }, 500);
    }
};
