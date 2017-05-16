from flask import Flask, request, url_for
from service import MusicService

app = Flask(__name__)
ms = MusicService()
#Start the continuous service
ms.start()

'''@app.route('/play', methods=['POST'])
def play():
	url = request.values.get('url')

	ms.player.play("tmp/test.mp3")
	return str(ms.player.get_state())'''

@app.route('/pause', methods=['GET'])
def pause():
	return str(ms.player.pause())

@app.route('/volume', methods=['POST'])
def volume():
	val = request.values.get('val')

	return str(ms.player.set_volume(int(val)))

@app.route('/stop', methods=['POST'])
def stop():
	return str(ms.player.stop())

if __name__ == '__main__':
	app.run(debug=True)