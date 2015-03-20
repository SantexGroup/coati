(function (angular) {

    var Config = function (stateProvider) {
        stateProvider.state('project.planning', {
            url: '/planning',
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

    var ProjectCtrlPlanning = function (rootScope, scope, state, modal, growl, ProjectService, TicketService, SprintService, SocketIO) {
        var vm = this;
        vm.ticket_detail = null;
        vm.searchBacklog = '';


        var getSprintsWithTickets = function (project_id) {
            SprintService.query(project_id).then(function (sprints) {
                vm.sprints = sprints;
                vm.one_started = false;
                angular.forEach(sprints, function (val, key) {
                    if (val.started && !val.finalized) {
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
            var modal_instance = modal.open({
                controller: 'TicketFormController as vm',
                templateUrl: 'ticket/ticket_form.tpl.html',
                resolve: {
                    item: function () {
                        return {
                            'editing': (tkt !== undefined ? true : false),
                            'project': vm.project,
                            'ticket': (tkt !== undefined ? tkt._id.$oid : null)
                        };
                    }
                }
            });
            modal_instance.result.then(function (tkt) {
                if (tkt.sprint) {
                    for (var i in vm.sprints) {
                        if (vm.sprints[i]._id.$oid === tkt.sprint._id.$oid) {
                            vm.sprints[i].tickets.push(tkt);
                            break;
                        }
                    }
                } else {
                    vm.tickets.push(tkt);
                }
                //Notify
                growl.addSuccessMessage('The ticket was saved successfully');
            });
            e.stopPropagation();
        };

        vm.renameSprint = function (sprint) {
            SprintService.update(sprint).then(function () {
                growl.addSuccessMessage('The sprint was renamed successfully');
            });
        };


        vm.saveQuickTicket = function (sprint) {
            var new_ticket = {
                title: vm.new_ticket,
                sprint: sprint
            };
            if (new_ticket.sprint) {
                new_ticket.sprint.pk = sprint._id.$oid;
            }
            TicketService.save(vm.project._id.$oid, new_ticket).then(function (tkt) {
                if (new_ticket.sprint) {
                    for (var i in vm.sprints) {
                        if (vm.sprints[i]._id.$oid === new_ticket.sprint.pk) {
                            vm.sprints[i].tickets.push(tkt);
                            break;
                        }
                    }
                } else {
                    vm.tickets.push(tkt);
                }
                vm.new_ticket = null;
            });
        };

        vm.clone_ticket = function (e, tkt) {
            TicketService.clone(vm.project._id.$oid, tkt._id.$oid).then(function (tkt) {
                vm.tickets.push(tkt);
                //getSprintsWithTickets(vm.project._id.$oid);
                //getTicketsForProject(vm.project._id.$oid);
                vm.new_ticket = null;
            });
            e.stopPropagation();
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
                    },
                    project: function () {
                        return vm.project._id.$oid;
                    }
                }
            });
            modal_instance.result.then(function () {
                getSprintsWithTickets(vm.project._id.$oid);
                getTicketsForProject(vm.project._id.$oid);
                growl.addSuccessMessage('The ticket was deleted successfully');
            });
            e.stopPropagation();
        };

        vm.startSprint = function (sprint) {
            var modal_instance = modal.open({
                controller: 'StartSprintController as vm',
                templateUrl: 'sprint/sprint_form.tpl.html',
                resolve: {
                    sprint: function () {
                        sprint.sprint_duration = vm.project.sprint_duration;
                        sprint.to_start = true;
                        return angular.copy(sprint);
                    },
                    project: function () {
                        return vm.project._id.$oid;
                    }
                }
            });
            modal_instance.result.then(function () {
                growl.addSuccessMessage('The sprint was started successfully');
                vm.one_started = true;
                getSprintsWithTickets(vm.project._id.$oid);
            });
        };

        vm.edit_sprint = function (sprint) {
            var modal_instance = modal.open({
                controller: 'StartSprintController as vm',
                templateUrl: 'sprint/sprint_form.tpl.html',
                resolve: {
                    sprint: function () {
                        sprint.sprint_duration = vm.project.sprint_duration;
                        sprint.to_start = false;
                        return angular.copy(sprint);
                    },
                    project: function () {
                        return vm.project._id.$oid;
                    }
                }
            });
            modal_instance.result.then(function () {
                growl.addSuccessMessage('The sprint was updated successfully');
                getSprintsWithTickets(vm.project._id.$oid);
            });
        };

        vm.stopSprint = function (sprint) {
            var modal_instance = modal.open({
                controller: 'StopSprintController as vm',
                templateUrl: 'sprint/stop_sprint.tpl.html',
                resolve: {
                    sprint: function () {
                        return angular.copy(sprint);
                    },
                    project: function () {
                        return vm.project._id.$oid;
                    }
                }
            });
            modal_instance.result.then(function () {
                growl.addSuccessMessage('The sprint was stopped successfully');
                getTicketsForProject(vm.project._id.$oid);
                getSprintsWithTickets(vm.project._id.$oid);
            });
        };

        vm.sortSprintOptions = {
            connectWith: '.sprint-section',
            forcePlaceholderSize: true,
            placeholder: 'placeholder-item',
            start: function (e, ui) {
                ui.placeholder.height(ui.helper.outerHeight());
            },
            update: function (e, ui) {
                this.updated = true;
            },
            stop: function (e, ui) {
                if (this.updated) {
                    var new_order = [];
                    angular.forEach(ui.item.sortable.sourceModel, function (val, key) {
                        new_order.push(val._id.$oid);
                    });
                    SprintService.update_order(vm.project._id.$oid, new_order);
                }
            }
        };

        vm.sortTicketOptions = {
            connectWith: '.task-list',
            forcePlaceholderSize: true,
            placeholder: 'placeholder-item',
            start: function (e, ui) {
                ui.placeholder.height(ui.helper.outerHeight());
            },
            update: function (e, ui) {
                this.updated = true;
                this.sender = ui.sender !== null ? ui.sender[0] : null;
            },
            stop: function (e, ui) {
                if (this.updated) {
                    var target, sender, ticket;
                    var new_order = [];
                    target = angular.element(ui.item.sortable.droptarget).scope();
                    sender = angular.element(ui.item.sortable.source).scope();
                    ticket = ui.item.sortable.model;
                    /* this happens with the order in the same sortable */
                    if (this.sender == null) {
                        if (target.sprint !== undefined) {
                            angular.forEach(target.sprint.tickets, function (v, k) {
                                new_order.push(v._id.$oid);
                            });
                            TicketService.update_sprint_order(vm.project._id.$oid, target.sprint._id.$oid, new_order);
                        } else {
                            angular.forEach(target.vm.tickets, function (v, k) {
                                new_order.push(v._id.$oid);
                            });
                            TicketService.update_backlog_order(vm.project._id.$oid, new_order);
                        }

                    } else {
                        var dest, source;

                        //prepare destination
                        if (target.sprint === undefined) {
                            angular.forEach(target.vm.tickets, function (v, k) {
                                new_order.push(v._id.$oid);
                            });
                            // goes to backlog
                            dest = {
                                project_id: target.vm.project._id.$oid,
                                order: new_order
                            };
                        } else {
                            //goes to sprint
                            angular.forEach(target.sprint.tickets, function (v, k) {
                                new_order.push(v._id.$oid);
                            });
                            // goes to backlog
                            dest = {
                                sprint_id: target.sprint._id.$oid,
                                order: new_order
                            };
                        }

                        //prepare source
                        if (sender.sprint === undefined) {
                            angular.forEach(target.vm.tickets, function (v, k) {
                                new_order.push(v._id.$oid);
                            });
                            // goes from backlog to sprint
                            source = {
                                ticket_id: ticket._id.$oid,
                                project_id: sender.vm.project._id.$oid,
                                number: ticket.number
                            };
                        } else {
                            //goes from sprint to sprint
                            source = {
                                ticket_id: ticket._id.$oid,
                                sprint_id: sender.sprint._id.$oid
                            };
                        }

                        var data = {
                            source: source,
                            dest: dest
                        };
                        TicketService.movement(vm.project._id.$oid, data);
                    }
                }
            }
        };

        vm.create_sprint = function () {
            SprintService.save(vm.project._id.$oid).then(function (sprint) {
                vm.sprints.push(sprint);
                growl.addSuccessMessage('The sprint was created successfully');
            });
        };

        vm.remove_sprint = function (sprint_id) {
            SprintService.erase(vm.project._id.$oid, sprint_id).then(function () {
                getSprintsWithTickets(vm.project._id.$oid);
                getTicketsForProject(vm.project._id.$oid);
                growl.addSuccessMessage('The sprint was deleted successfully');
            });
        };

        // get the project from the parent controller.
        vm.project = scope.$parent.project;


        // set the active tab
        scope.$parent.vm[state.current.tab_active] = true;

        vm.is_scrumm = function () {
            return vm.project.project_type === "S";
        };

        getTicketsForProject(vm.project._id.$oid);
        getSprintsWithTickets(vm.project._id.$oid);

        //broadcasting
        rootScope.$on('savedTicket', function (evt, tkt) {
            if (tkt.sprint) {
                for (var i in vm.sprints) {
                    if (vm.sprints[i]._id.$oid === tkt.sprint._id.$oid) {
                        for(var j in vm.sprints[i].tickets){
                            if(vm.sprints[i].tickets[j]._id.$oid === tkt._id.$oid){
                                vm.sprints[i].tickets[j] = tkt;
                                break;
                            }
                        }
                        break;
                    }
                }
            } else {
                for(var k in vm.tickets){
                    if(vm.tickets[k]._id.$oid === tkt._id.$oid){
                        vm.tickets[k] = tkt;
                        break;
                    }
                }
            }
        });

        //Socket actions
        SocketIO.on('backlog_order', function () {
            getTicketsForProject(vm.project._id.$oid);
        });

        SocketIO.on('ticket_movement', function () {
            getSprintsWithTickets(vm.project._id.$oid);
            getTicketsForProject(vm.project._id.$oid);
        });
        SocketIO.on('order_sprints', function () {
            getSprintsWithTickets(vm.project._id.$oid);
        });
        SocketIO.on('new_sprint', function () {
            getSprintsWithTickets(vm.project._id.$oid);
        });
        SocketIO.on('update_sprint', function () {
            getSprintsWithTickets(vm.project._id.$oid);
        });
        SocketIO.on('sprint_ticket_order', function () {
            getSprintsWithTickets(vm.project._id.$oid);
        });
        SocketIO.on('update_ticket', function () {
            getSprintsWithTickets(vm.project._id.$oid);
            getTicketsForProject(vm.project._id.$oid);
        });

    };

    Config.$inject = ['$stateProvider', '$translateProvider'];
    ProjectCtrlPlanning.$inject = ['$rootScope', '$scope', '$state', '$modal', 'growl', 'ProjectService', 'TicketService', 'SprintService', 'SocketIO'];

    angular.module('Coati.Planning', ['ui.router', 'ui.sortable', 'pascalprecht.translate',
        'Coati.Directives',
        'Coati.SocketIO',
        'Coati.Services.Project',
        'Coati.Services.Sprint',
        'Coati.Services.Ticket'])
        .config(Config)
        .controller('ProjectCtrlPlanning', ProjectCtrlPlanning);

}(angular));