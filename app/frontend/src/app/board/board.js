(function (angular) {

    var Config = function (stateProvider) {
        stateProvider.state('project.board', {
            url: 'board',
            views: {
                "project-board": {
                    controller: 'ProjectCtrlBoard',
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

    var ProjectCtrlBoard = function (scope, state, SprintService, ProjectService, TicketService) {
        scope.project_pk = state.params.project_pk;
        scope.data = {};

        var getSprintTickets = function(sprint_id){
            SprintService.get_tickets(sprint_id).then(function(tickets){
                scope.data.tickets = tickets;
            });
        };

        var getColumnConfiguration = function (project_pk) {
            ProjectService.get_columns(project_pk).then(function (cols) {
                scope.data.columns = cols;
                scope.$broadcast('dataloaded');
            });
        };

        var getProjectData = function (project_pk) {
            ProjectService.get(project_pk).then(function (prj) {
                scope.project = prj;
            });
        };

        scope.sortTickets = {
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
                    column: target._id.$oid,
                    order: new_order
                };
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

        SprintService.get_started(scope.project_pk).then(function (sprint) {
            scope.sprint = sprint;
            if (sprint.started) {
                getColumnConfiguration(scope.project_pk);
                getProjectData(scope.project_pk);
                getSprintTickets(scope.sprint._id.$oid);
            }
        });

    };

    Config.$inject = ['$stateProvider'];
    ProjectCtrlBoard.$inject = ['$scope', '$state', 'SprintService', 'ProjectService', 'TicketService'];

    angular.module('Coati.Board', ['ui.router',
        'Coati.Directives',
        'Coati.Services.Project',
        'Coati.Services.Ticket',
        'Coati.Services.Sprint'])
        .config(Config)
        .controller('ProjectCtrlBoard', ProjectCtrlBoard);

}(angular));
