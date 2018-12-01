const io = require('socket.io-client')('http://0.0.0.0:5000');

io.on('connect', () => {
	io.emit('c_connected');
});

io.on('s_artwork_available', (state) => {
    window.appComponent.updateClient(JSON.parse(state));
});

export default io;