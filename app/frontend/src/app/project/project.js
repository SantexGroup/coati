(function (angular) {

    function ConfigModule(stateProvider) {
        stateProvider
            .state('project-new', {
                url: '/project/new-project/',
                views: {
                    "main": {
                        controller: 'ProjectFormCtrl',
                        templateUrl: 'project/new_project.tpl.html'
                    }
                },
                data: {
                    pageTitle: 'New Project'
                }
            })
            .state('project', {
                url: '/project/:project_pk/',
                views: {
                    "main": {
                        controller: 'ProjectCtrl',
                        templateUrl: 'project/project.tpl.html'
                    }
                },
                data: {
                    pageTitle: 'Project Details'
                },
                reload: true
            })
            .state('project.planning', {
                url: 'planning',
                views: {
                    "project-planning": {
                        controller: 'ProjectCtrlPlanning',
                        templateUrl: 'project/planning.tpl.html'
                    }
                },
                tab_active: 'planning',
                data: {
                    pageTitle: 'Project Planning'
                },
                reload: true
            })
            .state('project.board', {
                url: 'board',
                views: {
                    "project-board": {
                        controller: 'ProjectCtrlBoard',
                        templateUrl: 'project/board.tpl.html'
                    }
                },
                tab_active: 'board',
                data: {
                    pageTitle: 'Project Board'
                },
                reload: true
            })
            .state('project.reports', {
                url: 'reports',
                views: {
                    "project-reports": {
                        controller: 'ProjectCtrlReports',
                        templateUrl: 'project/reports.tpl.html'
                    }
                },
                tab_active: 'reports',
                data: {
                    pageTitle: 'Project Reports'
                },
                reload: true
            })
            .state('project.settings', {
                url: 'settings',
                views: {
                    "project-settings": {
                        controller: 'ProjectCtrlSettings',
                        templateUrl: 'project/settings.tpl.html'
                    }
                },
                tab_active: 'settings',
                data: {
                    pageTitle: 'Project Settings'
                },
                reload: true
            });
    }


    function ProjectCtrl(scope, state) {

        scope.switchView = function (view) {
            state.go(view, {project_pk: state.params.project_pk}, {reload: true});
        };
        if (state.current.tab_active) {
            scope.tab_active = state.current.tab_active;
            scope[scope.tab_active] = true;
        } else {
            state.go('project.planning', {project_pk: state.params.project_pk}, {reload: true});
        }
    }

    function ProjectCtrlPlanning(scope, state, modal, ProjectService, TicketService, SprintService) {

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
    }

    function ProjectFormCtrl(scope, state, ProjectService) {
        scope.form = {};
        scope.project = {};
        scope.save = function () {
            if (scope.form.project_form.$valid) {
                ProjectService.save(scope.project).then(function (project) {
                    state.go('project.planning', {project_pk: project._id.$oid});
                }, function (err) {
                    console.log(err);
                });
            } else {
                scope.submitted = true;
            }
        };

        scope.cancel = function () {
            state.go('home');
        };
    }

    function ProjectCtrlBoard(scope, state, ProjectService) {

    }

    function ProjectCtrlReports(scope, state, ProjectService) {

    }

    function ProjectCtrlSettings(scope, rootScope, state, modal, ProjectService) {
        scope.data = {};

        scope.delete_col = function (item) {
            var col = angular.copy(item);
            col.pk = item._id.$oid;
            var modalInstance = modal.open({
                controller: 'ColumnDeleteController',
                templateUrl: 'settings/delete_column.tpl.html',
                resolve: {
                    column: function () {
                        return col;
                    }
                }
            });
            modalInstance.result.then(function () {
                getColumnConfiguration(scope.project._id.$oid);
            });
        };

        scope.add_or_edit = function (item) {
            if (item) {
                item = angular.copy(item);
                item.pk = item._id.$oid;
            }
            var modalInstance = modal.open({
                controller: 'ColumnFormController',
                templateUrl: 'settings/new_column_form.tpl.html',
                resolve: {
                    project: function () {
                        return scope.project._id.$oid;
                    },
                    column: function () {
                        return item;
                    }
                }
            });
            modalInstance.result.then(function () {
                getColumnConfiguration(scope.project._id.$oid);
            });
        };

        scope.save = function () {
            if (scope.form.project_form.$valid) {
                scope.project.owner_id = scope.project.owner.id;
                ProjectService.update(scope.project._id.$oid, scope.project).then(function(){
                    rootScope.$broadcast('notify', {
                        'title': 'Updated',
                        'description': 'The project settings were saved'
                    });
                });
            } else {
                scope.submitted = true;
            }
        };

        //order_columns
        scope.sortColumns = {
            accept: function (sourceItem, destItem) {
                return true;
            },
            orderChanged: function (event) {
                //do something
                var new_order = [];
                angular.forEach(scope.data.columns, function (val, key) {
                    new_order.push(val._id.$oid);
                });
                ProjectService.order_columns(scope.project._id.$oid, new_order);
            },
            containment: '#planning',
            containerPositioning: 'relative'
        };

        var getColumnConfiguration = function (project_id) {
            ProjectService.get_columns(project_id).then(function (cols) {
                scope.data.columns = cols;
            });
        };

        ProjectService.get(state.params.project_pk).then(function (prj) {
            scope.project = prj;
            getColumnConfiguration(prj._id.$oid);
        });
    }

    ConfigModule.$inject = ['$stateProvider'];
    ProjectCtrl.$inject = ['$scope', '$state'];
    ProjectCtrlPlanning.$inject = ['$scope', '$state', '$modal', 'ProjectService', 'TicketService', 'SprintService'];
    ProjectCtrlBoard.$inject = ['$scope', '$state', 'ProjectService'];
    ProjectCtrlReports.$inject = ['$scope', '$state', 'ProjectService'];
    ProjectCtrlSettings.$inject = ['$scope', '$rootScope', '$state', '$modal', 'ProjectService'];
    ProjectFormCtrl.$inject = ['$scope', '$state', 'ProjectService'];

    angular.module('Coati.Project', ['ui.router', 'ui.sortable',
        'Coati.Settings',
        'Coati.Directives',
        'Coati.ApiServices'])
        .config(ConfigModule)
        .controller('ProjectCtrl', ProjectCtrl)
        .controller('ProjectCtrlPlanning', ProjectCtrlPlanning)
        .controller('ProjectCtrlBoard', ProjectCtrlBoard)
        .controller('ProjectCtrlReports', ProjectCtrlReports)
        .controller('ProjectCtrlSettings', ProjectCtrlSettings)
        .controller('ProjectFormCtrl', ProjectFormCtrl);

}(angular));
