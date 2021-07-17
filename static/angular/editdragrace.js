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

		$scope.typeOptions = ['standard', 'all star', 'international']

		$scope.dragRace = {
			'pk': $scope.dragraceId,
			'season': 1,
			'franchise': null,
			'type': null,
			'queens': []
		}

		$scope.newQueen = null;

		$scope.updateRuleSet = function(typeOption) {
			$scope.dragRaceRules = [];
			angular.forEach($scope.ruleSet, function(rule) {
				if (rule.drag_race_types_list.includes(typeOption)) {
					$scope.dragRaceRules.push(rule);
				}
			});
		}


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

		$scope.removeQueen = function(queen){
			$scope.dragRace.queens.splice($scope.dragRace.queens.indexOf(queen), 1);
		}

		$scope.createUpdateDragRace = function() {
			$scope.successMessage = false;
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
						$scope.successMessage = response.data.message;
					} else {
						$scope.errors = [response.data.message, ];
					}
				}, function(err) {
					$scope.errors = ['There was some sort of error?', ];
				})

			}
			window.scrollTo(0,0);
		}

		$http.get('/api/queens/').then(
			function(response) {
				$scope.existingQueens = response.data;
			}
		)

		if($scope.dragraceId != 'None') {
			$scope.createNew = false;
		}else {
			$scope.createNew = true;
		}
		
		$http.get('/api/defaultrules/').then(
			function(response) {
				$scope.ruleSet = response.data;
				if(!$scope.createNew){
					$http.get('/api/dragrace/' + $scope.dragraceId + '/').then(
						function(response){
							$scope.dragRace = response.data;
							$scope.updateRuleSet($scope.dragRace.drag_race_type.name);
						}
					);
				}
			}
		);
		

	}
);

angular.bootstrap(document.getElementById("addEditDragRaceModule"), ['addEditDragRaceModule']);
