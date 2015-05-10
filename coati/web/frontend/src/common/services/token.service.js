(function (angular) {
    var Tokens = function (wnd, storage) {
        return {
            store: function (data) {
                var now = new Date().getTime();
                var expirationDate = now + (data['expires_in'] * 1000);
                storage.set('accessToken', data['access_token']);
                storage.set('refreshToken', data['refresh_token']);
                storage.set('expirationDate', expirationDate);
            },
            clean: function () {
                storage.set('accessToken', null);
                storage.set('refreshToken', null);
                storage.set('expirationDate', null);
            },
            get_access_token: function(){
                return storage.get('accessToken');
            }
        };

    };

    Tokens.$inject = ['$window', 'StorageService'];

    angular.module('Coati.Services.Token', ['Coati.Services.Storage'])
        .factory('TokenService', Tokens);

}(angular));