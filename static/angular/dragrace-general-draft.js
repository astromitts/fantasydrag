var generalDraftApp = angular.module('generalDraftModule', []);

generalDraftApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

generalDraftApp.controller(
	'generalDraftController',
	function($scope, $http) {	

		$scope.dragRaceId = document.getElementById('id_dragraceId').value;
		$scope.selectedCount = 0;

		$scope.toggleQueen = function(queen) {
			$scope.successMessage = null;
			$scope.errorMessage = null;
			if (queen.isSelected) {
				$scope.selectedQueens.splice($scope.selectedQueens.indexOf(queen), 1);
				queen.isSelected = false;
				$scope.selectedCount -= 1;
			} else if($scope.selectedCount < $scope.cap) {
				$scope.selectedQueens.push(queen);
				queen.isSelected = true;
				$scope.selectedCount += 1;
			}
		}

		$scope.submit = function() {
			$scope.successMessage = null;
			$scope.errorMessage = null;
			$http.post(
				'/api/dragrace/' + $scope.dragRaceId + '/generalpanel/',
				{'queens': $scope.selectedQueens}
			).then(
				function(response) {
					if (response.data.status == 'ok') {
						$scope.successMessage = response.data.message;
					} else {
						$scope.errorMessage = response.data.message;
					}
				}
			);
		}

		$http.get('/api/dragrace/' + $scope.dragRaceId + '/generalpanel/').then(
			function(response) {
				$scope.dragRace = response.data.drag_race;
				$scope.selectedQueens = [];
				$scope.selectedQueenPks = [];
				response.data.selected_queens.forEach(function(queen){
					$scope.selectedQueenPks.push(parseInt(queen.pk));
				});
				
				angular.forEach($scope.dragRace.queens, function(queen){
					if($scope.selectedQueenPks.indexOf(parseInt(queen.pk)) >= 0){
						queen.isSelected = true;
						$scope.selectedCount += 1;
						$scope.selectedQueens.push(queen);
					} else {
						queen.isSelected = false;
					}
				});
				$scope.cap = response.data.drag_race.general_draft_allowance;
			}
		);
	}
);

angular.bootstrap(document.getElementById("generalDraftModule"), ['generalDraftModule']);
