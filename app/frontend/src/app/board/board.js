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

    var ProjectCtrlBoard = function (scope, state, SprintService, ProjectService) {
        scope.project_pk = state.params.project_pk;
        scope.data = {};

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
                console.log(event);
            },
            orderChanged: function (event) {
                // This happens when a ticket is sorted in the backlog
                console.log(event);
            },
            containment: '#board-area-wrapper',
            containerPositioning: 'relative'
        };

        SprintService.get_started(scope.project_pk).then(function (sprint) {
            scope.sprint = sprint;
            if (sprint.started) {
                scope.data.tickets = sprint.tickets;
                getColumnConfiguration(scope.project_pk);
                getProjectData(scope.project_pk);
            }
        });

    };

    Config.$inject = ['$stateProvider'];
    ProjectCtrlBoard.$inject = ['$scope', '$state', 'SprintService', 'ProjectService'];

    angular.module('Coati.Board', ['ui.router',
        'Coati.Directives',
        'Coati.Services.Project',
        'Coati.Services.Sprint'])
        .config(Config)
        .controller('ProjectCtrlBoard', ProjectCtrlBoard);

}(angular));
