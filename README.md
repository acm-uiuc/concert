# Concert

Concert is the new music system for the ACM Office: https://concert.acm.illinois.edu/
### [IOS APP](https://github.com/acm-uiuc/office-iOS) 
### [ANDROID APP](https://github.com/acm-uiuc/office-android)

## Prerequisites

1. Make sure you have Python 3 installed: `python3 --version` (if you don't have it, install [here](https://www.python.org/downloads/))
2. Make sure you have virtualenv installed: `virtualenv --version` (if you don't have it, install with `pip3 install virtualenv`)
3. Make sure you have MongoDB installed: `mongod --version` (if you don't have it, install [here](https://docs.mongodb.com/manual/installation/#tutorials))
4. Make sure you have Redis installed: `redis-server --version` (if you don't have it, install [here](https://redis.io/topics/quickstart))
5. Make sure you have PulseAudio installed: `pulseaudio --version`
    - If you don't have PulseAudio installed, install with either `brew install pulseaudio` or `apt-get install pulseaudio` (which requires having either [brew](https://brew.sh) or [apt-get](https://wiki.debian.org/apt-get) on your system)
6. Install the VLC media player desktop application [here](https://www.videolan.org/vlc/index.html)

## Setup
1. In this project's main directory, run `virtualenv venv`
2. Run `source venv/bin/activate`
3. Run `pip3 install --upgrade -r requirements.txt`
4. Copy `config.py.template` into a new file called `config.py`. In that file, enter your various API keys and tokens.

## Usage
1. Start Redis: Run `systemctl start redis`
    - to check if it is currently running, replace `start` with `status`
        - replace `start` with `restart` if it is already running
2. Start MongoDB: Run `systemctl start mongodb` (may be `mongod` depending on your version)
    - use `status` and `restart` to check if it is currently running
3. In the project's main directory, run `source venv/bin/activate` (if not already in a virual enviroment) and then run `python3 main.py`
    - The client will be served at http://localhost:5000
