var panelDraftApp = angular.module('panelDraftModule', []);

panelDraftApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

panelDraftApp.controller(
	'panelDraftController',
	function($scope, $http) {	

		$scope.panelId = document.getElementById('id_panelId').value;

		$scope.alert = function(message) {
			alert(message);
		}

		$scope.updateDraftMeta = function(responseData) {
			$scope.panel.status = responseData.panel.status;
			$scope.drafts = responseData.drafts;
			$scope.wqDrafts = responseData.wq_drafts;
			$scope.isCurrentPlayer = responseData.is_current_participant;
			$scope.currentParticipant = $scope.participants[responseData.participant_pk];
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
			$scope.draftRounds = responseData.panel.draft_rounds;
			$scope.isCurrentPlayer = responseData.meta.is_current_participant;
			$scope.participant_order = responseData.panel.draft_order;
			$scope.setAvailableQueens(responseData);

			$scope.formattedDraftInfo = []
			angular.forEach($scope.draftRounds, function(data, draftIndex){
				var thisDraft = {}
				thisDraft.number = draftIndex;
				thisDraft.playerDrafts = []
				angular.forEach(data, function(hasDraft, playerIndex) {
					if(hasDraft) {
						thisDraft.playerDrafts.push(parseInt(playerIndex) + 1);
					}

				});
				$scope.formattedDraftInfo.push(thisDraft);
			});
		}

		$scope.updateApp = function(){
			$http.get('/api/panel/' + $scope.panelId + '/drafts/').then(function _updateDrafts(response){
				response.data.participants.forEach(function(p){
					$scope.participants[p.participant.pk].drafts = p.drafts;
					$scope.participants[p.participant.pk].wildcardDrafts = p.wq_drafts;
				});
				if($scope.panel.status == 'in draft' && response.data.panel.status == 'wildcards'){
					$scope.updateDraftMeta(response.data);
					$http.get('/api/panel/' + $scope.panelId + '/draft/').then(function _resetAvailableQueens(response){
						$scope.setAvailableQueens(response.data);
					});
				} else {
					$scope.updateDraftMeta(response.data);
					$http.get('/api/panel/' + $scope.panelId + '/availablequeens/').then(function _updateAvailableQueens(response){
						$scope.updateAvailableQueens(response.data);
					});
				}
			});
		}

		$scope.startDraft = function(draftType, variableNumber, wilcardAllowance) {
			$http.put(
				'/api/panel/' + $scope.panelId + '/draft/',
				{
					'request': 'start_draft'
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
			if(response.data.panel.status)
			$scope.draftLoop = window.setInterval(function startDraftLoop(){
				$scope.updateApp();
			}, 1000);
		});


	}
);

angular.bootstrap(document.getElementById("panelDraftModule"), ['panelDraftModule']);
