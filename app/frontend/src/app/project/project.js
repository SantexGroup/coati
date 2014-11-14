(function () {

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
                url: '/project/:slug/',
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
            .state('project.overview', {
                url: 'overview',
                views: {
                    "project-overview": {
                        controller: 'ProjectCtrlOverview',
                        templateUrl: 'project/overview.tpl.html'
                    }
                },
                tab_active: 'overview',
                data: {
                    pageTitle: 'Project Overview'
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
            state.go(view, {slug: state.params.slug}, {reload: true});
        };
        if (state.current.tab_active) {
            scope.tab_active = state.current.tab_active;
            scope[scope.tab_active] = true;
            scope.slug = state.params.slug;
        } else {
            state.go('project.overview', {slug: state.params.slug}, {reload: true});
        }
    }

    function ProjectCtrlOverview(scope, state, modal, ProjectService, TicketService, SprintService) {

        scope.data = {};


        var getSprintsWithTickets = function (project_id) {
            SprintService.query(project_id).then(function (sprints) {
                scope.data.sprints = sprints;
            });
        };

        var getTicketsForProject = function(project_id){
            TicketService.query(project_id).then(function(tkts){
                scope.data.tickets = tkts;
            });
        };

        scope.sortBacklog = {
            itemMoved: function (event) {
                // This happens when a ticket is moved from the Backlog to a Sprint
                
                console.log(event);
            },
            orderChanged: function (event) {
                // This happens when a ticket is sorted in the backlog
               var new_order = [];
                angular.forEach(scope.data.tickets, function(val, key){
                    new_order.push(val.ticket._id.$oid);
                });
                TicketService.update_order(scope.project._id.$oid, new_order);
            },
            containment: '#overview'
        };

        scope.sortTickets = {
            itemMoved: function (event) {
                // This happens when a ticket is moved from one Sprint to another
                console.log(event);
            },
            orderChanged: function (event) {
                // This happens when a ticket is sorted withing the same Sprint
                console.log(event);
            },
            containment: '#overview'
        };

        scope.sortSprints = {
            accept: function (sourceItem, destItem) {
                return sourceItem.element.hasClass('sprint-item');
            },
            orderChanged: function (event) {
                //do something
                var new_order = [];
                angular.forEach(scope.data.sprints, function(val, key){
                    new_order.push(val._id.$oid);
                });
                SprintService.update_order(scope.project._id.$oid, new_order);
            },
            containment: '#overview'
        };


        scope.create_sprint = function () {
            SprintService.save(scope.project._id.$oid).then(function (sprint) {
                scope.data.sprints.push(sprint);
            });
        };

        scope.remove_sprint = function (sprint_id) {
            SprintService.erase(sprint_id).then(function (sprint) {
                var index = -1;
                angular.forEach(scope.data.sprints, function (item, key) {
                    if (item._id.$oid == sprint_id) {
                        index = key;
                    }
                });
                if (index != -1) {
                    scope.data.sprints.splice(index, 1);
                }
            });
        };

        ProjectService.get(state.params.slug).then(function (prj) {
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
                    //ver aca
                    state.go('project.overview', {slug: project.slug});
                }, function(err){
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

    function ProjectCtrlSettings(scope, state, ProjectService) {

    }

    ConfigModule.$inject = ['$stateProvider'];
    ProjectCtrl.$inject = ['$scope', '$state'];
    ProjectCtrlOverview.$inject = ['$scope', '$state', '$modal', 'ProjectService', 'TicketService', 'SprintService'];
    ProjectCtrlBoard.$inject = ['$scope', '$state', 'ProjectService'];
    ProjectCtrlReports.$inject = ['$scope', '$state', 'ProjectService'];
    ProjectCtrlSettings.$inject = ['$scope', '$state', 'ProjectService'];
    ProjectFormCtrl.$inject = ['$scope', '$state', 'ProjectService'];

    angular.module('Coati.Projects', ['ui.router', 'ui.sortable',
        'Coati.Directives',
        'Coati.ApiServices'])
        .config(ConfigModule)
        .controller('ProjectCtrl', ProjectCtrl)
        .controller('ProjectCtrlOverview', ProjectCtrlOverview)
        .controller('ProjectCtrlBoard', ProjectCtrlBoard)
        .controller('ProjectCtrlReports', ProjectCtrlReports)
        .controller('ProjectCtrlSettings', ProjectCtrlSettings)
        .controller('ProjectFormCtrl', ProjectFormCtrl);

}());
