(function () {

    function ConfigModule(stateProvider) {
        stateProvider.state('project', {
            url: '/projects/:slug/',
            views: {
                "main": {
                    controller: 'ProjectCtrl',
                    templateUrl: 'project/project.tpl.html'
                }
            },
            data: {
                pageTitle: 'Project Overview'
            }
        });
    }

    function ProjectController(scope, state, ProjectService) {
        ProjectService.get(state.params.slug).then(function (prj) {
            scope.project = prj;
        });
    }

    ConfigModule.$inject = ['$stateProvider'];
    ProjectController.$inject = ['$scope', '$state', 'ProjectService'];

    angular.module('Koala.Projects', ['ui.router',
        'KoalaApp.Directives',
        'KoalaApp.ApiServices'])
        .config(ConfigModule)
        .controller('ProjectCtrl', ProjectController);

}());
