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
                pageTitle: 'Koala :: Home'
            }
        });
    }

    /**
     * Controller of main dashboard
     * @param scope
     * @param modal
     * @param ProjectService - API Service for Projects
     * @constructor
     */
    function MainController(scope, ProjectService) {
        scope.user = window.username;

        // Private methods
        var getDashboard = function () {

            ProjectService.query().then(function(projects){
               scope.projects = projects;
            });
        };


        // Public methods

        scope.getClass = function (activity) {
            var css = '';
            switch (activity.verb) {
                case 'delete':
                    css = 'red';
                    break;
                case 'add':
                    css = 'green';
                    break;
                case 'update':
                    css = 'blue';
                    break;
                case 'general':
                    css = 'purple';
                    break;
            }
            return css;
        };

        getDashboard();
    }

    //Injections
    ConfigModule.$inject = ['$stateProvider'];
    MainController.$inject = ['$scope', 'ProjectService'];


    angular.module('Coati.Home',
        ['ui.router', 'ui.bootstrap',
            'Coati.Directives',
            'Coati.ApiServices'])
        .config(ConfigModule)
        .controller('MainController', MainController);

}());


