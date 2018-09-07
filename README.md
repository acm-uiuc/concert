# Concert

Concert is the new music system for the ACM Office: https://concert.acm.illinois.edu/

## Prerequisites

1. Make sure you have Python 3 installed: `python3 --version`
  - If you don't have Python 3 installed, install [here](https://www.python.org/downloads/)
- Make sure you have virtualenv installed: `virtualenv --version`
  - If you don't have virtualenv installed, install with `pip3 install virtualenv`
- Make sure you have MongoDB installed: `mongod --version`
  - If you don't have MongoDB installed, install [here](https://docs.mongodb.com/manual/installation/#tutorials)
- Make sure you have Redis installed: `redis-server --version`
  - If you don't have Redis installed, install [here](https://redis.io/topics/quickstart)
- Make sure you have PulseAudio installed: `pulseaudio --version`
  - If you don't have PulseAudio installed, install with either `brew install pulseaudio` or `apt-get install pulseaudio` (which requires having either [brew](https://brew.sh) or [apt-get](https://wiki.debian.org/apt-get) on your system)
- Install the VLC media player desktop application [here](https://www.videolan.org/vlc/index.html)

## Setup
1. In this project's main directory, run `virtualenv venv`
- Run `source venv/bin/activate`
- Run `pip3 install --upgrade -r requirements.txt`

## Usage
1. In a separate terminal session, run `redis-server` (to start Redis)
- In another separate terminal session, run `mongod` (to start MongoDB)
- Lastly, in another separate terminal session, run `python3 main.py`
  - The client will be served at http://localhost:5000
