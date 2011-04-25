(function(panoptes, $) {

//  A hovering detail attached to a point on a bar chart
var Detail = function (point) {
	
	this.$point = $(point);
	this.id = this.$point.attr('id');
	
	this.title = this.$point.attr('title');
	if (this.title) {
		this.$point.removeAttr('title');
	}
		
	this.$detail = $("<p></p>");
	this.$detail.addClass(this.css.detailClass); 
	this.$detail.text(this.title);
	this.$point.find(this.css.yValue).append(this.$detail);
		
	this.xOffset = this.$detail.width() * 0.5;
	this.yOffset = this.$detail.height() * 2.25;  
};

//  CSS identifiers for the detail tooltip
Detail.prototype.css = {
	detailClass: "bar-chart-detail",
	yValue:      ".y"
};

//  Moves the detail to the given x and y coordinates
Detail.prototype.reposition = function(x, y) {
	this.$detail.offset({left: x - this.xOffset, top: y - this.yOffset});
};

//  Clears markup for the detail
Detail.prototype.remove = function() {
	this.$detail.remove();
	this.$point.attr('title', this.title);
};
	
//  A bar chart representing data in a two-column table of x- and y-values
var BarChart = function() {

	var css = {
		activeClass: "active",
		bar:         ".y",
		chart:       ".chart.bar",
		chosenClass: "chosen",
		detailClass: "bar-chart-detail",
		points:      ".points",
		point:       ".point",
		yDetail:     ".detail-link",
	};
	
	var details = {};
	
	var $detail = null;
	
	//  Show details for a single bar in the chart upon a click event
	var showDetails = function(e) {
		
		e.preventDefault();
		
		var $target = $(e.target);
		var $point = ($target.is(css.point)) ? $target : $target.parents(css.point);
		
		//  Load details for the x-value and mark it as selected
		panoptes.analytics.showPanelDetail(
			panoptes.stringDataFromClass($point, "point"));
		$(css.chart).find(css.point).removeClass(css.chosenClass);
		$point.addClass(css.chosenClass);
	};
	
	//  Get a detail tooltip for the given point, creating one if it doesn't exist
	var getOrCreateDetail = function(point) {
		var $point = $(point);
		var id = $point.attr('id');
		if (!details[id]) { details[id] = new Detail($point); }
		return details[id];
	};
	
	//  Provides details about the point being hovered over
	var showPointDetails = function(e) {

		$this = $(this);
		$this.addClass(css.activeClass);
		
		//  Render a hovering tooltip over the bar
		getOrCreateDetail($this);
		$this.mousemove(moveDetail);
	};
	
	//  Moves the detail with the user's mouse
	var moveDetail = function(e) {
		getOrCreateDetail(this).reposition(e.pageX, e.pageY);	
	};
	
	//  Hides details of a point
	var hidePointDetails = function(e) {
		
		var $this = $(this);
		$this.removeClass(css.activeClass);
		
		//  Hide the hovering detail
		var detail = getOrCreateDetail($this);
		detail.remove();
		delete details[detail.id];
		$this.unbind('mousemove', moveDetail);	
	};
	
	//  Make each y-value link show details in the supporting panels
	this.enableDetailLinks = function() {
		var $chart = $(css.chart);
		$chart.find(css.points).click(showDetails);
		$chart.find(css.point).hover(showPointDetails, hidePointDetails);
	};
	
};
	
$(document).ready(function() {

	var chart = new BarChart();
	chart.enableDetailLinks();

});
	
})(panoptes, jQuery);
