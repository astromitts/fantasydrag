var queenSearchApp = angular.module('queenSearchModule', []);

queenSearchApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

queenSearchApp.controller(
	'queenSearchController',
	function($scope, $http, $sce) {

		$scope.sceSafe = function(html) {
			return $sce.trustAsHtml(html);
		}

		$scope.search = function(){
			var filters = {}
			if($scope.franchise) {
				filters['franchise'] = $scope.franchise
			}
			if($scope.queenName) {
				filters['name'] = $scope.queenName;
			}

			$http.put(
				'/api/queens/search/', 
				{'filters': filters}
			).then(
				function(response) {
					$scope.queens = response.data;
					$(function () {
			  			$('[data-toggle="tooltip"]').tooltip()
					})
				}
			)
		}

		$scope.dragRacesAsList = function(drag_races) {
			var drag_race_names = []
			angular.forEach(drag_races, function(drag_race){
					drag_race_names.push(drag_race.display_name)
				}
			);
			return drag_race_names.join(', ')
		}

		$scope.state = 'loading';
		$http.get('/api/queens/search/').then(
			function(response) {
				$scope.queens = response.data;
				$(function () {
		  			$('[data-toggle="tooltip"]').tooltip()
				})
				$scope.state = 'loaded';
			}
		)
	}
);

angular.bootstrap(document.getElementById("queenSearchModule"), ['queenSearchModule']);
