var episodeWildQueensApp = angular.module('episodeWildQueensModule', []);

episodeWildQueensApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

episodeWildQueensApp.controller(
	'episodeWildQueensController',
	function($scope, $http) {
		$scope.episodeId = document.getElementById('id_episodeId').value;
		$scope.allQueens = [];

		$scope.updateCurrentQueen = function() {
			var selected = document.getElementById('id_queen');
			var selectedId = selected.options[selected.selectedIndex].value;
			$scope.currentQueen = $scope.allQueens[selectedId];
		}

		$scope.updateCurrentType = function() {
			var selected = document.getElementById('id_appearance');
			var selectedId = selected.options[selected.selectedIndex].value;
			$scope.currentType = $scope.appearanceTypes[selectedId];
		}


		$scope.addAppearance = function(rule, queen){
			$http.put(
				'/api/episode/' + $scope.episodeId + '/appearances/', 
				{
					'episode': $scope.episodeId,
					'queen': $scope.currentQueen.pk,
					'appearance': $scope.currentType.pk
				}
			).then(function pushAppearance(response){
					$scope.appearances.unshift(response.data);
				}
			)
		}


		$scope.deleteAppearance = function(appearance){
			$http.delete(
				'/api/episode/' + $scope.episodeId + '/appearances/' + appearance.pk + '/delete/', 
			).then(function pushAppearance(response){
					$scope.appearances.splice($scope.appearances.indexOf(appearance), 1);
				}
			)
		}

		$http.get('/api/queens/').then(function(response){
			$scope.allQueens = response.data;
			$scope.currentQueen = null;
		});

		$http.get('/api/appearancetypes/').then(function(response){
			$scope.appearanceTypes = response.data;
			$scope.currentType = null;
		});

		$http.get('/api/episode/' + $scope.episodeId + '/appearances/').then(
			function(response) {
				$scope.appearances = response.data;
			}
		);

	}
);

angular.bootstrap(document.getElementById("episodeWildQueensModule"), ['episodeWildQueensModule']);
