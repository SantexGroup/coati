(function(angular){

    var ProjectService = function(req, file_upload){
        return {
            'query': function(){
              return req.$do('/projects', req.METHODS.GET);
            },
            'save':function (data) {
                return req.$do('/projects', req.METHODS.POST, data);
            },
            'get': function(project_pk){
               return req.$do('/projects/' + project_pk, req.METHODS.GET);
            },
            'update': function(project_pk, data){
                return req.$do('/projects/' + project_pk, req.METHODS.UPDATE, data);
            },
            'erase': function(project_pk){
                return req.$do('/projects/' + project_pk, req.METHODS.DELETE);
            },
            'get_columns': function (project_pk) {
                return req.$do('/projects/' + project_pk + '/columns', req.METHODS.GET);
            },
            'update_column': function(project_pk, col_id, data){
                 return req.$do('/projects/' + project_pk + '/column/' + col_id, req.METHODS.UPDATE, data);
            },
            'delete_column': function (project_pk, col_id) {
                return req.$do('/projects/' + project_pk + '/column/' + col_id, req.METHODS.DELETE);
            },
            'add_column': function (project_pk, data) {
                return req.$do('/projects/' + project_pk + '/columns', req.METHODS.POST, data);
            },
            'order_columns': function (project_pk, data) {
                return req.$do('/project/' + project_pk + '/order_columns', req.METHODS.POST, data);
            },
            'get_members': function(project_pk){
                return req.$do('/projects/' + project_pk + '/members', req.METHODS.GET);
            },
            'add_members': function(project_pk, members){
                return req.$do('/projects/' + project_pk + '/members', req.METHODS.POST, members);
            },
            'remove_member': function(project_pk, member){
                return req.$do('/projects/' + project_pk + '/members/' + member, req.METHODS.DELETE);
            },
            'set_as_owner': function(project_pk, member){
                return req.$do('/projects/' + project_pk + '/members/' + member, req.METHODS.UPDATE, {});
            },
            'import_file': function(project_pk, file, extra_data){
                return file_upload.$do('/projects/' + project_pk + '/import', file, extra_data);
            }
        };
    };

    ProjectService.$inject = ['$requests', '$file_uploads'];

    angular.module('Coati.Services.Project', ['Coati.Helpers'])
        .factory('ProjectService', ProjectService);

}(angular));