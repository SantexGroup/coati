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
        stateProvider.state('error_403', {
            url: '/error/forbidden',
            views: {
                "main": {
                    templateUrl: 'error/forbidden.tpl.html'
                }
            },
            data: {
                pageTitle: 'Home'
            }
        });
    }

    //Injections
    ConfigModule.$inject = ['$stateProvider'];


    angular.module('Coati.Errors',
        ['ui.router', 'ui.bootstrap',
            'Coati.Directives'])
        .config(ConfigModule);

}(angular));


