(function (angular) {

    function TicketFormController(scope, modalInstance, TicketService, item) {

        scope.form = {};
        scope.ticket = item.ticket || {};
        if(item !== undefined) {
            scope.labels = item.ticket.labels || [];
        }else{
            scope.labels = [];
        }
        scope.save = function () {
            if (scope.form.ticket_form.$valid) {
                scope.ticket.labels = [];
                scope.labels.forEach(function(item){
                   scope.ticket.labels.push(item.text);
                });

                TicketService.save(item.project, scope.ticket).then(function (tkt) {
                    modalInstance.close();
                }, function(err){
                    modalInstance.dismiss('error');
                    console.log(err);
                });
            } else {
                scope.submitted = true;
            }
        };

        scope.cancel = function () {
            modalInstance.dismiss('cancelled');
        };
    }

    TicketFormController.$inject = ['$scope', '$modalInstance', 'TicketService', 'item'];

    angular.module('Coati.Ticket', ['ui.router','ngTagsInput',
        'Coati.Directives',
        'Coati.ApiServices'])
        .controller('TicketFormController', TicketFormController);


}(angular));
