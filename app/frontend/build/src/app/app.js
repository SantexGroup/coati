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

    function AppController(scope) {
        scope.search = function ($event) {
            // do noting yet
        };

        scope.$on('$stateChangeSuccess', function (event, toState) {
            if (angular.isDefined(toState.data.pageTitle)) {
                scope.pageTitle = toState.data.pageTitle + ' | Coati';
            }
            scope.actual_path = toState.name;
        });
    }

    // Injections
    ConfigApp.$inject = ['$interpolateProvider', '$locationProvider', '$urlRouterProvider'];
    AppController.$inject = ['$scope'];

    angular.module('KoalaApp', [
        'templates-app', 'templates-common',
        'ui.router', 'ui.bootstrap', 'ngCookies',
        'Koala.Config', 'KoalaApp.Directives', 'KoalaApp.Home',
        'KoalaApp.User', 'Koala.Projects', 'KoalaApp.Errors'])
        .config(ConfigApp)
        .filter('getByProperty', filterGetByProperty)
        .filter('getIndexByProperty', filterGetIndexByProperty)
        .controller('AppCtrl', AppController);

}());


