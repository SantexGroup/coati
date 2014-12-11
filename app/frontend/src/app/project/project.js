(function (angular) {

    function ConfigModule(stateProvider) {
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
                        controllerAs: 'vm'
                    }
                },
                data: {
                    pageTitle: 'Project Details'
                },
                reload: true
            });
    }


    function ProjectCtrl(state) {
        var vm = this;

        vm.switchView = function (view) {
            state.go(view, {project_pk: state.params.project_pk}, {reload: true});
        };
        if (state.current.tab_active) {
            //get project
            vm.tab_active = state.current.tab_active;
            vm[vm.tab_active] = true;

        } else {
            state.go('project.planning', {project_pk: state.params.project_pk}, {reload: true});
        }
    }

    function ProjectFormCtrl(state, ProjectService) {
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
    }


    ConfigModule.$inject = ['$stateProvider'];
    ProjectCtrl.$inject = ['$state'];

    ProjectFormCtrl.$inject = ['$state', 'ProjectService'];

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
