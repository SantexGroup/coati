(function(angular){

    var UserService = function(req){
        var BASE_URL = '/users/';
        return {
            'me': function () {
                var url = BASE_URL + 'me';
                return req.$do(url, req.METHODS.GET);
            },
            'search': function (q) {
                var url = BASE_URL + 'search/' + q;
                return req.$do(url, req.METHODS.GET);
            },
            'save': function (user) {
                var url = BASE_URL + 'me';
                return req.$do(url, req.METHODS.UPDATE, user);
            }
        };
    };

    UserService.$inject = ['$requests'];

    angular.module('Coati.Services.User', ['Coati.Helpers'])
        .factory('UserService', UserService);

}(angular));