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
                    templateUrl: 'app/user/user.tpl.html'
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
                UserService.update(vm.user._id.$oid, vm.user).then(function (data) {
                    modalInstance.close(data);
                });
            } else {
                vm.submitted = true;
            }
        };

        vm.close = function () {
            modalInstance.dismiss('closed');
        };


    };

    var UserController = function (rootScope, growl, modal, UserService) {

        var vm = this;
        vm.notifications = [];

        rootScope.$watch('user', function (new_value) {
            if (new_value !== undefined && new_value !== null) {
                vm.user = new_value;
            }
        });

        var getNotifications = function () {
            vm.notifications = [];
            UserService.notifications().then(function (not) {
                angular.forEach(not, function (v, k) {
                    var act = v;
                    act.activity.data = JSON.parse(v.activity.data);
                    vm.notifications.push(act);
                });
            });
        };

        vm.loadNotifications = getNotifications;

        vm.show_profile = function () {
            var modalInstance = modal.open({
                controller: 'UserProfileCtrl as vm',
                templateUrl: 'user/user.tpl.html'
            });
            modalInstance.result.then(function () {
                growl.addSuccessMessage('The user was updated successfully');
            });

        };

    };

    ConfigModule.$inject = ['$stateProvider'];
    UserController.$inject = ['$rootScope', 'growl', '$modal', 'UserService'];
    UserProfileController.$inject = ['$rootScope', '$modalInstance', 'UserService'];

    angular.module('Coati.User', ['ui.router',
        'Coati.Directives',
        'Coati.Services.User'])
        .config(ConfigModule)
        .controller('UserCtrl', UserController)
        .controller('UserProfileCtrl', UserProfileController);

}(angular));


