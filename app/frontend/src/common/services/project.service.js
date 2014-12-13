(function(angular){

    var ProjectService = function(req){
        return {
            'query': function(){
              return req.$do('/projects', req.METHODS.GET);
            },
            'save':function (data) {
                return req.$do('/projects', req.METHODS.POST, data);
            },
            'get': function(project_pk){
               return req.$do('/project/' + project_pk, req.METHODS.GET);
            },
            'update': function(project_pk, data){
                return req.$do('/project/' + project_pk, req.METHODS.UPDATE, data);
            },
            'get_columns': function (project_id) {
                return req.$do('/project/' + project_id + '/columns', req.METHODS.GET);
            },
            'update_column': function(col_id, data){
                 return req.$do('/project/column/' + col_id, req.METHODS.UPDATE, data);
            },
            'delete_column': function (col_id) {
                return req.$do('/project/column/' + col_id, req.METHODS.DELETE);
            },
            'add_column': function (project_id, data) {
                return req.$do('/project/' + project_id + '/columns', req.METHODS.POST, data);
            },
            'order_columns': function (project_id, data) {
                return req.$do('/project/' + project_id + '/order_columns', req.METHODS.POST, data);
            },
            'get_members': function(project_id){
                return req.$do('/project/' + project_id + '/members', req.METHODS.GET);
            },
            'add_members': function(project_id, members){
                return req.$do('/project/' + project_id + '/members', req.METHODS.POST, members);
            }
        };
    };

    ProjectService.$inject = ['$requests'];

    angular.module('Coati.Services.Project', ['Coati.Helpers'])
        .factory('ProjectService', ProjectService);

}(angular));