import os
import json
import datetime
import tornado.ioloop
import tornado.web
from tornado.concurrent import Future
from tornado import gen

id = 3
data = [
    {"ID": 1, "Message": "This is one comment", "Weather": "Any", "Temperature": 80, "Time": "TBD", "Likes": 0},
    {"ID": 2, "Message": "This is *another* comment", "Weather": "Any", "Temperature": 80, "Time": "TBD", "Likes": 0}
]

class PostBuffer(object):
    def __init__(self, cacheSize=200):
        self.subscribers = set()
        self.cache = data
        self.cacheSize = cacheSize
        
    def waitForMessages(self, cursor=None):
        resultFuture = Future()
        if cursor:
            newCount = 0
            for msg in reversed(self.cache):
                if msg["ID"] == cursor:
                    break;
                newCount += 1
            if newCount:
                resultFuture.set_result(self.cache[-newCount:])
                return resultFuture
        self.subscribers.add(resultFuture)
        return resultFuture
        
    def cancelWait(self, future):
        self.subscribers.remove(future)
        future.set_result([])
        
    def newMessages(self, messages):
        for future in self.subscribers:
            future.set_result(messages)
        self.subscribers = set()
        self.cache.extend(messages)
        if len(self.cache) > self.cacheSize:
            self.cache = self.cache[-self.cacheSize:]

class JsonHandler(tornado.web.RequestHandler):
    """Request handler where requests and responses speak JSON."""
    def prepare(self):
        # Incorporate request JSON into arguments dictionary.
        if self.request.body:
            try:
                json_data = tornado.escape.json_decode(self.request.body)
                self.request.arguments.update(json_data)
            except ValueError:
                message = 'Unable to parse JSON.'
                self.send_error(400, message=message) # Bad Request

        # Set up response dictionary.
        self.response = dict()

    def set_default_headers(self):
        self.set_header('Content-Type', 'application/json')

    '''def write_error(self, status_code, **kwargs):
        if 'message' not in kwargs:
            if status_code == 405:
                kwargs['message'] = 'Invalid HTTP method.'
            else:
                kwargs['message'] = 'Unknown error.'

        self.response = kwargs
        self.write_json()'''

    def write_json(self):
        output = json.dumps(self.response)
        self.write(output)

class PostHandler(JsonHandler):
    @gen.coroutine
    def get(self):
        try:
            cursor = self.get_argument("cursor", 0, True)
            self.future = globalPostBuffer.waitForMessages(cursor=cursor)
            messages = yield self.future
            if self.request.connection.stream.closed():
                return
            self.response = {"data": messages}
            self.write_json()
        except Exception as e:
            print("Error: " + str(e))
        
    @gen.coroutine
    def post(self):
        global id, data
        msg = self.request.arguments["Message"]
        weather = self.request.arguments["Weather"]
        temp = self.request.arguments["Temperature"]
        time = PostHandler.getISODate()
        newPost = self.buildPost(id, msg, weather, int(temp), time, 0)
        future = Future()
        future.set_result(newPost)
        result = yield future
        id += 1
        globalPostBuffer.newMessages([result])
        self.set_status(200)
        
    def on_connection_close(self):
        globalPostBuffer.cancelWait(self.future)
        
    def buildPost(self, id, msg, weather, temp, time, likes):
        return {"ID": id, "Message": msg, "Weather": weather, "Temperature": temp, "Time": time, "Likes": likes}
        
    def getISODate():
        date = datetime.datetime.utcnow().isoformat().split('.')[0]
        return '%sZ'%date

root = os.path.dirname(__file__)
port = 8888

settings = {
    "static_path": root,
    "cookie_secret": "a6301483f77f60",
    "xsrf_cookies": True,
}
application = tornado.web.Application([
    (r"/api/posts/submit", PostHandler),
    (r"/api/posts", PostHandler),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": root, "default_filename": "public/index.html"}),
])

if __name__ == '__main__':
    globalPostBuffer = PostBuffer()
    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()