(function (angular) {

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

    function AppController(scope, rootScope, state, stateParams, tokens) {

        rootScope.$on('$stateChangeStart', function (event, toState) {
            if (angular.isDefined(toState.data.pageTitle)) {
                scope.pageTitle = toState.data.pageTitle + ' | Coati';
            }
            scope.actual_path = toState.name;
            rootScope.state_name  = toState.name;
        });

        rootScope.$on('$stateChangeSuccess', function (event) {
            if (rootScope.state_name !== "login" && rootScope.state_name !== 'login_auth') {
                if (tokens.get_token() == null) {
                    event.preventDefault();
                    state.go('login', stateParams);
                }
            }
        });

    }

    // Injections
    ConfigApp.$inject = ['$interpolateProvider', '$locationProvider', '$urlRouterProvider'];
    AppController.$inject = ['$scope', '$rootScope','$state', '$stateParams', 'tokens'];

    angular.module('Coati', [
        'templates-app', 'templates-common',
        'ui.router', 'ui.bootstrap',
        'Coati.Config', 'Coati.Directives', 'Coati.Home',
        'Coati.Login',
        'Coati.User', 'Coati.Projects', 'Coati.Tickets', 'Coati.Errors'])
        .config(ConfigApp)
        .filter('getByProperty', filterGetByProperty)
        .filter('getIndexByProperty', filterGetIndexByProperty)
        .controller('AppCtrl', AppController);

}(angular));


