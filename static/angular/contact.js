var contactApp = angular.module('contactModule', []);

contactApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

contactApp.controller(
	'contactController',
	function($scope, $http) {
		$scope.status = 'loaded';
	}
);

angular.bootstrap(document.getElementById("contactModule"), ['contactModule']);
