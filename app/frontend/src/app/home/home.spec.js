describe('Home Test', function () {

    var $rootScope, $controller, $scope, httpBackend;
    beforeEach(module('Coati.Home'));

    beforeEach(inject(function ($injector) {
        $rootScope = $injector.get('$rootScope');
        $controller = $injector.get('$controller');
        httpBackend = $injector.get('$httpBackend');

    }));

    afterEach(function () {
        httpBackend.verifyNoOutstandingExpectation();
        httpBackend.verifyNoOutstandingRequest();
    });


    it("Test MainController methods", function () {
        var ctrl = $controller('MainController');
        expect(ctrl.getDashboard).not.toBe(undefined);
    });


});