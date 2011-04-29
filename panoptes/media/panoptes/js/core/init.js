(function(window) {

	var panoptes = {};

	//  Extracts a data value from a class name on an object as a string, or
	//  null if no suitable class name could be found.  Data value are
	//  contained in class names using a "class-name__data" pattern.
	panoptes.dataFromClass = function(el, className) {
		var data = null, matches=[];
		if (el && $(el).attr('class')) {
			var classes = $(el).attr('class').split(/\s+/);
			for (var i=0; i < classes.length; i++) {
				matches = classes[i].split("__");
				if (matches.length == 2 && matches[0] == className) {
					data = matches[1];
					break;
				}
			}
		}
		return data;
	};

	//  Returns a value in a class as an integer
	panoptes.intDataFromClass = function(el, className) {
		return parseInt(panoptes.dataFromClass(el, className));
	};

	//  Returns a value in a class as a string
	panoptes.stringDataFromClass = function(el, className) {
		return panoptes.dataFromClass(el, className);
	};

	//  Container for URLs, generally used in Ajax calls
	panoptes.urls = {};

	window.panoptes = panoptes;

})(window);
