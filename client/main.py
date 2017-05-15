import os
import sys
import json
import datetime
import tornado.ioloop
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado.concurrent import Future
from tornado import gen
from Lib import uuid

id = 1
data = {}
userActivity = {}

class PostBuffer(object):
    def __init__(self):
        self.subscribers = set()
        self.cache = data
        
    def getRelevantPosts(postList, conditions):
        return postList
        
    def waitForMessages(self, conditions, count=0):
        resultFuture = Future()
        subscriber = (conditions, resultFuture)
        if count > 0:
            relevantPosts = PostBuffer.getRelevantPosts([post for key, post in self.cache.items()], conditions)
            relevantCount = min(len(relevantPosts), count)
            if relevantCount > 0:
                resultFuture.set_result(relevantPosts[-relevantCount:])
            return subscriber
        self.subscribers.add(subscriber)
        return subscriber
        
    def cancelWait(self, subscriber):
        subscriber[1].set_result([])
        self.subscribers.remove(subscriber)
        
    def newMessages(self, messages):
        for subscriber in set(self.subscribers):
            relevantPosts = PostBuffer.getRelevantPosts(messages, subscriber[0])
            if len(relevantPosts) > 0:
                subscriber[1].set_result(relevantPosts)
                self.subscribers.discard(subscriber)
        for message in messages:
            self.cache[message["ID"]] = message
            
    def addLike(self, postID):
        if postID in self.cache.keys():
            self.changeLike(postID, self.cache[postID]["Likes"] + 1)
    
    def removeLike(self, postID):
        if postID in self.cache.keys():
            self.changeLike(postID, self.cache[postID]["Likes"] - 1)
    
    def changeLike(self, postID, likes):
        post = dict(self.cache[postID])
        post["Likes"] = likes
        self.newMessages([post])
        
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

    def write_error_custom(self, status_code, **kwargs):
        if 'message' not in kwargs:
            if status_code == 405:
                kwargs['message'] = 'Invalid HTTP method.'
            else:
                kwargs['message'] = 'Unknown error.'

        self.response = kwargs
        self.write_json()

    def write_json(self):
        output = json.dumps(self.response)
        self.write(output)        

class PostHandler(JsonHandler):
    @gen.coroutine
    def get(self):
        try:
            userID = self.get_argument("UserID", None, True)
            if userID is None or userID not in userActivity.keys():
                self.write_error_custom(401, message="Unauthorized request")
            else:
                count = int(self.get_argument("count", 0, True))
                conditionsDict = userActivity[userID]["Conditions"]
                conditionsPayload = (conditionsDict["Weather"], conditionsDict["Temperature"])
                self.subscriber = globalPostBuffer.waitForMessages(conditionsPayload, count=count)
                messages = yield self.subscriber[1]
                if self.request.connection.stream.closed():
                    return
                self.response = {"data": messages}
                self.write_json()
        except Exception as e:
            print("Error: " + str(e))
        
    @gen.coroutine
    def post(self):
        userID = self.request.arguments.get("UserID", None)
        if userID is None or userID not in userActivity.keys():
            self.write_error_custom(401, message="Unauthorized request")
        else:
            global data
            msg = self.request.arguments["Message"]
            conditions = userActivity[userID]["Conditions"]
            weather = conditions["Weather"]
            temp = conditions["Temperature"]
            newPost = PostHandler.buildPost(msg, weather, temp)
            future = Future()
            future.set_result(newPost)
            result = yield future
            globalPostBuffer.newMessages([result])
            self.set_status(200)
            self.response = {"error": ""}
            self.write_json()
        
    def on_connection_close(self):
        globalPostBuffer.cancelWait(self.subscriber)
        
    def buildPost(msg, weather, temp):
        global id
        newPost = {"ID": id, "Message": msg, "Weather": weather, "Temperature": temp, "Time": PostHandler.getISODate(), "Likes": 0}
        id += 1
        return newPost
        
    def getISODate():
        date = datetime.datetime.utcnow().isoformat().split('.')[0]
        return '%sZ'%date
        
class LikeHandler(JsonHandler):
    @gen.coroutine
    def post(self):
        userID = self.request.arguments.get("UserID", None)
        if userID is None or userID not in userActivity.keys():
            self.write_error_custom(401, message="Unauthorized request")
        else:
            postID = self.request.arguments.get("PostID", None)
            if postID is None:
                self.write_error_custom(400, message="Bad Post ID")
            else:
                liked = postID in userActivity[userID]["Liked"]
                if liked:
                    userActivity[userID]["Liked"].remove(postID)
                    globalPostBuffer.removeLike(postID)
                else:
                    userActivity[userID]["Liked"].add(postID)
                    globalPostBuffer.addLike(postID)

                likeFuture = Future()
                likeFuture.set_result(not liked)
                result = yield likeFuture
                self.response = {"Liked": result}
                self.write_json()
        
class UserHandler(JsonHandler):
    apikey = "9ad1eeb07ab80737"
    baseUrl = "http://api.wunderground.com/api/" + apikey
    
    @gen.coroutine
    def get(self):
        userFuture = Future()
        
        # determine guid
        guid = None
        while guid is None or str(guid) in userActivity.keys():
            guid = uuid.uuid4()
            
        # get and set user data
        ip = self.request.remote_ip
        self.getLocation(ip, lambda response: self.getConditions(response.body, lambda lat, lon, response2: self.setUserFuture(userFuture, str(guid), lat, lon, response2.body)))
        userEntry = yield userFuture
        userID = userEntry["UserID"]
        userActivity[userID] = userEntry
        self.response = {"UserID": userID}
        self.write_json()
        
    def getLocation(self, ip, handler):
        if ip is None:
            query = "https://ipinfo.io/json"
        else:
            query = "https://ipinfo.io/%s/json"%ip
        httpClient.fetch(query, lambda response : self.locationHandler(response, handler))
        
    def locationHandler(self, response, handler):
        json_ipinfo = tornado.escape.json_decode(response.body)
        if "bogon" in json_ipinfo and json_ipinfo["bogon"]:
            self.getLocation(None, handler)
        else:
            handler(response)
    
    def getConditions(self, ipinfo, handler):
        json_ipinfo = tornado.escape.json_decode(ipinfo)
        locSplit = json_ipinfo["loc"].split(",")
        lat = float(locSplit[0])
        lon = float(locSplit[1])
        
        query = "%s/%s/q/%s,%s.json"%(UserHandler.baseUrl, "conditions", lat, lon)
        httpClient.fetch(query, lambda response: handler(lat, lon, response))
    
    def setUserFuture(self, userFuture, userID, lat, lon, fullConditions):
        json_fullConditions = tornado.escape.json_decode(fullConditions)
        current_observation = json_fullConditions["current_observation"]
        temp = int(current_observation["temp_f"])
        weather = current_observation["weather"]
        
        userFuture.set_result({"UserID": userID, "Loc": {"Lat": lat, "Lon": lon}, "Conditions": {"Weather": weather, "Temperature": temp}, "Liked": set()})
        

root = os.path.dirname(__file__)
port = 8888

settings = {
    "static_path": root,
    "cookie_secret": "a6301483f77f60",
    "xsrf_cookies": True,
}
application = tornado.web.Application([
    (r"/api/checkin", UserHandler),
    (r"/api/posts/submit", PostHandler),
    (r"/api/posts/like", LikeHandler),
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