# Scheduler demo app

A demo of a web service using Flask and PostgreSQL.



## Libraries

Consider using [Flask-RESTful](https://flask-restful.readthedocs.io/).

## Setup Environment

The demo is built using Python 3, Flask, PostgreSQL, and React.js. The following is the Mac OS dev setup. Later, this could be moved to Docker?

    brew update
    brew install postgresql

&ldquo;To have launchd start postgresql now and restart at login:
  brew services start postgresql
Or, if you don't want/need a background service you can just run:
  pg_ctl -D /usr/local/var/postgres start&rdquo;

    virtualenv -p python3 virtualenvpy3
    pip install flask
    pip install psycopg2
    pip install python-dateutil
    pip install nose


### Node / React setup
* see: https://www.codementor.io/tamizhvendan/tutorials/beginner-guide-setup-reactjs-environment-npm-babel-6-webpack-du107r9zr

    brew install node
    mkdir my/project/dir
    npm i --save webpack
    npm i --save babel-loader babel-core babel-preset-es2015 babel-preset-react
    npm i --save react react-dom
    npm i --save whatwg-fetch
    npm i --save lodash
    npm i --save moment

Put webpack in watch mode:
    node ./node_modules/.bin/webpack -d --progress --colors --watch

