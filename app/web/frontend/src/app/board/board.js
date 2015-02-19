(function (angular) {

    var Config = function (stateProvider) {
        stateProvider.state('project.board', {
            url: '/board?ticket',
            views: {
                'project-board': {
                    controller: 'ProjectCtrlBoard',
                    controllerAs: 'vm',
                    templateUrl: 'board/board.tpl.html'
                }
            },
            tab_active: 'board',
            data: {
                pageTitle: 'Project Board'
            }
        });
    };

    var ProjectCtrlBoard = function (rootScope, scope, state, location, modal, SprintService, ProjectService, TicketService, SocketIO) {
        var vm = this;
        vm.enabled = false;
        vm.project_pk = scope.$parent.project._id.$oid;
        vm.project = scope.$parent.project;

        // set the active tab
        scope.$parent.vm[state.current.tab_active] = true;

        vm.is_scrumm = function(){
          return vm.project.project_type === 'S';
        };

        var getSprintTickets = function (sprint_id) {
            SprintService.get_tickets(vm.project._id.$oid, sprint_id).then(function (tickets) {
                vm.tickets = tickets;
            });
        };

        var getProjectTickets = function (project_pk) {
            TicketService.board(project_pk).then(function (tkts) {
                vm.tickets = tkts;
            });
        };

        var getMembers = function () {
            ProjectService.get_members(vm.project._id.$oid).then(function (usrs) {
                vm.users = usrs;
            });
        };

        var getColumnConfiguration = function (project_pk) {
            ProjectService.get_columns(project_pk).then(function (cols) {
                vm.columns = cols;
                rootScope.$broadcast('board-loaded');
            });
        };

        var reloadData = function(){
            getColumnConfiguration(vm.project._id.$oid);
            if (vm.is_scrumm()) {
                if (vm.sprint.started) {
                    getSprintTickets(vm.project._id.$oid);
                }
            } else {
                getProjectTickets(vm.project._id.$oid);
            }
        };

        var showTicketDetails = function (id) {
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
                reloadData();
            }, function () {
               reloadData();
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
                    var data = {};
                    /* this happens with the order in the same sortable */
                    if (this.sender == null) {
                        if (target.col) {
                            angular.forEach(ui.item.sortable.sourceModel, function (v, k) {
                                new_order.push(v._id.$oid);
                            });
                            //update order
                            data = {
                                order: new_order,
                                sprint: vm.sprint ? vm.sprint._id.$oid : null
                            };
                            TicketService.order_ticket_column(vm.project._id.$oid, target.col._id.$oid, data);
                        }

                    } else {
                        angular.forEach(ui.item.sortable.droptargetModel, function (v, k) {
                            new_order.push(v._id.$oid);
                        });
                        data = {
                            ticket: ticket._id.$oid,
                            order: new_order,
                            sprint: vm.sprint ? vm.sprint._id.$oid : null
                        };
                        if (target) {
                            if (target.col) {
                                data.column = target.col._id.$oid;
                            } else {
                                data.backlog = target.vm.sprint._id.$oid;
                            }
                            TicketService.transition(vm.project._id.$oid, data);
                        }

                    }
                }
            }
        };

        if (vm.is_scrumm()) {
            SprintService.get_started(vm.project._id.$oid).then(function (sprint) {
                vm.sprint = sprint;
                if (vm.sprint.started) {
                    vm.enabled = vm.sprint.started;
                    reloadData();
                    getMembers();
                }
            });
        } else {
            vm.enabled = true;
            reloadData();
            getMembers();
        }

        //Socket IO listeners
        SocketIO.on('ticket_transition', function () {
            reloadData();
        });
        SocketIO.on('new_column', function () {
            reloadData();
        });
        SocketIO.on('delete_column', function () {
            reloadData();
        });
        SocketIO.on('order_columns', function () {
            reloadData();
        });
        SocketIO.on('update_ticket', function () {
            reloadData();
        });

    };

    Config.$inject = ['$stateProvider', '$translateProvider'];
    ProjectCtrlBoard.$inject = ['$rootScope', '$scope', '$state', '$location', '$modal', 'SprintService', 'ProjectService', 'TicketService', 'SocketIO'];

    angular.module('Coati.Board', ['ui.router',
        'pascalprecht.translate',
        'Coati.SocketIO',
        'Coati.Directives',
        'Coati.Services.Project',
        'Coati.Services.Ticket',
        'Coati.Services.Sprint'])
        .config(Config)
        .controller('ProjectCtrlBoard', ProjectCtrlBoard);

}(angular));
