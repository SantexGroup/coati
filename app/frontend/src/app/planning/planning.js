(function (angular) {

    var Config = function (stateProvider) {
        stateProvider.state('project.planning', {
            url: 'planning',
            views: {
                "project-planning": {
                    controller: 'ProjectCtrlPlanning',
                    templateUrl: 'planning/planning.tpl.html'
                }
            },
            tab_active: 'planning',
            data: {
                pageTitle: 'Project Planning'
            },
            reload: true
        });
    };

    var ProjectCtrlPlanning = function (scope, state, modal, ProjectService, TicketService, SprintService) {

        scope.data = {};
        scope.ticket_detail = null;


        var getSprintsWithTickets = function (project_id) {
            SprintService.query(project_id).then(function (sprints) {
                scope.data.sprints = sprints;
                angular.forEach(sprints, function (val, key) {
                    if (val.started) {
                        scope.data.one_started = true;
                    }
                });
            });
        };

        var getTicketsForProject = function (project_id) {
            TicketService.query(project_id).then(function (tkts) {
                scope.data.tickets = tkts;
            });
        };

        scope.add_or_edit = function (e, tkt) {
            if (tkt) {
                tkt = angular.copy(tkt);
                tkt.pk = tkt._id.$oid;

            }
            var modal_instance = modal.open({
                controller: 'TicketFormController',
                templateUrl: 'ticket/ticket_form.tpl.html',
                resolve: {
                    item: function () {
                        return {
                            'editing': (tkt !== undefined ? true : false),
                            'project': scope.project._id.$oid,
                            'ticket': tkt
                        };
                    }
                }
            });
            modal_instance.result.then(function () {
                getSprintsWithTickets(scope.project._id.$oid);
                getTicketsForProject(scope.project._id.$oid);
            });
            e.stopPropagation();
        };

        scope.showDetail = function (tkt) {
            scope.loaded = false;
            scope.ticket_clicked = true;
            TicketService.get(tkt._id.$oid).then(function (tkt_item) {
                scope.ticket_detail = tkt_item;
                scope.loaded = true;
            });
        };

        scope.delete_ticket = function (e, tkt) {
            var ticket = angular.copy(tkt);
            ticket.pk = tkt._id.$oid;
            ticket.prefix = scope.project.prefix;
            var modal_instance = modal.open({
                controller: 'TicketDeleteController',
                templateUrl: 'ticket/delete_ticket.tpl.html',
                resolve: {
                    item: function () {
                        return ticket;
                    }
                }
            });
            modal_instance.result.then(function () {
                getSprintsWithTickets(scope.project._id.$oid);
                getTicketsForProject(scope.project._id.$oid);
            });
            e.stopPropagation();
        };

        scope.startSprint = function (sprint) {
            var modal_instance = modal.open({
                controller: 'StartSprintController',
                templateUrl: 'sprint/start_sprint.tpl.html',
                resolve: {
                    sprint: function () {
                        sprint.sprint_duration = scope.project.sprint_duration || 15;
                        return angular.copy(sprint);
                    }
                }
            });
            modal_instance.result.then(function () {
                //TODO: When sprint started see how to handle that no other sprint can started and this one must be stopped.

            });
        };

        scope.sortBacklog = {
            accept: function (sourceItem, destItem) {
                return sourceItem.element.hasClass('user-story') || sourceItem.element.hasClass('ticket-item');
            },
            itemMoved: function (event) {
                // This happens when a ticket is moved from the Backlog to a Sprint
                var source = event.source.itemScope.modelValue;
                var dest = event.dest.sortableScope.$parent.modelValue;
                var new_order = [];
                angular.forEach(event.dest.sortableScope.modelValue, function (val, key) {
                    new_order.push(val._id.$oid);
                });
                var data = {
                    source: {
                        ticket_id: source._id.$oid,
                        project_id: source.project._id.$oid,
                        number: source.number
                    },
                    dest: {
                        sprint_id: dest._id.$oid,
                        order: new_order
                    }
                };
                TicketService.movement(data);
            },
            orderChanged: function (event) {
                // This happens when a ticket is sorted in the backlog
                var new_order = [];
                angular.forEach(scope.data.tickets, function (val, key) {
                    new_order.push(val._id.$oid);
                });
                TicketService.update_backlog_order(scope.project._id.$oid, new_order);
            },
            containment: '#planning',
            containerPositioning: 'relative',
            type_sortable: 'project'
        };

        scope.sortTickets = {
            accept: function (sourceItem, destItem) {
                return sourceItem.element.hasClass('user-story') || sourceItem.element.hasClass('ticket-item');
            },
            itemMoved: function (event) {
                // This happens when a ticket is moved from one Sprint to another or backlog
                var dest = {};
                var new_order = [];
                var tickets = event.dest.sortableScope.modelValue;
                angular.forEach(tickets, function (val, key) {
                    new_order.push(val._id.$oid);
                });
                if (event.dest.sortableScope.options.type_sortable === 'project') {
                    dest = {
                        project_id: event.dest.sortableScope.$parent.project._id.$oid,
                        order: new_order
                    };
                } else {
                    dest = {
                        sprint_id: event.dest.sortableScope.$parent.modelValue._id.$oid,
                        order: new_order
                    };
                }
                var data = {
                    source: {
                        ticket_id: event.source.itemScope.modelValue._id.$oid,
                        sprint_id: event.source.sortableScope.$parent.modelValue._id.$oid
                    },
                    dest: dest
                };
                TicketService.movement(data);
            },
            orderChanged: function (event) {
                // This happens when a ticket is sorted withing the same Sprint
                var new_order = [];
                var tickets = event.source.sortableScope.modelValue;
                angular.forEach(tickets, function (val, key) {
                    new_order.push(val._id.$oid);
                });
                var sprint = event.source.sortableScope.$parent.modelValue;
                TicketService.update_sprint_order(sprint._id.$oid, new_order);
            },
            containment: '#planning',
            containerPositioning: 'relative',
            type_sortable: 'sprint'
        };

        scope.sortSprints = {
            accept: function (sourceItem, destItem) {
                return sourceItem.element.hasClass('sprint-item');
            },
            orderChanged: function (event) {
                //do something
                var new_order = [];
                angular.forEach(scope.data.sprints, function (val, key) {
                    new_order.push(val._id.$oid);
                });
                SprintService.update_order(scope.project._id.$oid, new_order);
            },
            containment: '#planning',
            containerPositioning: 'relative'
        };


        scope.create_sprint = function () {
            SprintService.save(scope.project._id.$oid).then(function (sprint) {
                scope.data.sprints.push(sprint);
            });
        };

        scope.remove_sprint = function (sprint_id) {
            SprintService.erase(sprint_id).then(function () {
                getSprintsWithTickets(scope.project._id.$oid);
                getTicketsForProject(scope.project._id.$oid);
            });
        };

        scope.update_sprint_name = function (sprint) {
            SprintService.update(sprint);
        };

        ProjectService.get(state.params.project_pk).then(function (prj) {
            scope.project = prj;
            getTicketsForProject(prj._id.$oid);
            getSprintsWithTickets(prj._id.$oid);
        });
    };

    Config.$inject = ['$stateProvider'];
    ProjectCtrlPlanning.$inject = ['$scope', '$state', '$modal', 'ProjectService', 'TicketService', 'SprintService'];

    angular.module('Coati.Planning', ['ui.router',
        'Coati.Directives',
        'Coati.Services.Project',
        'Coati.Services.Sprint',
        'Coati.Services.Ticket'])
        .config(Config)
        .controller('ProjectCtrlPlanning', ProjectCtrlPlanning);

}(angular));