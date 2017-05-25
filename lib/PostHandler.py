from lib.JsonHandler import JsonHandler
from lib.PostBuffer import PostBuffer
import tornado.web
from tornado.concurrent import Future
from tornado import gen

class PostHandler(JsonHandler):
    timeRangeSeconds = 2 * 3600
    temperatureRange = 5
    
    def initialize(self, postBuffer, emergencyBuffer, httpClient, userActivity, weatherCategories):
        self.postBuffer = postBuffer
        self.userActivity = userActivity
        self.subscriber = None

    @gen.coroutine
    def get(self):
        try:
            userID = self.get_argument("UserID", None, True)
            if userID is None or userID not in self.userActivity.keys():
                self.write_error_custom(401, message="Unauthorized request")
            else:
                # Retrieve our subscriber (conditions, future)
                count = int(self.get_argument("count", 0, True))
                endID = int(self.get_argument("endID", -1, True))
                conditionsDict = self.userActivity[userID]["Conditions"]
                conditionsPayload = (conditionsDict["Weather"], conditionsDict["Temperature"])
                self.subscriber = self.postBuffer.subscribe(lambda post : PostHandler.postRelevantFn(post, conditionsPayload), count=count, endID=endID)
                
                # Yield for new messages
                messages = yield self.postBuffer.getFuture(self.subscriber)
                if self.request.connection.stream.closed():
                    return
                    
                # Fulfill the long poll
                self.response = {"data": messages}
                self.write_json()
        except Exception as e:
            print("Error: " + str(e))
        
    @gen.coroutine
    def post(self):
        userID = self.request.arguments.get("UserID", None)
        if userID is None or userID not in self.userActivity.keys():
            self.write_error_custom(401, message="Unauthorized request")
        else:
            # Get the message and build the post
            msg = self.request.arguments["Message"]
            conditions = self.userActivity[userID]["Conditions"]
            weather = conditions["Weather"]
            temp = conditions["Temperature"]
            newPost = self.postBuffer.buildPost(msg, weather, temp)
            
            # Yield via a future for async triage purposes
            future = Future()
            future.set_result(newPost)
            
            # ...and update the buffer (which triggers long poll updates)
            result = yield future
            self.postBuffer.publish([result])
            
            # simple OK response
            self.set_status(200)
            self.response = {"error": ""}
            self.write_json()
            
    def postRelevantFn(post, conditions):
        timeDiffSeconds = PostBuffer.getDateDiffSeconds(PostBuffer.getISODate(), post["Time"])
        temperatureDiff = abs(post["Temperature"] - conditions[1])
        return (post["Weather"] == conditions[0]
            and timeDiffSeconds >= 0
            and timeDiffSeconds <= PostHandler.timeRangeSeconds
            and temperatureDiff <= PostHandler.temperatureRange)
        
    def on_connection_close(self):
        if self.subscriber is not None:
            self.postBuffer.cancelWait(self.subscriber)