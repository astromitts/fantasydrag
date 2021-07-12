var dashboardApp = angular.module('dashboardModule', []);

dashboardApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

dashboardApp.controller(
	'dashboardController',
	function($scope, $http) {
	}
);

angular.bootstrap(document.getElementById("dashboardModule"), ['dashboardModule']);
