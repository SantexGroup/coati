(function (angular) {

    var Config = function (stateProvider) {
        stateProvider.state('project.settings', {
            url: 'settings',
            views: {
                "project-settings": {
                    controller: 'ProjectCtrlSettings',
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


    var ProjectCtrlSettings = function (scope, rootScope, state, modal, ProjectService) {
        scope.data = {};

        scope.delete_col = function (item) {
            var col = angular.copy(item);
            col.pk = item._id.$oid;
            var modalInstance = modal.open({
                controller: 'ColumnDeleteController',
                templateUrl: 'settings/delete_column.tpl.html',
                resolve: {
                    column: function () {
                        return col;
                    }
                }
            });
            modalInstance.result.then(function () {
                getColumnConfiguration(scope.project._id.$oid);
            });
        };

        scope.add_or_edit = function (item) {
            if (item) {
                item = angular.copy(item);
                item.pk = item._id.$oid;
            }
            var modalInstance = modal.open({
                controller: 'ColumnFormController',
                templateUrl: 'settings/new_column_form.tpl.html',
                resolve: {
                    project: function () {
                        return scope.project._id.$oid;
                    },
                    column: function () {
                        return item;
                    }
                }
            });
            modalInstance.result.then(function () {
                getColumnConfiguration(scope.project._id.$oid);
            });
        };

        scope.save = function () {
            if (scope.form.project_form.$valid) {
                scope.project.owner_id = scope.project.owner.id;
                ProjectService.update(scope.project._id.$oid, scope.project).then(function () {
                    rootScope.$broadcast('notify', {
                        'title': 'Updated',
                        'description': 'The project settings were saved'
                    });
                });
            } else {
                scope.submitted = true;
            }
        };

        //order_columns
        scope.sortColumns = {
            accept: function (sourceItem, destItem) {
                return true;
            },
            orderChanged: function (event) {
                //do something
                var new_order = [];
                angular.forEach(scope.data.columns, function (val, key) {
                    new_order.push(val._id.$oid);
                });
                ProjectService.order_columns(scope.project._id.$oid, new_order);
            },
            containment: '#planning',
            containerPositioning: 'relative'
        };

        var getColumnConfiguration = function (project_id) {
            ProjectService.get_columns(project_id).then(function (cols) {
                scope.data.columns = cols;
            });
        };

        ProjectService.get(state.params.project_pk).then(function (prj) {
            scope.project = prj;
            getColumnConfiguration(prj._id.$oid);
        });
    };

    var ColumnFormController = function (scope, modalInstance, ProjectService, project, column) {

        scope.column = column || {};
        scope.form = {};
        scope.save = function () {
            if (scope.form.column_form.$valid) {
                if (column) {
                    ProjectService.update_column(column.pk, scope.column).then(function () {
                        modalInstance.close('ok');
                    }, function (err) {
                        modalInstance.dismiss('error');
                        console.log(err);
                    });
                } else {
                    ProjectService.add_column(project, scope.column).then(function () {
                        modalInstance.close('ok');
                    }, function (err) {
                        modalInstance.dismiss('error');
                        console.log(err);
                    });
                }
            } else {
                scope.submitted = true;
            }
        };

        scope.cancel = function () {
            modalInstance.dismiss('cancelled');
        };
    };

    var ColumnDeleteController = function (scope, modalInstance, ProjectService, column) {
        scope.column = column;
        scope.erase = function () {
            ProjectService.delete_column(column.pk).then(function () {
                modalInstance.close('delete');
            });
        };

        scope.cancel = function () {
            modalInstance.dismiss('cancelled');
        };
    };

    Config.$inject = ['$stateProvider'];
    ProjectCtrlSettings.$inject = ['$scope', '$rootScope', '$state', '$modal', 'ProjectService'];
    ColumnFormController.$inject = ['$scope', '$modalInstance', 'ProjectService', 'project', 'column'];
    ColumnDeleteController.$inject = ['$scope', '$modalInstance', 'ProjectService', 'column'];

    angular.module('Coati.Settings', ['ui.router',
        'Coati.Directives',
        'Coati.Services.Project'])
        .config(Config)
        .controller('ProjectCtrlSettings', ProjectCtrlSettings)
        .controller('ColumnFormController', ColumnFormController)
        .controller('ColumnDeleteController', ColumnDeleteController);

}(angular));
