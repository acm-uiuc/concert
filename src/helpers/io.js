const io = require('socket.io-client')('http://0.0.0.0:5000');

io.on('connect', function() {
	io.emit('connected');
});

export default io;