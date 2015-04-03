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
                'main': {
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
    function MainController(rootScope, state, modal, ProjectService, UserService) {
        var vm = this;

        vm.getDashboard = function () {

            ProjectService.query().then(function(projects){
               vm.projects = projects;
            });
        };

        vm.create_project = function(){
            var modal_instance = modal.open({
                controller: 'ProjectFormCtrl as vm',
                templateUrl: 'project/new_project.tpl.html'
            });
            modal_instance.result.then(function (project) {
                vm.projects.push(project);
            });
        };

        if(UserService.is_logged()) {
            vm.getDashboard();
        }
    }

    //Injections
    ConfigModule.$inject = ['$stateProvider', '$translateProvider'];
    MainController.$inject = ['$rootScope', '$state', '$modal', 'ProjectService', 'UserService'];


    angular.module('Coati.Home',
        ['ui.router', 'ui.bootstrap','pascalprecht.translate',
            'Coati.Directives',
            'Coati.Services.Project',
            'Coati.Services.User'])
        .config(ConfigModule)
        .controller('MainController', MainController);

}(angular));


