var dashboardApp = angular.module('dashboardModule', []);

dashboardApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

dashboardApp.controller(
	'dashboardController',
	function($scope, $http) {
		$scope.expandedEpisodes = [];
		$scope.expandedPanels = [];

		$scope.initQueryParams = function() {
			$scope.queryParams = getQueryObject({'drafts': [], 'panels': []});
		}

		$scope.initExpandedItems = function() {
			angular.forEach($scope.dragRaces, function(dragrace) {
				angular.forEach(dragrace.episodes, function(episode) {
					var pkStr = episode.pk.toString();
					if($scope.queryParams.drafts.indexOf(pkStr) >= 0){
						$scope.toggleEpisodeDraft(episode);
					}
				});				
				angular.forEach(dragrace.panels, function(panel) {
					var pkStr = panel.pk.toString();
					if($scope.queryParams.panels.indexOf(pkStr) >= 0){
						$scope.togglePanel(panel);
					}
				});
				if (dragrace.panels.length == 1) {
					$scope.togglePanel(dragrace.panels[0]);
				}
			});
		}

		$scope.toggleEpisodeDraft = function(episode){
			var pkStr = episode.pk.toString();
			if($scope.expandedEpisodes.indexOf(episode) !== -1) {
				$scope.expandedEpisodes.splice($scope.expandedEpisodes.indexOf(episode), 1);
				$scope.queryParams.drafts.splice($scope.queryParams.drafts.indexOf(pkStr), 1);
			} else {
				$scope.expandedEpisodes.push(episode);
				if($scope.queryParams.drafts.indexOf(pkStr) == -1){
					$scope.queryParams.drafts.push(pkStr);
				}
			}
			updateUrl($scope.queryParams, $scope.anchoredObject);
		};

		$scope.togglePanel = function(panel){
			var pkStr = panel.pk.toString();
			if($scope.expandedPanels.indexOf(panel) !== -1) {
				$scope.expandedPanels.splice($scope.expandedPanels.indexOf(panel), 1);
				$scope.queryParams.panels.splice($scope.queryParams.panels.indexOf(pkStr), 1);
			} else {
				$scope.expandedPanels.push(panel);
				if($scope.queryParams.panels.indexOf(pkStr) == -1){
					$scope.queryParams.panels.push(pkStr);
				}
			}
			updateUrl($scope.queryParams, $scope.anchoredObject);
		};

		$scope.ruvealScores = function(episode, dragrace) {
			$scope.state = 'loading';
			$http.post(
				'/api/stats/dashboard/',
				{
					'request': 'ruveal-episode', 
					'episode_id': episode.pk
				}
			).then(
				function(response){
					$scope.state = 'loaded';
					//window.location.pathname = episode.detail_url;
					location.reload();
				}
			);
		}

		$scope.hideScores = function(episode, dragrace) {
			$scope.state = 'loading';
			$http.post(
				'/api/stats/dashboard/',
				{
					'request': 'hide-episode', 
					'episode_id': episode.pk
				}
			).then(
				function(response){
					$scope.state = 'loaded';
					// window.location.pathname = episode.detail_url;
					location.reload();
				}
			);
		}

		$scope.getQueenEpisodeScore = function(queen, queens) {
			return 100;
		}

		$scope.fetchPastSeasons = function() {
			if(!$scope.oldDragRacesLoaded) {
				$scope.state = 'loading';
				if ($scope.user.is_site_admin) {
					var postUrl = '/api/stats/dashboard/admin/'
				} else {
					var postUrl = '/api/stats/dashboard/archived/'
				}
				$http.get(postUrl).then(function(response){
					$scope.oldDragRaces = response.data.drag_races;
					$(function () {
		  				$('[data-toggle="tooltip"]').tooltip()
					});
					$scope.oldDragRacesLoaded = true;
					$scope.state = 'loaded';
				});
			}
		}

		$scope.alert = function(message) {alert(message)};
		$scope.initQueryParams();
		$scope.state = 'loading';
		$scope.oldDragRacesLoaded = false;
		$scope.oldDragRaces = [];
		
		$http.get('/api/user/').then(function(response){
			$scope.user = response.data.user;
			$scope.featureFlags = response.data.flags;
			if ($scope.user.is_authenticated) {
				$http.get('/api/stats/dashboard/').then(function(response){
					$scope.dragRaces = response.data.drag_races;
					$scope.initExpandedItems();
					$(function () {
		  				$('[data-toggle="tooltip"]').tooltip()
					});
					$scope.state = 'loaded';
				});
			}
		});
	}
);

angular.bootstrap(document.getElementById("dashboardModule"), ['dashboardModule']);
