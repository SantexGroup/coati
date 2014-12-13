(function (angular) {

    var Config = function (stateProvider) {
        stateProvider.state('project.planning', {
            url: 'planning',
            views: {
                "project-planning": {
                    templateUrl: 'planning/planning.tpl.html',
                    controller: 'ProjectCtrlPlanning',
                    controllerAs: 'vm'
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
        var vm = this;
        vm.ticket_detail = null;


        var getSprintsWithTickets = function (project_id) {
            SprintService.query(project_id).then(function (sprints) {
                vm.sprints = sprints;
                angular.forEach(sprints, function (val, key) {
                    if (val.started) {
                        vm.one_started = true;
                    }
                });
            });
        };

        var getTicketsForProject = function (project_id) {
            TicketService.query(project_id).then(function (tkts) {
                vm.tickets = tkts;
            });
        };

        vm.add_or_edit = function (e, tkt) {
            if (tkt) {
                tkt = angular.copy(tkt);
                tkt.pk = tkt._id.$oid;

            }
            var modal_instance = modal.open({
                controller: 'TicketFormController as vm',
                templateUrl: 'ticket/ticket_form.tpl.html',
                resolve: {
                    item: function () {
                        return {
                            'editing': (tkt !== undefined ? true : false),
                            'project': vm.project._id.$oid,
                            'ticket': tkt
                        };
                    }
                }
            });
            modal_instance.result.then(function () {
                getSprintsWithTickets(vm.project._id.$oid);
                getTicketsForProject(vm.project._id.$oid);
            });
            e.stopPropagation();
        };

        vm.showDetail = function (tkt) {
            vm.loaded = false;
            vm.ticket_clicked = true;
            TicketService.get(tkt._id.$oid).then(function (tkt_item) {
                vm.ticket_detail = tkt_item;
                vm.loaded = true;
            });
        };

        vm.delete_ticket = function (e, tkt) {
            var ticket = angular.copy(tkt);
            ticket.pk = tkt._id.$oid;
            ticket.prefix = vm.project.prefix;
            var modal_instance = modal.open({
                controller: 'TicketDeleteController as vm',
                templateUrl: 'ticket/delete_ticket.tpl.html',
                resolve: {
                    item: function () {
                        return ticket;
                    }
                }
            });
            modal_instance.result.then(function () {
                getSprintsWithTickets(vm.project._id.$oid);
                getTicketsForProject(vm.project._id.$oid);
            });
            e.stopPropagation();
        };

        vm.startSprint = function (sprint) {
            var modal_instance = modal.open({
                controller: 'StartSprintController as vm',
                templateUrl: 'sprint/start_sprint.tpl.html',
                resolve: {
                    sprint: function () {
                        //TODO: Use config to get the sprint default duration
                        sprint.sprint_duration = vm.project.sprint_duration || 10;
                        return angular.copy(sprint);
                    }
                }
            });
            modal_instance.result.then(function () {
                vm.one_started = true;
            });
        };

        vm.sortBacklog = {
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
                angular.forEach(vm.tickets, function (val, key) {
                    new_order.push(val._id.$oid);
                });
                TicketService.update_backlog_order(vm.project._id.$oid, new_order);
            },
            containment: '#planning',
            containerPositioning: 'relative',
            type_sortable: 'project'
        };

        vm.sortTickets = {
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

        vm.sortSprints = {
            accept: function (sourceItem, destItem) {
                return sourceItem.element.hasClass('sprint-item');
            },
            orderChanged: function (event) {
                //do something
                var new_order = [];
                angular.forEach(vm.sprints, function (val, key) {
                    new_order.push(val._id.$oid);
                });
                SprintService.update_order(vm.project._id.$oid, new_order);
            },
            containment: '#planning',
            containerPositioning: 'relative'
        };


        vm.create_sprint = function () {
            SprintService.save(vm.project._id.$oid).then(function (sprint) {
                vm.sprints.push(sprint);
            });
        };

        vm.remove_sprint = function (sprint_id) {
            SprintService.erase(sprint_id).then(function () {
                getSprintsWithTickets(vm.project._id.$oid);
                getTicketsForProject(vm.project._id.$oid);
            });
        };

        vm.update_sprint_name = function (sprint) {
            SprintService.update(sprint);
        };

        // get the project from the parent controller.
        vm.project = scope.$parent.project;
        getTicketsForProject(vm.project._id.$oid);
        getSprintsWithTickets(vm.project._id.$oid);
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