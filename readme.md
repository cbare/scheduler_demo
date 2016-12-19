# Scheduler demo app

A demo of a web service using Flask and PostgreSQL.



## Libraries

Consider using [Flask-RESTful](https://flask-restful.readthedocs.io/).

## Setup Environment

brew update
brew install postgresql

    To have launchd start postgresql now and restart at login:
      brew services start postgresql
    Or, if you don't want/need a background service you can just run:
      pg_ctl -D /usr/local/var/postgres start


virtualenv -p python3 virtualenvpy3
pip install flask
pip install psycopg2
pip install python-dateutil


