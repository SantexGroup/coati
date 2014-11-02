angular.module('KoalaApp.Errors',
        ['ui.router', 'KoalaApp.Directives',
            'KoalaApp.ApiServices', 'KoalaApp.SocketIO'])
    .config(function ($stateProvider) {
        $stateProvider.state('not_found', {
            url: '/error/404/',
            views: {
                "main": {
                    controller: 'ErrorController',
                    templateUrl: 'extras/404.tpl.html'
                }
            },
            data: {
                pageTitle: 'Not Found'
            }
        });
    })
    .controller('ErrorController', function ($scope, $state) {

    });
