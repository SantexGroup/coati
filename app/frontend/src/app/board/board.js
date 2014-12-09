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

    var ProjectCtrlBoard = function (scope, state) {

    };

    Config.$inject = ['$stateProvider'];
    ProjectCtrlBoard.$inject = ['$scope', '$state'];

    angular.module('Coati.Board', ['ui.router',
        'Coati.Directives'])
        .config(Config)
        .controller('ProjectCtrlBoard', ProjectCtrlBoard);

}(angular));
