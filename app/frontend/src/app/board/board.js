(function (angular) {

    var Config = function (stateProvider) {
        stateProvider.state('project.board', {
            url: 'board',
            views: {
                "project-board": {
                    controller: 'ProjectCtrlBoard',
                    controllerAs: 'vm',
                    templateUrl: 'board/board.tpl.html'
                }
            },
            tab_active: 'board',
            data: {
                pageTitle: 'Project Board'
            },
            reload: true
        });
    };

    var ProjectCtrlBoard = function (rootScope, state, SprintService, ProjectService, TicketService) {
        var vm = this;

        vm.project_pk = state.params.project_pk;

        var getSprintTickets = function(sprint_id){
            SprintService.get_tickets(sprint_id).then(function(tickets){
                vm.tickets = tickets;
            });
        };

        var getColumnConfiguration = function (project_pk) {
            ProjectService.get_columns(project_pk).then(function (cols) {
                vm.columns = cols;
                rootScope.$broadcast('board-loaded');
            });
        };

        var getProjectData = function (project_pk) {
            ProjectService.get(project_pk).then(function (prj) {
                vm.project = prj;
            });
        };

        vm.checkAlert = function(col){
            if(col.max_cards <= col.tickets.length){
                return {backgroundColor: col.color_max_cards};
            }
        };

        vm.sortTickets = {
            accept: function (sourceItem, destItem) {
                return sourceItem.element.hasClass('ticket-item');
            },
            itemMoved: function (event) {
                // This happens when a ticket is moved from the Backlog to a Sprint
                var source = event.source.itemScope.tkt;
                var target = event.dest.sortableScope.$parent.col;

                var new_order = [];
                angular.forEach(event.dest.sortableScope.modelValue, function (val, key) {
                   new_order.push(val._id.$oid);
                });

                var data = {
                    ticket: source._id.$oid,
                    order: new_order
                };

                if(target){
                    data.column = target._id.$oid;
                }else{
                    data.backlog = vm.sprint._id.$oid;
                }
                TicketService.transition(data);
            },
            orderChanged: function (event) {
                // This happens when a ticket is sorted in the column
                var new_order = [];
                angular.forEach(event.source.sortableScope.modelValue, function (val, key) {
                    new_order.push(val._id.$oid);
                });
                var col_id = event.dest.sortableScope.$parent.col._id.$oid;
                if(col_id) {
                    var data = {
                        order: new_order
                    };
                    TicketService.order_ticket_column(col_id, data);
                }
            },
            containment: '#board-area-wrapper',
            containerPositioning: 'relative',
            scrollableContainer: '#board-area'
        };

        SprintService.get_started(vm.project_pk).then(function (sprint) {
            vm.sprint = sprint;
            if (vm.sprint.started) {
                getColumnConfiguration(vm.project_pk);
                getProjectData(vm.project_pk);
                getSprintTickets(vm.sprint._id.$oid);
            }
        });

    };

    Config.$inject = ['$stateProvider'];
    ProjectCtrlBoard.$inject = ['$rootScope', '$state', 'SprintService', 'ProjectService', 'TicketService'];

    angular.module('Coati.Board', ['ui.router',
        'Coati.Directives',
        'Coati.Services.Project',
        'Coati.Services.Ticket',
        'Coati.Services.Sprint'])
        .config(Config)
        .controller('ProjectCtrlBoard', ProjectCtrlBoard);

}(angular));
