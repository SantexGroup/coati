(function (angular) {

    var StorageService = function (wnd) {
        return {
            set: function (name, value) {
                wnd.localStorage.setItem(name, value);
            },
            get: function (name) {
                return wnd.localStorage.getItem(name);
            },
            put: function (name, value) {
                this.set(name, value);
            }
        };
    };

    StorageService.$inject = ['$window'];

    angular.module('Coati.Services.Storage', [])
        .factory('StorageService', StorageService);

}(angular));
