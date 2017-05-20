from celery import Celery
import downloader as dl

CELERY_NAME = 'concert'
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

celery = Celery(CELERY_NAME, backend=CELERY_RESULT_BACKEND, broker=CELERY_BROKER_URL)

@celery.task
def async_download(url):
	dl.download_song('https://www.youtube.com/watch?v=8mtA9GvpzwU')