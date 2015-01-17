(function (angular) {

    var Config = function (stateProvider, tagsInputProvider) {
        stateProvider.state('project.settings', {
            url: '/settings',
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


    var ProjectCtrlSettings = function (rootScope, tmo, filter, scope, state, modal, growl, ProjectService, SocketIO) {
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
                getMembers(vm.project._id.$oid);
            });
        };

        vm.remove_member = function (m) {
            var modalInstance = modal.open({
                controller: 'RemoveMemberController as vm',
                templateUrl: 'settings/remove_member.tpl.html',
                resolve: {
                    item: function () {
                        return {
                            'member': m,
                            'project': vm.project
                        };
                    }
                }
            });
            modalInstance.result.then(function () {
                growl.addSuccessMessage('The member was removed successfully');
                getMembers(vm.project._id.$oid);
            });
        };

        vm.set_as_owner = function (m) {
            ProjectService.set_as_owner(vm.project._id.$oid, m._id.$oid).then(function () {
                getMembers(vm.project._id.$oid);
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

        vm.delete_project = function () {
            var modalInstance = modal.open({
                controller: 'ProjectDeleteController as vm',
                templateUrl: 'project/delete_project.tpl.html',
                resolve: {
                    project: function () {
                        return vm.project;
                    }
                }
            });
            modalInstance.result.then(function () {
                state.go('home');
            });
        };

        vm.prepare_upload = function () {
            if (window.FileReader != null && (window.FileAPI == null || FileAPI.html5 !== false)) {
                tmo(function () {
                    var fileReader = new FileReader();
                    fileReader.readAsText(vm.json_file[0]);
                    fileReader.onload = function (e) {
                        tmo(function () {
                            vm.json_file.data = JSON.parse(e.target.result);
                        });
                    };
                });
            }
        };

        vm.confirm_upload = function () {
            vm.uploading = true;
            ProjectService.import_file(vm.project._id.$oid, vm.json_file,
                {'include_cards': vm.import_cards, 'include_cols': vm.import_cols})
                .success(function (rta) {
                    vm.json_file = null;
                    vm.uploading = false;
                    growl.addSuccessMessage('The file was imported successfully');
                    getColumnConfiguration(vm.project._id.$oid);
                }).error(function(){
                    vm.uploading = false;
                });
        };

        //order_columns
        vm.sortColumnOptions = {
            forcePlaceholderSize: true,
            placeholder: 'placeholder-item',
            start: function (e, ui) {
                ui.placeholder.height(ui.helper.outerHeight());
            },
            update: function (e, ui) {
                this.updated = true;
            },
            stop: function (e, ui) {
                if (this.updated) {
                    var new_order = [];
                    angular.forEach(ui.item.sortable.sourceModel, function (v, k) {
                        new_order.push(v._id.$oid);
                    });
                    //update order
                    ProjectService.order_columns(vm.project._id.$oid, new_order);
                }
            }
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
                    ProjectService.update_column(project, column.pk, vm.column).then(function () {
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
            ProjectService.delete_column(vm.column.project.$oid, vm.column.pk).then(function () {
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

    var RemoveMemberController = function (modalInstance, ProjectService, item) {
        var vm = this;
        vm.member = item.member;

        vm.erase = function () {
            ProjectService.remove_member(item.project._id.$oid, vm.member._id.$oid).then(function (rta) {
                modalInstance.close(rta);
            });
        };

        vm.cancel = function () {
            modalInstance.dismiss('canceled');
        };
    };

    Config.$inject = ['$stateProvider', 'tagsInputConfigProvider'];
    ProjectCtrlSettings.$inject = ['$rootScope', '$timeout', '$filter', '$scope', '$state', '$modal', 'growl', 'ProjectService', 'SocketIO'];
    ColumnFormController.$inject = ['$modalInstance', 'ProjectService', 'project', 'column'];
    ColumnDeleteController.$inject = ['$modalInstance', 'ProjectService', 'column'];
    MembersController.$inject = ['$modalInstance', 'UserService', 'ProjectService', 'project'];
    RemoveMemberController.$inject = ['$modalInstance', 'ProjectService', 'item'];

    angular.module('Coati.Settings', ['ui.router', 'ngTagsInput',
        'Coati.SocketIO',
        'Coati.Directives',
        'Coati.Services.User',
        'Coati.Services.Project'])
        .config(Config)
        .controller('ProjectCtrlSettings', ProjectCtrlSettings)
        .controller('ColumnFormController', ColumnFormController)
        .controller('ColumnDeleteController', ColumnDeleteController)
        .controller('RemoveMemberController', RemoveMemberController)
        .controller('MembersController', MembersController);

}(angular));
