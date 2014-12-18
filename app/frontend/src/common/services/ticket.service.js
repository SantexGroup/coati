(function(angular){

    var TicketService = function(req){
        return {
            'get': function (tkt_id) {
                return req.$do('/ticket/' + tkt_id, req.METHODS.GET);
            },
            'query': function (project_pk) {
                return req.$do('/tickets/' + project_pk, req.METHODS.GET);
            },
            'save': function (project_pk, tkt) {
                return req.$do('/tickets/' + project_pk, req.METHODS.POST, tkt);
            },
            'update_backlog_order': function (project_pk, data) {
                return req.$do('/tickets/' + project_pk + '/order', req.METHODS.POST, data);
            },
            'update_sprint_order': function (sprint_pk, data) {
                return req.$do('/tickets/sprint/' + sprint_pk + '/order', req.METHODS.POST, data);
            },
            'movement': function (data) {
                return req.$do('/ticket/movement', req.METHODS.POST, data);
            },
            'transition': function(data){
                return req.$do('/ticket/transition', req.METHODS.POST, data);
            },
            'order_ticket_column': function(column, data){
                return req.$do('/ticket/column/' + column + '/order', req.METHODS.POST, data);
            },
            'update': function(tkt_id, data){
                return req.$do('/ticket/' + tkt_id, req.METHODS.UPDATE, data);
            },
            'delete_ticket': function(tkt_id){
                return req.$do('/ticket/' + tkt_id, req.METHODS.DELETE);
            },
            'get_comments': function(tkt_id){
                return req.$do('/ticket/' + tkt_id + '/comments', req.METHODS.GET);
            },
            'add_comment': function(tkt_id, comment){
                return req.$do('/ticket/' + tkt_id + '/comments', req.METHODS.POST, comment);
            }
        };
    };

    TicketService.$inject = ['$requests'];

    angular.module('Coati.Services.Ticket', ['Coati.Helpers'])
        .factory('TicketService', TicketService);

}(angular));