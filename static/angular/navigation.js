var navApp = angular.module('navModule', []);

navApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

navApp.controller(
	'navController',
	function($scope, $http) {
		
	}
);

angular.bootstrap(document.getElementById("navModule"), ['navModule']);
