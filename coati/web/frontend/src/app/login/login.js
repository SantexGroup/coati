(function (angular) {

    function Config(stateProvider) {
        stateProvider.state('login', {
            url: '/login?next',
            views: {
                'master_view': {
                    controller: 'LoginController',
                    controllerAs: 'vm',
                    templateUrl: 'login/login.tpl.html'
                }
            },
            data: {
                pageTitle: 'Coati :: Login Page'
            },
            reload: true
        })
            .state('logout', {
                url: '/logout',
                views: {
                    'master_view': {
                        controller: 'LogoutController',
                        controllerAs: 'vm'
                    }
                },
                data:{
                    pageTitle: 'Coati :: Logout Page'
                }
            })

            .state('register', {
                url: '/register',
                views: {
                    'master_view': {
                        controller: 'RegisterController',
                        controllerAs: 'vm',
                        templateUrl: 'login/register.tpl.html'
                    }
                },
                data: {
                    pageTitle: 'Coati :: Register'
                }
            })

            .state('activate', {
                url: '/activation/:activation_code',
                views: {
                    'master_view': {
                        controller: 'ActivateController'
                    }
                },
                data: {
                    pageTitle: 'Coati :: Activation'
                }
            });
    }

    var LoginController = function (state, log, AppConfig, Facebook, GooglePlus, TokenService, StorageService, LoginService, UserService) {
        var vm = this;

        vm.form = {};
        vm.login = {};

        // TODO: maybe all following functions should be services
        var login = function (provider, token, userID) {
            var promise = null;

            if (provider) {
                var data = {
                    'provider': provider,
                    'token': token,
                    'user_id': userID
                };

                promise = LoginService.auth(data);
            } else {
                promise = LoginService.login(vm.credentials);
            }

            promise.then(function (data) {
                storeData(data);
                state.go('home');
            }, function (err) {
                log.debug(err);

                if(err.data.message) {
                    vm.serverError = err.data.message;
                }
            });
        };

        var storeData = function (data) {
            // Save the auth tokens and expiration time
            TokenService.store(data);

            // Save the logged user profile info.
            UserService.me().then(function(user){
                StorageService.set('user', JSON.stringify(user));
            }, function(err){
                TokenService.clean();
                StorageService.set('user', null);
                log.debug(err);
                state.go('login');
            });
        };

        vm.login_user = function () {
            if (vm.form.login.$valid) {
                login();
            } else {
                vm.submitted = true;
            }

        };

        vm.authenticate = function (provider) {
            if (provider === 'facebook') {
                Facebook.login(function (authResult) {
                    if (authResult.status === 'connected') {
                        login(
                            'facebook',
                            authResult.authResponse.accessToken,
                            authResult.authResponse.userID
                        );
                    }
                }, {scope: AppConfig.FACEBOOK_SCOPES });
            } else {
                GooglePlus.login().then(function (authResponse) {
                    if (authResponse['access_token']) {
                        GooglePlus.getUser().then(function (user) {
                            login(
                                'google',
                                authResponse.access_token, // jshint ignore:line
                                user.id
                            );
                        }, function (err) {
                            log.debug(err);
                        });
                    }
                }, function (err) {
                    log.debug(err);
                });
            }
        };
    };

    var ActivateController = function (state, UserService) {
        if (state.params.activation_code) {
            UserService.activateUser(state.params.activation_code).then(function (data) {
                state.go('login_auth', {token: data.token,
                    expire: data.expire}, {reload: true});
            });
        } else {
            state.go('login', {reload: true});
        }
    };


    var RegisterController = function (state, UserService) {
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

    /**
     * Logout Controller
     * @param state
     * @param tokenService
     * @param storageService
     * @constructor
     */
    var LogoutController = function (state, tokenService, storageService) {
        if (storageService.get('user')) {
            storageService.set('user', null);
            tokenService.clean();
        }
        state.go('login');
    };

    Config.$inject = ['$stateProvider', '$translateProvider'];
    LoginController.$inject = ['$state','$log', 'Conf', 'Facebook', 'GooglePlus', 'TokenService', 'StorageService', 'LoginService', 'UserService'];
    LogoutController.$inject = ['$state', 'TokenService', 'StorageService'];
    ActivateController.$inject = ['$state', 'UserService'];
    RegisterController.$inject = ['$state', 'UserService'];

    angular.module('Coati.Login',
        ['ui.router', 'ui.bootstrap', 'pascalprecht.translate',
            'Coati.Directives',
            'Coati.Helpers',
            'Coati.Config',
            'Coati.Services.Token',
            'Coati.Services.Login',
            'Coati.Services.User'])
        .config(Config)
        .controller('LoginController', LoginController)
        .controller('LogoutController', LogoutController)
        .controller('RegisterController', RegisterController)
        .controller('ActivateController', ActivateController);


}(angular));
