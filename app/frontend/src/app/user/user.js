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

    var UserController = function (rootScope, timeout, growl, modal, UserService, SocketIO) {

        var vm = this;
        vm.notifications = [];

        rootScope.$watch('user', function (new_value) {
            if (new_value !== undefined && new_value !== null) {
                vm.user = new_value;
                if(UserService.is_logged()){
                    SocketIO.user_channel(vm.user._id.$oid);
                }
            }
        });

        var preProcessNotifications = function (list) {
            vm.notifications = [];
            vm.all_notifications = list;
            angular.forEach(_.pull(list, 10), function (v, k) {
                var act = v;
                act.activity.data = JSON.parse(v.activity.data);
                vm.notifications.push(act);
            });
        };
        var getNotifications = function () {

            return UserService.notifications().then(function (list) {
                preProcessNotifications(list);
            });
        };

        vm.loadNotifications = function () {
            timeout(function () {
                if (!vm.all_notifications) {
                    if (UserService.is_logged()) {
                        getNotifications();
                    }
                }
                var items = _.filter(vm.all_notifications, function (n) {
                    return n.viewed === false;
                });
                if (items.length > 0) {
                    //Call to set as read
                    UserService.mark_as_viewed().then(function (list) {
                        preProcessNotifications(list);
                    });
                }
            }, 1500);
        };

        vm.show_profile = function () {
            var modalInstance = modal.open({
                controller: 'UserProfileCtrl as vm',
                templateUrl: 'user/user.tpl.html'
            });
            modalInstance.result.then(function () {
                growl.addSuccessMessage('The user was updated successfully');
            });

        };

        //Socket actions
        SocketIO.on('notify', function () {
            getNotifications();
        });

    };

    ConfigModule.$inject = ['$stateProvider'];
    UserController.$inject = ['$rootScope', '$timeout', 'growl', '$modal', 'UserService', 'SocketIO'];
    UserProfileController.$inject = ['$rootScope', '$modalInstance', 'UserService'];

    angular.module('Coati.User', ['ui.router',
        'Coati.SocketIO',
        'Coati.Directives',
        'Coati.Services.User'])
        .config(ConfigModule)
        .controller('UserCtrl', UserController)
        .controller('UserProfileCtrl', UserProfileController);

}(angular));


