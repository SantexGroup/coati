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
                    pageTitle: 'Coati :: Auth Page'
                },
                reload: true
            })
            .state('login_register', {
                url: '/register',
                views: {
                    "master_view": {
                        controller: 'RegisterController',
                        controllerAs: 'vm',
                        templateUrl: 'login/register.tpl.html'
                    }
                },
                data: {
                    pageTitle: 'Coati :: Register'
                }
            });
    }

    var LoginController = function(state, LoginService) {
        var vm = this;

        vm.form = {};
        vm.login = {};

        if (state.params && state.params.logout) {
            window.sessionStorage.clear();
        }

        vm.login_user = function () {
            if (vm.form.login.$valid) {
                LoginService.login(vm.login).then(function (data) {
                    state.go('login_auth', {token: data.token,
                        expire: data.expire}, {reload: true});
                }, function (err) {
                    vm.error = 'Login Invalid.';
                });
            } else {
                vm.submitted = true;
            }

        };

        vm.authenticate = function (provider) {
            LoginService.auth(provider);
        };
    };

    var LoginAuthController = function(rootScope, state, UserService, tokens) {
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
    };

    var RegisterController = function(state, UserService){
        var vm = this;

        vm.form = {};
        vm.user = {};

        vm.register = function () {
            if (vm.form.register.$valid) {
                UserService.register(vm.user).then(function (data) {
                    vm.success = data.success;
                }, function (err) {
                    vm.error = err.message.error;
                });
            } else {
                vm.submitted = true;
            }
        };
    };

    Config.$inject = ['$stateProvider'];
    LoginController.$inject = ['$state', 'LoginService'];
    LoginAuthController.$inject = ['$rootScope', '$state', 'UserService', 'tokens'];
    RegisterController.$inject = ['$state', 'UserService'];

    angular.module('Coati.Login',
        ['ui.router', 'ui.bootstrap',
            'Coati.Directives',
            'Coati.Helpers',
            'Coati.Services.Login',
            'Coati.Services.User'])
        .config(Config)
        .controller('LoginController', LoginController)
        .controller('RegisterController', RegisterController)
        .controller('LoginAuthController', LoginAuthController);


}(angular));
