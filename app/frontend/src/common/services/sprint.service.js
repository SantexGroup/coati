(function(angular){

    var SprintService = function(req){
        return {
            'query': function (project_pk) {
                return req.$do('/sprints/' + project_pk, req.METHODS.GET);
            },
            'save': function (project_pk, sp) {
                return req.$do('/sprints/' + project_pk, req.METHODS.POST, sp);
            },
            'erase': function (sprint_id) {
                return req.$do('/sprint/' + sprint_id, req.METHODS.DELETE);
            },
            'update': function (sprint) {
                return req.$do('/sprint/' + sprint._id.$oid, req.METHODS.UPDATE, sprint);
            },
            'update_order': function (project_pk, data) {
                return req.$do('/sprints/' + project_pk + '/order', req.METHODS.POST, data);
            },
            'get_started': function(project_pk){
                return req.$do('/sprints/' + project_pk + '/started', req.METHODS.GET);
            },
            'get_tickets': function(sprint_id){
               return req.$do('/sprint/' + sprint_id + '/tickets', req.METHODS.GET);
            }
        };
    };

    SprintService.$inject = ['$requests'];

    angular.module('Coati.Services.Sprint', ['Coati.Helpers'])
        .factory('SprintService', SprintService);

}(angular));