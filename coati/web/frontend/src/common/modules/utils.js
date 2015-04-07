(function (angular) {

    var RequestHelper = function (http, q, state, conf, tokens, growl) {
        return {
            METHODS: {
                UPDATE: 'PUT',
                POST: 'POST',
                DELETE: 'DELETE',
                PATCH: 'PATCH',
                GET: 'GET'
            },
            '$do': function (url, method, data, not_default) {

                var token = tokens.get_access_token();
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
                    if (status === 401) {
                        state.go(conf.STATE_401);
                        //Notify
                        growl.addErrorMessage('There was an error on the server side, please try again!');
                    }
                    if(status === 403){
                        state.go(conf.STATE_403);
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

    /**
     * Function that add utils to javascript objects
     * @returns {{isEmpty: 'isEmpty', cleanArray: cleanArray, toUrlString: 'toUrlString'}}
     * @constructor
     */
    var ObjectUtils = function () {
        return {
            'isEmpty': function (obj) {
                return Object.keys(obj).length === 0;
            },
            'isObject': function (val) {
                if (val === null || val === undefined) {
                    return false;
                }
                return ( (typeof val === 'function') || (typeof val === 'object') );
            },
            'cleanArray': function cleanArray(actual) {
                var newArray = [];
                for (var i = 0; i < actual.length; i++) {
                    if (actual[i]) {
                        newArray.push(actual[i]);
                    }
                }
                return newArray;
            },
            'toUrlString': function (obj) {
                var url = this.cleanArray(Object.keys(obj).map(function (k) {
                    if (!angular.isUndefined(obj[k]) && obj[k] !== null && obj[k] !== '') {
                        return encodeURIComponent(k) + '=' + encodeURIComponent(obj[k]);
                    }
                })).join('&');
                return url;
            }
        };
    };

    var UploadHelper = function (up, tokens, conf, growl) {
        return {
            '$do': function (url, files, extra_data, not_default) {
                var token = tokens.get_access_token();
                var headers = {};
                if (token) {
                    headers = {'Authorization': 'Token ' + token};
                }
                var endpoint = (not_default ? url : conf.BASE_API_URL + url);
                return up.upload({
                    headers: headers,
                    url: endpoint,
                    data: extra_data,
                    file: files
                }).error(function(){
                    //Notify
                    growl.addErrorMessage('There was an error on the server side, please try again!');

                });
            }
        };
    };

    var DownloaderHelper = function () {
        return {
            // for non-IE
            'download_file': function (name, mime_type, base64_string) {
                var byteString = atob(base64_string);

                // Convert that text into a byte array.
                var ab = new ArrayBuffer(byteString.length);
                var ia = new Uint8Array(ab);
                for (var i = 0; i < byteString.length; i++) {
                    ia[i] = byteString.charCodeAt(i);
                }
                var blob = new Blob([ia], {type: mime_type + ';charset=utf-8'});
                saveAs(blob, name);
            }
        };
    };

    RequestHelper.$inject = ['$http', '$q', '$state', 'Conf', 'TokenService', 'growl'];
    UploadHelper.$inject = ['$upload', 'TokenService', 'Conf', 'growl'];

    angular.module('Coati.Helpers', ['Coati.Config','Coati.Services.Token',
        'angular-growl',
        'angularFileUpload'])
        .factory('$requests', RequestHelper)
        .factory('$file_uploads', UploadHelper)
        .factory('$file_download', DownloaderHelper)
        .factory('$objects', ObjectUtils);

}(angular));

