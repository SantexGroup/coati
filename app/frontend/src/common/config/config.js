(function () {
    "use strict";
    /**
     * Define the global configuration parameters
     * @returns {{getItem: getItem, $get: $get}}
     * @constructor
     */
    function KoalaGlobalConfiguration() {

        var globals = {
            BASE_API_URL: '/api',
            CALLBACK_URL: '/login/auth',
            DEFAULT_CONTENT_TYPE: 'application/json; charset=utf-8',
            SOCKET_URL: 'http://localhost:9000',
            STATE_401: 'login',
            TICKET_TYPES: [
                {value:"U", name: 'User Story'},
                {value:"B", name: 'Bug'},
                {value:"F", name: 'Feature'},
                {value:"I", name: 'Improvement'},
                {value:"E", name: 'Epic'},
                {value:"T", name: 'Task'}
            ]
        };
        return {
            getItem: function (key) {
                return globals[key];
            },
            $get: function () {
                return globals;
            }
        };
    }

//angular module
    angular.module('Coati.Config', []).provider('Conf', KoalaGlobalConfiguration);
}());