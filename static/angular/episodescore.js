var episodeScoreApp = angular.module('episodeScoreModule', []);

episodeScoreApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

episodeScoreApp.controller(
	'episodeScoreController',
	function($scope, $http) {

		$scope.episodeId = document.getElementById('id_episodeId').value;

		$scope.setEpisodeProperties = function(responseData) {
			$scope.episode = {
				'pk': responseData.pk,
				'is_scored': responseData.is_scored,
				'title': responseData.title,
				'number': responseData.number
			}
		}

		$scope.addScore = function(rule, queen){
			$http.put(
				'/api/episode/' + $scope.episodeId + '/score/', 
				{
					'episode': $scope.episodeId,
					'queen': $scope.currentQueen.pk,
					'rule': $scope.currentRule.pk
				}
			).then(function pushScore(response){
					$scope.scores.unshift(response.data);
				}
			)
		}

		$scope.updateCurrentRule = function() {
			var selected = document.getElementById('id_rule');
			var selectedId = selected.options[selected.selectedIndex].value;
			$scope.currentRule = $scope.rules[selectedId];
		}

		$scope.updateCurrentQueen = function() {
			var selected = document.getElementById('id_queen');
			var selectedId = selected.options[selected.selectedIndex].value;
			$scope.currentQueen = $scope.queens[selectedId];
		}

		$scope.deleteScore = function(score) {
			$http.delete(
				'/api/episode/' + $scope.episodeId + '/score/' + score.pk + '/delete/', 
			).then(function pushScore(response){
					$scope.scores.splice($scope.scores.indexOf(score), 1);
				}
			)
		}

		$scope.patchEpisode = function(data) {
			$http.patch(
				'/api/episode/' + $scope.episodeId + '/score/',
				data 
			).then(function updateEpisode(response){
					$scope.setEpisodeProperties(response.data)
				}
			)
		}

		$http.get('/api/episode/' + $scope.episodeId + '/score/').then(function setAlerts(response){
			$scope.setEpisodeProperties(response.data)
			$scope.queens = response.data.queens;
			$scope.scores = response.data.scores;
			$scope.rules = response.data.rules;
			$scope.currentQueen = null;
			$scope.currentRule = null;
		});

	}
);

angular.bootstrap(document.getElementById("episodeScoreModule"), ['episodeScoreModule']);
