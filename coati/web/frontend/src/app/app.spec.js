describe('App Test', function () {

    var $rootScope, $controller, $scope, $state, $tokens;
    beforeEach(module('Coati'));

    beforeEach(inject(function ($injector) {
        $rootScope = $injector.get('$rootScope');
        $controller = $injector.get('$controller');
        $state = $injector.get('$state');
        $tokens = $injector.get('TokenService');
        $scope = $rootScope.$new();

    }));

    it('test mock', function(){
       expect(true).toBe(true);
    });


});