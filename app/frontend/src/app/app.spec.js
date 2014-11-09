describe('App Test', function () {

    var $rootScope, $controller, $scope, $state, $tokens;
    beforeEach(module('Coati'));

    beforeEach(inject(function ($injector) {
        $rootScope = $injector.get('$rootScope');
        $controller = $injector.get('$controller');
        $state = $injector.get('$state');
        $tokens = $injector.get('tokens');
        $scope = $rootScope.$new();

    }));

    it("Test $stateChangeStart of AppCtrl", function () {
        $controller('AppCtrl', {
            '$scope': $scope,
            '$state': $state
        });
        $state.go('home');
        expect($scope.pageTitle).toEqual('Home | Coati');
        expect($scope.actual_path).toEqual('home');
        expect($rootScope.state_name).toEqual($scope.actual_path);
    });

    it("Test $stateChangeSuccess of AppCtrl", function () {
        $controller('AppCtrl', {
            '$scope': $scope,
            '$state': $state
        });
        $tokens.get_token = function(){
          return null;
        };
        $state.go('home').then(function(st){
            expect($state.current.name).toEqual('login');
        });
    });
});