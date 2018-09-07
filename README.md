# Concert

Concert will be the new music system in the ACM Office.

Instructions on how to run:

First make sure you have virtualenv installed on your computer (http://docs.python-guide.org/en/latest/dev/virtualenvs/)
Also make sure you have VLC bindings and mongodb installed 

Concert targets Python 3 

Run `virtualenv venv`

Run `source venv/bin/activate`

Run `pip install --upgrade -r requirements.txt`

Install redis, vlc, pluseaudio and mongodb

To start, begin by starting ```redis-server``` and mongodb ```sudo service mongod start``` 

Then run ```python3 main.py```  

The client will be served at ```http://localhost:5000```
