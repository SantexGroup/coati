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




    ConfigModule.$inject = ['$stateProvider'];
    ProjectCtrl.$inject = ['$scope', '$state'];

    ProjectFormCtrl.$inject = ['$scope', '$state', 'ProjectService'];

    angular.module('Coati.Project', ['ui.router', 'ui.sortable',
        'Coati.Settings',
        'Coati.Planning',
        'Coati.Board',
        'Coati.Report',
        'Coati.Directives',
        'Coati.Services.Project'])
        .config(ConfigModule)
        .controller('ProjectCtrl', ProjectCtrl)
        .controller('ProjectFormCtrl', ProjectFormCtrl);

}(angular));
