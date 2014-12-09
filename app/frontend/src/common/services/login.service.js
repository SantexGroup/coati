(function(angular){

    var LoginService = function(conf){
        return {
            'auth': function (provider) {
                window.location.href = '/auth/authenticate?provider=' + provider + '&callback=' + conf.CALLBACK_URL;
            }
        };
    };

    LoginService.$inject = ['Conf'];

    angular.module('Coati.Services.Login', ['Coati.Config'])
        .factory('LoginService', LoginService);

}(angular));