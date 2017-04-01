'use strict';

const app = require('express')();
const execSync = require('child_process').execSync;
const http = require('http').Server(app);
const io = require('socket.io')(http);

let buffer = '';
let prev = '';

app.get('/', function(req, res) {
    res.send('<h1>Hello world</h1>');
});

io.origins('*:*');
io.on('connection', function(socket){
  console.log('a user connected');

  // Voice message came in
  socket.on('message', function(msg){
    if (msg === 'erase') {
      erase();
    }
    else if (msg === 'analyze') {
      analyze();
      clear();
    }
    else if (msg === 'clear') {
      clear();
    }
    else {
      buffer += prev;
      prev = msg + '. ';
    }
  });

  socket.on('disconnect', function(){
    console.log('user disconnected');
  });
});

// Speaker takes back his most recent sentence
function erase() {
  prev = '';
}

// Speaker has finished speaking
function analyze() {
  console.log('Voice: ' + buffer + prev);
}

function clear() {
  buffer = '';
  prev = '';
}

http.listen(3000, function(){
  console.log('listening on *:3000');
});
