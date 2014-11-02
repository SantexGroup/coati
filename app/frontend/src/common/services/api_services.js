var SOCKET_URL = 'http://localhost:9000';


angular.module('KoalaApp.Utils', ['ngCookies', 'Koala.Config'])
    .factory('$requests', function ($http, $q, $cookies, koalaConf) {
        return {
            METHODS: {
                UPDATE: 'PUT',
                POST: 'POST',
                DELETE: 'DELETE',
                PATCH: 'PATCH',
                GET: 'GET'
            },
            '$do': function (url, method, data) {

                $http.defaults.headers.common['X-CSRFToken'] = $cookies.csrftoken;

                var results = $q.defer();
                $http({
                    url: koalaConf.BASE_API_URL + url,
                    method: method,
                    data: data
                }).success(function (body) {
                    results.resolve(body);
                }).error(function (data, status) {
                    results.reject({
                        'message': data,
                        'code': status
                    });
                });
                return results.promise;
            }
        };
    });

angular.module('KoalaApp.ApiServices', ['KoalaApp.Utils'])

    .factory('UserService', function ($requests) {
        var BASE_URL = '/users/';
        return {
            me: function () {
                var url = BASE_URL + 'me';
                return $requests.$do(url, $requests.METHODS.GET);
            },
            search: function (q) {
                var url = BASE_URL + 'search/' + q;
                return $requests.$do(url, $requests.METHODS.GET);
            },
            save: function (user) {
                var url = BASE_URL + 'me';
                return $requests.$do(url, $requests.METHODS.UPDATE, user);
            }
        };
    })
    .factory('ClientService', function ($requests) {
        var BASE_URL = '/clients/';
        return {
            query: function () {
                return $requests.$do(BASE_URL, $requests.METHODS.GET);
            },
            update: function (organization, data) {
                return $requests.$do(organization.url, $requests.METHODS.UPDATE, data);
            },
            save: function (data) {
                return $requests.$do(BASE_URL, $requests.METHODS.POST, data);
            },
            erase: function (organization) {
                var url = BASE_URL + organization.slug;
                return $requests.$do(url, $requests.METHODS.DELETE);
            },
            get: function (slug) {
                var url = BASE_URL + slug;
                return $requests.$do(url, $requests.METHODS.GET);
            },
            projects: function(client){
                var url = BASE_URL + client + '/projects/';
                return $requests.$do(url, $requests.METHODS.GET);
            }
        };
    })
    .factory('ProjectService', function ($requests) {
        var BASE_URL = '/projects';
        return {
            query: function () {
                return $requests.$do(BASE_URL, $requests.METHODS.GET);
            },
            get: function(slug){
                var url = BASE_URL + '/' + slug;
                return $requests.$do(url, $requests.METHODS.GET);
            }
        };
    });
