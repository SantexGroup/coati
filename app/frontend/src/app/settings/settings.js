(function (angular) {

    var Config = function (stateProvider, tagsInputProvider) {
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

        tagsInputProvider.setDefaults('autoComplete', {
            maxResultsToShow: 20,
            debounceDelay: 300
        });
    };


    var ProjectCtrlSettings = function (scope, state, modal, growl, ProjectService) {
        var vm = this;
        vm.form = {};

        vm.delete_col = function (item) {
            var col = angular.copy(item);
            col.pk = item._id.$oid;
            var modalInstance = modal.open({
                controller: 'ColumnDeleteController as vm',
                templateUrl: 'settings/delete_column.tpl.html',
                resolve: {
                    column: function () {
                        return col;
                    }
                }
            });
            modalInstance.result.then(function () {
                getColumnConfiguration(vm.project._id.$oid);
                growl.addSuccessMessage('The column was removed successfully');
            });
        };

        vm.add_or_edit = function (item) {
            if (item) {
                item = angular.copy(item);
                item.pk = item._id.$oid;
            }
            var modalInstance = modal.open({
                controller: 'ColumnFormController as vm',
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
                growl.addSuccessMessage('The column was saved successfully');
            });
        };

        vm.add_new_member = function () {
            var modalInstance = modal.open({
                controller: 'MembersController as vm',
                templateUrl: 'settings/new_project_member.tpl.html',
                resolve: {
                    project: function () {
                        return vm.project._id.$oid;
                    }
                }
            });
            modalInstance.result.then(function () {
                growl.addSuccessMessage('The user was added as member successfully');
            });
        };

        vm.save = function () {
            if (vm.form.project_form.$valid) {
                vm.project.owner_id = vm.project.owner.id;
                ProjectService.update(vm.project._id.$oid, vm.project).then(function () {
                    growl.addSuccessMessage('The project was updated successfully');
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

        var getMembers = function (project_id) {
            ProjectService.get_members(project_id).then(function (members) {
                vm.members = members;
            });
        };

        // get the project from the parent controller.
        vm.project = scope.$parent.project;
        getColumnConfiguration(vm.project._id.$oid);
        getMembers(vm.project._id.$oid);
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

    var MembersController = function (modalInstance, UserService, ProjectService, project) {
        var vm = this;


        vm.loadMembers = function (query) {
            return UserService.search(query);
        };

        vm.save = function () {
            if (vm.members.length > 0) {
                ProjectService.add_members(project, vm.members).then(function (rta) {
                    modalInstance.close(rta);
                });
            }
        };

        vm.cancel = function () {
            modalInstance.dismiss('close');
        };
    };

    Config.$inject = ['$stateProvider', 'tagsInputConfigProvider'];
    ProjectCtrlSettings.$inject = ['$scope', '$state', '$modal', 'growl', 'ProjectService'];
    ColumnFormController.$inject = ['$modalInstance', 'ProjectService', 'project', 'column'];
    ColumnDeleteController.$inject = ['$modalInstance', 'ProjectService', 'column'];
    MembersController.$inject = ['$modalInstance', 'UserService', 'ProjectService', 'project'];

    angular.module('Coati.Settings', ['ui.router', 'ngTagsInput',
        'Coati.Directives',
        'Coati.Services.User',
        'Coati.Services.Project'])
        .config(Config)
        .controller('ProjectCtrlSettings', ProjectCtrlSettings)
        .controller('ColumnFormController', ColumnFormController)
        .controller('ColumnDeleteController', ColumnDeleteController)
        .controller('MembersController', MembersController);

}(angular));
