(function (angular) {

    var socket_module = function (rootScope, Conf) {
        var socket;
        if (typeof io !== 'undefined') {


            return {
                init: function(channel, user_id){
                    socket = io.connect(Conf.SOCKET_URL);
                    socket.emit('channel', {'key': channel, 'user_id': user_id});
                },
                on: function (eventName, callback) {
                    socket.on(eventName, function () {
                        var args;
                        args = arguments;
                        rootScope.$apply(function () {
                            callback.apply(socket, args);
                        });
                    });
                },
                emit: function (eventName, data, callback) {
                    socket.emit(eventName, data, function () {
                        var args;
                        args = arguments;
                        rootScope.$apply(function () {
                            if (callback) {
                                callback.apply(socket, args);
                            }
                        });
                    });
                }
            };
        } else {
            return {
                'on': function(eventName, callback){

                },
                'emit': function(eventName, data, callback){

                }
            };
        }
    };

    socket_module.$inject = ['$rootScope', 'Conf'];

    angular.module('Coati.SocketIO', ['Coati.Config'])
        .factory('SocketIO', socket_module);

}(angular));

