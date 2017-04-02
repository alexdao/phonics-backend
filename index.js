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
    else if (msg === 'load') {
      execSync('cp mobydickdata/p2.csv app/data/p2.csv');
      execSync('python3 main.py --demo');
    }
    else if (msg === 'demo') {
      execSync('cp story_demo/p2.csv app/data/p2.csv')
      execSync('python3 main.py --demo');
    }
    else {
      buffer += prev;
      prev = msg + '. ';
    }
  });

  socket.on('sending_image', function(msg){
    decodeBase64(msg.image);
    console.log('Received image!');
    execSync('rm app/data/nouns.txt');
		execSync('touch app/data/nouns.txt');
    execSync('./darknet detect cfg/yolo.cfg yolo.weights out.png');
    //execSync('open predictions.png');
    execSync('cp predictions.png app/data/phonphoto.png')
    execSync('python3 main.py --nouns app/data/nouns.txt')
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
  execSync('python3 main.py --text google_home_input.txt');
}

function clear() {
  buffer = '';
  prev = '';
}

http.listen(3000, function(){
  console.log('listening on *:3000');
});
