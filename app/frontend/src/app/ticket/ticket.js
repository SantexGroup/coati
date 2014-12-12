(function (angular) {

    var TicketFormController = function(modalInstance, TicketService, item) {
        var vm = this;

        vm.form = {};
        vm.ticket = item.ticket || {};
        if(item.ticket !== undefined) {
            vm.labels = item.ticket.labels || [];
        }else{
            vm.labels = [];
        }

        vm.save = function () {
            if (vm.form.ticket_form.$valid) {
                vm.ticket.labels = [];
                vm.labels.forEach(function(item){
                   vm.ticket.labels.push(item.text);
                });
                if(item.ticket){
                    TicketService.update(vm.ticket.pk, vm.ticket).then(function (tkt) {
                        modalInstance.close();
                    }, function (err) {
                        modalInstance.dismiss('error');
                        console.log(err);
                    });
                }else {
                    TicketService.save(item.project, vm.ticket).then(function (tkt) {
                        modalInstance.close();
                    }, function (err) {
                        modalInstance.dismiss('error');
                        console.log(err);
                    });
                }
            } else {
                vm.submitted = true;
            }
        };

        vm.cancel = function () {
            modalInstance.dismiss('cancelled');
        };
    };

    var TicketDeleteController = function(modalInstance, TicketService, item){
        var vm = this;
        vm.ticket = item;
        vm.erase = function(){
            TicketService.delete_ticket(vm.ticket.pk).then(function(){
                modalInstance.close('delete');
            });
        };

        vm.cancel = function(){
            modalInstance.dismiss('cancelled');
        };

    };

    TicketFormController.$inject = ['$modalInstance', 'TicketService', 'item'];
    TicketDeleteController.$inject = ['$modalInstance', 'TicketService', 'item'];

    angular.module('Coati.Ticket', ['ui.router','ngTagsInput',
        'Coati.Directives',
        'Coati.Services.Ticket'])
        .controller('TicketFormController', TicketFormController)
        .controller('TicketDeleteController', TicketDeleteController);


}(angular));
