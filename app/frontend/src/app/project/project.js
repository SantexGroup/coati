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

        var getTickets = function(project_id){
            TicketService.query(project_id).then(function (tickets) {
                scope.tickets = tickets;
            });
        };

        ProjectService.get(state.params.slug).then(function (prj) {
            scope.project = prj;
            getTickets(prj._id.$oid);
        });

        scope.show_ticket_form = function () {
            var modalDeleteInstance = modal.open({
                templateUrl: 'ticket/ticket_form.tpl.html',
                controller: 'TicketModalFormController',
                resolve: {
                    Project: function () {
                        return scope.project;
                    }
                }
            });
            modalDeleteInstance.result.then(function () {
                getTickets(scope.project._id.$oid);
            }, function (err) {
                console.log(err);
            });
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
    ProjectCtrlOverview.$inject = ['$scope', '$state', '$modal', 'ProjectService', 'TicketService'];
    ProjectCtrlBoard.$inject = ['$scope', '$state', 'ProjectService'];
    ProjectCtrlReports.$inject = ['$scope', '$state', 'ProjectService'];
    ProjectCtrlSettings.$inject = ['$scope', '$state', 'ProjectService'];

    angular.module('Koala.Projects', ['ui.router',
        'KoalaApp.Directives',
        'KoalaApp.ApiServices',
        'Koala.Tickets'])
        .config(ConfigModule)
        .controller('ProjectCtrl', ProjectCtrl)
        .controller('ProjectCtrlOverview', ProjectCtrlOverview)
        .controller('ProjectCtrlBoard', ProjectCtrlBoard)
        .controller('ProjectCtrlReports', ProjectCtrlReports)
        .controller('ProjectCtrlSettings', ProjectCtrlSettings);

}());
