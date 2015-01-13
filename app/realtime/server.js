var server = require('http').Server();
var io = require('socket.io')(server);


var redis = require('redis');


io.on('connection', function (socket) {

    console.log('Socket connected!!', socket.id);

    var client = redis.createClient(6379, '127.0.0.1', {auth_pass: 'c04t1'});

    //Project channel subscription
    socket.on('channel', function (data) {
        var channel = data.key;
        var user_id = data.user_id;
        socket.room = data.key;
        socket.join(data.key);
        socket.username = user_id;
        client.subscribe(channel);
    });

    client.on('message', function (channel, message) {
        console.log(channel, message);
        var data = JSON.parse(message);
        if (socket.username == data.user_id) {
            socket.broadcast.to(socket.room).emit(data.type, {});
        }
        socket.broadcast.to(socket.room).emit('notify', {});
    });

    client.on("error", function (err) {
        console.log('something', err);
    });


    socket.on('disconnect', function () {
        console.log('Disconnecting Socket:', socket.id);
        socket.leave(socket.room);
        client.quit();
    });
});

server.listen(9000);