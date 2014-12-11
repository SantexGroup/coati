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
        window.username = {'email': 'gastonrobledo@gmail.com'};
        var projects = [
            {'id':'123iouasnda12l31'},
            {'id':'123iouasdasnda12l31'},
            {'id':'123iou123asnda12l31'}
        ];
        httpBackend.when('GET', '/api/projects').respond(200, projects);
        httpBackend.expectGET('/api/projects');
        var ctrl = $controller('MainController');
        httpBackend.flush();
        expect(ctrl.user).toEqual(window.username);
        expect(ctrl.getDashboard).not.toBe(undefined);
        expect(ctrl.projects).toEqual(projects);
    });


});