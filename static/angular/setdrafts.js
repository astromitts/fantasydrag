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
			var participantCount = Object.keys($scope.participants).length;
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
			var participantCount = Object.keys($scope.participants).length;

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

		$scope.updateDraftMeta = function(responseData) {
			$scope.panel.status = responseData.panel.status;
			$scope.drafts = responseData.drafts;
			$scope.isCurrentPlayer = responseData.is_current_participant;
			$scope.currentParticipant = $scope.participants[responseData.participant_pk];
			$scope.draft.round = $scope.panel.round;
		}

		$scope.setAvailableQueens = function(responseData) {
			responseData.participants.forEach(function setQueens(p){
				$scope.participants[p.participant.pk] = {
					'pk': p.participant.pk,
					'name': p.participant.name,
					'availableQueens': p.available_queens

				}
			});
		}

		$scope.updateAvailableQueens = function(responseData) {
			responseData.participants.forEach(function updateQueens(p){
				var availableQueensPks = []
				p.available_queens.forEach(function pushQueenPks(queen){
					availableQueensPks.push(queen.pk);
				});
				$scope.participants[p.participant.pk].availableQueens.forEach(function checkQueen(queen) {
					if(!availableQueensPks.includes(queen.pk)) {
						$scope.participants[p.participant.pk]['availableQueens']
							.splice($scope.participants[p.participant.pk]['availableQueens'].indexOf(queen), 1);
					}
				});
			});
		}

		$scope.initAppData = function(responseData) {
			$scope.panel = responseData.panel;
			$scope.dragRace = responseData.panel.drag_race;
			$scope.isCaptain = responseData.meta.is_captain;
			$scope.isAdmin = responseData.meta.is_site_admin;
			$scope.participants = {};
			$scope.drafts = responseData.drafts;
			$scope.draft = responseData.panel.draft_data;
			$scope.isCurrentPlayer = responseData.meta.is_current_participant;
			$scope.setAvailableQueens(responseData);
			if($scope.panel.status == 'open') {
				$scope.draftType = 'byQueenCount';
				$scope.draftVariable = 0;
				$scope.setPreview($scope.draftType, 0);
			}
		}

		$scope.updateApp = function(){
			$http.get('/api/panel/' + $scope.panelId + '/drafts/').then(function initAppData(response){
				if($scope.panel.status == 'in draft' && response.data.panel.status == 'wildcards'){
					$scope.updateDraftMeta(response.data);
					$http.get('/api/panel/' + $scope.panelId + '/draft/').then(function initAppData(response){
						$scope.setAvailableQueens(response.data);
					});
				} else {
					$scope.updateDraftMeta(response.data);
					$http.get('/api/panel/' + $scope.panelId + '/availablequeens/').then(function initAppData(response){
						$scope.updateAvailableQueens(response.data);
					});
				}
			});
		}

		$scope.startDraft = function(draftType, variableNumber, wilcardAllowance) {
			$scope.setPreview(draftType, variableNumber);
			$http.put(
				'/api/panel/' + $scope.panelId + '/draft/',
				{
					'request': 'start_draft', 
					'draft_type': draftType,
					'variable_number': variableNumber,
					'draft_rules': $scope.draftPreview,
					'wildcard_allowance': wilcardAllowance,
				}
			).then(function reinitAppData(response){
				$scope.initAppData(response.data);
			});
		}
		$scope.draftPut = function(request_type) {	

			$http.put(
				'/api/panel/' + $scope.panelId + '/draft/',
				{'request': request_type}
			).then(function reinitAppData(response){
				if (request_type == 'reset') {
					$scope.initAppData(response.data);
				} else {
					$scope.updateApp();
				}
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

		$scope.selectQueen = function(queen) {
			if ($scope.selectedQueen == queen) {
				$scope.selectedQueen = null;
			} else {
				$scope.selectedQueen = queen;
			}
		}

		$scope.draftQueen = function(scroll) {
			$http.put(
				'/api/panel/' + $scope.panelId + '/draft/',
				{'request': 'add_draft', 'queen_id': $scope.selectedQueen.pk}
			).then(function reinitAppData(response){
				if(response.data.meta.status == 'ok'){
					$scope.updateApp();
					$scope.selectedQueen = null;
					if(scroll) {
						window.scrollTo(0, 0);
					}
				}
			});

		}

		$http.get('/api/panel/' + $scope.panelId + '/draft/').then(function initAppData(response){
			$scope.initAppData(response.data);
			var draftLoop = window.setInterval(function startDraftLoop(){
				$scope.updateApp();
			}, 1000);
		});


	}
);

angular.bootstrap(document.getElementById("panelDraftModule"), ['panelDraftModule']);
