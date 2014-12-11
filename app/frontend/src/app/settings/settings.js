(function (angular) {

    var Config = function (stateProvider) {
        stateProvider.state('project.settings', {
            url: 'settings',
            views: {
                "project-settings": {
                    controller: 'ProjectCtrlSettings',
                    controllerAs: 'vm',
                    templateUrl: 'settings/settings.tpl.html'
                }
            },
            tab_active: 'settings',
            data: {
                pageTitle: 'Project Settings'
            },
            reload: true
        });
    };


    var ProjectCtrlSettings = function (rootScope, state, modal, ProjectService) {
        var vm = this;
        vm.form = {};

        vm.delete_col = function (item) {
            var col = angular.copy(item);
            col.pk = item._id.$oid;
            var modalInstance = modal.open({
                controller: 'ColumnDeleteController',
                controllerAs: 'vm',
                templateUrl: 'settings/delete_column.tpl.html',
                resolve: {
                    column: function () {
                        return col;
                    }
                }
            });
            modalInstance.result.then(function () {
                getColumnConfiguration(vm.project._id.$oid);
            });
        };

        vm.add_or_edit = function (item) {
            if (item) {
                item = angular.copy(item);
                item.pk = item._id.$oid;
            }
            var modalInstance = modal.open({
                controller: 'ColumnFormController',
                controllerAs: 'vm',
                templateUrl: 'settings/new_column_form.tpl.html',
                resolve: {
                    project: function () {
                        return vm.project._id.$oid;
                    },
                    column: function () {
                        return item;
                    }
                }
            });
            modalInstance.result.then(function () {
                getColumnConfiguration(vm.project._id.$oid);
            });
        };

        vm.save = function () {
            if (vm.form.project_form.$valid) {
                vm.project.owner_id = vm.project.owner.id;
                ProjectService.update(vm.project._id.$oid, vm.project).then(function () {
                    rootScope.$broadcast('notify', {
                        'title': 'Updated',
                        'description': 'The project settings were saved'
                    });
                });
            } else {
                vm.submitted = true;
            }
        };

        //order_columns
        vm.sortColumns = {
            accept: function (sourceItem, destItem) {
                return true;
            },
            orderChanged: function (event) {
                //do something
                var new_order = [];
                angular.forEach(vm.columns, function (val, key) {
                    new_order.push(val._id.$oid);
                });
                ProjectService.order_columns(vm.project._id.$oid, new_order);
            },
            containment: '#planning',
            containerPositioning: 'relative'
        };

        var getColumnConfiguration = function (project_id) {
            ProjectService.get_columns(project_id).then(function (cols) {
                vm.columns = cols;
            });
        };

        ProjectService.get(state.params.project_pk).then(function (prj) {
            vm.project = prj;
            getColumnConfiguration(prj._id.$oid);
        });
    };

    var ColumnFormController = function (modalInstance, ProjectService, project, column) {
        var vm = this;
        vm.column = column || {};
        vm.form = {};
        vm.save = function () {
            if (vm.form.column_form.$valid) {
                if (column) {
                    ProjectService.update_column(column.pk, vm.column).then(function () {
                        modalInstance.close('ok');
                    }, function (err) {
                        modalInstance.dismiss('error');
                        console.log(err);
                    });
                } else {
                    ProjectService.add_column(project, vm.column).then(function () {
                        modalInstance.close('ok');
                    }, function (err) {
                        modalInstance.dismiss('error');
                        console.log(err);
                    });
                }
            } else {
                vm.submitted = true;
            }
        };

        vm.cancel = function () {
            modalInstance.dismiss('cancelled');
        };
    };

    var ColumnDeleteController = function (modalInstance, ProjectService, column) {
        var vm = this;
        vm.column = column;
        vm.erase = function () {
            ProjectService.delete_column(vm.column.pk).then(function () {
                modalInstance.close('delete');
            });
        };

        vm.cancel = function () {
            modalInstance.dismiss('cancelled');
        };
    };

    Config.$inject = ['$stateProvider'];
    ProjectCtrlSettings.$inject = ['$rootScope', '$state', '$modal', 'ProjectService'];
    ColumnFormController.$inject = ['$modalInstance', 'ProjectService', 'project', 'column'];
    ColumnDeleteController.$inject = ['$modalInstance', 'ProjectService', 'column'];

    angular.module('Coati.Settings', ['ui.router',
        'Coati.Directives',
        'Coati.Services.Project'])
        .config(Config)
        .controller('ProjectCtrlSettings', ProjectCtrlSettings)
        .controller('ColumnFormController', ColumnFormController)
        .controller('ColumnDeleteController', ColumnDeleteController);

}(angular));
