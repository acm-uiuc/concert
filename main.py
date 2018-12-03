from gevent import monkey
monkey.patch_all()

from config import config
import concert

if __name__ == "__main__":
    concert.start_concert(config)