(function(panoptes, $) {

var analysis = {

	css: {
		dateInputs: ".dates input",
		filterForm: "#data-filters",
		timeInputs: ".times input",
		weekdays:   "#id_weekdays"
	}

};

$(document).ready(function() {

	//  Configure data and time pickers for the filter form
	var $form = $(analysis.css.filterForm);
	$form.find(analysis.css.timeInputs).timePicker();
	$form.find(analysis.css.dateInputs).datepicker();

});

})(panoptes, jQuery);
