(function (angular) {

    var socket_module = function (rootScope, log, Conf) {
        var socket, actual_channel;
        if (typeof io !== 'undefined') {
            return {
                init: function () {
                    socket = io.connect(Conf.SOCKET_URL);
                },
                user_channel: function (user_id) {
                    socket.emit('user_channel', {
                        'user_id': user_id
                    });
                },
                channel: function (channel) {
                    if(channel !== actual_channel) {
                        rootScope.$watch('user', function (nv, ov) {
                            if (nv !== undefined && nv !== ov) {
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
                    log.info(eventName, callback);
                },
                'emit': function (eventName, data, callback) {
                    log.info(eventName, data, callback);
                },
                'init': function (channel, user_id) {
                    log.info(channel, user_id);
                },
                'user_channel': function (user_id) {
                    log.info(user_id);
                },
                'channel': function (channel) {
                    log.info(channel);
                }
            };
        }
    };

    socket_module.$inject = ['$rootScope', '$log', 'Conf'];

    angular.module('Coati.SocketIO', ['Coati.Config'])
        .factory('SocketIO', socket_module);

}(angular));

