var panelDraftApp = angular.module('panelDraftModule', []);

panelDraftApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

panelDraftApp.controller(
	'panelDraftController',
	function($scope, $http) {	

		$scope.panelId = document.getElementById('id_panelId').value;
		$scope.queenAllowance = 0;
		$scope.draftPreview = [];

		$scope.alert = function(message) {
			alert(message);
		}

		$scope.setPreviewForQueenAllowance = function(queenAllowance) {
			$scope.draftPreview = [];
			var queenCount = $scope.dragRace.queens.length;
			var queenDraftCount = queenAllowance * queenCount;
			var participantCount = $scope.participants.length;
			var queensPP = Math.floor(queenDraftCount / participantCount);
			var numPlayersGetExtra = queenDraftCount % participantCount;
			
			for (i=1; i<=participantCount; i++) {
				if(i <= participantCount - numPlayersGetExtra){
					$scope.draftPreview.push({'draftKey': 'Player ' + i, 'numDrafts': queensPP});
				} else {
					$scope.draftPreview.push({'draftKey': 'Player ' + i, 'numDrafts': queensPP + 1});
				}
			}
		}

		$scope.setPreviewForTeamSize = function(teamSize) {
			$scope.draftPreview = [];
			var queenCount = $scope.dragRace.queens.length;
			var participantCount = $scope.participants.length;

			// the number of drafts that will happen, if each participant gets teamSize drafts
			var totalDraftCount = teamSize * participantCount;

			if (totalDraftCount <= queenCount) {
				for (i=1; i<=queenCount; i++) {
					if(i <= totalDraftCount){
						$scope.draftPreview.push({'draftKey': 'Queen ' + i, 'numDrafts': 1});
					} else {
						$scope.draftPreview.push({'draftKey': 'Queen ' + i, 'numDrafts': 0});
					}
				}
			} else {
				// How many times does the number of queens divid into the total number of drafts?
				var playersPerQueen = Math.floor(totalDraftCount / queenCount);
				// How many draft slots are left over?
				var extraDraftSlots = totalDraftCount - queenCount * playersPerQueen;

				for (i=1; i<=queenCount; i++) {
					if(i <= queenCount - extraDraftSlots){
						$scope.draftPreview.push({'draftKey': 'Queen ' + i, 'numDrafts': playersPerQueen});
					} else {
						$scope.draftPreview.push({'draftKey': 'Queen ' + i, 'numDrafts': playersPerQueen + 1});
					}
				}
			}
			

		}

		$scope.setPreview = function(draftType, variableNumber) {
			$scope.draftType = draftType;
			if(draftType == 'byQueenCount') {
				$scope.setPreviewForQueenAllowance(variableNumber);
			} else {
				$scope.setPreviewForTeamSize(variableNumber);
			}
		}

		$scope.setAppData = function(responseData) {
			$scope.panel = responseData.panel;
			$scope.dragRace = responseData.panel.drag_race;
			$scope.isCaptain = responseData.meta.is_captain;
			$scope.isAdmin = responseData.meta.is_site_admin;
			$scope.participants = responseData.participants;
			$scope.drafts = responseData.drafts;
			$scope.draft = responseData.panel.draft_data;

			$scope.currentParticipant = $scope.participants[0].participant;
			$scope.availableQueens = $scope.participants[0].available_queens;
			$scope.participants.forEach(function checkIfCurrent(p){
				if(p.participant.pk == $scope.panel.draft_data.current_participant) {
					$scope.currentParticipant = p.participant;
					$scope.availableQueens = p.available_queens;
				}
			});
			if($scope.panel.status == 'open') {
				$scope.draftType = 'byQueenCount';
				$scope.draftVariable = 0;
				$scope.setPreview($scope.draftType, 0);
			}
		}

		$scope.startDraft = function(draftType, variableNumber) {
			$scope.setPreview(draftType, variableNumber);
			$http.put(
				'/api/panel/' + $scope.panelId + '/draft/',
				{
					'request': 'start_draft', 
					'draft_type': draftType,
					'variable_number': variableNumber,
					'draft_rules': $scope.draftPreview,
				}
			).then(function resetAppData(response){
				$scope.setAppData(response.data);
			});
		}
		$scope.draftPut = function(request_type) {	

			$http.put(
				'/api/panel/' + $scope.panelId + '/draft/',
				{'request': request_type}
			).then(function resetAppData(response){
				$scope.setAppData(response.data);
			});

		}

		$scope.updateRound = function() {
			var selected = document.getElementById('id_queen');
			var queenId = selected.options[selected.selectedIndex].value;
			$http.put(
				'/api/panel/' + $scope.panelId + '/draft/',
				{'request': 'update_round', 'number': $scope.panel.draft_data.draft_index}
			);

		}

		$scope.selectQueen = function() {
			var selected = document.getElementById('id_queen');
			var queenId = selected.options[selected.selectedIndex].value;
			$http.put(
				'/api/panel/' + $scope.panelId + '/draft/',
				{'request': 'add_draft', 'queen_id': queenId}
			).then(function resetAppData(response){
				$scope.setAppData(response.data);
			});

		}

		$http.get('/api/panel/' + $scope.panelId + '/draft/').then(function setAppData(response){
			$scope.setAppData(response.data);
		});

	}
);

angular.bootstrap(document.getElementById("panelDraftModule"), ['panelDraftModule']);
