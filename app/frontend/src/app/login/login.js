(function (angular) {

    function Config(stateProvider) {
        stateProvider.state('login', {
            url: '/login?logout',
            views: {
                "master_view": {
                    controller: 'LoginController',
                    templateUrl: 'login/login.tpl.html'
                }
            },
            data: {
                pageTitle: 'Coati :: Login Page'
            }
        })
            .state('login_auth', {
                url: '/login/auth?token&expire',
                views: {
                    "master_view": {
                        controller: 'LoginAuthController'
                    }
                },
                data: {
                    pageTitle: 'Coati :: Login Page'
                }
            });
    }

    function LoginController(scope, state, LoginService) {

        if (state.params && state.params.logout) {
            window.sessionStorage.clear();
        }

        scope.authenticate = function (provider) {
            LoginService.auth(provider);
        };
    }

    function LoginAuthController(scope, state, tokens) {
        if (state.params.token) {
            tokens.store_token(state.params.token, state.params.expire);
            state.go('home', {reload: true});
        } else {
            state.go('login', {reload: true});
        }
    }

    Config.$inject = ['$stateProvider'];
    LoginController.$inject = ['$scope', '$state', 'LoginService'];
    LoginAuthController.$inject = ['$scope', '$state', 'tokens'];

    angular.module('Coati.Login',
        ['ui.router', 'ui.bootstrap',
            'Coati.Directives',
            'Coati.Helpers',
            'Coati.Services.Login'])
        .config(Config)
        .controller('LoginController', LoginController)
        .controller('LoginAuthController', LoginAuthController);


}(angular));
