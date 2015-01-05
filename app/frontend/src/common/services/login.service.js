(function(angular){

    var LoginService = function(req, conf){
        return {
            'auth': function (provider) {
                window.location.href = '/auth/authenticate?provider=' + provider + '&callback=' + conf.CALLBACK_URL;
            },
            'login': function(data){
                return req.$do('/user/login', req.METHODS.POST, data);
            }
        };
    };

    LoginService.$inject = ['$requests', 'Conf'];

    angular.module('Coati.Services.Login', ['Coati.Config', 'Coati.Helpers'])
        .factory('LoginService', LoginService);

}(angular));