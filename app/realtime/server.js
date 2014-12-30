var server = require('http').Server();
var io = require('socket.io')(server);


var usernames = [];

var redis = require('redis');


io.on('connection', function (socket) {

    console.log('Socket connected!!', socket.id);

    var client = redis.createClient(6379, '127.0.0.1', {auth_pass: 'c04t1'});
    socket.on('channel', function (data) {
        var room = data.key;
        socket.room = room;
        socket.join(room);
        client.subscribe(room);
    });

    client.on('message', function (channel, message) {
        console.log(message);
        var data = JSON.parse(message);
        socket.broadcast.to(channel).emit(data.type, data.data);
    });

    client.on("error", function (err) {
        console.log('something', err);
    });


    socket.on('disconnect', function () {
        socket.leave(socket.room);
        client.quit();
    });
});

server.listen(9000);