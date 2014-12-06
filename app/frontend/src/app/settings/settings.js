(function (angular) {

    var ColumnFormController = function (scope, modalInstance, ProjectService, project) {

        scope.column = {};
        scope.form = {};
        scope.save = function () {
            if (scope.form.column_form.$valid) {
                ProjectService.add_column(project, scope.column).then(function (col) {
                    modalInstance.close(col);
                }, function (err) {
                    modalInstance.dismiss('error');
                    console.log(err);
                });
            } else {
                scope.submitted = true;
            }
        };

        scope.cancel = function () {
            modalInstance.dismiss('cancelled');
        };
    };

    ColumnFormController.$inject = ['$scope', '$modalInstance', 'ProjectService', 'project'];

    angular.module('Coati.Settings', ['ui.router',
        'Coati.Directives',
        'Coati.ApiServices'])
        .controller('ColumnFormController', ColumnFormController);

}(angular));
