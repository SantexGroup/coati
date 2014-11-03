(function () {

    function TicketModalFormController(scope, modalInstance, TicketService, Project) {
        scope.form = {};
        scope.ticket = {};
        scope.labels = [];
        scope.save = function () {
            if (scope.form.ticket_form.$valid) {
                scope.ticket.labels = [];
                scope.labels.forEach(function(item){
                   scope.ticket.labels.push(item.text);
                });
                TicketService.save(Project._id.$oid, scope.ticket).then(function (tkt) {
                    modalInstance.close(tkt);
                }, function(err){
                    console.log(err);
                });
            } else {
                scope.submitted = true;
            }
        };

        scope.cancel = function () {
            modalInstance.dismiss();
        };
    }

    TicketModalFormController.$inject = ['$scope', '$modalInstance', 'TicketService', 'Project'];

    angular.module('Koala.Tickets', ['ui.router','ngTagsInput',
        'KoalaApp.Directives',
        'KoalaApp.ApiServices'])
        .controller('TicketModalFormController', TicketModalFormController);


}());
