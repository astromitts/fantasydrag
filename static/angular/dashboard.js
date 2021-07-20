var dashboardApp = angular.module('dashboardModule', []);

dashboardApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

dashboardApp.controller(
	'dashboardController',
	function($scope, $http) {
		$scope.expandedEpisodes = [];
		$scope.expandedPanels = [];

		$scope.toggleEpisodeDraft = function(episode){
			if($scope.expandedEpisodes.indexOf(episode) !== -1) {
				$scope.expandedEpisodes.splice($scope.expandedEpisodes.indexOf(episode), 1);
			} else {
				$scope.expandedEpisodes.push(episode);
			}
		};

		$scope.togglePanel = function(panel){
			if($scope.expandedPanels.indexOf(panel) !== -1) {
				$scope.expandedPanels.splice($scope.expandedPanels.indexOf(panel), 1);
			} else {
				$scope.expandedPanels.push(panel);
			}
		};

		$scope.alert = function(message) {alert(message)};

		$http.get('/api/user/').then(function(response){
			$scope.user = response.data.user;
			$scope.featureFlags = response.data.flags;
			if ($scope.user.is_authenticated) {
				$http.get('/api/dashboard/').then(function(response){
					$scope.dragRaces = response.data.drag_races;

					$(function () {
		  				$('[data-toggle="tooltip"]').tooltip()
					})
				});
			}
		});
	}
);

angular.bootstrap(document.getElementById("dashboardModule"), ['dashboardModule']);
