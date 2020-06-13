from app.main import app 
from werkzeug.wsgi import DispatcherMiddleware

from test_dash import app as app1
  
application = DispatcherMiddleware(flask_app, {
    '/app1': app1.server,
})

if __name__ == "__main__": 
        app.run()