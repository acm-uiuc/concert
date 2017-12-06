# Concert

Concert will be the new music system in the ACM Office.

Instructions on how to run:

First make sure you have virtualenv installed on your computer (http://docs.python-guide.org/en/latest/dev/virtualenvs/)

Run `virtualenv venv`

Run `source venv/bin/activate`

Run `pip install --upgrade -r requirements.txt`

Execute the commands "celery worker -A celery_tasks" and "python server.py" in a terminal, then navigate to localhost:5000 in your preferred web browser.
