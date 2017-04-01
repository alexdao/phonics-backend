'use strict';

const app = require('express')();
const execSync = require('child_process').execSync;
const http = require('http').Server(app);
const io = require('socket.io')(http);

app.get('/', function(req, res) {
    res.send('<h1>Hello world</h1>');
}); 

io.origins('*:*');
io.on('connection', function(socket){
  console.log('a user connected');

  // Voice message came in
  socket.on('message', function(msg){
    console.log('Voice: ' + msg);
  });

  socket.on('disconnect', function(){
    console.log('user disconnected');
  });
});

http.listen(3000, function(){
  console.log('listening on *:3000');
});
