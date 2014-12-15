(function (angular) {

    function Config(stateProvider) {
        stateProvider.state('login', {
            url: '/login?logout',
            views: {
                "master_view": {
                    controller: 'LoginController',
                    controllerAs: 'vm',
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

    function LoginController(state, LoginService) {
        var vm = this;
        if (state.params && state.params.logout) {
            window.sessionStorage.clear();
        }

        vm.authenticate = function (provider) {
            LoginService.auth(provider);
        };
    }

    function LoginAuthController(rootScope, state, UserService, tokens) {
        if (state.params.token) {
            tokens.store_token(state.params.token, state.params.expire);

            //Get here the user logged
            if (UserService.is_logged()) {
                UserService.me().then(function (user) {
                    window.sessionStorage.setItem('user', JSON.stringify(user));
                    rootScope.user = user;
                });
            }

            state.go('home', {reload: true});
        } else {
            state.go('login', {reload: true});
        }
    }

    Config.$inject = ['$stateProvider'];
    LoginController.$inject = ['$state', 'LoginService'];
    LoginAuthController.$inject = ['$rootScope','$state','UserService', 'tokens'];

    angular.module('Coati.Login',
        ['ui.router', 'ui.bootstrap',
            'Coati.Directives',
            'Coati.Helpers',
            'Coati.Services.Login',
            'Coati.Services.User'])
        .config(Config)
        .controller('LoginController', LoginController)
        .controller('LoginAuthController', LoginAuthController);


}(angular));
