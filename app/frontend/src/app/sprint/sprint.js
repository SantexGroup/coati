(function (angular) {

    var StartSprintController = function (scope, conf, filter, modalInstance, SprintService, sprint) {
        var vm = this;
        vm.sprint = sprint;
        vm.form = {};
        vm.format = conf.DATE_FORMAT;

        var today = new Date();

        vm.min_date = today;
        vm.max_date = addDays(today, vm.sprint.sprint_duration);

        //set defaults
        vm.sprint.start_date = filter('date')(vm.min_date, vm.format);
        vm.sprint.end_date = filter('date')(vm.max_date, vm.format);

        //check change of start date
        scope.$watch('vm.sprint.start_date', function () {
            vm.max_date = filter('date')(addDays(vm.sprint.start_date, vm.sprint.sprint_duration), vm.format);
            vm.sprint.end_date = filter('date')(vm.max_date, vm.format);
        });

        // Datapicker options
        vm.dateOptions = {
            formatYear: 'yyyy',
            startingDay: 1,
            showWeeks: false
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

        vm.stopSprint = function(){
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

    StartSprintController.$inject = ['$scope','Conf', '$filter', '$modalInstance', 'SprintService', 'sprint'];
    StopSprintController.$inject = ['$modalInstance', 'SprintService', 'sprint'];

    angular.module('Coati.Sprint', ['ui.router',
        'Coati.Config',
        'Coati.Directives',
        'Coati.Services.Sprint'])
        .controller('StartSprintController', StartSprintController)
        .controller('StopSprintController', StopSprintController);

}(angular));
