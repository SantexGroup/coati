var server = require('http').Server();
var io = require('socket.io')(server);


var redis = require('redis');



io.on('connection', function (socket) {
    var client = redis.createClient(6379, '127.0.0.1', {auth_pass: 'c04t1'});
    var client2 = redis.createClient(6379, '127.0.0.1', {auth_pass: 'c04t1'});
    console.log('Socket connected!!', socket.id);

    socket.on('user_channel', function (data) {
        console.log(socket.id, ' Joined user channel', data.user_id);
        var user_id = data.user_id;
        socket.username = user_id;
        client2.subscribe(user_id);
    });

    client2.on('message', function (channel, message) {
        var data = JSON.parse(message);
        if(socket.username != data.user_id) {
            socket.emit('notify', {});
        }
    });

    client2.on("error", function (err) {
        console.log('something', err);
    });


    //Project channel subscription
    socket.on('channel', function (data) {
        console.log(socket.id, ' Joined project channel', data.user_id);
        var channel = data.key;
        var user_id = data.user_id;
        socket.room = data.key;
        socket.join(data.key);
        socket.username = user_id;
        client.subscribe(channel);
    });

    client.on('message', function (channel, message) {
        var data = JSON.parse(message);
        if (socket.username == data.user_id) {
            socket.broadcast.to(socket.room).emit(data.type, {});
        }
    });

    client.on("error", function (err) {
        console.log('something', err);
    });


    socket.on('disconnect', function () {
        console.log('Disconnecting Socket:', socket.id);
        socket.leave(socket.room);
        client.quit();
        client2.quit();
    });
});

server.listen(8001);