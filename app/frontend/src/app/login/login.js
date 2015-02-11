(function (angular) {

    function Config(stateProvider) {
        stateProvider.state('login', {
            url: '/login?logout&next',
            views: {
                "master_view": {
                    controller: 'LoginController',
                    controllerAs: 'vm',
                    templateUrl: 'login/login.tpl.html'
                }
            },
            data: {
                pageTitle: 'Coati :: Login Page'
            },
            reload:true
        })
            .state('login_auth', {
                url: '/login/auth?token&expire&next',
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
            })

            .state('login_activate', {
                url: '/login/activate_user/:activation_code',
                views: {
                    "master_view": {
                        controller: 'ActivateController'
                    }
                },
                data: {
                    pageTitle: 'Coati :: Activation'
                }
            });
    }

    var LoginController = function(state, LoginService, StorageService) {
        var vm = this;

        vm.form = {};
        vm.login = {};

        if (state.params && state.params.logout) {
            StorageService.set('token_data', null);
            StorageService.set('user', null);
        }

        vm.login_user = function () {
            if (vm.form.login.$valid) {
                vm.login.next = state.params.next;
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
            LoginService.auth(provider, state.params.next);
        };
    };

    var ActivateController = function(state, UserService) {
        if (state.params.activation_code) {
            UserService.activateUser(state.params.activation_code).then(function(data){
                 state.go('login_auth', {token: data.token,
                        expire: data.expire}, {reload: true});
            });
        } else {
            state.go('login', {reload: true});
        }
    };

    var LoginAuthController = function(rootScope, state, UserService, tokens, StorageService) {
        if (state.params.token) {
            tokens.store_token(state.params.token, state.params.expire);

            //Get here the user logged
            if (UserService.is_logged()) {
                UserService.me().then(function (user) {
                    StorageService.set('user', JSON.stringify(user));
                    rootScope.user = user;
                });
            }
            if(state.params.next && state.params.next !== 'undefined'){
                window.location.href = state.params.next;
            }else {
                state.go('home', {reload: true});
            }
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

    Config.$inject = ['$stateProvider', '$translateProvider'];
    LoginController.$inject = ['$state', 'LoginService', 'StorageService'];
    ActivateController.$inject = ['$state', 'UserService'];
    LoginAuthController.$inject = ['$rootScope', '$state', 'UserService', 'tokens', 'StorageService'];
    RegisterController.$inject = ['$state', 'UserService'];

    angular.module('Coati.Login',
        ['ui.router', 'ui.bootstrap', 'pascalprecht.translate',
            'Coati.Directives',
            'Coati.Helpers',
            'Coati.Services.Storage',
            'Coati.Services.Login',
            'Coati.Services.User'])
        .config(Config)
        .controller('LoginController', LoginController)
        .controller('RegisterController', RegisterController)
        .controller('ActivateController', ActivateController)
        .controller('LoginAuthController', LoginAuthController);


}(angular));
