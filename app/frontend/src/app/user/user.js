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
        })
            .state('notifications', {
                url: '/notifications',
                views: {
                    "main": {
                        controller: 'NotificationController',
                        controllerAs: 'vm',
                        templateUrl: 'user/notifications/all.tpl.html'
                    }
                },
                data: {
                    pageTitle: 'Notifications'
                }
            });

    }

    var UserProfileController = function (rootScope, modalInstance, UserService) {
        var vm = this;
        vm.user = rootScope.user;
        vm.image = {
            resized: {
                dataURL: vm.user.picture
            }
        };

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

    var UserController = function (rootScope, filter, timeout, growl, modal, UserService, SocketIO) {

        var vm = this;
        vm.new_notifications = [];

        rootScope.$watch('user', function (new_value) {
            if (new_value !== undefined && new_value !== null) {
                vm.user = new_value;
                if (UserService.is_logged()) {
                    SocketIO.user_channel(vm.user._id.$oid);
                }
            }
        });

        var preProcessNotifications = function (list) {
            vm.all_notifications = list;
            vm.new_notifications = filter('filter')(vm.all_notifications, {viewed: false});
        };
        var getNotifications = function () {

            return UserService.notifications(10).then(function (list) {
                preProcessNotifications(list);
            });
        };

        vm.loadNotifications = function () {
            if (UserService.is_logged()) {
                if (!vm.all_notifications) {
                    getNotifications();
                }
                timeout(function () {
                    if (vm.new_notifications.length > 0) {
                        //Call to set as read
                        UserService.mark_as_viewed(10).then(function (list) {
                            preProcessNotifications(list);
                        });
                    }
                }, 5000);
            }
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

    var NotificationController = function (rootScope, UserService, SocketIO) {
        var vm = this;

        var getNotifications = function () {

            UserService.notifications().then(function (list) {
                vm.all_notifications = list;
            });
        };

        getNotifications();

        //Socket actions
        SocketIO.on('notify', function () {
            getNotifications();
        });
    };

    ConfigModule.$inject = ['$stateProvider', '$translateProvider'];
    UserController.$inject = ['$rootScope', '$filter', '$timeout', 'growl', '$modal', 'UserService', 'SocketIO'];
    NotificationController.$inject = ['$rootScope', 'UserService', 'SocketIO'];
    UserProfileController.$inject = ['$rootScope', '$modalInstance', 'UserService'];

    angular.module('Coati.User', ['ui.router', 'pascalprecht.translate',
        'Coati.SocketIO',
        'Coati.Directives',
        'Coati.Services.User'])
        .config(ConfigModule)
        .controller('UserCtrl', UserController)
        .controller('NotificationController', NotificationController)
        .controller('UserProfileCtrl', UserProfileController);

}(angular));


