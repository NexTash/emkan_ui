// Workaround for a Frappe v15 bug in ControlAutocomplete, which MultiSelectPills

(function () {
	const Control = frappe.ui && frappe.ui.form && frappe.ui.form.ControlAutocomplete;
	if (!Control) return;

	const proto = Control.prototype;
	const original_parse_options = proto.parse_options;

	proto.get_input_value = function () {
		if (this.$input) {
			const label = this.$input.val();
			if (!label) {
				return label;
			}
			const item = this._data?.find((i) => i.label == label);
			return item ? item.value : label;
		}
	};

	proto.parse_options = function (options) {
		options = original_parse_options.call(this, options);
		if (Array.isArray(options)) {
			for (const o of options) {
				if (o && typeof o === "object" && !o.label) o.label = o.value;
			}
		}
		return options;
	};
})();
