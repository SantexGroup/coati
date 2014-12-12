(function(angular){

    var UserService = function(req){
        return {
            'search': function (q) {
                var url =  '/users/search/' + q;
                return req.$do(url, req.METHODS.GET);
            }
        };
    };

    UserService.$inject = ['$requests'];

    angular.module('Coati.Services.User', ['Coati.Helpers'])
        .factory('UserService', UserService);

}(angular));