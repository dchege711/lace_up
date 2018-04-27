# Navigating the Code Base

* LaceUp is a web application. There is the frontend (what users interact with, the pretty stuff), there's a backend (where the magic actually happens). [This looks kinda right](https://www.reddit.com/r/ProgrammerHumor/comments/7zfgwg/frontend_vs_backend/).

* For the front end, we're using plain old vanilla JavaScript. For the backend, we're using [Flask](http://flask.pocoo.org/docs/0.12/quickstart/#rendering-templates), a lightweight Python framework for web apps.

* For illustrative purposes, let's assume that you wish to create a 'My Account` page.

## [./static/ folder](https://github.com/dchege711/lace_up/tree/master/static)

* This contains static assets such as images and JavaScript scripts that run in the web app's background. 

* For example, you might add ./static/HandleUserActions.js, and in HandleUserActions.js you might include functions such as `updateUserPreferences(), deactivateUserAccount(), makeHTTPRequest()`, etc.

## [./templates/ folder](https://github.com/dchege711/lace_up/tree/master/templates) 

* Contains the HTML files that the user sees. The folder is named 'templates' because Flask expects the folder containing the HTML files to be named as such.

* For example, you might add ./templates/account_page.html. In account_page.html, you might have some HTML/CSS, a form element, a reference to ./static/HandleUserActions.js, and calls to relevant functions such as `updateUserPreferences()`

## [Router: app_handler.py]

* app_handler.py is our router. Routers know how to handle requests, e.g. https://lace-up.herokuapp.com/login/ is treated differently from https://lace-up.herokuapp.com/register/.

* For example, the app's homepage might include a link to 'My Account' with `href='/account/'`. Once the link is clicked, the web application will then look for `@app.route('/account/', methods=["POST", "GET"])` which tells the web app what to do. In case of a `GET` request, the function might as well return "account_page.html".


## [./back_end_scripts/ folder](https://github.com/dchege711/lace_up/tree/master/back_end_scripts)

* We could have had all the backend code within `app_handler.py`, but that would have gotten all messy. We therefore created a folder that defines Python functions and classes that help make `app_handler.py` a bit more organized. 

* The `sys.path.insert(0, os.path.join(os.getcwd(), "back_end_scripts"))` line in `app_handler.py` allows `app_handler.py` to call functions defined in ./back_end_scripts/*

* For example, you might modify ./back_end_scripts/user_actions.py such that you can request the user account details from the database. Take care when writing new code, there's a balance between reinventing the wheel and breaking current functionality.

## Miscellaneous

* `.gitignore` filters out some of the files that need not be tracked on Git. For instance, running a Python class automatically creates a .pyc file. We don't need to track this .pyc file since it's automatically generated.

* `Procfile` is required by Heroku. In our case, it tells Heroku several things: we're running a web application; we'll be using gunicorn (which is a Python HTTP server), and Heroku should start by running app_handler.py.

* `requirements.txt` allows us to keep track of our package dependencies. Heroku also reads this file so that it knows which packages need to be installed in the dyno that will be running our application.

* `runtime.txt` tells Heroku to use Python 3.6.4 when running our web app.