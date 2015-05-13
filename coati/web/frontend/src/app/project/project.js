(function (angular) {

    var ResolveProject = function (rootScope, stateParams, ProjectService) {
        return ProjectService.get(stateParams.project_pk).then(function(prj){
            rootScope.project = prj;
            return prj;
        });
    };

    var Config = function (stateProvider) {
        stateProvider
            .state('project', {
                url: '/project/:project_pk',
                resolve: {
                    project: ResolveProject
                },
                //template:'<ui-view/>',
                abstract: true,
                reload: true
            });
    };


    var ProjectCtrl = function (rootScope, state, SocketIO) {
        var vm = this;

        vm.check_permission = function () {
            return vm.project.owner._id.$oid === rootScope.user._id.$oid;
        };

        vm.is_scrumm = function () {
            return vm.project.project_type === 'S';
        };

        rootScope.$watch('project', function(nv){
            vm.project = nv;
            if(vm.project){
                SocketIO.channel(vm.project._id.$oid);
            }
        });

    };

    var ProjectFormCtrl = function (state, modalInstance, ProjectService) {
        var vm = this;
        vm.form = {};
        vm.project = {};
        vm.save = function () {
            if (vm.form.project_form.$valid) {
                ProjectService.save(vm.project).then(function (project) {
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

    ResolveProject.$inject = ['$rootScope', '$stateParams', 'ProjectService'];
    Config.$inject = ['$stateProvider', '$translateProvider'];
    ProjectCtrl.$inject = ['$rootScope', '$state', 'SocketIO'];
    ProjectDeleteController.$inject = ['$modalInstance', 'ProjectService', 'project'];
    ProjectFormCtrl.$inject = ['$state', '$modalInstance', 'ProjectService'];

    angular.module('Coati.Project', ['ui.router', 'pascalprecht.translate',
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
