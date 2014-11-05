(function () {

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
                url: '/login/auth?token',
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

        if(state.params && state.params.logout){
            window.sessionStorage.clear();
        }

        scope.authenticate = function (provider) {
            LoginService.auth(provider).then(function (rta) {
                console.log(rta);
            });
        };
    }

    function LoginAuthController(scope, state) {
        if (state.params.token) {
            window.sessionStorage.setItem('token', state.params.token);
            state.go('home');
        } else {
            state.go('login');
        }
    }

    Config.$inject = ['$stateProvider'];
    LoginController.$inject = ['$scope', '$state', 'LoginService'];
    LoginAuthController.$inject = ['$scope', '$state'];

    angular.module('KoalaApp.Login',
        ['ui.router', 'ui.bootstrap',
            'KoalaApp.Directives',
            'KoalaApp.ApiServices'])
        .config(Config)
        .controller('LoginController', LoginController)
        .controller('LoginAuthController', LoginAuthController);


}());
