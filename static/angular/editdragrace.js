var addEditDragRaceApp = angular.module('addEditDragRaceModule', []);

addEditDragRaceApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

addEditDragRaceApp.controller(
	'addEditDragRaceController',
	function($scope, $http, $window) {
		$scope.dragraceId = document.getElementById('id_dragrace_id').value;
		$scope.errors = [];
		$scope.successMessage = false;
		$scope.franchiseOptions = [
			'US', 'UK', 'Canada', 'Down Under'
		]

		$scope.typeOptions = ['standard', 'all star']

		$scope.dragRace = {
			'pk': $scope.dragraceId,
			'season': 1,
			'franchise': null,
			'type': null,
			'queens': [],
			'rules': []
		}

		$scope.newQueen = null;
		$scope.newRule = null;


		$scope.addExistingQueen = function(queen){
			$scope.dragRace.queens.push(JSON.parse(queen));
			document.getElementById('id_queens').value = '';
		}

		$scope.addNewQueen = function(){
			if($scope.newQueen) {
				$scope.dragRace.queens.unshift({"pk": null, "name": $scope.newQueen});
				$scope.newQueen = null;
			}
		}

		$scope.addNewRule = function(){
			if($scope.newRule) {
				$scope.dragRace.rules.unshift(
					{
						"pk": null, 
						"name": $scope.newRule,
						"description": '',
						"point_value": 0
					}
				);
				$scope.newRule = null;
			}
		}

		$scope.removeQueen = function(queen){
			$scope.dragRace.queens.splice($scope.dragRace.queens.indexOf(queen), 1);
		}

		$scope.removeRule = function(rule){
			$scope.dragRace.rules.splice($scope.dragRace.rules.indexOf(rule), 1);
		}

		$scope.createUpdateDragRace = function(event) {
			$scope.successMessage = false;
			event.preventDefault();
			$scope.errors = [];
			if($scope.dragRace.season < 1) {
				$scope.errors.push('Season must be 1 or more');
			}
			if(!$scope.dragRace.franchise) {
				$scope.errors.push('Select a franchise');
			}
			if(!$scope.dragRace.race_type) {
				$scope.errors.push('Select a Drag Race type');
			}
			if($scope.errors.length == 0){
				$http.post(
					'/api/dragrace/',
					{
						'pk': $scope.dragRace.pk,
						'season': $scope.dragRace.season,
						'franchise': $scope.dragRace.franchise,
						'race_type': $scope.dragRace.race_type,
						'queens': $scope.dragRace.queens,
						'rules': $scope.dragRace.rules,
					}
				).then(function(response){
					if(response.data.status == 'ok') {
						if($scope.createNew) {
							$scope.createNew = false;
							window.history.pushState('', '', '/dragrace/edit/' + response.data.drag_race.pk + '/');
						}
						$scope.dragRace = response.data.drag_race;
						window.scrollTo(0,0);
						$scope.successMessage = response.data.message;
					} else {
						$scope.errors = [response.data.message, ];
					}

				}, function(err) {
					$scope.errors = ['There was some sort of error?', ];
				})
			}
		}

		$http.get('/api/queens/').then(
			function(response) {
				$scope.existingQueens = response.data;
			}
		)

		if($scope.dragraceId != 'None') {
			$scope.createNew = false;
			$http.get('/api/dragrace/' + $scope.dragraceId + '/').then(
				function(response){
					$scope.dragRace = response.data;
				}
			);
		} else {
			$scope.createNew = true;
			$http.get('/api/defaultrules/').then(
				function(response) {
					$scope.dragRace.rules = response.data;
				}
			);
		}

	}
);

angular.bootstrap(document.getElementById("addEditDragRaceModule"), ['addEditDragRaceModule']);