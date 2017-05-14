import os
import sys
import json
import datetime
import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado.concurrent import Future
from tornado import gen

id = 3
data = [
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
        
class WeatherHandler(JsonHandler):

    apikey = "9ad1eeb07ab80737"
    baseUrl = "http://api.wunderground.com/api/" + apikey
    
    @gen.coroutine
    def get(self):
        lat = self.get_argument("lat", None)
        lon = self.get_argument("lon", None)
        weatherFuture = Future()
        if lat is None or lon is None:
            weatherFuture.set_result({"Weather": None, "Temperature": None})
        else:
            if useMockup:
                weatherFuture.set_result({"Weather": "Overcast", "Temperature": 69})
            else:
                handler = lambda response : WeatherHandler.handleResponse(weatherFuture, response)
                query = "%s/%s/q/%s,%s.json"%(WeatherHandler.baseUrl, "conditions", lat, lon)
                httpClient.fetch(query, handler)
        self.response = yield weatherFuture
        self.write_json()
        
    def handleResponse(future, response):
        json_data = tornado.escape.json_decode(response.body)
        current_observation = json_data["current_observation"]
        temp = int(current_observation["temp_f"])
        weather = current_observation["weather"]
        future.set_result({"Weather": weather, "Temperature": temp})
        

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
        global data
        msg = self.request.arguments["Message"]
        weather = self.request.arguments["Weather"]
        temp = self.request.arguments["Temperature"]
        newPost = PostHandler.buildPost(msg, weather, int(temp))
        future = Future()
        future.set_result(newPost)
        result = yield future
        globalPostBuffer.newMessages([result])
        self.set_status(200)
        self.response = {"error": ""}
        self.write_json()
        
    def on_connection_close(self):
        globalPostBuffer.cancelWait(self.future)
        
    def buildPost(msg, weather, temp):
        global id
        newPost = {"ID": id, "Message": msg, "Weather": weather, "Temperature": temp, "Time": PostHandler.getISODate(), "Likes": 0}
        id += 1
        return newPost
        
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
    (r"/api/weather", WeatherHandler),
    (r"/api/posts/submit", PostHandler),
    (r"/api/posts", PostHandler),
    (r"/(.*)", tornado.web.StaticFileHandler, {"path": root, "default_filename": "public/index.html"}),
])

useMockup = False
if __name__ == '__main__':
    try:
        for arg in sys.argv[1:]:
            if arg == "-m":
                useMockup = True
                print("Using mockup...")
        httpClient = AsyncHTTPClient()
        globalPostBuffer = PostBuffer()
        globalPostBuffer.newMessages([PostHandler.buildPost("[System] Welcome!", "Any", 69)])
        application.listen(port)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt as e:
        print(str(e))
        httpClient.close()