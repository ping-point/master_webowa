var app = angular.module("myApp", []);
app.controller("myCtrl", function($scope) {
	$scope.proba = 5;
	$scope.open = false;
	$scope.menu = function(){
		if($scope.open)
			$scope.open = false;
		else
			$scope.open = !$scope.open;
	}
});