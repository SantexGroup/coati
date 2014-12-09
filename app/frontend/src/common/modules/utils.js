(function(angular){

    var Tokens = function(){
        return {
            'get_token': function () {
                var token_data = window.sessionStorage.getItem('token_data');
                if (token_data != null) {
                    token_data = JSON.parse(token_data);
                    var expire_in_seconds = token_data['expire'];
                    var token = token_data['token'];
                    var now = new Date().getTime();
                    var expire = now + (expire_in_seconds * 1000);
                    if (expire >= now) {
                        return token;
                    }
                }
                return null;
            },
            'store_token': function (token, expire) {
                var data = {
                    'token': token,
                    'expire': expire
                };
                window.sessionStorage.setItem('token_data', JSON.stringify(data));
            }
        };
    };

    var RequestHelper = function(http, q, state, conf, tokens){
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
                if (token) {
                    http.defaults.headers.common['Authorization'] = 'Token ' + token;
                }

                var results = q.defer();
                http({
                    url: (not_default ? url : conf.BASE_API_URL + url),
                    method: method,
                    data: data
                }).success(function (body) {
                    results.resolve(body);
                }).error(function (data, status) {
                    if (status == 401) {
                        state.go('login');
                    }
                    results.reject({
                        'message': data,
                        'code': status
                    });
                });
                return results.promise;
            }
        };
    };

    RequestHelper.$inject = ['$http', '$q', '$state', 'Conf', 'tokens'];

    angular.module('Coati.Helpers', ['Coati.Config'])
        .factory('tokens', Tokens)
        .factory('$requests', RequestHelper);

}(angular));

