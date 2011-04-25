(function(panoptes, $) {

//  An abstract panel on the analytics page
var Panel = function(cssID) {
	this.cssID = cssID;
};

//  CSS identifiers for panels
Panel.prototype.css = {
	container: ".panel"
};

//  Update the contents of the panel with the given markup
Panel.prototype.updateMarkup = function(markup) {
	$(this.cssID).replaceWith(markup);
};

var panels = {
	css: {
		filterForm:  "#data-filters",
		formXDetail: "#data-filters #id_x_detail",
		loading:     "#ajax-loading",
		overlay:     "#ajax-loading .overlay",
		panels:      ".panel"
	},
};

//  Show a loading message before form submission
panels.beforePanelUpdateSubmit = function(formData, $form, options) {
	panoptes.analytics.showLoading();
};

//  Update the contents of the supporting panels with the returned markup
panels.updatePanelMarkup = function(data) {

	if (data.success) {
		for (var panel in data.markup.panels) {
			panoptes.analytics.panels[panel].updateMarkup(data.markup.panels[panel]);
		}
	}
	
	//  Reset the filter form's x-index
	$(panels.css.formXDetail).val('');
	panoptes.analytics.hideLoading();
};

//  Show a page-wide loading message
panoptes.analytics.showLoading = function() {
	$("body").prepend(panoptes.analytics.fragments["loading"]);
};

//  Hide the page-wide loading message
panoptes.analytics.hideLoading = function() {
	$(panels.css.loading).remove();
};

//  Update the contents of the current panels for the x-value detail
panoptes.analytics.showPanelDetail = function(xDetail) {
	
	$(panels.css.formXDetail).val(xDetail);
	
	//  Resubmit the filter form to the Ajax URL and use its response to update
	//  the panels' markup
	$(panels.css.filterForm).ajaxSubmit({
		beforeSubmit: panels.beforePanelUpdateSubmit,
		dataType:     'json',
		success:      panels.updatePanelMarkup,
		url:          panoptes.urls['update-supporting-panels']
	});
	
};

$(document).ready(function() {

	//  Instantiate any available panels
	var panel_slug;
	$(panels.css.panels).each(function(i, el) {
		panel_slug = panoptes.stringDataFromClass(el, "panel");
		panoptes.analytics.panels[panel_slug] = new Panel("#" + $(el).attr('id'));
	});
		
});

})(panoptes, jQuery);
