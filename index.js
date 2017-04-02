'use strict';

const app = require('express')();
const execSync = require('child_process').execSync;
const http = require('http').Server(app);
const io = require('socket.io')(http);
const fs = require('fs');

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

  socket.on('sending_image', function(msg){
    decodeBase64(msg.image);
    console.log('Received image!');
    execSync('rm nouns.txt');
		execSync('touch nouns.txt');
    execSync('./darknet detect cfg/yolo.cfg yolo.weights out.png');
    execSync('open predictions.png');
  });

  socket.on('disconnect', function(){
    console.log('user disconnected');
  });
});


function decodeBase64(base64Data) {
  fs.writeFileSync("out.png", base64Data, 'base64', function(err) {
    if (err != null) {
      console.log('Error ' + err);
    }
  });
}

// Speaker takes back his most recent sentence
function erase() {
  prev = '';
}

// Speaker has finished speaking
function analyze() {
  execSync('rm google_home_input.txt');
  execSync('touch google_home_input.txt');
  fs.writeFileSync("google_home_input.txt", buffer + prev, 'utf-8', function(err) {
    if (err != null) {
      console.log('Error ' + err);
    }
  });
  console.log('Voice: ' + buffer + prev);
  //TODO: Uncomment this
  // execSync('python3 main.py --text google_home_input.txt');
}

function clear() {
  buffer = '';
  prev = '';
}

http.listen(3000, function(){
  console.log('listening on *:3000');
});
