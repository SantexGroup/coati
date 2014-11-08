describe('app test case', function () {

    var $rootScope, $scope;
    beforeEach(module('Coati'));

    beforeEach(inject(function ($injector) {
        var $controller;
        $rootScope = $injector.get('$rootScope');
        $controller = $injector.get('$controller');
        $scope = $rootScope.$new();
        $controller('AppCtrl', {
            $scope: $scope
        });
    }));

    it("check scope not null", function () {
        expect($scope).not.toBe(null);
    });
});