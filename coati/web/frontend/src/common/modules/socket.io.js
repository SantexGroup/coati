(function (angular) {

    var socket_module = function (log, rootScope, Conf) {
        var socket, actual_channel;
        if (typeof io !== 'undefined') {
            var ch = io;
            return {
                init: function () {
                    socket = ch.connect(Conf.SOCKET_URL);
                },
                user_channel: function (user_id) {
                    socket.emit('user_channel', {
                        'user_id': user_id
                    });
                },
                channel: function (channel) {
                    if(channel !== actual_channel) {
                        rootScope.$watch('user', function (nv) {
                            if (nv !== undefined) {
                                actual_channel = channel;
                                socket.emit('channel', {
                                    'key': channel,
                                    'user_id': rootScope.user._id.$oid
                                });
                            }
                        });
                    }
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
                'on': function (eventName, callback) {
                    log.debug(eventName, callback);
                },
                'emit': function (eventName, data, callback) {
                    log.debug(eventName, data, callback);
                },
                'init': function (channel, user_id) {
                    log.debug(channel, user_id);
                },
                'user_channel': function (user_id) {
                    log.debug(user_id);
                },
                'channel': function (channel) {
                    log.debug(channel);
                }
            };
        }
    };

    socket_module.$inject = ['$log', '$rootScope', 'Conf'];

    angular.module('Coati.SocketIO', ['Coati.Config'])
        .factory('SocketIO', socket_module);

}(angular));

