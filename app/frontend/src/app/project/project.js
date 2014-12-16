(function (angular) {

    var ResolveProject = function (stateParams, ProjectService) {
        return ProjectService.get(stateParams.project_pk);
    };

    var Config = function (stateProvider) {
        stateProvider
            .state('project-new', {
                url: '/project/new-project/',
                views: {
                    "main": {
                        controller: 'ProjectFormCtrl',
                        controllerAs: 'vm',
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
                        templateUrl: 'project/project.tpl.html',
                        controller: 'ProjectCtrl',
                        controllerAs: 'vm',
                        resolve: {
                            project: ResolveProject
                        }
                    }
                },
                data: {
                    pageTitle: 'Project Details'
                },
                reload: true
            });
    };


    var ProjectCtrl = function (scope, rootScope, state, project) {
        //Keep the project in this scope so any child can access it without re-call.
        scope.project = project;

        var vm = this;

        vm.switchView = function (view) {
            state.go(view, {project_pk: state.params.project_pk}, {reload: true});
        };

        vm.check_permission = function () {
            return project.owner.id === rootScope.user._id.$oid;
        };

        if (state.current.tab_active) {
            //get project
            vm.tab_active = state.current.tab_active;
            vm[vm.tab_active] = true;

        } else {
            state.go('project.planning', {project_pk: state.params.project_pk}, {reload: true});
        }

        rootScope.$on("$stateChangeSuccess", function (event, toState, toParams, fromState, fromParams) {
            vm.tab_active = state.current.tab_active;
            vm[vm.tab_active] = true;
            vm[fromState.tab_active] = false;
        });
    };

    var ProjectFormCtrl = function (state, ProjectService) {
        var vm = this;
        vm.form = {};
        vm.project = {};
        vm.save = function () {
            if (vm.form.project_form.$valid) {
                ProjectService.save(vm.project).then(function (project) {
                    state.go('project.planning', {project_pk: project._id.$oid});
                }, function (err) {
                    console.log(err);
                });
            } else {
                vm.submitted = true;
            }
        };

        vm.cancel = function () {
            state.go('home');
        };
    };


    ResolveProject.$inject = ['$stateParams', 'ProjectService'];
    Config.$inject = ['$stateProvider'];
    ProjectCtrl.$inject = ['$scope', '$rootScope', '$state', 'project'];

    ProjectFormCtrl.$inject = ['$state', 'ProjectService'];

    angular.module('Coati.Project', ['ui.router', 'ui.sortable',
        'Coati.Settings',
        'Coati.Planning',
        'Coati.Board',
        'Coati.Report',
        'Coati.Directives',
        'Coati.Services.Project'])
        .config(Config)
        .controller('ProjectCtrl', ProjectCtrl)
        .controller('ProjectFormCtrl', ProjectFormCtrl);

}(angular));
