(function () {

    function Config(stateProvider){
        stateProvider
            .state('new_ticket', {
                url: '/tickets-for/:project_pk/new-ticket',
                views: {
                    "main":{
                        controller: 'TicketFormController',
                        templateUrl: 'ticket/ticket_form.tpl.html'
                    }
                },
                data: {
                    pageTitle: 'Adding New Ticket'
                }
            });
    }


    function TicketFormController(scope, state, TicketService) {

        scope.form = {};
        scope.ticket = {};
        scope.labels = [];
        scope.save = function () {
            if (scope.form.ticket_form.$valid) {
                scope.ticket.labels = [];
                scope.labels.forEach(function(item){
                   scope.ticket.labels.push(item.text);
                });
                TicketService.save(state.params.project_pk, scope.ticket).then(function (tkt) {
                    //ver aca
                }, function(err){
                    console.log(err);
                });
            } else {
                scope.submitted = true;
            }
        };

        scope.cancel = function () {
            state.go('project.overview', {slug: Project.slug});
        };
    }

    Config.$inject = ['$stateProvider'];
    TicketFormController.$inject = ['$scope', '$state', 'TicketService'];

    angular.module('Coati.Tickets', ['ui.router','ngTagsInput',
        'Coati.Directives',
        'Coati.ApiServices'])
        .config(Config)
        .controller('TicketFormController', TicketFormController);


}());
