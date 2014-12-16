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

    var UserProfileController = function (rootScope, modalInstance, UserService) {
        var vm = this;
        vm.user = rootScope.user;

        vm.save = function () {
            if (vm.form.user_form.$valid) {
                vm.user.picture = vm.image ? vm.image.resized.dataURL : '';
                UserService.update(vm.user.id, vm.user).then(function (data) {
                    rootScope.$broadcast('notify', {
                        'title': 'Profile Updated',
                        'description': 'The profile was updated'
                    });
                });
            } else {
                vm.submitted = true;
            }
        };

        vm.close = function () {
            modalInstance.dismiss('closed');
        };


    };

    var UserController = function (rootScope, modal) {

        var vm = this;

        rootScope.$watch('user', function(new_value){
            if(new_value !== undefined && new_value !== null) {
                vm.user = new_value;
            }
        });


        vm.show_profile = function () {
            var modalInstance = modal.open({
                controller: 'UserProfileCtrl as vm',
                templateUrl: 'user/user.tpl.html'
            });
            modalInstance.result.then(function () {
                //see here!
            });

        };

    };

    ConfigModule.$inject = ['$stateProvider'];
    UserController.$inject = ['$rootScope', '$modal'];
    UserProfileController.$inject = ['$rootScope', '$modalInstance', 'UserService'];

    angular.module('Coati.User', ['ui.router',
        'Coati.Directives',
        'Coati.Services.User'])
        .config(ConfigModule)
        .controller('UserCtrl', UserController)
        .controller('UserProfileCtrl', UserProfileController);

}(angular));


