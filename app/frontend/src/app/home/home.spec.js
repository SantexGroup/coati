describe('Home Test', function () {

    var $rootScope, $controller, $scope, httpBackend;
    beforeEach(module('Coati.Home'));

    beforeEach(inject(function ($injector) {
        $rootScope = $injector.get('$rootScope');
        $controller = $injector.get('$controller');
        httpBackend = $injector.get('$httpBackend');
        $scope = $rootScope.$new();

    }));

    afterEach(function () {
        httpBackend.verifyNoOutstandingExpectation();
        httpBackend.verifyNoOutstandingRequest();
    });


    it("Test MainController methods", function () {
        window.username = {'email': 'gastonrobledo@gmail.com'};
        var projects = [
            {'id':'123iouasnda12l31'},
            {'id':'123iouasdasnda12l31'},
            {'id':'123iou123asnda12l31'}
        ];
        httpBackend.when('GET', '/api/projects').respond(200, projects);
        httpBackend.expectGET('/api/projects');
        $controller('MainController', {
            '$scope': $scope
        });
        httpBackend.flush();
        expect($scope.user).toEqual(window.username);
        expect($scope.getDashboard).not.toBe(undefined);
        expect($scope.projects).toEqual(projects);
    });


});