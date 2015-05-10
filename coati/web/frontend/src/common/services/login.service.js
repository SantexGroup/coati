(function(angular){

    var LoginService = function(req){
        return {
            'auth': function (data) {
                return req.$do('/auth/authorized', req.METHODS.POST, data);
            },
            'login': function(data){
                return req.$do('/token', req.METHODS.POST, data);
            }
        };
    };

    LoginService.$inject = ['$requests'];

    angular.module('Coati.Services.Login', ['Coati.Helpers'])
        .factory('LoginService', LoginService);

}(angular));