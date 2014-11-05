(function () {

    function ConfigApp(interpolate, location, urlRoute) {
        urlRoute.when('/', '/home/');
        //urlRoute.otherwise('/error/404/');
        location.html5Mode(true);
        location.hashPrefix('!');
        interpolate.startSymbol('<[');
        interpolate.endSymbol(']>');
    }

    // Filters
    function filterGetByProperty() {
        return function (propertyName, propertyValue, collection) {
            for (var i = 0; i < collection.length; i++) {
                var v = collection[i];
                if (v[propertyName] === propertyValue) {
                    return v;
                }
            }
            return null;
        };
    }

    function filterGetIndexByProperty() {
        return function (propertyName, propertyValue, collection) {
            for (var i = 0; i < collection.length; i++) {
                var v = collection[i];
                if (v[propertyName] === propertyValue) {
                    return i;
                }
            }
            return null;
        };
    }

    function AppController(scope, rootScope, stateParams, LoginService) {

        scope.search = function ($event) {
            // do noting yet
        };

        rootScope.$on('$stateChangeStart', function (event, toState) {
            if (angular.isDefined(toState.data.pageTitle)) {
                scope.pageTitle = toState.data.pageTitle + ' | Coati';
            }
            scope.actual_path = toState.name;
            rootScope.state_name  = toState.name;
        });

        rootScope.$on('$stateChangeSuccess', function (event) {
            if (rootScope.state_name !== "login") {
                if (window.sessionStorage.getItem('token') == null) {
                    event.preventDefault();
                    state.go('login', stateParams);
                }
            }
        });

    }

    // Injections
    ConfigApp.$inject = ['$interpolateProvider', '$locationProvider', '$urlRouterProvider'];
    AppController.$inject = ['$scope', '$rootScope', '$stateParams', 'LoginService'];

    angular.module('KoalaApp', [
        'templates-app', 'templates-common',
        'ui.router', 'ui.bootstrap', 'ngCookies',
        'Koala.Config', 'KoalaApp.Directives', 'KoalaApp.Home',
        'KoalaApp.Login',
        'KoalaApp.User', 'Koala.Projects', 'Koala.Tickets', 'KoalaApp.Errors'])
        .config(ConfigApp)
        .filter('getByProperty', filterGetByProperty)
        .filter('getIndexByProperty', filterGetIndexByProperty)
        .controller('AppCtrl', AppController);

}());


