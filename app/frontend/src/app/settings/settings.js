(function (angular) {

    var ColumnFormController = function (scope, modalInstance, ProjectService, project, column) {

        scope.column = column || {};
        scope.form = {};
        scope.save = function () {
            if (scope.form.column_form.$valid) {
                if(column){
                    ProjectService.update_column(column.pk, scope.column).then(function () {
                        modalInstance.close('ok');
                    }, function (err) {
                        modalInstance.dismiss('error');
                        console.log(err);
                    });
                }else {
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

    var ColumnDeleteController = function(scope, modalInstance, ProjectService, column){
        scope.column = column;
        scope.erase = function(){
            ProjectService.delete_column(column.pk).then(function(){
                modalInstance.close('delete');
            });
        };

        scope.cancel = function(){
            modalInstance.dismiss('cancelled');
        };
    };


    ColumnFormController.$inject = ['$scope', '$modalInstance', 'ProjectService', 'project', 'column'];
    ColumnDeleteController.$inject = ['$scope', '$modalInstance', 'ProjectService', 'column'];

    angular.module('Coati.Settings', ['ui.router',
        'Coati.Directives',
        'Coati.ApiServices'])
        .controller('ColumnFormController', ColumnFormController)
        .controller('ColumnDeleteController', ColumnDeleteController);

}(angular));
