(function () {
    "use strict";
    /**
     * Define the global configuration parameters
     * @returns {{getItem: getItem, $get: $get}}
     * @constructor
     */
    function GlobalConfiguration() {

        var globals = {
            BASE_API_URL: '/api',
            CALLBACK_URL: '/login/auth',
            DEFAULT_CONTENT_TYPE: 'application/json; charset=utf-8',
            SOCKET_URL: 'http://localhost:8001',
            STATE_401: 'login',
            STATE_403: 'error_403',
            DATE_FORMAT: 'MM/dd/yyyy',
            TICKET_TYPES: [
                {value:"U", name: 'User Story'},
                {value:"B", name: 'Bug'},
                {value:"F", name: 'Feature'},
                {value:"I", name: 'Improvement'},
                {value:"E", name: 'Epic'},
                {value:"T", name: 'Task'}
            ],
            TICKET_DEPENDENCIES: [
                {value:"B", name: "BLOCKED"},
                {value:"BB", name: "BLOCKED_BY"},
                {value:"C", name: "CLONED"},
                {value:"CB", name: "CLONED_BY"},
                {value:"D", name: "DUPLICATED"},
                {value:"DB", name: "DUPLICATED_BY"},
                {value:"R", name: "RELATED"}
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
    angular.module('Coati.Config', []).provider('Conf', GlobalConfiguration);
}());