var server = require('http').Server();
var io = require('socket.io')(server);

var usernames = [];

io.on('connection', function (socket) {

    console.log('Socket connected!!', socket.id);

    socket.on('project', function (data) {
        var user = data.user;
        var room = data.room;
        if (!usernames[user.username]) {
            socket.room = room;
            socket.username = user.username;
            usernames[user.username] = user;
            socket.join(room);
        }
        socket.emit('onUsersInBoards', {users: usernames});
        socket.broadcast.to(room).emit('onUsersInBoards', {users: usernames});
    });

    socket.on('disconnect', function () {
        delete usernames[socket.username];
        socket.broadcast.to(socket.room).emit('onUsersInBoards', {users: usernames});
        socket.leave(socket.room);
    });
});

server.listen(9000);