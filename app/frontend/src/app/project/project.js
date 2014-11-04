(function () {

    function ConfigModule(stateProvider) {
        stateProvider
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

    function ProjectCtrlOverview(scope, state, modal, ProjectService, TicketService) {

        var getBacklogTickets = function(project_id){
            TicketService.query(project_id).then(function (tickets) {
                scope.tickets = tickets;
            });
        };

        var getSprintsWithTickets = function(project_id){
            ProjectService.get_sprints(project_id).then(function(sprints){
                scope.sprints = sprints;
            });
        };

        ProjectService.get(state.params.slug).then(function (prj) {
            scope.project = prj;
            getBacklogTickets(prj._id.$oid);
        });

        scope.create_sprint = function(){
            ProjectService.add_sprint(scope.project._id.$oid).then(function(sprint){
               scope.sprints.push(sprint);
            });
        }
    }

    function ProjectCtrlBoard(scope, state, ProjectService) {

    }

    function ProjectCtrlReports(scope, state, ProjectService) {

    }

    function ProjectCtrlSettings(scope, state, ProjectService) {

    }

    ConfigModule.$inject = ['$stateProvider'];
    ProjectCtrl.$inject = ['$scope', '$state'];
    ProjectCtrlOverview.$inject = ['$scope', '$state', '$modal', 'ProjectService', 'TicketService'];
    ProjectCtrlBoard.$inject = ['$scope', '$state', 'ProjectService'];
    ProjectCtrlReports.$inject = ['$scope', '$state', 'ProjectService'];
    ProjectCtrlSettings.$inject = ['$scope', '$state', 'ProjectService'];

    angular.module('Koala.Projects', ['ui.router',
        'KoalaApp.Directives',
        'KoalaApp.ApiServices'])
        .config(ConfigModule)
        .controller('ProjectCtrl', ProjectCtrl)
        .controller('ProjectCtrlOverview', ProjectCtrlOverview)
        .controller('ProjectCtrlBoard', ProjectCtrlBoard)
        .controller('ProjectCtrlReports', ProjectCtrlReports)
        .controller('ProjectCtrlSettings', ProjectCtrlSettings);

}());
