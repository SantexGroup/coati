(function () {
    /**
     * Home Module
     */

    /**
     * Configuration of routes and other things in this module
     * @param stateProvider
     * @constructor
     */
    function ConfigModule(stateProvider) {
        stateProvider.state('home', {
            url: '/home/',
            views: {
                "main": {
                    controller: 'MainController',
                    templateUrl: 'home/home.tpl.html'
                }
            },
            data: {
                pageTitle: 'Home'
            }
        });
    }

    /**
     * Controller of main dashboard
     * @param scope
     * @param ProjectService - API Service for Projects
     * @constructor
     */
    function MainController(scope, state, ProjectService) {
        scope.user = window.username;

        scope.getDashboard = function () {

            ProjectService.query().then(function(projects){
               scope.projects = projects;
            });
        };

        scope.create_project = function(){
            state.go('project-new');
        };

        scope.getDashboard();
    }

    //Injections
    ConfigModule.$inject = ['$stateProvider'];
    MainController.$inject = ['$scope', '$state', 'ProjectService'];


    angular.module('Coati.Home',
        ['ui.router', 'ui.bootstrap',
            'Coati.Directives',
            'Coati.ApiServices'])
        .config(ConfigModule)
        .controller('MainController', MainController);

}());


