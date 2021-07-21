var queenDetailApp = angular.module('queenDetailModule', []);

queenDetailApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

queenDetailApp.controller(
	'queenDetailController',
	function($scope, $http) {
		$scope.queenId = document.getElementById('id_queenId').value;
		$scope.state = 'loading';

		$http.get('/api/stats/queen/' + $scope.queenId + '/').then(
			function(response) {
				$scope.queen = response.data.queen;
				$scope.averageScore = response.data.stats.primary_stat_display;
				$scope.stats = response.data.stats.data;
				$scope.isScored = Object.keys($scope.stats.drag_races).length > 0;
				$scope.state = 'loaded';
			}
		);
	}
);

angular.bootstrap(document.getElementById("queenDetailModule"), ['queenDetailModule']);
