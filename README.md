# Concert
[![Build Status](https://travis-ci.org/acm-uiuc/concert.svg?branch=master)](https://travis-ci.org/acm-uiuc/concert)

Concert is ACM's music system for the office. You can find a link to the website [here](https://concert.acm.illinois.edu/)

## Getting Started

These instructions will get you a copy of the project up and running on your local (unix-based) machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

* Python3
  * [MacOS](http://docs.python-guide.org/en/latest/starting/install3/osx/)
  * [Linux](http://docs.python-guide.org/en/latest/starting/install3/linux/)
* [pip](https://pip.pypa.io/en/stable/installing/)
* [MongoDB](https://docs.mongodb.com/manual/installation/)
* [Redis](https://redis.io/topics/quickstart)
* VLC
  * [MaxOs](https://wiki.videolan.org/Documentation:Installing_VLC/#Mac_OS_X)
  * [Linux](https://packages.ubuntu.com/trusty/libdevel/libvlc-dev)

### Installing and Running

Instructions on how to get Concert up and running on your local environment

#### Clone this Repo
```
git clone https://github.com/acm-uiuc/concert
```

#### Install Python Requirements
```
pip3 install requirements
```

#### Start Redis
```
redis-server
```

#### Start MongoDB

On Linux
```
sudo service mongod start
```
On Mac
```
mongod
```

#### Running Concert

In one terminal window run the flask app
```
python3 app.py
```

In another terminal window start up celery
```
celery worker -A downloader
```

## Running the tests

Tests are currently a WIP, but currently there are some tests for testing song downloading functionality
```
python3 -m tests.songtests
```

## Authors

* **Tommy Yu** - *Initial work, feature development* - [tommypacker](https://github.com/tommypacker)
* **Rauhul Varma** - *iOS Development* - [rauhul](https://github.com/rauhul)
* **Sujay Patwardhan** - *iOS Development* - [sujaypat](https://github.com/sujaypat)

See also the list of [contributors](https://github.com/acm-uiuc/concert/graphs/contributors) who participated in this project.

## License

This project is licensed under the NCSA License - see the [LICENSE.md](LICENSE) file for details

## Acknowledgments

* Aashish for getting concert deployed
* Childish Gambino for making Redbone
