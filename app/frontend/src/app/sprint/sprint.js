(function (angular) {

    var Config = function (stateProvider) {
        stateProvider.state('project.archived', {
            url: '/archived-sprints',
            views: {
                "project-archived": {
                    controller: 'ArchivedSprintController',
                    controllerAs: 'vm',
                    templateUrl: 'sprint/archived.tpl.html'
                }
            },
            tab_active: 'archived',
            data: {
                pageTitle: 'Archived Sprints'
            },
            reloadOnSearch: false,
            reload: true
        });
    };

    var ArchivedSprintController = function (rootScope, scope, modal, SprintService, SocketIO) {

        var vm = this;

        vm.project = scope.$parent.project;

        var getSprintsWithTickets = function (project_id) {
            SprintService.archived(project_id).then(function (sprints) {
                vm.sprints = sprints;
            });
        };


        vm.showDetails = function (e, tkt) {
            if (tkt) {
                tkt = angular.copy(tkt);
                tkt.pk = tkt._id.$oid;

            }
            var modal_instance = modal.open({
                controller: 'TicketDetailController as vm',
                templateUrl: 'ticket/ticket_detail_view.tpl.html',
                resolve: {
                    item: function () {
                        return {
                            'project': vm.project,
                            'ticket_id': tkt._id.$oid,
                            'disabled': true
                        };
                    }
                }
            });
            modal_instance.result.then(function () {
                getSprintsWithTickets(vm.project._id.$oid);
            });
            e.stopPropagation();
        };

        getSprintsWithTickets(vm.project._id.$oid);

    };

    var StartSprintController = function (scope, conf, filter, modalInstance, SprintService, sprint) {
        var vm = this;
        vm.sprint = sprint;
        vm.form = {};
        vm.format = conf.DATE_FORMAT;

        var today = new Date();

        vm.min_date = today;
        vm.max_date = new Date(today.getTime() + vm.sprint.sprint_duration * 24 * 60 * 60 * 1000);

        //set defaults
        vm.sprint.start_date = filter('date')(vm.min_date, vm.format);
        vm.sprint.end_date = filter('date')(vm.max_date, vm.format);

        //check change of start date
        scope.$watch(function(){
            return vm.sprint.start_date;
        }, function (new_val) {
            if(new_val instanceof Date) {
                var md = new Date(new_val.getTime() + vm.sprint.sprint_duration * 24 * 60 * 60 * 1000);
                vm.max_date = filter('date')(md, vm.format);
                vm.sprint.end_date = filter('date')(vm.max_date, vm.format);
            }
        });

        // Datapicker options
        vm.dateOptions = {
            formatYear: 'yyyy',
            startingDay: 1,
            showWeeks: false,
            formatMonth: 'MMM',
            showButtonBar: false
        };
        // Datapicker open
        vm.openStartDate = function ($event) {
            $event.preventDefault();
            $event.stopPropagation();
            vm.startDateOpened = true;
        };

        vm.openEndDate = function ($event) {
            $event.preventDefault();
            $event.stopPropagation();
            vm.endDateOpened = true;
        };


        vm.save = function () {
            if (vm.form.sprint_form.$valid) {
                vm.sprint.for_starting = true;
                SprintService.update(vm.sprint).then(function (sp) {
                    modalInstance.close();
                }, function (err) {
                    modalInstance.dismiss('error');
                    console.log(err);
                });
            } else {
                vm.submitted = true;
            }
        };

        vm.cancel = function () {
            modalInstance.dismiss('cancelled');
        };
    };

    var StopSprintController = function (modalInstance, SprintService, sprint) {
        var vm = this;

        vm.sprint = sprint;

        vm.stopSprint = function () {
            vm.sprint.for_finalized = true;
            SprintService.update(vm.sprint).then(function (sp) {
                modalInstance.close();
            }, function (err) {
                modalInstance.dismiss('error');
            });
        };

        vm.cancel = function () {
            modalInstance.dismiss('cancelled');
        };
    };

    Config.$inject = ['$stateProvider'];
    ArchivedSprintController.$inject = ['$rootScope', '$scope', '$modal', 'SprintService', 'SocketIO'];
    StartSprintController.$inject = ['$scope', 'Conf', '$filter', '$modalInstance', 'SprintService', 'sprint'];
    StopSprintController.$inject = ['$modalInstance', 'SprintService', 'sprint'];

    angular.module('Coati.Sprint', ['ui.router',
        'Coati.Config',
        'Coati.SocketIO',
        'Coati.Directives',
        'Coati.Services.Sprint'])
        .config(Config)
        .controller('ArchivedSprintController', ArchivedSprintController)
        .controller('StartSprintController', StartSprintController)
        .controller('StopSprintController', StopSprintController);

}(angular));
