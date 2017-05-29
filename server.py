from flask import Flask, request, url_for
from celery_tasks import async_download
from service import MusicService
import validators

app = Flask(__name__)

ms = MusicService()
ms.start()

@app.route('/play', methods=['POST'])
def play():
	return str(ms.player.cur_state())

@app.route('/pause', methods=['POST'])
def pause():
	return str(ms.player.pause())

@app.route('/volume', methods=['POST'])
def volume():
	val = request.values.get('val')
	return str(ms.player.set_volume(int(val)))

@app.route('/skip', methods=['POST'])
def skip():
	return str(ms.play_next())

@app.route('/stop', methods=['POST'])
def stop():
	return str(ms.player.stop())

@app.route('/dl', methods=['POST'])
def download():
	url = request.values.get('url')
	if not validators.url(url):
		return str("Invalid Url")

	async_download.apply_async(args=[url])
	return str("Downloading Song")

@app.route('/position', methods=['POST'])
def set_position():
	percentage = float(request.values.get('percentage'))
	return ms.set_time(percentage)

if __name__ == '__main__':
	app.run(debug=True, use_reloader=False)