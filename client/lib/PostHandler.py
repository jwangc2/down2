from lib.JsonHandler import JsonHandler
import tornado.web
from tornado.concurrent import Future
from tornado import gen

class PostHandler(JsonHandler):
    def initialize(self, postBuffer, httpClient, userActivity):
        self.postBuffer = postBuffer
        self.userActivity = userActivity

    @gen.coroutine
    def get(self):
        try:
            userID = self.get_argument("UserID", None, True)
            if userID is None or userID not in self.userActivity.keys():
                self.write_error_custom(401, message="Unauthorized request")
            else:
                # Retrieve our subscriber (conditions, future)
                count = int(self.get_argument("count", 0, True))
                conditionsDict = self.userActivity[userID]["Conditions"]
                conditionsPayload = (conditionsDict["Weather"], conditionsDict["Temperature"])
                self.subscriber = self.postBuffer.waitForMessages(conditionsPayload, count=count)
                
                # Yield for new messages
                messages = yield self.subscriber[1]
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
            self.postBuffer.newMessages([result])
            
            # simple OK response
            self.set_status(200)
            self.response = {"error": ""}
            self.write_json()
        
    def on_connection_close(self):
        self.postBuffer.cancelWait(self.subscriber)