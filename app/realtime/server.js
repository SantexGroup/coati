var server = require('http').Server();
var io = require('socket.io')(server);


var usernames = [];

var redis = require('redis');


io.on('connection', function (socket) {

    console.log('Socket connected!!', socket.id);

    var client = redis.createClient(6379, '127.0.0.1', {auth_pass: 'c04t1'});

    //Project channel subscription
    socket.on('channel', function (data) {
        console.log(data);
        var room = data.key;
        var user_id = data.user_id;
        socket.room = room;
        socket.join(room);
        socket.username = user_id;
        client.subscribe(room);
    });

    client.on('message', function (channel, message) {
        var data = JSON.parse(message);
        console.log(data.type);
        if (socket.username == data.user_id) {
            socket.broadcast.to(channel).emit(data.type, {});
        }
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