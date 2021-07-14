var panelApp = angular.module('panelModule', []);

panelApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

panelApp.controller(
	'panelController',
	function($scope, $http, $sce) {
		$scope.dragraceId = document.getElementById('id_dragrace_id').value;
		$scope.panelId = document.getElementById('id_panel_id').value;

		if ($scope.dragraceId) {
			$scope.apiBase = '/api/dragrace/' + $scope.dragraceId + '/panel/create/';
		} else {
			$scope.apiBase = '/api/panel/' + $scope.panelId + '/edit/';
			$http.get($scope.apiBase).then(function(response){
				$scope.panelName = response.data.name;
				$scope.panelType = response.data.panel_type;
				$scope.wildcardAllowance = response.data.wildcard_allowance;
				$scope.particintLimit = response.data.participant_limit;
			});
		}

		$scope.formPhase = 'panelType';
		$scope.submitable = false

		$scope.sceSafe = function(html) {
			return $sce.trustAsHtml(html);
		}

		$scope.checkPanelName = function() {
			if($scope.panelName){
				$http.get($scope.apiBase, {params: {'request': 'checkname', 'name': $scope.panelName}}).then(
					function(response) {
						$scope.error = response.data.message;
						if (!$scope.error) {
							$scope.submitable = true;
						} else {
							$scope.submitable = false;
						}
					}
				);
			} else {
				$scope.submitable = false;
			}
		}

		$scope.reversePhase = function() {
			$scope.error = null;
			if($scope.formPhase == 'particintLimit') {
				$scope.formPhase = 'panelType';
			} else if ($scope.formPhase == 'wildcardAllowance') {
				$scope.formPhase = 'particintLimit';
			} else if ($scope.formPhase == 'panelName') {
				$scope.formPhase = 'wildcardAllowance';
			}
		}

		$scope.advancePhase = function(event) {
			event.preventDefault();
			if($scope.formPhase == 'panelType') {
				if($scope.panelType) {
					$scope.formPhase = 'particintLimit';
					$scope.error = null;
				} else {
					$scope.error = 'Please select an option'
				}
			} else if($scope.formPhase == 'particintLimit') {
				if($scope.particintLimit) {
					$scope.formPhase = 'wildcardAllowance';
					$scope.error = null;
				} else {
					$scope.error = 'Please enter a particiant limit'
				}
				$scope.formPhase = 'wildcardAllowance';
			} else if($scope.formPhase == 'wildcardAllowance') {
				$scope.formPhase = 'panelName';
				$scope.error = null;
			} else {
				event.run();
			}
		}
	}
);

angular.bootstrap(document.getElementById("panelModule"), ['panelModule']);
