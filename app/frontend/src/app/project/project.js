(function (angular) {

    var ResolveProject = function (stateParams, ProjectService) {
        return ProjectService.get(stateParams.project_pk);
    };

    var Config = function (stateProvider) {
        stateProvider
            .state('project', {
                url: '/project/:project_pk',
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


    var ProjectCtrl = function (scope, rootScope, state, project, SocketIO) {
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
            if(state.current.name.indexOf('project') !== -1) {
                if (vm.tab_active === undefined) {
                    state.go('project.planning', {project_pk: state.params.project_pk}, {reload: true});
                } else {
                    vm[vm.tab_active] = true;
                    vm[fromState.tab_active] = false;
                }
            }
        });

        SocketIO.channel(scope.project._id.$oid);
    };

    var ProjectFormCtrl = function (state, modalInstance, ProjectService, growl) {
        var vm = this;
        vm.form = {};
        vm.project = {};
        vm.save = function () {
            if (vm.form.project_form.$valid) {
                ProjectService.save(vm.project).then(function (project) {
                    growl.addSuccessMessage('The project was created successfully');
                    modalInstance.close(project);
                });
            } else {
                vm.submitted = true;
            }
        };

        vm.cancel = function () {
            modalInstance.dismiss('closed');
        };
    };

    var ProjectDeleteController = function (modalInstance, ProjectService, project) {
        var vm = this;
        vm.project = project;
        vm.erase = function () {
            ProjectService.erase(vm.project._id.$oid).then(function () {
                modalInstance.close('delete');
            });
        };

        vm.cancel = function () {
            modalInstance.dismiss('cancelled');
        };
    };

    ResolveProject.$inject = ['$stateParams', 'ProjectService'];
    Config.$inject = ['$stateProvider'];
    ProjectCtrl.$inject = ['$scope', '$rootScope', '$state', 'project', 'SocketIO'];
    ProjectDeleteController.$inject = ['$modalInstance', 'ProjectService', 'project'];
    ProjectFormCtrl.$inject = ['$state', '$modalInstance', 'ProjectService', 'growl'];

    angular.module('Coati.Project', ['ui.router',
        'Coati.SocketIO',
        'Coati.Settings',
        'Coati.Planning',
        'Coati.Board',
        'Coati.Report',
        'Coati.Directives',
        'Coati.Services.Project'])
        .config(Config)
        .controller('ProjectCtrl', ProjectCtrl)
        .controller('ProjectDeleteController', ProjectDeleteController)
        .controller('ProjectFormCtrl', ProjectFormCtrl);

}(angular));
