(function (angular) {

    function TicketFormController(scope, modalInstance, TicketService, item) {

        scope.form = {};
        scope.ticket = item.ticket || {};
        if(item.ticket !== undefined) {
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
                if(item.ticket){
                    TicketService.update(scope.ticket.pk, scope.ticket).then(function (tkt) {
                        modalInstance.close();
                    }, function (err) {
                        modalInstance.dismiss('error');
                        console.log(err);
                    });
                }else {
                    TicketService.save(item.project, scope.ticket).then(function (tkt) {
                        modalInstance.close();
                    }, function (err) {
                        modalInstance.dismiss('error');
                        console.log(err);
                    });
                }
            } else {
                scope.submitted = true;
            }
        };

        scope.cancel = function () {
            modalInstance.dismiss('cancelled');
        };
    }

    var TicketDeleteController = function(scope, modalInstance, TicketService, item){
        scope.ticket = item;
        scope.erase = function(){
            TicketService.delete_ticket(scope.ticket.pk).then(function(){
                modalInstance.close('delete');
            });
        };

        scope.cancel = function(){
            modalInstance.dismiss('cancelled');
        };

    };

    TicketFormController.$inject = ['$scope', '$modalInstance', 'TicketService', 'item'];
    TicketDeleteController.$inject = ['$scope', '$modalInstance', 'TicketService', 'item'];

    angular.module('Coati.Ticket', ['ui.router','ngTagsInput',
        'Coati.Directives',
        'Coati.ApiServices'])
        .controller('TicketFormController', TicketFormController)
        .controller('TicketDeleteController', TicketDeleteController);


}(angular));
