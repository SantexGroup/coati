(function (angular) {

    /**
     * Configuration module users
     * @param stateProvider
     * @constructor
     */
    function ConfigModule(stateProvider) {
        stateProvider.state('profile', {
            url: '/profile/me/',
            views: {
                "main": {
                    controller: 'UserProfileCtrl',
                    templateUrl: 'user/user.tpl.html'
                }
            },
            data: {
                pageTitle: 'User Profile'
            }
        });
    }

    function UserProfileController(rootScope, UserService) {
        var vm = this;
        rootScope.$watch('userGlobal', function (user) {
            if (user != null) {
                vm.user = rootScope.userGlobal;
                if (vm.user.profile && vm.user.profile.picture !== '') {
                    vm.image = {
                        resized: {
                            dataURL: vm.user.profile.picture
                        }
                    };
                }
                vm.save = function (image, form) {
                    vm.user.profile = {
                        id: scope.user.id,
                        picture: image ? image.resized.dataURL : ''
                    };
                    UserService.save(vm.user).then(function (data) {
                        console.log('USER UPDATED');
                    });
                };
            }
        });

    }

    function UserController(rootScope, state, UserService) {
        //To Do
    }

    ConfigModule.$inject = ['$stateProvider'];
    UserController.$inject = ['$rootScope', '$state', 'UserService'];
    UserProfileController.$inject = ['$rootScope', 'UserService'];

    angular.module('Coati.User', ['ui.router',
        'Coati.Directives',
        'Coati.Services.User'])
        .config(ConfigModule)
        .controller('UserCtrl', UserController)
        .controller('UserProfileCtrl', UserProfileController);

}(angular));


