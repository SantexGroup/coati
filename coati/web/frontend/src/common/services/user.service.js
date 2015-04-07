(function (angular) {

    var UserService = function (req, tokens) {
        return {
            'search': function (q) {
                return req.$do('/users/search/' + q, req.METHODS.GET);
            },
            'update': function (pk, data) {
                return req.$do('/users/' + pk, req.METHODS.UPDATE, data);
            },
            'register': function (data) {
                return req.$do('/users/register', req.METHODS.POST, data);
            },
            'get': function (pk) {
                return req.$do('/users/' + pk, req.METHODS.GET);
            },
            'me': function () {
                return req.$do('/users/me', req.METHODS.GET);
            },
            'notifications': function (per_page) {
                var q = per_page ? '?total=' + per_page : '';
                return req.$do('/users/me/notifications' + q, req.METHODS.GET);
            },
            'mark_as_viewed': function (per_page) {
                var q = per_page ? '?total=' + per_page : '';
                return req.$do('/users/me/notifications' + q, req.METHODS.UPDATE);
            },
            'activateUser': function (code) {
                return req.$do('/users/activate/' + code, req.METHODS.GET);
            },
            'is_logged': function () {
                return tokens.get_access_token() !== null;
            }
        };
    };

    UserService.$inject = ['$requests', 'TokenService'];

    angular.module('Coati.Services.User', ['Coati.Helpers', 'Coati.Services.Token'])
        .factory('UserService', UserService);

}(angular));