(function (angular) {

    var StartSprintController = function(modalInstance, SprintService, sprint) {
        var vm = this;
        vm.sprint = sprint;
        vm.form = {};
        vm.format = 'MM/dd/yyyy';

        var today = new Date();

        vm.min_date = today;
        vm.max_date = addDays(today, vm.sprint.sprint_duration);

        //set defaults
        vm.sprint.start_date = vm.min_date;
        vm.sprint.end_date = vm.max_date;

        //check change of start date
        vm.$watch('vm.sprint.start_date',function(){
          vm.max_date = addDays(vm.sprint.start_date, vm.sprint.sprint_duration);
          vm.sprint.end_date = vm.max_date;
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


        vm.save = function(){
            if (vm.form.sprint_form.$valid) {
                vm.sprint.for_starting = true;
                SprintService.update(vm.sprint).then(function (sp) {
                    modalInstance.close();
                }, function(err){
                    modalInstance.dismiss('error');
                    console.log(err);
                });
            } else {
                vm.submitted = true;
            }
        };

        vm.cancel = function(){
            modalInstance.dismiss('cancelled');
        };
    };

    StartSprintController.$inject = ['$modalInstance', 'SprintService', 'sprint'];

    angular.module('Coati.Sprint', ['ui.router',
        'Coati.Directives',
        'Coati.Services.Sprint'])
        .controller('StartSprintController', StartSprintController);

}(angular));
