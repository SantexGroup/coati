(function (angular) {

    var Config = function (stateProvider) {
        stateProvider.state('project.board', {
            url: '/board?ticket',
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
            reloadOnSearch: false,
            reload: true
        });
    };

    var ProjectCtrlBoard = function (rootScope, state, location, modal, SprintService, ProjectService, TicketService, SocketIO) {
        var vm = this;

        vm.project_pk = state.params.project_pk;

        var getSprintTickets = function (sprint_id) {
            SprintService.get_tickets(sprint_id).then(function (tickets) {
                vm.tickets = tickets;
            });
        };

        var getMembers = function () {
            ProjectService.get_members(vm.project_pk).then(function (usrs) {
                vm.users = usrs;
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
                if (state.params.ticket) {
                    showTicketDetails(state.params.ticket);
                }
            });
        };

        var showTicketDetails = function (id) {
            vm.already_showed = true;

            var args = location.search();
            if (!args.ticket) {
                location.search('ticket', id);
            }

            vm.modal_ticket_instance = modal.open({
                controller: 'TicketDetailController as vm',
                templateUrl: 'ticket/ticket_detail_view.tpl.html',
                resolve: {
                    item: function () {
                        return {
                            'project': vm.project,
                            'ticket_id': id
                        };
                    }
                }
            });
            vm.modal_ticket_instance.result.then(function () {
                vm.already_showed = false;
                getColumnConfiguration(vm.project_pk);
                getSprintTickets(vm.sprint._id.$oid);
                location.search('');

            }, function () {
                vm.already_showed = false;
                getColumnConfiguration(vm.project_pk);
                getSprintTickets(vm.sprint._id.$oid);
                location.search('');
            });

        };

        vm.showDetails = function (e, tkt) {
            showTicketDetails(tkt);
            e.stopPropagation();
        };


        vm.checkAlert = function (col) {
            if (col.max_cards <= col.tickets.length) {
                return {backgroundColor: col.color_max_cards};
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
                        if(target.col) {
                            angular.forEach(ui.item.sortable.sourceModel, function (v, k) {
                                new_order.push(v._id.$oid);
                            });
                            //update order
                            data = {
                                order: new_order,
                                sprint: vm.sprint._id.$oid
                            };
                            TicketService.order_ticket_column(target.col._id.$oid, data);
                        }

                    } else {
                        angular.forEach(ui.item.sortable.droptargetModel, function (v, k) {
                            new_order.push(v._id.$oid);
                        });
                        var data = {
                            ticket: ticket._id.$oid,
                            order: new_order,
                            sprint: vm.sprint._id.$oid
                        };
                        if(target) {
                            if (target.col) {
                                data.column = target.col._id.$oid;
                            } else {
                                data.backlog = target.vm.sprint._id.$oid;
                            }
                            TicketService.transition(data);
                        }

                    }
                }
            }
        };


        SprintService.get_started(vm.project_pk).then(function (sprint) {
            vm.sprint = sprint;
            if (vm.sprint.started) {
                getColumnConfiguration(vm.project_pk);
                getProjectData(vm.project_pk);
                getSprintTickets(vm.sprint._id.$oid);
                getMembers();
            }
        });


        //Socket IO listeners

        SocketIO.init(vm.project_pk, rootScope.user._id.$oid);
        SocketIO.on('ticket_transition', function(){
            if (vm.sprint.started) {
                getSprintTickets(vm.sprint._id.$oid);
                getColumnConfiguration(vm.project_pk);
            }
        });
        SocketIO.on('new_column', function(){
            if (vm.sprint.started) {
                getSprintTickets(vm.sprint._id.$oid);
                getColumnConfiguration(vm.project_pk);
            }
        });
        SocketIO.on('delete_column', function(){
            if (vm.sprint.started) {
                getSprintTickets(vm.sprint._id.$oid);
                getColumnConfiguration(vm.project_pk);
            }
        });
        SocketIO.on('order_columns', function(){
            if (vm.sprint.started) {
                getSprintTickets(vm.sprint._id.$oid);
                getColumnConfiguration(vm.project_pk);
            }
        });
        SocketIO.on('update_ticket', function () {
            if (vm.sprint.started) {
                getSprintTickets(vm.sprint._id.$oid);
                getColumnConfiguration(vm.project_pk);
            }
        });


        //This is for control back button and show modal or not
        rootScope.$watch(function () {
            return location.search();
        }, function () {
            var params = location.search();
            if (params.ticket && !vm.already_showed) {
                if (vm.project) {
                    showTicketDetails(params.ticket);
                }
            } else {
                if (vm.already_showed && vm.modal_ticket_instance && !params.ticket) {
                    vm.modal_ticket_instance.close();
                    vm.already_showed = false;
                }
            }
        }, true);

    };

    Config.$inject = ['$stateProvider'];
    ProjectCtrlBoard.$inject = ['$rootScope', '$state', '$location', '$modal', 'SprintService', 'ProjectService', 'TicketService', 'SocketIO'];

    angular.module('Coati.Board', ['ui.router',
        'Coati.SocketIO',
        'Coati.Directives',
        'Coati.Services.Project',
        'Coati.Services.Ticket',
        'Coati.Services.Sprint'])
        .config(Config)
        .controller('ProjectCtrlBoard', ProjectCtrlBoard);

}(angular));
