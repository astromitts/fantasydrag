var profileApp = angular.module('profileModule', []);

profileApp.config(['$httpProvider', function($httpProvider) {
    $httpProvider.defaults.xsrfCookieName = 'csrftoken';
    $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

profileApp.controller(
	'profileController',
	function($scope, $http) {
		$scope.editProfile = false;
		$scope.error = null;

		$scope.updateUser = function(data, editVar) {
			$http.patch(
				'/api/profile/',
				{
					'first_name': $scope.user.first_name,
					'last_name': $scope.user.last_name,
					'email': $scope.user.email,
					'display_name': $scope.user.display_name,
				}
			).then(
				function(response){
					if(response.data.status == 'ok') {
						$scope.editProfile = false;
						$scope.error = null;
					} else {
						$scope.error = response.data.message;
					}
				}, function(err) {
					$scope.error = 'There was some sort of error?';
				}
			)
		}

		$scope.checkPassword = function(currentPassword, newPassword, confirmPassword) {
			$scope.passwordErrors = null;
			if(currentPassword && newPassword) {
				if (newPassword != confirmPassword) {
					$scope.passwordErrors = ['Passwords must match', ];
				} else {
					$scope.passwordErrors = getPasswordErrors(newPassword);
				}
				if (!$scope.passwordErrors.length){
					$http.post(
						'/api/profile/',
						{
							'request': 'check-password',
							'password': currentPassword
						}
					).then(function(response){
						if(response.data.status == 'ok') {
							$http.post(
								'/api/profile/',
								{
									'request': 'set-password',
									'password': newPassword
								}
							).then(function(response){
								if(response.data.status == 'ok') {
									$scope.success = 'Password updated!';
									$scope.editPassword = false;
								} else {
									$scope.passwordErrors = [response.data.message, ];
								}
							});
						} else {
							$scope.passwordErrors = [response.data.message, ];
						}
					});
				}
			} 
		}

		$http.get('/api/profile/').then(
			function setProfile(response) {
				$scope.user = response.data;
			}
		);
	}
);

angular.bootstrap(document.getElementById("profileModule"), ['profileModule']);
