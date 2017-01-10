# Scheduler demo app

A demo of a web service using Flask and PostgreSQL and a web client built with React.


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


### Tests

To run tests, be in the root directory of the project. Add `-s` flag to see more output.

    nosetests -v tests


### Node / React setup
* see: [Setting Up a React.js Environment Using Npm, Babel 6 and Webpack](https://www.codementor.io/tamizhvendan/tutorials/beginner-guide-setup-reactjs-environment-npm-babel-6-webpack-du107r9zr)

We'll use [nodejs](https://nodejs.org/) to run webpack and babel in our development environment. This lets us code in React's [.jsx](https://facebook.github.io/react/docs/jsx-in-depth.html) declarative syntax and the [ES6](http://es6-features.org/) dialect of javascript. Fetch will perform our HTTP requests and [momentjs] will make dealing with dates much nicer.

    brew install node
    mkdir my/project/dir
    npm i --save webpack
    npm i --save babel-loader babel-core babel-preset-es2015 babel-preset-react
    npm i --save react react-dom
    npm i --save whatwg-fetch
    npm i --save moment

Put webpack in watch mode:

    node ./node_modules/.bin/webpack -d --progress --colors --watch

