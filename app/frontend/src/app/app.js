(function (angular) {

    function ConfigApp(interpolate, location, urlRoute, growlProvider) {
        urlRoute.when('/', '/home/');
        location.html5Mode({
            enabled: true,
            requireBase: false
        });
        location.hashPrefix('!');
        interpolate.startSymbol('<[');
        interpolate.endSymbol(']>');
        growlProvider.globalTimeToLive(5000);
        growlProvider.onlyUniqueMessages(true);
    }


    // Filters
    function sumValue() {
        return function (items, field) {
            var total = 0, i = 0;
            if (items !== undefined) {
                for (i = 0; i < items.length; i++) {
                    total += items[i][field] || 0;
                }
            }
            return total;
        };
    }

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

    function filterTicketTypes(){
        return function(types, type){
            var value = null;
            for(var i=0; i<types.length; i++){
                var v = types[i];
                if(v.value === type){
                    value = v.name;
                    break;
                }
            }
            return value;
        };
    }

    function AppController(scope, rootScope, state, stateParams, tokens) {

        rootScope.$on('$stateChangeStart', function (event, toState) {

            if (angular.isDefined(toState.data.pageTitle)) {
                scope.pageTitle = toState.data.pageTitle + ' | Coati';
            }
            scope.actual_path = toState.name;
            rootScope.state_name = toState.name;
        });

        rootScope.$on('$stateChangeSuccess', function (event) {
            if (rootScope.state_name !== "login" &&
                rootScope.state_name !== 'login_auth' &&
                rootScope.state_name !== 'login_register') {
                if (tokens.get_token() == null) {
                    event.preventDefault();
                    state.go('login', stateParams, {reload:true, notify: false});
                }
            }
        });

    }

    var RunApp = function(rootScope, state, stateParams, objects, editableOptions,editableThemes ){

        editableThemes.bs3.inputClass = 'input-sm';
        editableThemes.bs3.buttonsClass = 'btn-sm';
        editableOptions.theme = 'bs3';

        var user = null;
        try{
            user = JSON.parse(window.localStorage.getItem('user'));
            if(objects.isObject(user)) {
                rootScope.user = user;
            }else{
                if(window.location.href.indexOf('login') < 0) {
                    stateParams.next = window.location.href;
                    state.go('login', stateParams);
                }
            }
        }catch(err){

        }

    };

    // Injections
    RunApp.$inject = ['$rootScope', '$state', '$stateParams', '$objects', 'editableOptions', 'editableThemes'];
    ConfigApp.$inject = ['$interpolateProvider', '$locationProvider', '$urlRouterProvider', 'growlProvider'];
    AppController.$inject = ['$scope', '$rootScope', '$state', '$stateParams', 'tokens'];

    angular.module('Coati', [
        'templates-app', 'templates-common',
        'ui.router', 'ui.bootstrap', 'angular-growl', 'xeditable',
        'Coati.Config', 'Coati.Directives', 'Coati.Home',
        'Coati.Login', 'Coati.Helpers',
        'Coati.User', 'Coati.Project', 'Coati.Ticket', 'Coati.Sprint'])
        .config(ConfigApp)
        .run(RunApp)
        .filter('getByProperty', filterGetByProperty)
        .filter('getIndexByProperty', filterGetIndexByProperty)
        .filter('sumValue', sumValue)
        .filter('ticketTypes', filterTicketTypes)
        .controller('AppCtrl', AppController);

}(angular));


