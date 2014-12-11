(function (angular) {
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
                    controllerAs: 'vm',
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
    function MainController(state, ProjectService) {
        var vm = this;

        vm.user = window.username;

        vm.getDashboard = function () {

            ProjectService.query().then(function(projects){
               vm.projects = projects;
            });
        };

        vm.create_project = function(){
            state.go('project-new');
        };

        vm.getDashboard();
    }

    //Injections
    ConfigModule.$inject = ['$stateProvider'];
    MainController.$inject = ['$state', 'ProjectService'];


    angular.module('Coati.Home',
        ['ui.router', 'ui.bootstrap',
            'Coati.Directives',
            'Coati.Services.Project'])
        .config(ConfigModule)
        .controller('MainController', MainController);

}(angular));


