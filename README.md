## cpydemo

This is a simple example project for cherrypy that implements a ReSTful API
with SQLAlchemy and a SQLite3 database serving as the backend

## Starting the app

To start the project, simply do the following:

0. Optionally, create a virtualenv and switch to it.
1. Install the requirements using pip: `pip install -r requirements.txt`
2. Run `python start_app.py "/cpydemo"`
3. Open a web browser or ReST client (I like Postman) and navigate to
http://localhost:8080/cpydemo

You can them perform GET, POST, PUT, PATCH, and DELETE HTTP methods at a given
endpoint to read (GET), update (POST, PATCH), create (POST, PUT), and
delete (DELETE) endpoints.

## Code source
The SQLAlchemy plugin and tool code was cribbed from
http://www.defuze.org/archives/222-integrating-sqlalchemy-into-a-cherrypy-application.html