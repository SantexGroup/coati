(function (angular) {

    var TicketService = function (req, file_upload) {
        return {
            'get': function (project_pk, tkt_id) {
                return req.$do('/project/' + project_pk + '/ticket/' + tkt_id, req.METHODS.GET);
            },
            'query': function (project_pk) {
                return req.$do('/project/' + project_pk + '/tickets', req.METHODS.GET);
            },
            'closed_tickets': function (project_pk) {
                return req.$do('/project/' + project_pk + '/tickets/archived', req.METHODS.GET);
            },
            'search': function (query) {
                return req.$do('/tickets/search/' + query, req.METHODS.GET);
            },
            'save': function (project_pk, tkt) {
                return req.$do('/project/' + project_pk + '/tickets', req.METHODS.POST, tkt);
            },
            'update_backlog_order': function (project_pk, data) {
                return req.$do('/project/' + project_pk + '/tickets/order', req.METHODS.POST, data);
            },
            'update_sprint_order': function (project_pk, sprint_pk, data) {
                return req.$do('/project/' + project_pk + '/tickets/sprint/' + sprint_pk + '/order', req.METHODS.POST, data);
            },
            'movement': function (project_pk, data) {
                return req.$do('/project/' + project_pk + '/ticket/movement', req.METHODS.POST, data);
            },
            'transition': function (project_pk, data) {
                return req.$do('/project/' + project_pk + '/ticket/transition', req.METHODS.POST, data);
            },
            'order_ticket_column': function (project_pk, column, data) {
                return req.$do('/project/' + project_pk + '/ticket/column/' + column + '/order', req.METHODS.POST, data);
            },
            'update': function (project_pk, tkt_id, data) {
                return req.$do('/project/' + project_pk + '/ticket/' + tkt_id, req.METHODS.UPDATE, data);
            },
            'delete_ticket': function (project_pk, tkt_id) {
                return req.$do('/project/' + project_pk + '/ticket/' + tkt_id, req.METHODS.DELETE);
            },
            'get_comments': function (project_pk, tkt_id) {
                return req.$do('/project/' + project_pk + '/ticket/' + tkt_id + '/comments', req.METHODS.GET);
            },
            'add_comment': function (project_pk, tkt_id, comment) {
                return req.$do('/project/' + project_pk + '/ticket/' + tkt_id + '/comments', req.METHODS.POST, comment);
            },
            'upload_attachments': function (project_pk, tkt_id, files, extra_data) {
                return file_upload.$do('/project/' + project_pk + '/ticket/' + tkt_id + '/attachments', files, extra_data);
            },
            'delete_attachment': function (project_pk, tkt_id, att_id) {
                return req.$do('/project/' + project_pk + '/ticket/' + tkt_id + '/attachments/' + att_id + '/delete', req.METHODS.DELETE);
            },
            'assign_member': function (project_pk, tkt_id, member) {
                return req.$do('/project/' + project_pk + '/ticket/' + tkt_id + '/assignments/' + member, req.METHODS.UPDATE);
            },
            'remove_member': function (project_pk, tkt_id, member) {
                return req.$do('/project/' + project_pk + '/ticket/' + tkt_id + '/assignments/' + member, req.METHODS.DELETE);
            }

        };
    };

    TicketService.$inject = ['$requests', '$file_uploads'];

    angular.module('Coati.Services.Ticket', ['Coati.Helpers'])
        .factory('TicketService', TicketService);

}(angular));