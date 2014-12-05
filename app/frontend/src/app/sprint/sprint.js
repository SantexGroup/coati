(function (angular) {

    function StartSprintController(scope, modalInstance, SprintService, sprint) {
        scope.sprint = sprint;
        scope.form = {};
        scope.format = 'MM/dd/yyyy';

        var today = new Date();

        scope.min_date = today;
        scope.max_date = addDays(today, 15);

        //set defaults
        scope.sprint.start_date = scope.min_date;
        scope.sprint.end_date = scope.max_date;

        //check change of start date
        scope.$watch('sprint.start_date',function(){
          scope.max_date = addDays(scope.sprint.start_date, 15);
          scope.sprint.end_date = scope.max_date;
        });

        // Datapicker options
        scope.dateOptions = {
            formatYear: 'yyyy',
            startingDay: 1,
            showWeeks: false
        };
        // Datapicker open
        scope.openStartDate = function ($event) {
            $event.preventDefault();
            $event.stopPropagation();
            scope.startDateOpened = true;
        };

        scope.openEndDate = function ($event) {
            $event.preventDefault();
            $event.stopPropagation();
            scope.endDateOpened = true;
        };


        scope.save = function(){
            if (scope.form.sprint_form.$valid) {
                scope.sprint.for_starting = true;
                SprintService.update(scope.sprint).then(function (sp) {
                    modalInstance.close();
                }, function(err){
                    modalInstance.dismiss('error');
                    console.log(err);
                });
            } else {
                scope.submitted = true;
            }
        };

        scope.cancel = function(){
            modalInstance.dismiss('cancelled');
        };
    }

    StartSprintController.$inject = ['$scope', '$modalInstance', 'SprintService', 'sprint'];

    angular.module('Coati.Sprint', ['ui.router', 'ui.sortable',
        'Coati.Directives',
        'Coati.ApiServices'])
        .controller('StartSprintController', StartSprintController);

}(angular));
