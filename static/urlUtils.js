function getAnchor() {
	return location.hash.substring(1);
}

function getQueryObject(defaultParams) {
	var search = location.search.substring(1);
		if(search) {
		var anchorList = search.split('#');
		if (anchorList.length > 0) {
			anchor = anchorList.pop()
		}
		var searchObj = JSON.parse('{"' + decodeURI(search).replace(/"/g, '\\"').replace(/&/g, '","').replace(/=/g,'":"') + '"}');

		var queryObj = {}
		for (const [key, value] of Object.entries(searchObj)) {
		  queryObj[key] = value.split(",");
		}
		for (const [key, value] of Object.entries(defaultParams)) {
			if(key in queryObj == false) {
				queryObj[key] = value;
			}
		}
		return queryObj;
	}
	if (defaultParams != undefined) {
		return defaultParams;
	}
	return {};
}

function toQueryString(queryObj) {
	searchObjs = [];

	for (const [key, value] of Object.entries(queryObj)) {
		if (Array.isArray(value)) {
			if(value.length > 0) {
				searchObjs.push(key + '=' + value.join(","));
			}
		} else {
			searchObjs.push(key + '=' + value);
		}
	}
	return '?' + searchObjs.join('&');

}

function updateUrl(queryObj, anchorStr) {
	var qs = toQueryString(queryObj);
	if(anchorStr != undefined) {
		qs = qs + '#' + anchorStr;
	}
	window.history.pushState(null, null, qs)
}

function isScrolledIntoView(el) {
    var rect = el.getBoundingClientRect();
    var elemTop = rect.top;
    var elemBottom = rect.bottom;

    // Only completely visible elements return true:
    var isVisible = (elemTop >= 0) && (elemBottom <= window.innerHeight);
    // Partially visible elements return true:
    //isVisible = elemTop < window.innerHeight && elemBottom >= 0;
    return isVisible;
}
