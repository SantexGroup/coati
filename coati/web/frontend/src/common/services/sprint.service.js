(function (angular) {

    var SprintService = function (req) {
        return {
            'query': function (project_pk) {
                return req.$do('/projects/' + project_pk + '/sprints', req.METHODS.GET);
            },
            'all': function (project_pk) {
                return req.$do('/projects/' + project_pk + '/sprints/all', req.METHODS.GET);
            },
            'archived': function (project_pk) {
                return req.$do('/projects/' + project_pk + '/sprints/archived', req.METHODS.GET);
            },
            'save': function (project_pk) {
                return req.$do('/projects/' + project_pk + '/sprints', req.METHODS.POST, {});
            },
            'erase': function (project_pk, sprint) {
                return req.$do('/projects/' + project_pk + '/sprints/' + sprint._id.$oid, req.METHODS.DELETE);
            },
            'update': function (project_id, sprint) {
                return req.$do('/projects/' + project_id + '/sprints/' + sprint._id.$oid, req.METHODS.UPDATE, sprint);
            },
            'update_order': function (project_pk, data) {
                return req.$do('/projects/' + project_pk + '/sprints/order', req.METHODS.POST, data);
            },
            'get_started': function (project_pk) {
                return req.$do('/projects/' + project_pk + '/sprints/started', req.METHODS.GET);
            },
            'get_tickets': function (project_pk, sprint_id) {
                return req.$do('/projects/' + project_pk + '/sprints/' + sprint_id + '/tickets', req.METHODS.GET);
            },
            'get_chart': function (project_pk, sprint_id) {
                return req.$do('/projects/' + project_pk + '/sprints/' + sprint_id + '/chart', req.METHODS.GET);
            }
        };
    };

    SprintService.$inject = ['$requests'];

    angular.module('Coati.Services.Sprint', ['Coati.Helpers'])
        .factory('SprintService', SprintService);

}(angular));