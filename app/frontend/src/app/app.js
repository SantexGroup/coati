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
    var sumValue = function () {
        return function (items, field) {
            var total = 0, i = 0;
            if (items !== undefined) {
                for (i = 0; i < items.length; i++) {
                    total += items[i][field] || 0;
                }
            }
            return total;
        };
    };

    var filterGetByProperty = function () {
        return function (propertyName, propertyValue, collection) {
            for (var i = 0; i < collection.length; i++) {
                var v = collection[i];
                if (v[propertyName] === propertyValue) {
                    return v;
                }
            }
            return null;
        };
    };

    var filterGetIndexByProperty = function () {
        return function (propertyName, propertyValue, collection) {
            for (var i = 0; i < collection.length; i++) {
                var v = collection[i];
                if (v[propertyName] === propertyValue) {
                    return i;
                }
            }
            return null;
        };
    };

    var filterTicketTypes = function () {
        return function (types, type) {
            var value = null;
            for (var i = 0; i < types.length; i++) {
                var v = types[i];
                if (v.value === type) {
                    value = v.name;
                    break;
                }
            }
            return value;
        };
    };

    var filterTrustedHTML = function ($sce) {
        return function (text) {
            return $sce.trustAsHtml(text);
        };
    };

    var AppController = function (scope, rootScope, state, stateParams, modal, tokens, TicketService, SocketIO) {
        var vm = this;
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
                    state.go('login', stateParams, {reload: true, notify: false});
                }
            }
        });

        vm.searchTickets = function (query) {
            vm.loading_results = true;
            return TicketService.search(query).then(function (rta) {
                vm.loading_results = false;
                return rta.map(function (item) {
                    var result = {
                        label: item.project.prefix + '-' + item.number + ': ' + item.title,
                        description: item.description,
                        data: item
                    };
                    return result;
                });
            });
        };


        vm.on_select_result = function (item, model, label, value) {
            return model.label;
        };

        //Init Socket interaction
        SocketIO.init();
    };

    var RunApp = function (rootScope, state, stateParams, objects, editableOptions, editableThemes) {

        editableThemes.bs3.inputClass = 'input-sm';
        editableThemes.bs3.buttonsClass = 'btn-sm';
        editableOptions.theme = 'bs3';

        var user = null;
        try {
            user = JSON.parse(window.localStorage.getItem('user'));
            if (objects.isObject(user)) {
                rootScope.user = user;
            } else {
                if (window.location.href.indexOf('login') < 0) {
                    stateParams.next = window.location.href;
                    state.go('login', stateParams);
                }
            }
        } catch (err) {

        }

    };

    // Injections
    filterTrustedHTML.$inject = ['$sce'];
    RunApp.$inject = ['$rootScope', '$state', '$stateParams', '$objects', 'editableOptions', 'editableThemes'];
    ConfigApp.$inject = ['$interpolateProvider', '$locationProvider', '$urlRouterProvider', 'growlProvider'];
    AppController.$inject = ['$scope', '$rootScope', '$state', '$stateParams', '$modal', 'tokens', 'TicketService', 'SocketIO'];

    angular.module('Coati', [
        'templates-app', 'templates-common', 'angular-loading-bar',
        'ui.router', 'ui.bootstrap', 'angular-growl', 'xeditable',
        'Coati.SocketIO',
        'Coati.Config',
        'Coati.Directives',
        'Coati.Services.Ticket',
        'Coati.Errors',
        'Coati.Home',
        'Coati.Login', 'Coati.Helpers',
        'Coati.User', 'Coati.Project', 'Coati.Ticket', 'Coati.Sprint'])
        .config(ConfigApp)
        .run(RunApp)
        .filter('getByProperty', filterGetByProperty)
        .filter('getIndexByProperty', filterGetIndexByProperty)
        .filter('sumValue', sumValue)
        .filter('ticketTypes', filterTicketTypes)
        .filter('trustedHtml', filterTrustedHTML)
        .controller('AppCtrl', AppController);


}(angular));


