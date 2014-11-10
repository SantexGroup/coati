var SOCKET_URL = 'http://localhost:9000';


angular.module('Coati.Utils', ['ngCookies', 'Coati.Config'])
    .factory('tokens', function(){
        return {
            'get_token': function(){
                var token_data = window.sessionStorage.getItem('token_data');
                if(token_data != null){
                   token_data = JSON.parse(token_data);
                   var expire_in_seconds = token_data['expire'];
                   var token = token_data['token'];
                   var now = new Date().getTime();
                   var expire = now + (expire_in_seconds * 1000);
                   if(expire >= now){
                       return token;
                   }
                }
                return null;
            },
            'store_token': function(token, expire){
                var data = {
                    'token': token,
                    'expire': expire
                };
                window.sessionStorage.setItem('token_data', JSON.stringify(data));
            }
        };
    })
    .factory('$requests', function ($http, $q, $state, $cookies, Conf, tokens) {
        return {
            METHODS: {
                UPDATE: 'PUT',
                POST: 'POST',
                DELETE: 'DELETE',
                PATCH: 'PATCH',
                GET: 'GET'
            },
            '$do': function (url, method, data, not_default) {

                var token = tokens.get_token();
                if(token) {
                    $http.defaults.headers.common['Authorization'] = 'Token ' + token;
                }

                var results = $q.defer();
                $http({
                    url: (not_default ? url : Conf.BASE_API_URL + url),
                    method: method,
                    data: data
                }).success(function (body) {
                    results.resolve(body);
                }).error(function (data, status) {
                    if(status == 401){
                        $state.go('login');
                    }
                    results.reject({
                        'message': data,
                        'code': status
                    });
                });
                return results.promise;
            }
        };
    });

angular.module('Coati.ApiServices', ['Coati.Utils', 'Coati.Config'])

    .factory('LoginService', function($requests, Conf){
        return {
            'auth': function(provider){
                window.location.href = '/auth/authenticate?provider='+provider+'&callback='+Conf.CALLBACK_URL;
            }
        };
    })
    .factory('UserService', function ($requests) {
        var BASE_URL = '/users/';
        return {
            'me': function () {
                var url = BASE_URL + 'me';
                return $requests.$do(url, $requests.METHODS.GET);
            },
            'search': function (q) {
                var url = BASE_URL + 'search/' + q;
                return $requests.$do(url, $requests.METHODS.GET);
            },
            'save': function (user) {
                var url = BASE_URL + 'me';
                return $requests.$do(url, $requests.METHODS.UPDATE, user);
            }
        };
    })
    .factory('ProjectService', function ($requests) {
        return {
            'query': function () {
                return $requests.$do('/projects', $requests.METHODS.GET);
            },
            'get': function (slug) {
                var url = '/project/' + slug;
                return $requests.$do(url, $requests.METHODS.GET);
            }
        };
    })
    .factory('TicketService', function ($requests) {
        return {
            'query': function (project_pk) {
                return $requests.$do('/tickets/' + project_pk, $requests.METHODS.GET);
            },
            'save': function(project_pk, tkt){
                return $requests.$do('/tickets/' + project_pk, $requests.METHODS.POST, tkt);
            },
            'update_order': function(project_pk, data){
                return $requests.$do('/tickets/' + project_pk + '/order', $requests.METHODS.POST, data);
            }
        };
    })
    .factory('SprintService', function ($requests) {
        return {
            'query': function (project_pk) {
                return $requests.$do('/sprints/' + project_pk, $requests.METHODS.GET);
            },
            'save': function(project_pk, sp){
                return $requests.$do('/sprints/' + project_pk, $requests.METHODS.POST, sp);
            },
            'erase': function(sprint_id){
                return $requests.$do('/sprint/' + sprint_id, $requests.METHODS.DELETE);
            },
            'update_order': function(project_pk, data){
                return $requests.$do('/sprints/' + project_pk + '/order', $requests.METHODS.POST, data);
            }
        };
    });
